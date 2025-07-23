# BacktestService Examples

This directory contains examples demonstrating how to use the BacktestService for portfolio backtesting analysis.

## Files

### `backtest_demo.py`
Basic demonstration of BacktestService functionality:
- Service initialization and configuration
- Portfolio allocation retrieval
- Performance metrics calculation
- Supported time periods overview

**Usage:**
```bash
python examples/backtest_demo.py
```

### `module2_integration.py`
Complete Module 2 workflow demonstration:
- Integration between AllocationService and BacktestService
- Multi-period backtesting (1Y, 5Y, 10Y)
- Comprehensive performance analysis
- Risk-adjusted returns analysis

**Usage:**
```bash
python examples/module2_integration.py
```

## Real-World Usage

To use the BacktestService with real data:

1. **Get Alpaca API Credentials**
   - Sign up at [Alpaca](https://alpaca.markets/)
   - Get your API key and secret key
   - Use paper trading for testing

2. **Set up BacktestService**
   ```python
   from portfolio_insight.portfolio.backtest import BacktestService
   from portfolio_insight.portfolio.allocation import AllocationService
   
   # Initialize services
   allocation_service = AllocationService()
   backtest_service = BacktestService()
   
   # Configure allocation service (E*TRADE)
   allocation_service.start_session()
   allocation_service.get_accounts()
   allocation_service.set_account(account_data)
   
   # Configure backtest service (Alpaca)
   backtest_service.set_alpaca_credentials(api_key, secret_key)
   backtest_service.set_allocation_service(allocation_service)
   ```

3. **Run Backtests**
   ```python
   # Single period backtest
   result = backtest_service.run_backtest("1Y")
   
   # Multiple period comparison
   results = backtest_service.run_multiple_period_backtest()
   ```

## Performance Metrics

The BacktestService calculates the following metrics:

- **CAGR (Compound Annual Growth Rate)**: Annualized return rate
- **Total Return**: Overall percentage gain/loss
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure

## Supported Time Periods

- `1Y`: 1 Year backtest
- `5Y`: 5 Year backtest  
- `10Y`: 10 Year backtest

## Integration with Module 1

The BacktestService seamlessly integrates with the existing AllocationService from Module 1:

1. Use AllocationService to get current portfolio allocation
2. Use BacktestService to analyze historical performance of that allocation
3. Compare different time periods to understand long-term trends
4. Use metrics to make informed investment decisions

## Error Handling

The service includes comprehensive error handling for:
- Missing API credentials
- Invalid time periods
- Missing portfolio data
- API connection issues
- Insufficient historical data

All methods return structured responses with `success` flags and error messages for robust error handling.