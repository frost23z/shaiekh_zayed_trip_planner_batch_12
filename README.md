# Smart Group Trip Planner API

A REST API for managing group trips, travelers, expenses, and trip lifecycle rules.
Built with **Python 3, Flask, and SQLite** (Flask-SQLAlchemy for persistence, Pydantic for request validation).

## Overview

A travel organization needs a backend to manage group trips. A trip has a destination, date range,
budget, capacity, travelers, expenses, and a lifecycle status. The API enforces all business rules
server-side and prevents invalid operations such as:

- overbooking and duplicate participation
- overlapping trips for the same traveler
- overspending the budget
- invalid status transitions

There is no frontend, authentication, or deployment setup; all responses are JSON.

## Prerequisites

- Python 3.10+
- Bash

## Run from a fresh clone (recommended)

```bash
git clone https://github.com/frost23z/shaiekh_zayed_trip_planner_batch_12.git
cd shaiekh_zayed_trip_planner_batch_12
./run.sh
```

`run.sh` will:

1. create (or reuse) a local virtual environment in `.venv`
2. install dependencies from `requirements.txt`
3. start the Flask API on **<http://127.0.0.1:5000>** (database tables are created automatically on startup)

If the script is not executable, run `chmod +x run.sh` once.

## Manual run (fallback)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Run the tests

```bash
source .venv/bin/activate
pip install pytest
python -m pytest -q
```

Tests use a temporary SQLite file per test (injected through `create_app(config_overrides)`),
so they never touch the real database.

## API endpoints

| Method | Endpoint                                      | Purpose                  |
| ------ | --------------------------------------------- | ------------------------ |
| GET    | `/health`                                     | Application health       |
| POST   | `/api/v1/trips`                               | Create a trip            |
| GET    | `/api/v1/trips`                               | List trips               |
| GET    | `/api/v1/trips/<trip_id>`                     | Get one trip             |
| PUT    | `/api/v1/trips/<trip_id>`                     | Update a trip            |
| DELETE | `/api/v1/trips/<trip_id>`                     | Delete a trip            |
| POST   | `/api/v1/trips/<trip_id>/travelers`           | Add a traveler           |
| DELETE | `/api/v1/trips/<trip_id>/travelers/<traveler_id>` | Remove a traveler   |
| POST   | `/api/v1/trips/<trip_id>/expenses`            | Add an expense           |
| PATCH  | `/api/v1/trips/<trip_id>/status`              | Change trip status       |
| GET    | `/api/v1/trips/<trip_id>/summary`             | Calculated trip summary  |

### Status codes

| Code | Meaning                                                                                  |
| ---- | ---------------------------------------------------------------------------------------- |
| 200  | Successful retrieval, update, or delete                                                  |
| 201  | Resource created (trip, traveler added, expense added)                                   |
| 400  | Invalid request data or validation failure (including malformed JSON)                    |
| 404  | Unknown trip, or traveler not part of the trip                                           |
| 409  | Business conflict (duplicate traveler, full trip, overlap, budget, invalid status/transition) |
| 415  | Request body is not sent as `application/json`                                           |

### Error response shape

```json
{
  "error": "TRIP_FULL",
  "message": "The trip has reached its maximum traveler capacity."
}
```

Validation errors (400) also include a `details` list:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [{ "field": "budget", "message": "Input should be greater than 0" }]
}
```

Error codes used: `VALIDATION_ERROR`, `TRIP_NOT_FOUND`, `TRAVELER_NOT_FOUND`, `DUPLICATE_TRAVELER`,
`TRIP_FULL`, `TRAVELER_OVERLAP`, `BUDGET_EXCEEDED`, `BUDGET_BELOW_EXPENSES`,
`MAX_TRAVELERS_BELOW_CURRENT`, `INVALID_TRIP_STATUS`, `INVALID_STATUS_TRANSITION`.

## Example requests and responses

**Create a trip** — `POST /api/v1/trips`

```bash
curl -X POST http://127.0.0.1:5000/api/v1/trips \
  -H "Content-Type: application/json" \
  -d '{"destination":"Cox'"'"'s Bazar","start_date":"2026-10-20","end_date":"2026-10-23","budget":30000,"max_travelers":5}'
