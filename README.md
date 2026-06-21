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
   uv run pre-commit install -t pre-commit -t commit-msg
   ```

4. Copy the example environment file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

## Architecture

The backend follows **Clean Architecture**, organized by layer. The dependency
rule points inward — outer layers depend on inner ones, never the reverse:

```
gateways  →  usecases  →  interfaces  ←  repositories / security
(routers)   (app rules)   (ports)         (adapters / details)
                              ↑
                          entities (pure domain core)
```

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| Entities | `app/entities/` | Pure domain objects, no framework dependencies. |
| Interfaces | `app/interfaces/` | Abstract ports (`Protocol`): `UserRepository`, `PasswordHasher`, `TokenProvider`. |
| Use cases | `app/usecases/` | Application rules (`RegisterUser`, `AuthenticateUser`), depending only on interfaces. |
| Repositories | `app/repositories/` | SQLAlchemy implementations of the persistence ports + ORM models. |
| Security | `app/security/` | Adapters for hashing (`pwdlib`/Argon2) and JWT (`PyJWT`). |
| Gateways | `app/gateways/` | FastAPI routers, request/response schemas and dependency-injection wiring. |

Because use cases depend only on the interfaces, they are unit-tested with
in-memory fakes (`tests/fakes.py`) — no database or HTTP needed. This is what
demonstrates SOLID (notably the Dependency Inversion Principle) in practice.

### Authentication

Account creation and login use the current FastAPI-recommended stack:
`pwdlib` (Argon2) for password hashing and `PyJWT` for access tokens via the
OAuth2 password flow.

- `POST /auth/register` — create an account.
- `POST /auth/login` — exchange email/password for a JWT access token.
- `GET /users/me` — example protected route (requires `Authorization: Bearer <token>`).

## Testing

```bash
uv run pytest            # unit (use cases with fakes) + integration (API end-to-end)
```

## Configuration

App configuration is managed with [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) in `app/config.py`. Settings are loaded from environment variables and/or a `.env` file (see `.env.example` for the available options).

## Development

Run the project (FastAPI app, served by uvicorn):

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Or use the helper script (binds to 0.0.0.0 so it can be tunneled):

```bash
bash scripts/serve.sh
```

The default database is a local SQLite file (`comequeta.db`), created
automatically on startup — no external database required (see ADR 0003).

## Exposing the backend publicly via ngrok (demo)

For an academic demo, run the backend locally and expose it to the internet
with [ngrok](https://ngrok.com/) — a tunnel, **not** a database (the data stays
in the local SQLite file on this machine).

1. Install ngrok and authenticate once with your free account:
   ```bash
   ngrok config add-authtoken <SEU_AUTHTOKEN>
   ```
2. Start the backend (e.g. `bash scripts/serve.sh`).
3. In another terminal, open the tunnel to port 8000:
   ```bash
   ngrok http 8000
   ```
4. Copy the public HTTPS URL ngrok prints (e.g. `https://abc123.ngrok-free.app`)
   and point the frontend at it via `VITE_API_URL` (in
   `../comequeta-frontend/.env`). WebSockets (the chat at `/ws/chat`) tunnel over
   `wss://` through the same URL.

Notes:
- The free ngrok URL changes on every run (reserve a domain if you need a stable
  one). CORS already allows the app's origins (see `app/config.py`).
- The frontend sends the `ngrok-skip-browser-warning` header so API calls skip
  ngrok's interstitial page.

### Linting, formatting and type checking

This project follows **[PEP 8](https://peps.python.org/pep-0008/)** enforced by [Ruff](https://docs.astral.sh/ruff/) (79-character lines, pycodestyle, pep8-naming) and [ty](https://github.com/astral-sh/ty) for type checking. These run automatically on commit via [pre-commit](https://pre-commit.com/).

Commit messages are validated on commit via pre-commit (`scripts/validate-commit-msg.sh`). They must follow Conventional Commits: `<type>: <lower-case-subject>` (e.g. `feat: add user registration`). Allowed types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `ci`, `build`, `perf`, `revert`.

Test a message manually:

```bash
echo "feat: add user registration" | bash scripts/validate-commit-msg.sh /dev/stdin
```

```bash
uv run ruff check .       # PEP 8 lint
uv run ruff format .      # PEP 8 format
uv run ty check           # type check
```

To run all pre-commit hooks against every file:

```bash
uv run pre-commit run --all-files
```

### OpenAPI schema

The OpenAPI schema can be exported to JSON for use by frontend codegen tools:

```bash
uv run python scripts/generate_openapi.py                    # writes ./openapi.json
uv run python scripts/generate_openapi.py ../comequeta-frontend/openapi.json
```

## Adding dependencies

```bash
uv add <package>          # runtime dependency
uv add --dev <package>    # development dependency
```
