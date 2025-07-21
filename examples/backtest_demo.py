#!/usr/bin/env python3
"""
Example usage of the BacktestService for portfolio backtesting.

This script demonstrates how to use the BacktestService to:
1. Set up the service with allocation and Alpaca data
2. Run backtests for different time periods
3. Analyze portfolio performance metrics

Note: This example uses mock data for demonstration purposes.
In a real scenario, you would use actual Alpaca API credentials.
"""

import sys
import os
from datetime import datetime, date
from unittest.mock import Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.backtest import BacktestService, BacktestPeriod
from portfolio.allocation import AllocationService


def create_mock_allocation_service():
    """Create a mock allocation service with sample portfolio data."""
    mock_service = Mock()

    # Mock current portfolio allocation
    mock_service.get_current_portfolio_allocation.return_value = {
        "success": True,
        "current_allocation": {
            "AAPL": 10000.0,  # $10,000 in Apple
            "GOOGL": 8000.0,  # $8,000 in Google
            "MSFT": 6000.0,  # $6,000 in Microsoft
            "TSLA": 4000.0,  # $4,000 in Tesla
            "AMZN": 2000.0,  # $2,000 in Amazon
        },
        "positions": [
            {"symbol": "AAPL", "market_value": 10000.0},
            {"symbol": "GOOGL", "market_value": 8000.0},
            {"symbol": "MSFT", "market_value": 6000.0},
            {"symbol": "TSLA", "market_value": 4000.0},
            {"symbol": "AMZN", "market_value": 2000.0},
        ],
    }

    return mock_service


def create_mock_historical_data():
    """Create mock historical data for demonstration."""
    # Simulate 1 year of daily data with some volatility
    base_date = date(2023, 1, 1)

    historical_data = {"AAPL": [], "GOOGL": [], "MSFT": [], "TSLA": [], "AMZN": []}

    # Starting prices
    prices = {"AAPL": 150.0, "GOOGL": 100.0, "MSFT": 250.0, "TSLA": 200.0, "AMZN": 90.0}

    # Generate 252 trading days of data
    for i in range(252):
        current_date = date(2023, 1, 1)

        for symbol in historical_data.keys():
            # Simulate some price movement (random walk with slight upward bias)
            import random

            change = random.gauss(0.001, 0.02)  # Small positive bias with volatility
            prices[symbol] *= 1 + change

            historical_data[symbol].append(
                {
                    "date": current_date,
                    "open": prices[symbol] * 0.99,
                    "high": prices[symbol] * 1.02,
                    "low": prices[symbol] * 0.98,
                    "close": prices[symbol],
                    "volume": random.randint(1000000, 5000000),
                }
            )

    return historical_data


def demonstrate_backtest_service():
    """Demonstrate the BacktestService functionality."""
    print("BacktestService Demo")
    print("=" * 50)

    # 1. Create BacktestService instance
    backtest_service = BacktestService()
    print("✓ BacktestService created")

    # 2. Set up allocation service (normally this would be a real AllocationService)
    allocation_service = create_mock_allocation_service()
    result = backtest_service.set_allocation_service(allocation_service)
    print(f"✓ Allocation service configured: {result['message']}")

    # 3. Check service status
    status = backtest_service.get_service_status()
    print(f"Service status:")
    print(
        f"  - Allocation service: {'✓' if status['allocation_service_configured'] else '✗'}"
    )
    print(f"  - Alpaca client: {'✓' if status['alpaca_configured'] else '✗'}")
    print(f"  - Fully configured: {'✓' if status['fully_configured'] else '✗'}")
    print()

    # 4. Get current portfolio allocation
    portfolio_result = backtest_service.get_portfolio_allocation()
    if portfolio_result["success"]:
        allocation = portfolio_result["current_allocation"]
        total_value = sum(allocation.values())

        print("Current Portfolio Allocation:")
        for symbol, value in allocation.items():
            percentage = (value / total_value) * 100
            print(f"  {symbol}: ${value:,.2f} ({percentage:.1f}%)")
        print(f"  Total: ${total_value:,.2f}")
        print()

    # 5. Demonstrate portfolio performance calculation
    print("Portfolio Performance Calculation Demo:")

    # Create mock historical data
    historical_data = create_mock_historical_data()

    performance_result = backtest_service.calculate_portfolio_performance(
        allocation, historical_data, 100000
    )

    if performance_result["success"]:
        metrics = performance_result["performance_metrics"]

        print("Performance Metrics:")
        print(f"  CAGR: {metrics['cagr']:.2%}")
        print(f"  Total Return: {metrics['total_return']:.2%}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"  Start Value: ${metrics['start_value']:,.2f}")
        print(f"  End Value: ${metrics['end_value']:,.2f}")
        print(f"  Years: {metrics['years']:.2f}")
        print()
    else:
        print(f"Performance calculation failed: {performance_result['error']}")

    # 6. Demonstrate supported periods
    print("Supported Backtest Periods:")
    periods = [
        BacktestPeriod.ONE_YEAR,
        BacktestPeriod.FIVE_YEARS,
        BacktestPeriod.TEN_YEARS,
    ]

    for period in periods:
        start_date, end_date = BacktestPeriod.get_date_range(period)
        days = (end_date - start_date).days
        print(
            f"  {period}: {days} days ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
        )
    print()

    # 7. Show what a real backtest would look like (without Alpaca credentials)
    print("Sample Backtest Results (would require Alpaca API credentials):")

    sample_results = {
        "1Y": {"cagr": 0.12, "max_drawdown": 0.08, "sharpe_ratio": 1.5},
        "5Y": {"cagr": 0.09, "max_drawdown": 0.15, "sharpe_ratio": 1.2},
        "10Y": {"cagr": 0.11, "max_drawdown": 0.22, "sharpe_ratio": 1.1},
    }

    print("Period | CAGR   | Max DD | Sharpe")
    print("-------|--------|--------|-------")
    for period, metrics in sample_results.items():
        print(
            f"{period:6} | {metrics['cagr']:5.1%} | {metrics['max_drawdown']:5.1%} | {metrics['sharpe_ratio']:5.2f}"
        )

    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("\nTo use with real data:")
    print("1. Get Alpaca API credentials (paper or live)")
    print("2. Call backtest_service.set_alpaca_credentials(api_key, secret_key)")
    print("3. Use backtest_service.run_backtest(period) for real backtesting")


if __name__ == "__main__":
    demonstrate_backtest_service()
