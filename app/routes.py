from flask import Blueprint, jsonify, request

from app import db, services
from app.dtos import TripCreate, TripUpdate
from app.models import Trip

trip_bp = Blueprint("trip", __name__)


@trip_bp.post("/")
def create_trip():
    data = TripCreate.model_validate(request.get_json())
    return jsonify(services.create_trip(data)), 201


@trip_bp.get("/")
def get_trips():
    return jsonify(services.get_trips()), 200


@trip_bp.get("/<int:trip_id>")
def get_trip(trip_id: int):
    trip = services.get_trip(trip_id)
    if not trip:
        return trip_not_found_response(trip_id)

    return jsonify(trip), 200


@trip_bp.put("/<int:trip_id>")
def update_trip(trip_id: int):
    trip = services.update_trip(trip_id, TripUpdate.model_validate(request.get_json()))
    if not trip:
        return trip_not_found_response(trip_id)
    return jsonify(trip), 200


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


def trip_not_found_response(trip_id: int):
    return jsonify(
        {
            "error": "TRIP_NOT_FOUND",
            "message": f"Trip with ID {trip_id} was not found.",
        }
    ), 404
