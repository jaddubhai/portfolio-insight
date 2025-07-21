# AllocationService

End-to-end investment allocation service that integrates E*TRADE API session management, account selection, portfolio data, and market data for UI applications.

## Usage

```python
from portfolio.allocation import AllocationService
import utils

# Initialize and authenticate
service = AllocationService()
session_result = service.start_session(utils.KeyType.SANDBOX)

# Select account
accounts = service.get_accounts()["accounts"]
service.set_account(accounts[0])

# Calculate allocation
target_allocation = {"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3}
result = service.calculate_allocation(target_allocation, 5000.0)

if result["success"]:
    recommendations = result["allocation_recommendations"]
    breakdown = result["allocation_breakdown"]
```

## Core Methods

### Session Management
- `start_session(key_type)` - Start OAuth session
- `is_session_active()` - Check session status
- `get_session_status()` - Get session details

### Account Management  
- `get_accounts()` - List available accounts
- `set_account(account_data)` - Select active account
- `is_account_selected()` - Check if account selected
- `get_account_summary()` - Get account details

### Allocation Calculation
- `calculate_allocation(target_allocation, investment_amount)` - Main calculation method
- `get_allocation_summary(target_allocation, investment_amount)` - Full analysis
- `get_current_portfolio_allocation()` - Current holdings
- `get_current_prices(symbols)` - Market prices

## Response Format

```python
{
    "success": True,
    "allocation_recommendations": {"AAPL": 10, "GOOGL": 5},
    "allocation_breakdown": {
        "AAPL": {
            "shares": 10,
            "price_per_share": 150.0,
            "investment_value": 1500.0,
            "percentage_of_investment": 30.0
        }
    },
    "total_investment_value": 4750.0,
    "unused_cash": 250.0
}
```

## Error Handling

All methods return `{"success": False, "error": "message"}` on failure. Common validation:

```python
# Validate target allocation sums to 1.0
if abs(sum(target_allocation.values()) - 1.0) > 0.001:
    return {"error": "Target allocation must sum to 100%"}

# Check session and account status
if not service.is_session_active():
    return {"error": "Please authenticate first"}
```