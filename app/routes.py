from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app import db
from app.dtos import TripCreate, TripResponse
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

    response = TripResponse.model_validate(trip).model_dump(mode="json")
    return jsonify(response), 201


@trip_bp.get("/")
def get_trips():
    trips = db.session.scalars(select(Trip)).all()

    response = [
        TripResponse.model_validate(trip).model_dump(mode="json") for trip in trips
    ]
    return jsonify(response), 200


@trip_bp.get("/<int:trip_id>")
def get_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return jsonify(
            {
                "error": "TRIP_NOT_FOUND",
                "message": f"Trip with ID {trip_id} was not found.",
            }
        ), 404

    return jsonify(TripResponse.model_validate(trip).model_dump(mode="json")), 200
