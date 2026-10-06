from flask import Blueprint, jsonify, request

from app import db
from app.dtos import TripCreate
from app.models import Trip

trip_bp = Blueprint("trip", __name__)


@trip_bp.post("/")
def create_trip():
    data = TripCreate.model_validate(request.get_json())

    trip = Trip(
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        budget=data.budget,
        max_travelers=data.max_travelers,
    )

    db.session.add(trip)
    db.session.commit()

    return jsonify({"message": "Trip created successfully", "trip_id": trip.id}), 201
