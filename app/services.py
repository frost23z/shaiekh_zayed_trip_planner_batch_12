from sqlalchemy import select

from app import db
from app.dtos import TripCreate, TripResponse
from app.models import Trip


def create_trip(data: TripCreate):
    trip = Trip(
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        budget=data.budget,
        max_travelers=data.max_travelers,
    )

    db.session.add(trip)
    db.session.commit()

    response = TripResponse.model_validate(trip).model_dump(mode="json")

    return response


def get_trips():
    trips = db.session.scalars(select(Trip)).all()

    response = [
        TripResponse.model_validate(trip).model_dump(mode="json") for trip in trips
    ]
    return response


def get_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return None

    response = TripResponse.model_validate(trip).model_dump(mode="json")
    return response
