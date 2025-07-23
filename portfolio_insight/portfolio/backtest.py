from typing import Dict, Optional, List, Any, Tuple
import math
import sys
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

# Import utils from the parent package
from .. import utils

try:
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False


class BacktestPeriod:
    """Enumeration of supported backtest periods."""

    ONE_YEAR = "1Y"
    FIVE_YEARS = "5Y"
    TEN_YEARS = "10Y"

    @classmethod
    def get_date_range(cls, period: str) -> Tuple[datetime, datetime]:
        """
        Get start and end dates for a given period.

        Args:
            period: Period string (1Y, 5Y, 10Y)

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = datetime.now()

        if period == cls.ONE_YEAR:
            start_date = end_date - relativedelta(years=1)
        elif period == cls.FIVE_YEARS:
            start_date = end_date - relativedelta(years=5)
        elif period == cls.TEN_YEARS:
            start_date = end_date - relativedelta(years=10)
        else:
            raise ValueError(f"Unsupported period: {period}")

        return start_date, end_date


def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Args:
        start_value: Initial portfolio value
        end_value: Final portfolio value
        years: Number of years

    Returns:
        CAGR as a decimal (e.g., 0.08 for 8%)
    """
    if start_value <= 0 or years <= 0:
        return 0.0

    return (end_value / start_value) ** (1 / years) - 1


