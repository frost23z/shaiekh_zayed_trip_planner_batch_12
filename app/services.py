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
