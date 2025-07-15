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

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
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
