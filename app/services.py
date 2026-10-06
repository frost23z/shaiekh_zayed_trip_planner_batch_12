from sqlalchemy import select

from app import db
from app.dtos import TripCreate, TripResponse, TripUpdate
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


def update_trip(trip_id: int, data: TripUpdate):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return None

    update_data = data.model_dump(exclude_none=True)

    new_start_date = update_data.get("start_date", trip.start_date)
    new_end_date = update_data.get("end_date", trip.end_date)

    if new_end_date <= new_start_date:
        raise ValueError("trip end_date must be later than start_date.")

    for key, value in update_data.items():
        setattr(trip, key, value)

    db.session.commit()

    response = TripResponse.model_validate(trip).model_dump(mode="json")
    return response
