import pytest


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_and_get_trip(client, make_trip):
    trip = make_trip()
    response = client.get(f"/api/v1/trips/{trip['id']}")
    assert response.status_code == 200
    assert response.get_json()["destination"] == "Cox's Bazar"
    assert response.get_json()["status"] == "PLANNED"


@pytest.mark.parametrize(
    "overrides",
    [
        {"end_date": "2026-10-20"},  # end == start
        {"end_date": "2026-10-19"},  # end < start
        {"budget": 0},
        {"max_travelers": 0},
    ],
)
def test_create_trip_rejects_invalid_input(client, overrides):
    payload = {
        "destination": "Sylhet",
        "start_date": "2026-10-20",
        "end_date": "2026-10-23",
        "budget": 1000,
        "max_travelers": 3,
        **overrides,
    }
    response = client.post("/api/v1/trips", json=payload)
    assert response.status_code == 400


def test_unknown_trip_returns_404(client):
    assert client.get("/api/v1/trips/999").status_code == 404


def test_duplicate_traveler_is_rejected(client, make_trip, add_traveler):
    trip = make_trip()
    assert add_traveler(trip["id"]).status_code == 201

    response = add_traveler(trip["id"], email="AYESHA@example.com")  # case-insensitive
    assert response.status_code == 409
    assert response.get_json()["error"] == "DUPLICATE_TRAVELER"


def test_capacity_is_enforced_at_exact_full(client, make_trip, add_traveler):
    trip = make_trip(max_travelers=1)
    assert add_traveler(trip["id"], email="a@example.com").status_code == 201

    response = add_traveler(trip["id"], email="b@example.com")
    assert response.status_code == 409
    assert response.get_json()["error"] == "TRIP_FULL"


def test_overlapping_trips_rejected_but_back_to_back_allowed(
    client, make_trip, add_traveler
):
    first = make_trip(start_date="2026-10-20", end_date="2026-10-23")
    overlapping = make_trip(start_date="2026-10-22", end_date="2026-10-25")
    back_to_back = make_trip(start_date="2026-10-23", end_date="2026-10-26")

    assert add_traveler(first["id"]).status_code == 201

    response = add_traveler(overlapping["id"])
    assert response.status_code == 409
    assert response.get_json()["error"] == "TRAVELER_OVERLAP"

    assert add_traveler(back_to_back["id"]).status_code == 201


def test_expense_exact_remaining_budget_ok_and_above_fails(client, make_trip):
    trip = make_trip(budget=1000)
    url = f"/api/v1/trips/{trip['id']}/expenses"

    assert client.post(url, json={"title": "Hotel", "amount": 600}).status_code == 201
    assert client.post(url, json={"title": "Food", "amount": 400}).status_code == 201

    response = client.post(url, json={"title": "Extra", "amount": 1})
    assert response.status_code == 409
    assert response.get_json()["error"] == "BUDGET_EXCEEDED"


def test_non_positive_expense_is_rejected(client, make_trip):
    trip = make_trip()
    response = client.post(
        f"/api/v1/trips/{trip['id']}/expenses", json={"title": "Bad", "amount": 0}
    )
    assert response.status_code == 400


def test_summary_calculations(client, make_trip, add_traveler):
    trip = make_trip(budget=10000, max_travelers=3)
    add_traveler(trip["id"])
    client.post(
        f"/api/v1/trips/{trip['id']}/expenses", json={"title": "Bus", "amount": 2500}
    )

    summary = client.get(f"/api/v1/trips/{trip['id']}/summary").get_json()
    assert summary == {
        "traveler_count": 1,
        "available_seats": 2,
        "total_expense": 2500,
        "remaining_budget": 7500,
    }


def test_max_travelers_cannot_drop_below_current_count(client, make_trip, add_traveler):
    trip = make_trip(max_travelers=3)
    add_traveler(trip["id"], email="a@example.com")
    add_traveler(trip["id"], email="b@example.com")

    response = client.put(f"/api/v1/trips/{trip['id']}", json={"max_travelers": 1})
    assert response.status_code == 409


@pytest.mark.parametrize(
    "path, target, expected_status",
    [
        (["ONGOING"], "COMPLETED", 200),
        (["CANCELLED"], "PLANNED", 409),  # out of CANCELLED
        (["ONGOING", "COMPLETED"], "CANCELLED", 409),  # out of COMPLETED
        ([], "COMPLETED", 409),  # PLANNED -> COMPLETED skips ONGOING
    ],
)
def test_status_transitions(client, make_trip, path, target, expected_status):
    trip = make_trip()
    url = f"/api/v1/trips/{trip['id']}/status"
    for step in path:
        assert client.patch(url, json={"status": step}).status_code == 200

    assert client.patch(url, json={"status": target}).status_code == expected_status


def test_status_restrictions_on_travelers_expenses_and_edits(
    client, make_trip, add_traveler
):
    trip = make_trip()
    base = f"/api/v1/trips/{trip['id']}"

    # ONGOING: no new travelers, but expenses are still allowed.
    client.patch(f"{base}/status", json={"status": "ONGOING"})
    assert add_traveler(trip["id"]).status_code == 409
    assert (
        client.post(
            f"{base}/expenses", json={"title": "Fuel", "amount": 100}
        ).status_code
        == 201
    )

    # COMPLETED: nothing is allowed.
    client.patch(f"{base}/status", json={"status": "COMPLETED"})
    assert (
        client.post(
            f"{base}/expenses", json={"title": "Late", "amount": 100}
        ).status_code
        == 409
    )
    assert client.put(base, json={"destination": "Bandarban"}).status_code == 409
