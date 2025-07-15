#!/usr/bin/env python3
"""
Test suite for the calculate_investment_allocation function.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from portfolio.allocation import calculate_investment_allocation


def test_basic_allocation():
    """Test basic allocation scenario."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_portfolio = {"AAPL": 500.0, "GOOGL": 500.0}
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Basic allocation test: {security} -> ${amount}")
    assert security in target_allocation, f"Security {security} not in target allocation"
    assert amount >= 0, "Amount should be non-negative"
    assert amount <= investment_amount, "Amount should not exceed investment amount"
    print("✓ Basic allocation test passed")


def test_empty_portfolio():
    """Test with empty current portfolio."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_portfolio = {}
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Empty portfolio test: {security} -> ${amount}")
    assert security in target_allocation, f"Security {security} not in target allocation"
    assert amount > 0, "Amount should be positive for empty portfolio"
    print("✓ Empty portfolio test passed")


def test_single_security():
    """Test with single security."""
    target_allocation = {"AAPL": 1.0}
    investment_amount = 500.0
    current_portfolio = {"AAPL": 1000.0}
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Single security test: {security} -> ${amount}")
    assert security == "AAPL", f"Expected AAPL, got {security}"
    assert amount >= 0, "Amount should be non-negative"
    print("✓ Single security test passed")


def test_underallocated_security():
    """Test prioritizing underallocated securities."""
    target_allocation = {"AAPL": 0.7, "GOOGL": 0.3}
    investment_amount = 1000.0
    current_portfolio = {"AAPL": 100.0, "GOOGL": 900.0}  # AAPL is way underallocated
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Underallocated test: {security} -> ${amount}")
    # AAPL should be prioritized since it's way under its 70% target
    assert security == "AAPL", f"Expected AAPL (underallocated), got {security}"
    assert amount > 0, "Amount should be positive for underallocated security"
    print("✓ Underallocated security test passed")


def test_zero_investment():
    """Test with zero investment amount."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 0.0
    current_portfolio = {"AAPL": 500.0, "GOOGL": 500.0}
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Zero investment test: {security} -> ${amount}")
    assert amount == 0.0, f"Expected 0 amount for zero investment, got {amount}"
    print("✓ Zero investment test passed")


def test_tie_breaking():
    """Test tie-breaking with random selection."""
    target_allocation = {"AAPL": 0.33, "GOOGL": 0.33, "MSFT": 0.33}  # Equal allocations for true ties
    investment_amount = 1000.0
    current_portfolio = {}  # Empty portfolio means all have same priority
    
    # Run multiple times to test randomness
    securities_chosen = set()
    for i in range(15):
        result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
        security, amount = result
        securities_chosen.add(security)
        assert security in target_allocation, f"Security {security} not in target allocation"
        assert amount > 0, "Amount should be positive"
    
    print(f"Tie-breaking test: Securities chosen across 15 runs: {securities_chosen}")
    # With equal allocations and random selection, we should see different securities chosen
    assert len(securities_chosen) > 1, "Should have multiple securities chosen with random tie-breaking"
    print("✓ Tie-breaking test passed")


def test_invalid_inputs():
    """Test with invalid inputs."""
    # Test with empty target allocation
    result = calculate_investment_allocation({}, 1000.0, {"AAPL": 500.0})
    security, amount = result
    assert security is None and amount == 0.0, "Should return None, 0.0 for empty target"
    
    # Test with negative investment amount
    result = calculate_investment_allocation({"AAPL": 1.0}, -100.0, {"AAPL": 500.0})
    security, amount = result
    assert security is None and amount == 0.0, "Should return None, 0.0 for negative investment"
    
    print("✓ Invalid inputs test passed")


def test_balanced_portfolio():
    """Test with perfectly balanced portfolio."""
    target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
    investment_amount = 1000.0
    current_portfolio = {"AAPL": 600.0, "GOOGL": 400.0}  # Already balanced
    
    result = calculate_investment_allocation(target_allocation, investment_amount, current_portfolio)
    security, amount = result
    
    print(f"Balanced portfolio test: {security} -> ${amount}")
    assert security in target_allocation, f"Security {security} not in target allocation"
    assert amount > 0, "Amount should be positive even for balanced portfolio"
    
    # Both securities should need investment to maintain proportions with new money
    # AAPL should need 600 (60% of 2000 - 600 current)
    # GOOGL should need 400 (40% of 2000 - 400 current)
    expected_amounts = {"AAPL": 600.0, "GOOGL": 400.0}
    assert amount == expected_amounts[security], f"Expected {expected_amounts[security]} for {security}, got {amount}"
    print("✓ Balanced portfolio test passed")


def run_all_tests():
    """Run all tests."""
    print("Running calculate_investment_allocation tests...")
    print("=" * 50)
    
    test_basic_allocation()
    test_empty_portfolio()
    test_single_security()
    test_underallocated_security()
    test_zero_investment()
    test_tie_breaking()
    test_balanced_portfolio()
    test_invalid_inputs()
    
    print("=" * 50)
    print("✓ All tests passed!")


if __name__ == "__main__":
    run_all_tests()