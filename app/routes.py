from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app import db, services
from app.dtos import TripCreate, TripResponse, TripUpdate
from app.models import Trip

trip_bp = Blueprint("trip", __name__)


@trip_bp.post("/")
def create_trip():
    data = TripCreate.model_validate(request.get_json())
    return jsonify(services.create_trip(data)), 201


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


@trip_bp.put("/<int:trip_id>")
def update_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return jsonify(
            {
                "error": "TRIP_NOT_FOUND",
                "message": f"Trip with ID {trip_id} was not found.",
            }
        ), 404

    data = TripUpdate.model_validate(request.get_json())

    update_data = data.model_dump(exclude_none=True)

    new_start_date = update_data.get("start_date", trip.start_date)
    new_end_date = update_data.get("end_date", trip.end_date)

    if new_end_date <= new_start_date:
        raise ValueError("trip end_date must be later than start_date.")

    for key, value in update_data.items():
        setattr(trip, key, value)

    db.session.commit()

    return jsonify(TripResponse.model_validate(trip).model_dump(mode="json")), 200


@trip_bp.delete("/<int:trip_id>")
def delete_trip(trip_id: int):
    trip = db.session.get(Trip, trip_id)
    if not trip:
        return jsonify(
            {
                "error": "TRIP_NOT_FOUND",
                "message": f"Trip with ID {trip_id} was not found.",
            }
        ), 404

    db.session.delete(trip)
    db.session.commit()

    return jsonify({"message": f"Trip with ID {trip_id} has been deleted."}), 200