```

`201 Created`

```json
{
  "id": 1,
  "destination": "Cox's Bazar",
  "start_date": "2026-10-20",
  "end_date": "2026-10-23",
  "budget": 30000,
  "max_travelers": 5,
  "status": "PLANNED",
  "travelers": [],
  "expenses": []
}
```

**Add a traveler** — `POST /api/v1/trips/1/travelers`

```json
{ "name": "Ayesha Rahman", "email": "ayesha@example.com" }
```

`201 Created` — returns the full trip with `travelers` populated:

```json
{ "id": 1, "status": "PLANNED", "travelers": [{ "id": 1, "name": "Ayesha Rahman", "email": "ayesha@example.com" }], "...": "..." }
```

Adding the same email again → `409`:

```json
{ "error": "DUPLICATE_TRAVELER", "message": "Traveler is already added to this trip." }
```

**Add an expense** — `POST /api/v1/trips/1/expenses`

```json
{ "title": "Hotel", "amount": 12000 }
```

`201 Created` — returns the full trip with the expense in `expenses`.

**Trip summary** — `GET /api/v1/trips/1/summary`

`200 OK`

```json
{
  "traveler_count": 1,
  "available_seats": 4,
  "total_expense": 12000,
  "remaining_budget": 18000
}
```

**Change status** — `PATCH /api/v1/trips/1/status`

```json
{ "status": "ONGOING" }
```

`200 OK` returns the updated trip. An invalid transition (e.g. `PLANNED` → `COMPLETED`) → `409`:

```json
{
  "error": "INVALID_STATUS_TRANSITION",
  "message": "Trip cannot transition from PLANNED to COMPLETED."
}
```

**Unknown trip** — `GET /api/v1/trips/99` → `404`

```json
{ "error": "TRIP_NOT_FOUND", "message": "Trip with ID 99 was not found." }
```

## Business rules and assumptions

| Rule  | Implementation                                                                              |
| ----- | ------------------------------------------------------------------------------------------- |
| BR-01 | `end_date` must be later than `start_date` (checked on create and update)                   |
| BR-02 | `budget` must be a positive integer                                                         |
| BR-03 | `max_travelers` must be a positive integer                                                  |
| BR-04 | Traveler identity is the **email** (stored lowercase); the same email cannot join a trip twice |
| BR-05 | A trip never holds more travelers than `max_travelers` (exactly full is allowed, one more is `TRIP_FULL`) |
| BR-06 | A traveler cannot join trips with overlapping dates; back-to-back trips (end date = next start date) are allowed |
| BR-07 | Expense `amount` must be a positive integer                                                 |
| BR-08 | Total expenses may equal the budget but never exceed it                                     |
| BR-09 | `max_travelers` cannot be reduced below the current traveler count                          |
| BR-10 | Travelers can only be added while the trip is `PLANNED`                                     |
| BR-11 | Expenses can only be added while the trip is `PLANNED` or `ONGOING`                         |
| BR-12 / BR-13 | `COMPLETED` and `CANCELLED` trips cannot be edited, accept travelers/expenses, or change status |
| BR-14 | Allowed transitions: `PLANNED → ONGOING → COMPLETED`, `PLANNED → CANCELLED`, `ONGOING → CANCELLED` |

Additional assumptions:

- Money values (`budget`, `amount`) are whole integers.
- `PUT /trips/<id>` is a partial update: send at least one field; omitted fields keep their value.
- Updating the budget below the expenses already added is rejected (`BUDGET_BELOW_EXPENSES`).
- Changing a trip's dates re-checks overlap for every traveler already on that trip.
- Removing a traveler detaches them from the trip; the traveler record itself is kept so the same email can join other trips.
- Traveler `name` must be 3–100 characters; `email` must be a valid address.

## Project structure

```text
.
├── run.py              # Flask entry point (python run.py)
├── run.sh              # One-command setup + start script
├── requirements.txt    # Pinned dependencies
├── README.md
├── .gitignore
├── app/
│   ├── __init__.py     # create_app(config_overrides) factory, db init, blueprints
│   ├── config.py       # Configuration (database URI)
│   ├── models.py       # Trip, Traveler, Expense, trip_travelers association table
│   ├── dtos.py         # Pydantic request/response schemas and input validation
│   ├── errors.py       # AppError and JSON error handlers
│   ├── routes.py       # HTTP layer (thin controllers)
│   └── services.py     # Business rules and database operations
└── tests/
    ├── conftest.py     # Fixtures (isolated app + temp database per test)
    └── test_trip_planner.py
```

Request flow: `routes.py` validates the body with a Pydantic DTO → calls a function in `services.py`
→ the service enforces business rules and reads/writes via SQLAlchemy models → the result is
returned as JSON. Rule violations raise `AppError`, which `errors.py` turns into the JSON error response.

## How SQLite is initialized and stored

- The database URI defaults to `sqlite:///trip_planner.db` and can be overridden with the
  `DATABASE_URL` environment variable.
- Flask-SQLAlchemy stores the file at `instance/trip_planner.db`.
- Tables are created automatically on startup (`db.create_all()` inside `create_app`), so no manual SQL
  or setup is needed. Data persists across restarts.
- The database file is generated locally and is **not committed** (it is listed in `.gitignore`).
- To reset all data, stop the server and delete `instance/trip_planner.db`.

Schema: `trips`, `travelers` (unique `email`), `expenses` (FK → `trips`), and a `trip_travelers`
association table (many-to-many between trips and travelers).

## Known limitations

- No authentication, pagination, or filtering on `GET /api/v1/trips`.
- Money is stored as integers (no decimals or currency handling).
- No database migrations; schema changes require deleting the local database file.
- `run.py` starts Flask in debug mode, which is intended for local use only.
- Overlap and capacity checks are not guarded against truly concurrent requests (SQLite, single local process).
