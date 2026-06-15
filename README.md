# Comé que Tá Backend

Backend for the Comé que Tá project, built with FastAPI and SQLAlchemy.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

1. Clone the repository and enter the project directory:

   ```bash
   git clone <repo-url>
   cd comequeta-backend
   ```

2. Install dependencies (this also creates a `.venv` automatically):

   ```bash
   uv sync
   ```

3. Install the pre-commit hooks (run once after cloning):

   ```bash
   uv run pre-commit install
   ```

## Development

Run the project:

```bash
uv run main.py
```

### Linting, formatting and type checking

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting/formatting and [ty](https://github.com/astral-sh/ty) for type checking. These run automatically on commit via [pre-commit](https://pre-commit.com/), but can also be run manually:

```bash
uv run ruff check .       # lint
uv run ruff format .      # format
uv run ty check           # type check
```

To run all pre-commit hooks against every file:

```bash
uv run pre-commit run --all-files
```

## Adding dependencies

```bash
uv add <package>          # runtime dependency
uv add --dev <package>    # development dependency
```
