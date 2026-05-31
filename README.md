# Gatekeeper

> **Gatekeeper** is a lightweight auth service built with FastAPI, SQLModel and PostgreSQL. It provides registration, login, logout, token refresh, and async architecture.

---

## Features

- Async FastAPI app with JWT-based authentication
- PostgreSQL database support via `asyncpg`
- Registration, login, logout, refresh token endpoints
- Role assignment for new users
- Docker-ready deployment with `docker compose`
- `.env`-based configuration for easy environment switching

---

## Tech stack

- Python 3.12
- FastAPI
- SQLModel
- SQLAlchemy AsyncIO
- PostgreSQL
- Uvicorn
- Docker / Docker Compose

---

## Project structure

- `src/` — application source code
- `src/config/` — database and dependency config
- `src/models/` — SQLModel ORM models
- `src/schemas/` — request/response data models
- `src/services/` — business logic for auth, tokens, registration, logout
- `src/routers/` — API routes
- `src/utils/` — DB initialization helpers
- `compose.yaml` — Docker Compose configuration
- `.env` — environment configuration

---

## Environment setup

Create or update the root `.env` file with values like these:

```env
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=app_db
DATABASE_URL=postgresql+asyncpg://app_user:app_password@db:5432/app_db
SECRET_KEY=replace-this-with-a-secure-secret
ALGORITHM=HS256
```

> Note: The `DATABASE_URL` host should be `db` when running with Docker Compose, because the service is named `db` in `compose.yaml`.

---

## Docker Launch

From the repository root:

```bash
docker compose up --build
```

Then visit:

```bash
http://localhost:8000/docs
```

### Handy Docker commands

```bash
docker compose down

docker compose stop

docker compose logs -f
```

---

## Local development

If you prefer not to use Docker, install Python dependencies in a virtual environment:

```bash
python3.12 -m venv gatevenv
source gatevenv/bin/activate
pip install -r requirements.txt
```

Then run the app:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Ensure `.env` is present in the project root or `src/` if the app loads it from there.

---

## API endpoints

| Route | Method | Description |
| --- | --- | --- |
| `/auth/register` | POST | Register a new user |
| `/auth/login` | POST | Authenticate and receive tokens |
| `/auth/logout` | POST | Invalidate current refresh token |
| `/auth/refresh` | POST | Refresh access token |

Typically the app uses `schemas` under `src/schemas/` for request/response validation.

---

## Implementation notes

- The project uses async database sessions and `db.exec(...)` everywhere for SQLModel compatibility.
- `src/config/database.py` is configured to use `AsyncSession` from `sqlmodel.ext.asyncio.session`.
- The `main.py` lifecycle calls `utils.init_db()` to prepare the DB at app startup.

---

## Tips

- Change `SECRET_KEY` to a strong value before deploying
- Use `docker compose logs -f` to inspect startup issues
- Open `http://localhost:8000/docs` for interactive API docs

---

## Fun touch

```
  ___       _        _                    
 / _ \ __ _| |_ __ _| |__   __ _ ___  ___ 
| | | / _` | __/ _` | '_ \ / _` / __|/ _ \
| |_| | (_| | || (_| | |_) | (_| \__ \  __/
 \___/ \__,_|\__\__,_|_.__/ \__,_|___/\___|
```

Thanks for using Gatekeeper!
