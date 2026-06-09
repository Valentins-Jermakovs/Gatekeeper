# Gatekeeper

> **Gatekeeper** is a lightweight auth service built with FastAPI, SQLModel and PostgreSQL. It provides registration, login, logout, refresh-token support, role-based user management, and async execution.

---

## Features

- Async FastAPI application with JWT authentication
- PostgreSQL support via `asyncpg` and `SQLModel`
- Register, login, logout, refresh token endpoints
- Role-aware user search and admin user management
- Docker Compose deployment ready
- Environment configuration via `.env`

---

## Tech stack

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-000000?style=for-the-badge)
![asyncpg](https://img.shields.io/badge/asyncpg-2C2C2C?style=for-the-badge)
![Uvicorn](https://img.shields.io/badge/Uvicorn-222222?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-0db7ed?style=for-the-badge&logo=docker&logoColor=white)

---

## Project structure

- `src/` — application source code
- `src/config/` — database and dependency configuration
- `src/models/` — SQLModel ORM models
- `src/schemas/` — request/response data models
- `src/services/` — business logic for auth, tokens, users, and passwords
- `src/api/` — API route definitions
- `src/utils/` — database initialization helpers
- `compose.yaml` — Docker Compose configuration
- `.env` — environment configuration

---

## Environment setup

The app loads environment variables from a `.env` file at startup.

### Required root `.env`

```env
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=app_db
DATABASE_URL=postgresql+asyncpg://app_user:app_password@db:5432/app_db
SECRET_KEY=replace-this-with-a-secure-secret
ALGORITHM=HS256
```

> When using Docker Compose, the database hostname should be `db` because the service is named `db` in `compose.yaml`.

---

## Docker launch

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

### Useful Docker commands

```bash
docker compose down

docker compose stop

docker compose logs -f
```

---

## Local development

Install dependencies in a virtual environment:

```bash
python3.12 -m venv gatevenv
source gatevenv/bin/activate
pip install -r requirements.txt
```

Run the app locally:

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API endpoints

| Route | Method | Description |
| --- | --- | --- |
| `/auth/register` | POST | Register a new user and return access and refresh tokens |
| `/auth/login` | POST | Authenticate a user with username/password |
| `/auth/logout` | POST | Invalidate a refresh token and logout the user |
| `/token/refresh` | POST | Refresh an access token using a refresh token |
| `/metrics/stats` | GET | Return CPU and memory usage statistics |
| `/users/me` | GET | Return the currently authenticated user |
| `/users/me/email` | PATCH | Change the current user's email |
| `/users/me/username` | PATCH | Change the current user's username |
| `/users/me/password` | PATCH | Change the current user's password |
| `/users/me/set-password` | POST | Set a new password for the current user |
| `/users/add-roles` | PATCH | Add roles to one or more users (admin only) |
| `/users/remove-roles` | DELETE | Remove roles from one or more users (admin only) |
| `/users/change-status` | PATCH | Enable or disable users in batch (admin only) |
| `/users/users` | GET | List users with pagination and search by username, email, or role |

### Example user search

```http
GET /users/users?limit=20&offset=0&search=admin
```

---

## Implementation notes

- `src/main.py` loads `.env` values and adds session middleware using `SECRET_KEY`.
- `src/utils/init_db.py` initializes the database schema at application startup.
- `src/services/users/user_service.py` supports searching users by username, email, or role name.
- The app uses async SQLModel sessions with `db.exec(...)`.

---

## Tips

- Use a strong `SECRET_KEY` before deploying.
- Check `http://localhost:8000/docs` for interactive API docs.
- Use `docker compose logs -f` to inspect startup issues.

---

## Fun touch

```text
  ___       _        _                    
 / _ \ __ _| |_ __ _| |__   __ _ ___  ___ 
| | | / _` | __/ _` | '_ \ / _` / __|/ _ \
| |_| | (_| | || (_| | |_) | (_| \__ \  __/
 \___/ \__,_|\__\__,_|_.__/ \__,_|___/\___/
```

Thanks for using Gatekeeper!
