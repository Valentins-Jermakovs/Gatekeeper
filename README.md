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

- `Python 3.12` • `FastAPI` • `SQLModel` • `SQLAlchemy AsyncIO` • `PostgreSQL` • `Uvicorn` • `Docker` • `Docker Compose`

### Tech tags

`Python` `FastAPI` `SQLModel` `PostgreSQL` `OAuth2` `JWT` `Docker` `Compose` `asyncpg`

### Architecture illustration

![Architecture illustration](./illustration.png)

---

## Project structure

- `src/` — application source code
- `src/config/` — database and dependency config
- `src/models/` — SQLModel ORM models
- `src/schemas/` — request/response data models
- `src/services/` — business logic for auth, tokens, registration, logout
- `src/api/` — API routes and OAuth endpoints
- `src/utils/` — DB initialization helpers
- `compose.yaml` — Docker Compose configuration
- `.env` — environment configuration

---

## Environment setup

The app loads environment variables from both root `.env` and `src/.env`.

### Recommended root `.env` for Docker Compose

```env
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=app_db
DATABASE_URL=postgresql+asyncpg://app_user:app_password@db:5432/app_db
SECRET_KEY=replace-this-with-a-secure-secret
ALGORITHM=HS256
```

### Recommended `src/.env` for Google OAuth

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
FRONTEND_URL=http://localhost:5170/login
```

> Note: When the app runs in Docker Compose, the database host must be `db` because the service is named `db` in `compose.yaml`.

> Note: `GOOGLE_REDIRECT_URI` must exactly match the redirect URI configured in the Google Cloud OAuth client.

---

## Docker Launch

From the repository root:

```bash
docker compose up --build
```

The service will be available at:

```bash
http://localhost:8000
```

Open the FastAPI docs at:

```bash
http://localhost:8000/docs
```

### Docker Compose environment behavior

- `./.env` provides core configuration values such as `DATABASE_URL` and `SECRET_KEY`.
- `src/.env` provides Google OAuth settings used by the app.
- The app uses `db` as the PostgreSQL hostname inside Docker.

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
| `/auth/register` | POST | Register a new user and receive access/refresh tokens |
| `/auth/login` | POST | Authenticate a user with username/password |
| `/auth/logout` | POST | Invalidate the current refresh token |
| `/auth/google/login` | GET | Redirect to Google OAuth login |
| `/auth/google/callback` | GET | Google OAuth callback endpoint |
| `/token/refresh` | POST | Exchange a refresh token for a new access token |
| `/token/verify` | GET | Verify an access token is valid |

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
