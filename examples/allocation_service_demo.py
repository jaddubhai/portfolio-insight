#!/usr/bin/env python3
"""
Example usage of the AllocationService for UI integration.

This demonstrates how a UI application would use the AllocationService
to provide end-to-end investment allocation functionality.
"""

import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portfolio.allocation import AllocationService
import utils


class MockAllocationServiceDemo:
    """
    Mock demonstration of how a UI would interact with AllocationService.

    This class simulates the UI workflow without requiring actual E*TRADE credentials.
    """

    def __init__(self):
        self.service = AllocationService()

    def simulate_ui_workflow(self):
        """Simulate a complete UI workflow for investment allocation."""
        print("🚀 Portfolio Insight - Investment Allocation Demo")
        print("=" * 50)

        # This would normally require real authentication
        print("\n📝 Note: This is a simulation showing the intended workflow.")
        print("In actual usage, you would:")
        print("1. Call service.start_session() with real E*TRADE OAuth")
        print("2. Use real account data from E*TRADE API")
        print("3. Get live market data")
        print("\nSimulating the workflow with mock data...\n")

        # Simulate Step 1: Authentication
        print("Step 1: User Authentication")
        print("- User would complete OAuth flow")
        print("- Session established with E*TRADE")
        print("✓ Authentication simulated")

        # Simulate Step 2: Account Selection
        print("\nStep 2: Account Selection")
        mock_accounts = [
            {
                "accountIdKey": "ABC123",
                "institutionType": "BROKERAGE",
                "accountDesc": "INDIVIDUAL BROKERAGE",
                "accountStatus": "ACTIVE",
            },
            {
                "accountIdKey": "DEF456",
                "institutionType": "BROKERAGE",
                "accountDesc": "ROTH IRA",
                "accountStatus": "ACTIVE",
            },
        ]

        print("Available accounts:")
        for i, account in enumerate(mock_accounts):
            print(f"  {i+1}. {account['accountDesc']} ({account['accountIdKey']})")

        print("✓ User selects account: Individual Brokerage")

        # Simulate Step 3: Portfolio Analysis
        print("\nStep 3: Current Portfolio Analysis")
        mock_portfolio = {"AAPL": 5000.00, "GOOGL": 3000.00, "MSFT": 2000.00}

        total_value = sum(mock_portfolio.values())
        print(f"Current portfolio value: ${total_value:,.2f}")
        print("Current holdings:")
        for symbol, value in mock_portfolio.items():
            percentage = (value / total_value) * 100
            print(f"  {symbol}: ${value:,.2f} ({percentage:.1f}%)")

        # Simulate Step 4: Target Allocation Input
        print("\nStep 4: Target Allocation Setup")
        target_allocation = {
            "AAPL": 0.40,  # 40%
            "GOOGL": 0.30,  # 30%
            "MSFT": 0.20,  # 20%
            "TSLA": 0.10,  # 10%
        }

        print("Target allocation:")
        for symbol, percentage in target_allocation.items():
            print(f"  {symbol}: {percentage*100:.0f}%")

        # Simulate Step 5: Investment Amount
        investment_amount = 3000.00
        print(f"\nStep 5: Investment Amount")
        print(f"Amount to invest: ${investment_amount:,.2f}")

        # Simulate Step 6: Market Data & Calculation
        print(f"\nStep 6: Market Data & Allocation Calculation")
        mock_prices = {"AAPL": 150.00, "GOOGL": 200.00, "MSFT": 100.00, "TSLA": 250.00}

        print("Current market prices:")
        for symbol, price in mock_prices.items():
            print(f"  {symbol}: ${price:.2f}")

        # Use the actual calculation function
        from portfolio.allocation import calculate_investment_allocation

        allocation_result = calculate_investment_allocation(
            target_allocation=target_allocation,
            investment_amount=investment_amount,
            current_allocation=mock_portfolio,
            current_prices=mock_prices,
        )

        # Simulate Step 7: Display Results
        print(f"\nStep 7: Investment Recommendations")
        print("Recommended purchases:")

        total_investment = 0
        for symbol, shares in allocation_result.items():
            if shares > 0:
                investment_value = shares * mock_prices[symbol]
                total_investment += investment_value
                print(
                    f"  {symbol}: {shares} shares @ ${mock_prices[symbol]:.2f} = ${investment_value:.2f}"
                )

        unused_cash = investment_amount - total_investment
        print(f"\nTotal recommended investment: ${total_investment:.2f}")
        print(f"Unused cash: ${unused_cash:.2f}")

        # Show projected allocation
        print(f"\nProjected Portfolio After Investment:")
        future_total = total_value + investment_amount

        projected_portfolio = mock_portfolio.copy()
        for symbol, shares in allocation_result.items():
            if shares > 0:
                projected_portfolio[symbol] = projected_portfolio.get(symbol, 0) + (
                    shares * mock_prices[symbol]
                )

        for symbol in target_allocation:
            current_value = projected_portfolio.get(symbol, 0)
            percentage = (current_value / future_total) * 100
            target_percentage = target_allocation[symbol] * 100
            print(
                f"  {symbol}: ${current_value:.2f} ({percentage:.1f}% vs {target_percentage:.1f}% target)"
            )

        print("\n✓ Allocation analysis complete!")

    def demonstrate_api_usage(self):
        """Demonstrate the actual API usage pattern for developers."""
        print("\n" + "=" * 50)
        print("🔧 Developer API Usage Example")
        print("=" * 50)

        print(
            """
# Example code for UI developers:

from portfolio.allocation import AllocationService
import utils

# 1. Initialize service
service = AllocationService()

# 2. Start authenticated session (requires user interaction)
try:
    session_result = service.start_session(utils.KeyType.SANDBOX)  # or LIVE
    if not session_result["success"]:
        print("Authentication failed:", session_result["error"])
        return
except Exception as e:
    print("Authentication error:", e)
    return

# 3. Get available accounts
accounts_result = service.get_accounts()
if accounts_result["success"]:
    accounts = accounts_result["accounts"]
    # Present accounts to user for selection
    # selected_account = user_selection_logic(accounts)
else:
    print("Failed to get accounts:", accounts_result["error"])
    return

# 4. Set the selected account
set_result = service.set_account(selected_account)
if not set_result["success"]:
    print("Failed to set account:", set_result["error"])
    return

# 5. Get user's target allocation and investment amount
target_allocation = {
    "AAPL": 0.40,   # User input: 40%
    "GOOGL": 0.30,  # User input: 30%
    "MSFT": 0.30    # User input: 30%
}
investment_amount = 5000.00  # User input

# 6. Calculate allocation recommendations
allocation_result = service.calculate_allocation(target_allocation, investment_amount)

if allocation_result["success"]:
    # Present results to user
    recommendations = allocation_result["allocation_recommendations"]
    breakdown = allocation_result["allocation_breakdown"]
    
    print("Investment recommendations:")
    for symbol, shares in recommendations.items():
        if shares > 0:
            details = breakdown[symbol]
            print(f"{symbol}: {shares} shares @ ${details['price_per_share']:.2f}")
    
    print(f"Total investment: ${allocation_result['total_investment_value']:.2f}")
    print(f"Unused cash: ${allocation_result['unused_cash']:.2f}")
else:
    print("Allocation calculation failed:", allocation_result["error"])

# 7. Optional: Get comprehensive summary
summary_result = service.get_allocation_summary(target_allocation, investment_amount)
if summary_result["success"]:
    # Contains both account summary and allocation analysis
    account_info = summary_result["account_summary"]
    allocation_info = summary_result["allocation_analysis"]
    # Present comprehensive view to user
"""
        )

    def show_error_handling_examples(self):
        """Show common error handling patterns."""
        print("\n" + "=" * 50)
        print("⚠️  Error Handling Examples")
        print("=" * 50)

        print(
            """
Common error scenarios and how to handle them:

1. Authentication Failures:
   - Invalid credentials
   - Network connectivity issues
   - E*TRADE API unavailable
   
2. Account Issues:
   - No accounts found
   - Account access restricted
   - Account not suitable for trading

3. Market Data Issues:
   - Symbol not found
   - Price data unavailable
   - Market closed

4. Calculation Issues:
   - Invalid target allocation (doesn't sum to 1.0)
   - Insufficient investment amount
   - No actionable recommendations

Example error handling:

def handle_allocation_request(target_allocation, investment_amount):
    service = AllocationService()
    
    # Validate inputs
    if abs(sum(target_allocation.values()) - 1.0) > 0.001:
        return {"error": "Target allocation must sum to 100%"}
    
    if investment_amount <= 0:
        return {"error": "Investment amount must be positive"}
    
    # Check session status
    if not service.is_session_active():
        return {"error": "Please authenticate first"}
    
    if not service.is_account_selected():
        return {"error": "Please select an account"}
    
    # Perform calculation with error handling
    try:
        result = service.calculate_allocation(target_allocation, investment_amount)
        return result
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}
"""
        )


def main():
    """Run the complete demonstration."""
    demo = MockAllocationServiceDemo()

    # Run the UI workflow simulation
    demo.simulate_ui_workflow()

    # Show API usage examples
    demo.demonstrate_api_usage()

    # Show error handling
    demo.show_error_handling_examples()

    print("\n" + "=" * 50)
    print("📋 Summary")
    print("=" * 50)
    print(
        """
The AllocationService provides a complete end-to-end solution for:

✓ Session Management - OAuth authentication with E*TRADE
✓ Account Management - List and select user accounts  
✓ Portfolio Data - Retrieve current holdings and values
✓ Market Data - Get real-time price information
✓ Allocation Calculation - Smart investment recommendations
✓ Comprehensive Reporting - Detailed analysis and breakdowns

This service is designed to be used by UI applications to provide
users with intelligent investment allocation recommendations based
on their target portfolio allocation and available investment funds.

The service handles all the complexity of integrating multiple APIs
and provides a simple, consistent interface for UI developers.
"""
    )


if __name__ == "__main__":
    main()
