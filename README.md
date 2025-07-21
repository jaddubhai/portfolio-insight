# (WIP) portfolio-insight

![CI](https://github.com/jaddubhai/portfolio-insight/workflows/CI/badge.svg)

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

### Testing

The project includes comprehensive tests for the portfolio allocation functionality.

#### Running Tests

To run all tests:
```bash
python run_tests.py
```

Or run individual test files:
```bash
python tests/test_allocation.py
python tests/test_allocation_service.py
```

#### Test Structure

- `tests/test_allocation.py` - Tests for the core allocation calculation functions
- `tests/test_allocation_service.py` - Tests for the AllocationService class and end-to-end workflows

#### Continuous Integration

GitHub Actions automatically runs tests on all pull requests and pushes to the main branch. The CI pipeline:

- Tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Checks code formatting with Black
- Runs the complete test suite
- Ensures all pre-commit hooks pass

All tests must pass before a pull request can be merged.
