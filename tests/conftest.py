import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test_trip_planner.db'}",
        }
    )
    return app.test_client()


@pytest.fixture
def make_trip(client):
    def _make_trip(**overrides):
        payload = {
            "destination": "Cox's Bazar",
            "start_date": "2026-10-20",
            "end_date": "2026-10-23",
            "budget": 30000,
            "max_travelers": 2,
        }
        payload.update(overrides)
        response = client.post("/api/v1/trips", json=payload)
        assert response.status_code == 201
        return response.get_json()

    return _make_trip


@pytest.fixture
def add_traveler(client):
    def _add_traveler(trip_id, email="ayesha@example.com", name="Ayesha Rahman"):
        return client.post(
            f"/api/v1/trips/{trip_id}/travelers",
            json={"name": name, "email": email},
        )

    return _add_traveler
