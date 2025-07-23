#!/usr/bin/env python3
"""
Integration example showing how BacktestService works with AllocationService.

This demonstrates the complete workflow for Module 2 of the application:
1. Get current portfolio allocation
2. Run backtest analysis for different time periods
3. Display comprehensive performance metrics
"""

import sys
import os
from unittest.mock import Mock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio_insight.portfolio.backtest import BacktestService, BacktestPeriod
from portfolio_insight.portfolio.allocation import AllocationService


def create_realistic_mock_services():
    """Create realistic mock services for demonstration."""

    # Mock AllocationService with a diversified portfolio
    allocation_service = Mock(spec=AllocationService)
    allocation_service.get_current_portfolio_allocation.return_value = {
        "success": True,
        "current_allocation": {
            "SPY": 15000.0,  # S&P 500 ETF - 30%
            "QQQ": 10000.0,  # NASDAQ ETF - 20%
            "VTI": 8000.0,  # Total Stock Market ETF - 16%
            "AAPL": 7000.0,  # Apple - 14%
            "MSFT": 5000.0,  # Microsoft - 10%
            "GOOGL": 3000.0,  # Google - 6%
            "BND": 2000.0,  # Bond ETF - 4%
        },
        "positions": [
            {"symbol": "SPY", "market_value": 15000.0, "shares": 35},
            {"symbol": "QQQ", "market_value": 10000.0, "shares": 28},
            {"symbol": "VTI", "market_value": 8000.0, "shares": 35},
            {"symbol": "AAPL", "market_value": 7000.0, "shares": 40},
            {"symbol": "MSFT", "market_value": 5000.0, "shares": 15},
            {"symbol": "GOOGL", "market_value": 3000.0, "shares": 18},
            {"symbol": "BND", "market_value": 2000.0, "shares": 25},
        ],
    }

    return allocation_service


def simulate_backtest_results():
    """Simulate realistic backtest results for different periods."""
    return {
        BacktestPeriod.ONE_YEAR: {
            "success": True,
            "backtest_summary": {
                "period": "1Y",
                "initial_value": 50000,
                "symbols": ["SPY", "QQQ", "VTI", "AAPL", "MSFT", "GOOGL", "BND"],
            },
            "performance_metrics": {
                "cagr": 0.15,
                "total_return": 0.15,
                "max_drawdown": 0.08,
                "sharpe_ratio": 1.8,
                "start_value": 50000,
                "end_value": 57500,
                "years": 1.0,
            },
        },
        BacktestPeriod.FIVE_YEARS: {
            "success": True,
            "backtest_summary": {
                "period": "5Y",
                "initial_value": 50000,
                "symbols": ["SPY", "QQQ", "VTI", "AAPL", "MSFT", "GOOGL", "BND"],
            },
            "performance_metrics": {
                "cagr": 0.12,
                "total_return": 0.76,
                "max_drawdown": 0.18,
                "sharpe_ratio": 1.4,
                "start_value": 50000,
                "end_value": 88000,
                "years": 5.0,
            },
        },
        BacktestPeriod.TEN_YEARS: {
            "success": True,
            "backtest_summary": {
                "period": "10Y",
                "initial_value": 50000,
                "symbols": ["SPY", "QQQ", "VTI", "AAPL", "MSFT", "GOOGL", "BND"],
            },
            "performance_metrics": {
                "cagr": 0.095,
                "total_return": 1.47,
                "max_drawdown": 0.25,
                "sharpe_ratio": 1.2,
                "start_value": 50000,
                "end_value": 123500,
                "years": 10.0,
            },
        },
    }


def display_portfolio_summary(allocation_result):
    """Display current portfolio allocation summary."""
    if not allocation_result["success"]:
        print(f"Error getting portfolio: {allocation_result['error']}")
        return

    allocation = allocation_result["current_allocation"]
    total_value = sum(allocation.values())

    print("Current Portfolio Allocation:")
    print("=" * 50)
    print(f"{'Symbol':<8} {'Value':<12} {'Weight':<10} {'Type'}")
    print("-" * 50)

    # Categorize holdings
    for symbol, value in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
        weight = (value / total_value) * 100

        # Simple categorization
        if symbol in ["SPY", "QQQ", "VTI"]:
            asset_type = "ETF"
        elif symbol in ["BND"]:
            asset_type = "Bond ETF"
        else:
            asset_type = "Stock"

        print(f"{symbol:<8} ${value:>9,.0f} {weight:>7.1f}% {asset_type}")

    print("-" * 50)
    print(f"{'Total':<8} ${total_value:>9,.0f} {100:>7.1f}%")
    print()


