# Todo App — Flask API + React Client + Docker

A small but production-shaped todo application, built as a teaching artifact for
a software-engineering / DevOps course. The emphasis is on **clean architecture,
correct HTTP semantics, and clear separation of concerns** rather than clever
tricks.

It is deliberately split into two independent services that communicate **only
over HTTP/JSON**:

- **backend** — Flask as a pure JSON REST API (no HTML rendering)
- **frontend** — a React SPA built with Vite, served by nginx in production
- **mysql** — MySQL 8 for storage

---

## Architecture

```
                    Browser (http://localhost:8080)
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │  frontend  (nginx :80, published on 8080)  │
        │  • serves the built React SPA              │
        │  • proxies /api/* ──► backend:5000         │
        └───────────────────────────────────────────┘
                              │  HTTP/JSON
                              ▼
        ┌───────────────────────────────────────────┐
        │  backend  (gunicorn + Flask :5000)         │
        │  • JSON REST API under /api/todos          │
        │  • app factory + blueprint + extensions    │
        │  • schema via Flask-Migrate (no create_all)│
        └───────────────────────────────────────────┘
                              │  SQL (mysql+pymysql)
                              ▼
        ┌───────────────────────────────────────────┐
        │  mysql 8.0  (:3306, named volume)          │
        │  • database `flask`, table `todo`          │
        └───────────────────────────────────────────┘
```

Both proxies (Vite in dev, nginx in prod) forward `/api` to the backend on the
same origin, so **the browser never deals with CORS**. Flask-Cors is still wired
up in the factory for flexibility (e.g. calling the API from a different host).

```
todo-app/
├── docker-compose.yml          # mysql + backend + frontend (+ test profile)
├── README.md
├── backend/
│   ├── Dockerfile              # python:3.12-slim, gunicorn
│   ├── requirements.txt
│   ├── .env.example
│   ├── wsgi.py                 # gunicorn entrypoint: `wsgi:app`
│   ├── migrations/             # Flask-Migrate / Alembic
│   └── app/
│       ├── __init__.py         # create_app(config_name) — the app factory
│       ├── config.py           # BaseConfig / DevConfig / TestConfig / ProdConfig
│       ├── extensions.py       # db, migrate, cors (bare instances)
│       ├── models.py           # Todo model + to_dict()
│       └── api/todos.py        # todos blueprint (/api/todos)
├── frontend/
│   ├── Dockerfile              # multi-stage: node build ──► nginx serve
│   ├── nginx.conf              # SPA fallback + /api proxy
│   ├── vite.config.js          # dev server :5173 + /api proxy
│   └── src/
│       ├── main.jsx
│       ├── App.jsx             # owns state, optimistic updates
│       ├── api/client.js       # todosApi: list/create/toggle/remove
│       └── components/         # AddTodo, TodoList, TodoItem
└── tests/                      # integration smoke test (CI)
```

---

## Run everything with Docker

```bash
docker compose up --build
```

This builds and starts all three services. Then, **on the very first run only**,
create/adopt the database schema (the app does *not* call `create_all` — see
below). In a second terminal:

```bash
# Fresh database (no existing data): create the `todo` table.
docker compose exec backend flask db upgrade
```

Now open **http://localhost:8080** and create / toggle / delete todos.

| Service  | URL                              | Notes                          |
|----------|----------------------------------|--------------------------------|
| frontend | http://localhost:8080            | the app you actually use       |
| backend  | http://localhost:5000/api/todos  | raw JSON API                   |
| backend  | http://localhost:5000/health     | `{"status": "ok"}`             |
| mysql    | localhost:3306                    | database `flask`               |

Tear down with `docker compose down` (add `-v` to also delete the data volume).