def calculate_max_drawdown(portfolio_values: List[float]) -> float:
    """
    Calculate maximum drawdown from a series of portfolio values.

    Args:
        portfolio_values: List of portfolio values over time

    Returns:
        Maximum drawdown as a decimal (e.g., 0.15 for 15% drawdown)
    """
    if not portfolio_values or len(portfolio_values) < 2:
        return 0.0

    peak = portfolio_values[0]
    max_drawdown = 0.0

    for value in portfolio_values:
        if value > peak:
            peak = value

        drawdown = (peak - value) / peak
        max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe ratio from a series of returns.

    Args:
        returns: List of periodic returns
        risk_free_rate: Annual risk-free rate (default 2%)

    Returns:
        Sharpe ratio
    """
    if not returns or len(returns) < 2:
        return 0.0

    returns_array = np.array(returns)

    # Convert annual risk-free rate to daily
    daily_risk_free = (1 + risk_free_rate) ** (1 / 252) - 1

    excess_returns = returns_array - daily_risk_free

    if np.std(excess_returns) == 0:
        return 0.0

    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)


class BacktestService:
    """
    End-to-end service for portfolio backtesting that integrates portfolio allocation
    with historical market data from Alpaca API to calculate performance metrics.
    """

    def __init__(self):
        """Initialize the backtest service."""
        self.alpaca_client = None
        self.allocation_service = None

    def set_alpaca_credentials(
        self, api_key: str, secret_key: str, paper: bool = True
    ) -> Dict[str, Any]:
        """
        Set Alpaca API credentials for historical data access.

        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            paper: Whether to use paper trading environment

        Returns:
            Dictionary containing success status
        """
        if not ALPACA_AVAILABLE:
            return {
                "success": False,
                "error": "alpaca-py library is not installed. Please install it to use backtesting features.",
            }

        try:
            self.alpaca_client = StockHistoricalDataClient(api_key, secret_key)
            return {
                "success": True,
                "message": "Alpaca credentials set successfully",
                "environment": "paper" if paper else "live",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to set Alpaca credentials: {str(e)}",
            }

    def set_allocation_service(self, allocation_service) -> Dict[str, Any]:
        """
        Set the allocation service for getting current portfolio data.

        Args:
            allocation_service: Instance of AllocationService

        Returns:
            Dictionary containing success status
        """
        try:
            self.allocation_service = allocation_service
            return {"success": True, "message": "Allocation service set successfully"}
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to set allocation service: {str(e)}",
            }

    def get_portfolio_allocation(self) -> Dict[str, Any]:
        """
        Get current portfolio allocation using the allocation service.

        Returns:
            Dictionary containing current allocation or error information
        """
        if not self.allocation_service:
            return {
                "success": False,
                "error": "Allocation service not set. Please call set_allocation_service() first.",
            }

        try:
            return self.allocation_service.get_current_portfolio_allocation()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get portfolio allocation: {str(e)}",
            }

    def get_historical_data(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Fetch historical price data from Alpaca for the specified symbols and date range.

        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            Dictionary containing historical data or error information
        """
        if not self.alpaca_client:
            return {
                "success": False,
                "error": "Alpaca client not configured. Please call set_alpaca_credentials() first.",
            }

        if not symbols:
            return {
                "success": False,
                "error": "No symbols provided for historical data fetch.",
            }

        try:
            # Create request for historical bars
            request_params = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date,
            )

            # Fetch the data
            bars = self.alpaca_client.get_stock_bars(request_params)

            # Convert to a more usable format
            historical_data = {}
            for symbol in symbols:
                if symbol in bars.data:
                    symbol_data = []
                    for bar in bars.data[symbol]:
                        symbol_data.append(
                            {
                                "date": bar.timestamp.date(),
                                "open": float(bar.open),
                                "high": float(bar.high),
                                "low": float(bar.low),
                                "close": float(bar.close),
                                "volume": int(bar.volume),
                            }
                        )
                    historical_data[symbol] = symbol_data
                else:
                    historical_data[symbol] = []

            return {
                "success": True,
                "historical_data": historical_data,
                "symbols": symbols,
                "start_date": start_date.date(),
                "end_date": end_date.date(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch historical data: {str(e)}",
            }

    def calculate_portfolio_performance(
        self,
        allocation: Dict[str, float],
        historical_data: Dict[str, List[Dict]],
        initial_value: float = 100000,
    ) -> Dict[str, Any]:
        """
        Calculate portfolio performance metrics based on allocation and historical data.

        Args:
            allocation: Portfolio allocation as {symbol: value}
            historical_data: Historical price data from get_historical_data
            initial_value: Initial portfolio value for calculation

        Returns:
            Dictionary containing performance metrics
        """
        try:
            if not allocation or not historical_data:
                return {
                    "success": False,
                    "error": "Missing allocation or historical data",
                }

            # Calculate total current value for allocation percentages
            total_current_value = sum(allocation.values())
            if total_current_value <= 0:
                return {
                    "success": False,
                    "error": "Invalid portfolio allocation - total value must be positive",
                }

            # Find common date range across all symbols
            all_dates = set()
            for symbol, data in historical_data.items():
                if symbol in allocation and data:
                    symbol_dates = set(item["date"] for item in data)
                    if not all_dates:
                        all_dates = symbol_dates
                    else:
                        all_dates = all_dates.intersection(symbol_dates)

            if not all_dates:
                return {
                    "success": False,
                    "error": "No common dates found across symbols",
                }

            # Sort dates
            sorted_dates = sorted(all_dates)

            # Calculate portfolio value for each date
            portfolio_values = []
            daily_returns = []

            for i, date in enumerate(sorted_dates):
                portfolio_value = 0.0

                for symbol, current_value in allocation.items():
                    if symbol in historical_data and historical_data[symbol]:
                        # Find price for this date
                        symbol_data = {
                            item["date"]: item for item in historical_data[symbol]
                        }
                        if date in symbol_data:
                            price = symbol_data[date]["close"]

                            # Calculate allocation percentage
                            allocation_pct = current_value / total_current_value

                            # For first date, calculate shares based on initial investment
                            if i == 0:
                                if not hasattr(self, "_shares"):
                                    self._shares = {}
                                first_price = price
                                shares = (allocation_pct * initial_value) / first_price
                                self._shares[symbol] = shares

                            # Calculate current value based on shares
                            if hasattr(self, "_shares") and symbol in self._shares:
                                portfolio_value += self._shares[symbol] * price

                portfolio_values.append(portfolio_value)

                # Calculate daily return
                if i > 0 and portfolio_values[i - 1] > 0:
                    daily_return = (
                        portfolio_value - portfolio_values[i - 1]
                    ) / portfolio_values[i - 1]
                    daily_returns.append(daily_return)

            if len(portfolio_values) < 2:
                return {
                    "success": False,
                    "error": "Insufficient data for performance calculation",
                }

            # Calculate performance metrics
            start_value = portfolio_values[0]
            end_value = portfolio_values[-1]
            years = len(sorted_dates) / 252  # Approximate trading days per year

            cagr = calculate_cagr(start_value, end_value, years)
            max_drawdown = calculate_max_drawdown(portfolio_values)
            sharpe_ratio = calculate_sharpe_ratio(daily_returns)

            # Calculate total return
            total_return = (
                (end_value - start_value) / start_value if start_value > 0 else 0
            )

            return {
                "success": True,
                "performance_metrics": {
                    "cagr": cagr,
                    "total_return": total_return,
                    "max_drawdown": max_drawdown,
                    "sharpe_ratio": sharpe_ratio,
                    "start_value": start_value,
                    "end_value": end_value,
                    "years": years,
                    "trading_days": len(sorted_dates),
                },
                "portfolio_values": portfolio_values,
                "dates": sorted_dates,
                "daily_returns": daily_returns,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate portfolio performance: {str(e)}",
            }
        finally:
            # Clean up temporary shares calculation
            if hasattr(self, "_shares"):
                delattr(self, "_shares")

    def run_backtest(
        self, period: str, initial_value: float = 100000
    ) -> Dict[str, Any]:
        """
        Run a complete backtest for the specified period using current portfolio allocation.

        Args:
            period: Backtest period (1Y, 5Y, 10Y)
            initial_value: Initial portfolio value for backtest

        Returns:
            Dictionary containing complete backtest results
        """
        try:
            # Validate period
            if period not in [
                BacktestPeriod.ONE_YEAR,
                BacktestPeriod.FIVE_YEARS,
                BacktestPeriod.TEN_YEARS,
            ]:
                return {
                    "success": False,
                    "error": f"Unsupported period: {period}. Supported periods: 1Y, 5Y, 10Y",
                }

            # Get portfolio allocation
            allocation_result = self.get_portfolio_allocation()
            if not allocation_result["success"]:
                return allocation_result

            allocation = allocation_result["current_allocation"]
            if not allocation:
                return {
                    "success": False,
                    "error": "No current portfolio allocation found",
                }

            # Get date range for the period
            start_date, end_date = BacktestPeriod.get_date_range(period)

            # Get symbols from allocation
            symbols = list(allocation.keys())

            # Fetch historical data
            historical_result = self.get_historical_data(symbols, start_date, end_date)
            if not historical_result["success"]:
                return historical_result

            historical_data = historical_result["historical_data"]

            # Calculate performance
            performance_result = self.calculate_portfolio_performance(
                allocation, historical_data, initial_value
            )
            if not performance_result["success"]:
                return performance_result

            # Compile results
            return {
                "success": True,
                "backtest_summary": {
                    "period": period,
                    "start_date": start_date.date(),
                    "end_date": end_date.date(),
                    "initial_value": initial_value,
                    "symbols": symbols,
                    "allocation": allocation,
                },
                "performance_metrics": performance_result["performance_metrics"],
                "detailed_data": {
                    "portfolio_values": performance_result["portfolio_values"],
                    "dates": performance_result["dates"],
                    "daily_returns": performance_result["daily_returns"],
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to run backtest: {str(e)}"}

    def run_multiple_period_backtest(
        self, periods: List[str] = None, initial_value: float = 100000
    ) -> Dict[str, Any]:
        """
        Run backtests for multiple periods and compare results.

        Args:
            periods: List of periods to test (defaults to all supported periods)
            initial_value: Initial portfolio value for backtest

        Returns:
            Dictionary containing results for all periods
        """
        if periods is None:
            periods = [
                BacktestPeriod.ONE_YEAR,
                BacktestPeriod.FIVE_YEARS,
                BacktestPeriod.TEN_YEARS,
            ]

        results = {}

        for period in periods:
            result = self.run_backtest(period, initial_value)
            results[period] = result

        # Calculate summary statistics
        successful_results = {
            p: r for p, r in results.items() if r.get("success", False)
        }

        if successful_results:
            summary = {
                "periods_tested": list(successful_results.keys()),
                "comparison": {},
            }

            for period, result in successful_results.items():
                metrics = result["performance_metrics"]
                summary["comparison"][period] = {
                    "cagr": metrics["cagr"],
                    "total_return": metrics["total_return"],
                    "max_drawdown": metrics["max_drawdown"],
                    "sharpe_ratio": metrics["sharpe_ratio"],
                }
        else:
            summary = {"error": "No successful backtest results"}

        return {
            "success": len(successful_results) > 0,
            "results": results,
            "summary": summary,
        }

    def is_configured(self) -> bool:
        """Check if the service is properly configured."""
        return self.alpaca_client is not None and self.allocation_service is not None

    def get_service_status(self) -> Dict[str, Any]:
        """Get current service configuration status."""
        return {
            "alpaca_configured": self.alpaca_client is not None,
            "allocation_service_configured": self.allocation_service is not None,
            "fully_configured": self.is_configured(),
            "alpaca_available": ALPACA_AVAILABLE,
        }


# Dummy function for backwards compatibility
def run_backtest(portfolio, start_date, end_date):
    """
    Legacy function for backwards compatibility.
    Use BacktestService for full functionality.
    """
    return {
        "error": "Legacy function. Please use BacktestService for full backtesting functionality."
    }