def display_backtest_results(results):
    """Display backtest results in a formatted table."""
    print("Backtest Performance Analysis:")
    print("=" * 80)

    # Header
    print(
        f"{'Period':<8} {'CAGR':<8} {'Total Ret':<10} {'Max DD':<10} {'Sharpe':<8} {'End Value':<12}"
    )
    print("-" * 80)

    # Results for each period
    for period in [
        BacktestPeriod.ONE_YEAR,
        BacktestPeriod.FIVE_YEARS,
        BacktestPeriod.TEN_YEARS,
    ]:
        if period in results and results[period]["success"]:
            metrics = results[period]["performance_metrics"]

            print(
                f"{period:<8} "
                f"{metrics['cagr']:>6.1%} "
                f"{metrics['total_return']:>8.1%} "
                f"{metrics['max_drawdown']:>8.1%} "
                f"{metrics['sharpe_ratio']:>7.2f} "
                f"${metrics['end_value']:>10,.0f}"
            )
        else:
            error_msg = results.get(period, {}).get("error", "No data")
            print(f"{period:<8} Error: {error_msg}")

    print("-" * 80)


def analyze_performance(results):
    """Provide performance analysis and insights."""
    print("\nPerformance Analysis:")
    print("=" * 50)

    successful_results = {p: r for p, r in results.items() if r.get("success", False)}

    if not successful_results:
        print("No successful backtest results to analyze.")
        return

    # CAGR analysis
    cagrs = {
        period: result["performance_metrics"]["cagr"]
        for period, result in successful_results.items()
    }

    best_cagr_period = max(cagrs, key=cagrs.get)
    worst_cagr_period = min(cagrs, key=cagrs.get)

    print(f"• Best CAGR: {best_cagr_period} ({cagrs[best_cagr_period]:.1%})")
    print(f"• Worst CAGR: {worst_cagr_period} ({cagrs[worst_cagr_period]:.1%})")

    # Risk analysis
    drawdowns = {
        period: result["performance_metrics"]["max_drawdown"]
        for period, result in successful_results.items()
    }

    lowest_dd_period = min(drawdowns, key=drawdowns.get)
    highest_dd_period = max(drawdowns, key=drawdowns.get)

    print(
        f"• Lowest Risk: {lowest_dd_period} ({drawdowns[lowest_dd_period]:.1%} max drawdown)"
    )
    print(
        f"• Highest Risk: {highest_dd_period} ({drawdowns[highest_dd_period]:.1%} max drawdown)"
    )

    # Risk-adjusted returns
    sharpes = {
        period: result["performance_metrics"]["sharpe_ratio"]
        for period, result in successful_results.items()
    }

    best_sharpe_period = max(sharpes, key=sharpes.get)

    print(
        f"• Best Risk-Adjusted Return: {best_sharpe_period} (Sharpe: {sharpes[best_sharpe_period]:.2f})"
    )

    # Investment growth analysis
    if BacktestPeriod.TEN_YEARS in successful_results:
        ten_year = successful_results[BacktestPeriod.TEN_YEARS]["performance_metrics"]
        initial = ten_year["start_value"]
        final = ten_year["end_value"]
        growth = final - initial

        print(f"\n10-Year Investment Growth:")
        print(f"• Initial Investment: ${initial:,.0f}")
        print(f"• Final Value: ${final:,.0f}")
        print(f"• Total Growth: ${growth:,.0f}")
        print(f"• Money Multiplier: {final/initial:.2f}x")


def demonstrate_module2_integration():
    """Demonstrate Module 2 integration between AllocationService and BacktestService."""
    print("Portfolio Insight - Module 2: Backtest Analysis")
    print("=" * 60)
    print()

    # 1. Create and configure services
    allocation_service = create_realistic_mock_services()
    backtest_service = BacktestService()

    # Configure backtest service
    setup_result = backtest_service.set_allocation_service(allocation_service)
    if not setup_result["success"]:
        print(f"Failed to setup backtest service: {setup_result['error']}")
        return

    print("✓ Services configured successfully")
    print()

    # 2. Display current portfolio
    allocation_result = backtest_service.get_portfolio_allocation()
    display_portfolio_summary(allocation_result)

    # 3. Simulate backtest results (in real usage, this would call backtest_service.run_backtest)
    print("Running backtest analysis...")
    backtest_results = simulate_backtest_results()
    print("✓ Backtest completed for all periods")
    print()

    # 4. Display results
    display_backtest_results(backtest_results)

    # 5. Provide analysis
    analyze_performance(backtest_results)

    print("\n" + "=" * 60)
    print("Module 2 Analysis Complete!")
    print("\nKey Features Demonstrated:")
    print("• Portfolio allocation calculation")
    print("• Multi-period backtesting (1Y, 5Y, 10Y)")
    print("• Performance metrics calculation:")
    print("  - Compound Annual Growth Rate (CAGR)")
    print("  - Maximum Drawdown")
    print("  - Sharpe Ratio")
    print("• Risk-adjusted performance analysis")

    print("\nNext Steps for Real Implementation:")
    print("• Set up Alpaca API credentials")
    print("• Connect to live E*TRADE portfolio data")
    print("• Run actual historical backtests")
    print("• Implement portfolio optimization recommendations")


if __name__ == "__main__":
    demonstrate_module2_integration()