> **macOS note:** port `5000` is used by the AirPlay Receiver (System Settings →
> General → AirDrop & Handoff → *AirPlay Receiver*). If `docker compose up` fails
> with *"address already in use"* on `5000`, either turn AirPlay Receiver off or
> change the backend's published port in `docker-compose.yml` (e.g. `"5001:5000"`).
> The app itself is unaffected — the frontend reaches the backend over the
> internal compose network, not the host's `5000`.

---

## Database migrations (Flask-Migrate)

**Schema is managed exclusively by Flask-Migrate.** There is intentionally no
`db.create_all()` and no `before_first_request` hook. This mirrors real
projects, where schema changes are versioned, reviewed, and applied
deterministically.

A first migration (`migrations/versions/0001_initial_todo.py`) is included; it
describes the existing `todo` table (`id` / `title` / `complete`).

### First-time setup

- **Fresh database** (nothing to preserve):
  ```bash
  docker compose exec backend flask db upgrade
  ```
  This runs the initial migration and creates the `todo` table.

- **Existing database with data you want to keep** (this project evolved from an
  app that already created the `todo` table): tell Alembic the schema is already
  there, *without* running the migration, so no data is touched:
  ```bash
  docker compose exec backend flask db stamp head
  ```

### On later schema changes

Edit the model in `backend/app/models.py`, then:

```bash
docker compose exec backend flask db migrate -m "describe the change"
docker compose exec backend flask db upgrade
```

> `flask db init` has already been run — the `migrations/` folder is committed,
> so you do **not** run it again. You would only use it to bootstrap migrations
> in a brand-new project.

---

## Local development (without Docker)

You need a MySQL running locally (or point the env vars at any MySQL). The
backend's test config uses in-memory SQLite, so tests need no database at all.

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env            # then edit DB_* to match your local MySQL
export FLASK_APP=wsgi.py
export FLASK_CONFIG=dev

flask db upgrade                # create the schema (first time)
flask run --port 5000           # dev server on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:5000`, so run the
backend alongside it. To point the SPA at a different API base, set
`VITE_API_URL` (defaults to `/api`).

---

## API contract

Base path: `/api/todos`. All requests/responses are JSON. A todo looks like:

```json
{ "id": 1, "title": "Buy groceries", "complete": false }
```

| Method & path                | Body                                   | Success           | Errors |
|------------------------------|----------------------------------------|-------------------|--------|
| `GET /api/todos`             | —                                      | `200` array of todos (ordered by id) | — |
| `POST /api/todos`            | `{ "title": "…" }`                     | `201` created todo | `400` empty/missing title |
| `PATCH /api/todos/<id>`      | `{ "title"?: "…", "complete"?: bool }` | `200` updated todo | `400` empty title · `404` unknown id |
| `DELETE /api/todos/<id>`     | —                                      | `204` no content   | `404` unknown id |
| `GET /health`                | —                                      | `200 {"status":"ok"}` | — |

`PATCH` is a **partial** update: send only the fields you want to change.
Error responses are JSON, e.g. `{"error": "not found", "message": "todo 9 not found"}`.

### Quick check with curl

```bash
curl localhost:5000/api/todos
curl -X POST localhost:5000/api/todos -H 'Content-Type: application/json' -d '{"title":"Buy milk"}'
curl -X PATCH localhost:5000/api/todos/1 -H 'Content-Type: application/json' -d '{"complete":true}'
curl -X DELETE localhost:5000/api/todos/1 -i
```

---

## Why it's built this way

**Application factory (`create_app`).** The app is constructed inside a function
rather than as a module-level global. That lets us build differently-configured
apps for dev, prod, and tests (in-memory SQLite) from the same code, and it
avoids the circular-import problems a global `app` object invites. The
extensions (`db`, `migrate`, `cors`) live as bare instances in `extensions.py`
and are bound to a specific app via `init_app()` inside the factory — so models
and blueprints import `db` without importing the app.

