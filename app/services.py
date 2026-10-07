from sqlalchemy import select

from app import db
from app.dtos import (
    TravelerCreate,
    TripCreate,
    TripResponse,
    TripUpdate,
)
from app.models import Traveler, Trip


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


def delete_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return None

    db.session.delete(trip)
    db.session.commit()

    return {"message": f"Trip with ID {trip_id} has been deleted."}


def add_traveler_to_trip(trip_id: int, traveler_data: TravelerCreate):
    trip = db.session.get(Trip, trip_id)

    if not trip:
        return None

    if trip.status != "PLANNED":
        raise ValueError("Travelers can only be added to planned trips.")

    if len(trip.travelers) >= trip.max_travelers:
        raise ValueError("Trip has reached its maximum number of travelers.")

    traveler = db.session.scalar(
        select(Traveler).where(Traveler.email == traveler_data.email)
    )

    if traveler is None:
        traveler = Traveler(
            name=traveler_data.name,
            email=traveler_data.email,
        )

    if traveler in trip.travelers:
        raise ValueError("Traveler is already added to this trip.")

    for existing_trip in traveler.trips:
        if (
            existing_trip.start_date < trip.end_date
            and existing_trip.end_date > trip.start_date
        ):
            raise ValueError("Traveler already has a trip with overlapping dates.")

    trip.travelers.append(traveler)

    db.session.commit()

    return TripResponse.model_validate(trip).model_dump(mode="json")


def trip_not_found_response(trip_id: int):
    return {
        "error": "TRIP_NOT_FOUND",
        "message": f"Trip with ID {trip_id} was not found.",
    }
