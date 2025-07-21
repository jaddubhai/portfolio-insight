#!/usr/bin/env python3
"""
Test suite for the BacktestService class.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.backtest import (
    BacktestService,
    BacktestPeriod,
    calculate_cagr,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
)


class TestBacktestCalculations:
    """Test class for backtest calculation functions."""

    def test_calculate_cagr(self):
        """Test CAGR calculation."""
        # Test normal case
        cagr = calculate_cagr(1000, 1200, 2)
        expected = (1200 / 1000) ** (1 / 2) - 1
        assert abs(cagr - expected) < 0.0001

        # Test edge cases
        assert calculate_cagr(0, 1000, 1) == 0.0
        assert calculate_cagr(1000, 1000, 0) == 0.0
        assert calculate_cagr(-1000, 1000, 1) == 0.0
        print("✓ CAGR calculation tests passed")

    def test_calculate_max_drawdown(self):
        """Test maximum drawdown calculation."""
        # Test normal case
        values = [1000, 1100, 1050, 950, 1200, 900, 1300]
        max_dd = calculate_max_drawdown(values)

        # Maximum peak was 1200, minimum after that was 900
        expected = (1200 - 900) / 1200
        assert abs(max_dd - expected) < 0.0001

        # Test edge cases
        assert calculate_max_drawdown([]) == 0.0
        assert calculate_max_drawdown([1000]) == 0.0
        assert calculate_max_drawdown([1000, 1100, 1200]) == 0.0  # Only gains
        print("✓ Max drawdown calculation tests passed")

    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        # Test normal case with positive returns
        returns = [0.01, 0.02, -0.01, 0.015, 0.005] * 50  # 250 returns
        sharpe = calculate_sharpe_ratio(returns, 0.02)
        assert isinstance(sharpe, float)

        # Test edge cases
        assert calculate_sharpe_ratio([]) == 0.0
        assert calculate_sharpe_ratio([0.01]) == 0.0
        assert calculate_sharpe_ratio([0.01, 0.01, 0.01]) == 0.0  # No volatility
        print("✓ Sharpe ratio calculation tests passed")

    def test_backtest_period(self):
        """Test BacktestPeriod functionality."""
        # Test date range calculation
        start_1y, end_1y = BacktestPeriod.get_date_range(BacktestPeriod.ONE_YEAR)
        start_5y, end_5y = BacktestPeriod.get_date_range(BacktestPeriod.FIVE_YEARS)
        start_10y, end_10y = BacktestPeriod.get_date_range(BacktestPeriod.TEN_YEARS)

        # Check that periods are correctly spaced
        assert (end_1y - start_1y).days >= 360
        assert (end_5y - start_5y).days >= 1800
        assert (end_10y - start_10y).days >= 3600

        # Test invalid period
        try:
            BacktestPeriod.get_date_range("INVALID")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        print("✓ BacktestPeriod tests passed")


class TestBacktestService:
    """Test class for BacktestService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = BacktestService()
        self.mock_allocation_service = Mock()
        self.mock_alpaca_client = Mock()

    def test_initialization(self):
        """Test BacktestService initialization."""
        service = BacktestService()
        assert service.alpaca_client is None
        assert service.allocation_service is None
        assert not service.is_configured()
        print("✓ Initialization test passed")

    def test_set_allocation_service(self):
        """Test setting allocation service."""
        result = self.service.set_allocation_service(self.mock_allocation_service)

        assert result["success"] is True
        assert self.service.allocation_service == self.mock_allocation_service
        print("✓ Set allocation service test passed")

    @patch("portfolio.backtest.ALPACA_AVAILABLE", True)
    @patch("portfolio.backtest.StockHistoricalDataClient")
    def test_set_alpaca_credentials_success(self, mock_client_class):
        """Test successful Alpaca credentials setup."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = self.service.set_alpaca_credentials("test_key", "test_secret")

        assert result["success"] is True
        assert result["environment"] == "paper"
        assert self.service.alpaca_client == mock_client
        mock_client_class.assert_called_once_with("test_key", "test_secret")
        print("✓ Set Alpaca credentials success test passed")

    @patch("portfolio.backtest.ALPACA_AVAILABLE", False)
    def test_set_alpaca_credentials_no_library(self):
        """Test Alpaca credentials setup when library is not available."""
        result = self.service.set_alpaca_credentials("test_key", "test_secret")

        assert result["success"] is False
        assert "alpaca-py library is not installed" in result["error"]
        print("✓ Set Alpaca credentials no library test passed")

    def test_get_portfolio_allocation_no_service(self):
        """Test portfolio allocation without allocation service."""
        result = self.service.get_portfolio_allocation()

        assert result["success"] is False
        assert "Allocation service not set" in result["error"]
        print("✓ Get portfolio allocation no service test passed")

    def test_get_portfolio_allocation_success(self):
        """Test successful portfolio allocation retrieval."""
        self.service.allocation_service = self.mock_allocation_service

        mock_allocation = {
            "success": True,
            "current_allocation": {"AAPL": 5000.0, "GOOGL": 3000.0},
        }
        self.mock_allocation_service.get_current_portfolio_allocation.return_value = (
            mock_allocation
        )

        result = self.service.get_portfolio_allocation()

        assert result["success"] is True
        assert result["current_allocation"] == {"AAPL": 5000.0, "GOOGL": 3000.0}
        print("✓ Get portfolio allocation success test passed")

    def test_get_historical_data_no_client(self):
        """Test historical data retrieval without Alpaca client."""
        result = self.service.get_historical_data(
            ["AAPL"], datetime.now(), datetime.now()
        )

        assert result["success"] is False
        assert "Alpaca client not configured" in result["error"]
        print("✓ Get historical data no client test passed")

    def test_get_historical_data_no_symbols(self):
        """Test historical data retrieval with no symbols."""
        self.service.alpaca_client = self.mock_alpaca_client

        result = self.service.get_historical_data([], datetime.now(), datetime.now())

        assert result["success"] is False
        assert "No symbols provided" in result["error"]
        print("✓ Get historical data no symbols test passed")

    def test_get_historical_data_success(self):
        """Test successful historical data retrieval."""
        self.service.alpaca_client = self.mock_alpaca_client

        # Mock historical data response
        mock_bar = Mock()
        mock_bar.timestamp = datetime(2023, 1, 1)
        mock_bar.open = 150.0
        mock_bar.high = 155.0
        mock_bar.low = 148.0
        mock_bar.close = 152.0
        mock_bar.volume = 1000000

        mock_bars = Mock()
        mock_bars.data = {"AAPL": [mock_bar]}

        self.mock_alpaca_client.get_stock_bars.return_value = mock_bars

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        result = self.service.get_historical_data(["AAPL"], start_date, end_date)

        assert result["success"] is True
        assert "AAPL" in result["historical_data"]
        assert len(result["historical_data"]["AAPL"]) == 1
        assert result["historical_data"]["AAPL"][0]["close"] == 152.0
        print("✓ Get historical data success test passed")

    def test_calculate_portfolio_performance_success(self):
        """Test successful portfolio performance calculation."""
        allocation = {"AAPL": 5000.0, "GOOGL": 3000.0}

        # Mock historical data
        historical_data = {
            "AAPL": [
                {"date": date(2023, 1, 1), "close": 150.0},
                {"date": date(2023, 1, 2), "close": 155.0},
                {"date": date(2023, 1, 3), "close": 160.0},
            ],
            "GOOGL": [
                {"date": date(2023, 1, 1), "close": 100.0},
                {"date": date(2023, 1, 2), "close": 105.0},
                {"date": date(2023, 1, 3), "close": 110.0},
            ],
        }

        result = self.service.calculate_portfolio_performance(
            allocation, historical_data, 100000
        )

        assert result["success"] is True
        assert "performance_metrics" in result
        assert "cagr" in result["performance_metrics"]
        assert "max_drawdown" in result["performance_metrics"]
        assert "sharpe_ratio" in result["performance_metrics"]
        assert len(result["portfolio_values"]) == 3
        print("✓ Calculate portfolio performance success test passed")

    def test_calculate_portfolio_performance_missing_data(self):
        """Test portfolio performance calculation with missing data."""
        result = self.service.calculate_portfolio_performance({}, {}, 100000)

        assert result["success"] is False
        assert "Missing allocation or historical data" in result["error"]
        print("✓ Calculate portfolio performance missing data test passed")

    def test_run_backtest_invalid_period(self):
        """Test backtest with invalid period."""
        result = self.service.run_backtest("INVALID")

        assert result["success"] is False
        assert "Unsupported period" in result["error"]
        print("✓ Run backtest invalid period test passed")

    def test_run_backtest_no_allocation_service(self):
        """Test backtest without allocation service."""
        result = self.service.run_backtest("1Y")

        assert result["success"] is False
        assert "Allocation service not set" in result["error"]
        print("✓ Run backtest no allocation service test passed")

    def test_run_multiple_period_backtest(self):
        """Test multiple period backtest."""
        # Mock the run_backtest method to return successful results
        self.service.run_backtest = Mock()
        mock_result = {
            "success": True,
            "performance_metrics": {
                "cagr": 0.08,
                "total_return": 0.10,
                "max_drawdown": 0.05,
                "sharpe_ratio": 1.2,
            },
        }
        self.service.run_backtest.return_value = mock_result

        result = self.service.run_multiple_period_backtest(["1Y", "5Y"])

        assert result["success"] is True
        assert "1Y" in result["results"]
        assert "5Y" in result["results"]
        assert "comparison" in result["summary"]
        print("✓ Run multiple period backtest test passed")

    def test_service_status_methods(self):
        """Test service status checking methods."""
        # Test initial state
        assert not self.service.is_configured()

        status = self.service.get_service_status()
        assert not status["alpaca_configured"]
        assert not status["allocation_service_configured"]
        assert not status["fully_configured"]

        # Test with services configured
        self.service.alpaca_client = self.mock_alpaca_client
        self.service.allocation_service = self.mock_allocation_service

        assert self.service.is_configured()

        status = self.service.get_service_status()
        assert status["alpaca_configured"]
        assert status["allocation_service_configured"]
        assert status["fully_configured"]

        print("✓ Service status methods test passed")


def run_backtest_service_tests():
    """Run all BacktestService tests."""
    print("Running BacktestService tests...")
    print("=" * 60)

    # Test calculation functions
    calc_test_class = TestBacktestCalculations()
    calc_methods = [
        method for method in dir(calc_test_class) if method.startswith("test_")
    ]

    for test_method in calc_methods:
        getattr(calc_test_class, test_method)()

    # Test service class
    service_test_class = TestBacktestService()
    service_methods = [
        method for method in dir(service_test_class) if method.startswith("test_")
    ]

    for test_method in service_methods:
        service_test_class.setup_method()
        getattr(service_test_class, test_method)()

    print("=" * 60)
    print("✓ All BacktestService tests passed!")


def test_integration_scenario():
    """Test a realistic integration scenario."""
    print("\nTesting integration scenario...")

    # This simulates a complete workflow:
    # 1. Configure BacktestService
    # 2. Set allocation service
    # 3. Run backtest

    service = BacktestService()

    # Mock allocation service
    mock_allocation_service = Mock()
    mock_allocation_service.get_current_portfolio_allocation.return_value = {
        "success": True,
        "current_allocation": {"AAPL": 6000.0, "GOOGL": 4000.0},
    }

    # Set allocation service
    result = service.set_allocation_service(mock_allocation_service)
    assert result["success"], f"Failed to set allocation service: {result}"

    # Test service status
    status = service.get_service_status()
    assert status["allocation_service_configured"]
    assert not status["fully_configured"]  # No Alpaca client yet

    print("✓ Integration scenario test passed")


if __name__ == "__main__":
    # Run backtest service tests
    run_backtest_service_tests()

    # Run integration scenario
    test_integration_scenario()

    print("\n" + "=" * 60)
    print("✓ All BacktestService tests completed successfully!")
