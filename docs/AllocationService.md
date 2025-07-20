# AllocationService - End-to-End Investment Allocation

## Overview

The `AllocationService` provides a comprehensive end-to-end backend flow for calculating investment allocations. It integrates session management, account selection, portfolio data retrieval, market data, and allocation calculation into a single, easy-to-use service designed for UI applications.

## Features

- **Session Management**: OAuth authentication with E*TRADE API
- **Account Management**: List and select user accounts
- **Portfolio Data**: Retrieve current holdings and market values
- **Market Data**: Get real-time price information for securities
- **Allocation Calculation**: Intelligent investment recommendations
- **Comprehensive Reporting**: Detailed analysis and breakdowns
- **Error Handling**: Robust error handling and validation

## Quick Start

```python
from portfolio.allocation import AllocationService
import utils

# 1. Initialize the service
service = AllocationService()

# 2. Start authenticated session
session_result = service.start_session(utils.KeyType.SANDBOX)
if not session_result["success"]:
    print("Authentication failed:", session_result["error"])
    return

# 3. Get and select account
accounts_result = service.get_accounts()
if accounts_result["success"]:
    selected_account = accounts_result["accounts"][0]  # Select first account
    service.set_account(selected_account)

# 4. Define target allocation and investment amount
target_allocation = {
    "AAPL": 0.40,   # 40%
    "GOOGL": 0.30,  # 30%
    "MSFT": 0.30    # 30%
}
investment_amount = 5000.00

# 5. Calculate allocation recommendations
result = service.calculate_allocation(target_allocation, investment_amount)
if result["success"]:
    recommendations = result["allocation_recommendations"]
    for symbol, shares in recommendations.items():
        if shares > 0:
            print(f"Buy {shares} shares of {symbol}")
```

## API Reference

### Core Methods

#### `start_session(key_type: utils.KeyType = utils.KeyType.SANDBOX) -> Dict[str, Any]`

Starts an authenticated session using OAuth. Requires user interaction for authorization.

**Parameters:**
- `key_type`: Either `utils.KeyType.SANDBOX` or `utils.KeyType.LIVE`

**Returns:**
- Dictionary with `success` boolean and session information

#### `get_accounts() -> Dict[str, Any]`

Retrieves list of available accounts for the authenticated user.

**Returns:**
- Dictionary with `success` boolean and `accounts` list

#### `set_account(account_data: Dict[str, Any]) -> Dict[str, Any]`

Sets the active account for portfolio operations.

**Parameters:**
- `account_data`: Account information dictionary with required fields

**Returns:**
- Dictionary with `success` boolean and status message

#### `calculate_allocation(target_allocation: Dict[str, float], investment_amount: float) -> Dict[str, Any]`

Calculates investment allocation recommendations.

**Parameters:**
- `target_allocation`: Target allocation percentages (must sum to 1.0)
- `investment_amount`: Amount of money to invest

**Returns:**
- Comprehensive dictionary with allocation recommendations and analysis

### Utility Methods

#### `get_account_summary() -> Dict[str, Any]`

Gets comprehensive account summary including balance and portfolio.

#### `get_current_portfolio_allocation() -> Dict[str, Any]`

Gets current portfolio positions formatted for allocation calculation.

#### `get_current_prices(symbols: List[str]) -> Dict[str, Any]`

Gets current market prices for specified symbols.

#### `get_allocation_summary(target_allocation: Dict[str, float], investment_amount: float) -> Dict[str, Any]`

Gets complete allocation analysis including account info and recommendations.

### Status Methods

#### `is_session_active() -> bool`

Checks if there's an active authenticated session.

#### `is_account_selected() -> bool`

Checks if an account has been selected.

#### `get_session_status() -> Dict[str, Any]`

Gets current session and account status information.

## Response Format

### Successful Allocation Response

```python
{
    "success": True,
    "allocation_recommendations": {
        "AAPL": 10,    # Number of shares to buy
        "GOOGL": 5,
        "MSFT": 15
    },
    "allocation_breakdown": {
        "AAPL": {
            "shares": 10,
            "price_per_share": 150.0,
            "investment_value": 1500.0,
            "percentage_of_investment": 30.0
        },
        # ... similar for other symbols
    },
    "total_investment_value": 4750.0,
    "unused_cash": 250.0,
    "target_allocation": {"AAPL": 0.4, "GOOGL": 0.3, "MSFT": 0.3},
    "current_allocation": {"AAPL": 2000.0, "GOOGL": 1500.0},
    "current_prices": {"AAPL": 150.0, "GOOGL": 200.0, "MSFT": 100.0},
    "investment_amount": 5000.0
}
```

### Error Response

```python
{
    "success": False,
    "error": "Description of the error that occurred"
}
```

## Error Handling

The service includes comprehensive error handling for common scenarios:

1. **Authentication Failures**: Invalid credentials, network issues
2. **Account Issues**: No accounts found, restricted access
3. **Market Data Issues**: Symbol not found, missing prices
4. **Calculation Issues**: Invalid allocations, insufficient funds

Example error handling pattern:

```python
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
    
    # Perform calculation
    try:
        result = service.calculate_allocation(target_allocation, investment_amount)
        return result
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}
```

## UI Integration

The service is designed to support intuitive UI workflows:

1. **Authentication Flow**: Guide user through OAuth process
2. **Account Selection**: Present available accounts for selection
3. **Portfolio Display**: Show current holdings and allocations
4. **Target Setup**: Allow user to define desired allocation percentages
5. **Investment Input**: Capture investment amount
6. **Results Display**: Present recommendations in user-friendly format

## Testing

Comprehensive test suite is available:

```bash
# Run original allocation function tests
python tests/test_allocation.py

# Run AllocationService tests
python tests/test_allocation_service.py

# Run demonstration
python examples/allocation_service_demo.py
```

## Dependencies

- `rauth`: OAuth authentication
- `typing`: Type hints
- Standard library modules

## Environment Support

- **Sandbox**: For testing and development (`utils.KeyType.SANDBOX`)
- **Live**: For production use (`utils.KeyType.LIVE`)

## Security Considerations

- OAuth tokens are handled securely
- No sensitive data is stored persistently
- All API communications use HTTPS
- Error messages don't expose sensitive information

## Performance

- Efficient API usage with batch requests where possible
- Minimal data transfer and processing
- Fast calculation algorithms
- Proper error handling to avoid unnecessary retries

## Limitations

- Requires active internet connection
- Subject to E*TRADE API rate limits
- Market data availability depends on trading hours
- OAuth sessions have expiration times

## Support

For issues or questions:
1. Check the comprehensive test suite for usage examples
2. Review the demonstration script for workflow guidance
3. Examine error handling patterns for troubleshooting