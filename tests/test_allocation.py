#!/usr/bin/env python3
"""
Test suite for the calculate_investment_allocation function.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.allocation import calculate_investment_allocation


def test_basic_allocation():
    """Test basic allocation scenario."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_allocation = {"AAPL": 500.0, "GOOGL": 500.0}
    current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Basic allocation test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    # Check that all recommendations are non-negative integers
    for security, shares in result.items():
        assert security in target_allocation, f"Security {security} not in target allocation"
        assert isinstance(shares, int), f"Shares should be integer, got {type(shares)}"
        assert shares >= 0, f"Shares should be non-negative, got {shares}"
    print("✓ Basic allocation test passed")


def test_empty_portfolio():
    """Test with empty current portfolio."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_allocation = {}
    current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Empty portfolio test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    # With empty portfolio, all securities should be under-allocated
    assert len(result) == 2, "Should recommend purchases for both securities"
    # Check proportional allocation: AAPL gets 60% of $1000 = $600 = 4 shares at $150
    # GOOGL gets 40% of $1000 = $400 = 2 shares at $200
    expected_aapl_shares = int(600 / 150)  # 4 shares
    expected_googl_shares = int(400 / 200)  # 2 shares
    assert result.get("AAPL", 0) == expected_aapl_shares, f"Expected {expected_aapl_shares} AAPL shares, got {result.get('AAPL', 0)}"
    assert result.get("GOOGL", 0) == expected_googl_shares, f"Expected {expected_googl_shares} GOOGL shares, got {result.get('GOOGL', 0)}"
    print("✓ Empty portfolio test passed")


def test_single_security():
    """Test with single security."""
    target_allocation = {"AAPL": 1.0}
    investment_amount = 500.0
    current_allocation = {"AAPL": 1000.0}
    current_prices = {"AAPL": 150.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Single security test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    # Since AAPL should get 100% of future value but already has some allocation,
    # it should still be under-allocated and get recommended shares
    assert "AAPL" in result, "AAPL should be in result"
    assert result["AAPL"] >= 0, "AAPL shares should be non-negative"
    print("✓ Single security test passed")


def test_underallocated_security():
    """Test prioritizing underallocated securities."""
    target_allocation = {"AAPL": 0.7, "GOOGL": 0.3}
    investment_amount = 1000.0
    current_allocation = {"AAPL": 100.0, "GOOGL": 900.0}  # AAPL is way underallocated
    current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Underallocated test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    # AAPL should get more allocation since it's more underallocated
    # Current total: 1000, Future total: 2000
    # AAPL target: 70% of 2000 = 1400, current: 100, gap: 1300/2000 = 0.65
    # GOOGL target: 30% of 2000 = 600, current: 900, gap: -300/2000 = -0.15 (overallocated)
    # Only AAPL should be recommended
    assert "AAPL" in result, "AAPL should be recommended"
    assert result.get("AAPL", 0) > 0, "AAPL should get positive shares"
    assert result.get("GOOGL", 0) == 0, "GOOGL should not be recommended (overallocated)"
    print("✓ Underallocated security test passed")


def test_zero_investment():
    """Test with zero investment amount."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 0.0
    current_allocation = {"AAPL": 500.0, "GOOGL": 500.0}
    current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Zero investment test: {result}")
    assert result == {}, f"Expected empty dict for zero investment, got {result}"
    print("✓ Zero investment test passed")


def test_proportional_allocation():
    """Test proportional allocation based on gaps."""
    target_allocation = {"AAPL": 0.5, "GOOGL": 0.3, "MSFT": 0.2}
    investment_amount = 1000.0
    current_allocation = {}  # Empty portfolio
    current_prices = {"AAPL": 100.0, "GOOGL": 200.0, "MSFT": 50.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Proportional allocation test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # With empty portfolio, gaps are equal to target allocations
    # AAPL: 50% * $1000 = $500 = 5 shares at $100
    # GOOGL: 30% * $1000 = $300 = 1 share at $200 
    # MSFT: 20% * $1000 = $200 = 4 shares at $50
    expected = {"AAPL": 5, "GOOGL": 1, "MSFT": 4}
    
    for security, expected_shares in expected.items():
        assert result.get(security, 0) == expected_shares, f"Expected {expected_shares} {security} shares, got {result.get(security, 0)}"
    
    print("✓ Proportional allocation test passed")


def test_invalid_inputs():
    """Test with invalid inputs."""
    current_prices = {"AAPL": 150.0}
    
    # Test with empty target allocation
    result = calculate_investment_allocation({}, 1000.0, {"AAPL": 500.0}, current_prices)
    assert result == {}, "Should return empty dict for empty target"

    # Test with negative investment amount
    result = calculate_investment_allocation({"AAPL": 1.0}, -100.0, {"AAPL": 500.0}, current_prices)
    assert result == {}, "Should return empty dict for negative investment"

    print("✓ Invalid inputs test passed")


def test_balanced_portfolio():
    """Test with perfectly balanced portfolio."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_allocation = {"AAPL": 600.0, "GOOGL": 400.0}  # Already balanced
    current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Balanced portfolio test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # Current total: 1000, Future total: 2000
    # Both securities need to maintain their proportion with new money
    # AAPL target: 60% of 2000 = 1200, current: 600, gap: 600/2000 = 0.3
    # GOOGL target: 40% of 2000 = 800, current: 400, gap: 400/2000 = 0.2
    # Total gap: 0.5, so AAPL gets 60% of investment, GOOGL gets 40%
    # AAPL: $600 = 4 shares at $150
    # GOOGL: $400 = 2 shares at $200
    expected = {"AAPL": 4, "GOOGL": 2}
    
    for security, expected_shares in expected.items():
        assert result.get(security, 0) == expected_shares, f"Expected {expected_shares} {security} shares, got {result.get(security, 0)}"
    
    print("✓ Balanced portfolio test passed")


def test_missing_prices():
    """Test with missing price information."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_allocation = {}
    current_prices = {"AAPL": 150.0}  # Missing GOOGL price

    result = calculate_investment_allocation(
        target_allocation, investment_amount, current_allocation, current_prices
    )

    print(f"Missing prices test: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    # AAPL should get shares, GOOGL should get 0 shares due to missing price
    assert result.get("AAPL", 0) > 0, "AAPL should get shares"
    assert result.get("GOOGL", 0) == 0, "GOOGL should get 0 shares (missing price)"
    print("✓ Missing prices test passed")


def run_all_tests():
    """Run all tests."""
    print("Running calculate_investment_allocation tests...")
    print("=" * 50)

    test_basic_allocation()
    test_empty_portfolio()
    test_single_security()
    test_underallocated_security()
    test_zero_investment()
    test_proportional_allocation()
    test_balanced_portfolio()
    test_invalid_inputs()
    test_missing_prices()

    print("=" * 50)
    print("✓ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
