# (WIP) portfolio-insight
Based on etrade Python SDK. The app has 2 modules:
Module 1:
- Takes in a target portfolio allocation (either via text input, or an image of a portfolio)
- Takes in an investment amount
- Outputs the stocks/securities that the user should invest in with the above amount to maintain/get closer to target allocation

Module 2:
The goal of module 2 is to help a user identify/iterate on their portfolio allocation. For a given portfolio allocation (again, either via text input, or image), it should:
- Do a backtest of the portfolio over a configurable time-period, and output metrics like growth rate, max drawdown, asset correlations, and any others you deem fit
- It should allow users to tweak the allocation slightly and re-generate metrics
- Includes a chat button for users to ask an LLMs to recommend sample portfolios, and then refresh metrics

## Project Structure

The project follows a standard Python package structure:

```
portfolio-insight/
├── README.md
├── requirements.txt
├── setup.py
├── portfolio_insight/          # Main package
│   ├── __init__.py
│   ├── accounts.py            # E*TRADE account management
│   ├── market.py              # Market data retrieval
│   ├── order.py               # Order management
│   ├── utils.py               # Authentication and utilities
│   ├── portfolio/             # Portfolio management subpackage
│   │   ├── __init__.py
│   │   ├── allocation.py      # Investment allocation logic
│   │   └── backtest.py        # Portfolio backtesting
│   └── llm/                   # LLM integration
│       ├── __init__.py
│       └── chat.py
├── ui/                        # React-based user interface (separate from Python package)
├── tests/                     # Test package
│   ├── __init__.py
│   ├── test_allocation.py
│   └── test_allocation_service.py
└── docs/
    └── AllocationService.md
```

## Development Setup

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jaddubhai/portfolio-insight.git
   cd portfolio-insight
   ```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jaddubhai/portfolio-insight.git
   cd portfolio-insight
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```
   
   This installs the package as an editable package, which means changes to the source code 
   will be immediately available without reinstalling.

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Usage

After installation, you can import and use the package modules:

```python
from portfolio_insight.portfolio.allocation import AllocationService, calculate_investment_allocation
from portfolio_insight import utils

# Example: Using the allocation service
service = AllocationService()
service.start_session(utils.KeyType.SANDBOX)  # or utils.KeyType.LIVE

# Example: Using the allocation function directly
target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
investment_amount = 1000.0
current_allocation = {"AAPL": 500.0, "GOOGL": 500.0}
current_prices = {"AAPL": 150.0, "GOOGL": 200.0}

recommendations = calculate_investment_allocation(
    target_allocation, investment_amount, current_allocation, current_prices
)
```

### Running Tests

Run the test suite:
```bash
python tests/test_allocation.py
python tests/test_allocation_service.py
```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Code Formatting

This project uses [Black](https://github.com/psf/black) for code formatting to ensure consistent code style.

#### Running Black

To format all Python files:
```bash
black .
```

To check if files are formatted correctly without making changes:
```bash
black --check .
```

To see what changes would be made:
```bash
black --diff .
```

#### Pre-commit Hooks

Pre-commit hooks are configured to automatically run Black on staged files before each commit. The hooks are installed automatically when you run `pre-commit install`.

To run hooks manually on all files:
```bash
pre-commit run --all-files
```