**API / client split.** The backend speaks only JSON; the frontend owns all
rendering. The single seam between them is `src/api/client.js`, a thin wrapper
that centralizes the base URL, JSON headers, non-OK error handling, and the
`204` (no body) case. Swapping the UI or adding a second client (mobile, CLI)
means reusing the same HTTP contract, not rewriting server logic.

**Optimistic updates.** Toggling and deleting update the local state
*immediately*, then call the API. If the request fails, the previous state is
restored and an error is shown. The UI feels instant while staying correct — the
classic optimistic-UI pattern, kept small enough to read in one sitting.

**Migrations, not `create_all`.** `create_all` is convenient but silently drifts
from your models and can't express changes to existing tables. Flask-Migrate
(Alembic) versions every schema change as a reviewable file you apply
deterministically — the same way you'd manage a real production database. Here
it's also what lets us adopt the **existing** `todo` table without a
drop/recreate: `flask db stamp head` records the schema as current without
touching data.

---

## Troubleshooting

Real issues hit while getting this project running, with the exact fix for each.

### 1. Docker credential helper missing

**Symptom** — `docker compose up --build` fails while pulling a base image:

```
error getting credentials - err: exec: "docker-credential-desktop": executable file not found in $PATH
```

**Cause** — `~/.docker/config.json` sets `"credsStore": "desktop"`, but the
`docker-credential-desktop` helper isn't on `PATH` (a leftover from Docker
Desktop being removed, moved, or installed from a DMG that's no longer mounted).

**Fix** — remove the `"credsStore"` line from `~/.docker/config.json`:

```jsonc
{
    "auths": {},
    // "credsStore": "desktop",   <-- delete this line
    "currentContext": "desktop-linux"
}
```

With empty `auths` and only public images to pull, Docker fetches them
anonymously — no helper needed.

### 2. MySQL volume version downgrade

**Symptom** — the `mysql` container exits unhealthy with:

```
Invalid MySQL server downgrade: Cannot downgrade from 90600 to 80046
```

**Cause** — the named data volume was initialized by a **newer** MySQL major
version (9.x) than the image this project pins (`mysql:8.0`). MySQL refuses to
open data files written by a newer server.

**Fix** (this is a teaching project with disposable data — this **deletes the DB
volume**):

```bash
docker compose down -v
docker compose up --build
```

`-v` removes the volume so MySQL 8.0 reinitializes it cleanly. Re-run the
first-time `flask db upgrade` afterwards.

### 3. Port 5000 collides with macOS AirPlay Receiver

**Symptom** — `curl localhost:5000/...` returns `403` with a header like
`Server: AirTunes/...` instead of the backend's response.

**Cause** — on macOS Ventura and later, the **AirPlay Receiver** listens on port
`5000`.

**Fix** — either turn AirPlay Receiver off (*System Settings → General → AirDrop
& Handoff → AirPlay Receiver*) and use `5000`, or publish the backend on a
different host port. This project maps it to **`5001:5000`** in
`docker-compose.yml`, so use `http://localhost:5001` for direct backend calls.

> This only affects the **host-side** port. Inside the Docker network nginx
> still proxies to `backend:5000`, so no `proxy_pass` change is needed and the
> frontend at `http://localhost:8080` is unaffected.

### 4. `404 {"error":"not found"}` from the API

**Symptom** — an API call returns the JSON 404 body: `{"error":"not found", ...}`.

Two distinct causes:

- **Trailing-slash mismatch on collection routes.** The client calls
  `/api/todos` (no trailing slash), so the collection routes must bind to the
  bare blueprint prefix with `@bp.get("")` / `@bp.post("")` — **not**
  `@bp.get("/")`, which would register `/api/todos/` and fail to match. (Path
  params like `/<int:todo_id>` are unaffected.)
- **Hitting the backend root `/` directly.** This returned 404 by design until
  the root index route was added; `/` now returns a small JSON pointer to the
  API. Either way, remember the **real UI lives at `http://localhost:8080`**, not
  on the backend port.
