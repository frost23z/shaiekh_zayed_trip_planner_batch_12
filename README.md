# Smart Group Trip Planner API

A small REST for managing group trips, travelers, expenses, and trip lifecycle.

## Run instructions

1. Clone the repo

    ```bash
    git clone https://github.com/frost23z/shaiekh_zayed_trip_planner_batch_12.git
    cd shaiekh_zayed_trip_planner_batch_12
    ```

2. Run the command with single command

    ```bash
    ./run.sh
    ```

    `run.sh` creates (or reuses) `.venv`, installs    `requirements.txt`, starts the API on
    **<http://127.0.0.1:5000>**.
  
3. Alternatively, you can manully preprare the environment and run the app.

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python run.py
    ```

## API

| Method | Endpoint                      | Purpose                |
| ------ | ----------------------------- | ---------------------- |
| GET    | `/health`                     | Application health     |
| POST   | `/api/v1/trips`               | Create a trip          |
| GET    | `/api/v1/trips`               | List trips             |
| GET    | `/api/v1/trips/<trip_id>`     | Get one trip           |
| PUT    | `/api/v1/trips/<trip_id>`     | Update a trip          |
| DELETE | `/api/v1/trips/<trip_id>`     | Delete a trip          |
