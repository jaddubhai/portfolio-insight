# portfolio-insight

A Python-based portfolio analysis and insight tool.

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

### Dependencies

- `rauth`: OAuth 1.0/2.0 authentication library for API access
- `black`: Code formatter (development dependency)
- `pre-commit`: Pre-commit hooks framework (development dependency)