from flask import Blueprint, jsonify, request

from app import services
from app.dtos import ExpenseCreate, TravelerCreate, TripCreate, TripUpdate

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
        return jsonify(services.trip_not_found_response(trip_id)), 404

    return jsonify(trip), 200


@trip_bp.put("/<int:trip_id>")
def update_trip(trip_id: int):
    trip = services.update_trip(trip_id, TripUpdate.model_validate(request.get_json()))
    if not trip:
        return jsonify(services.trip_not_found_response(trip_id)), 404
    return jsonify(trip), 200


@trip_bp.delete("/<int:trip_id>")
def delete_trip(trip_id: int):
    result = services.delete_trip(trip_id)
    if not result:
        return jsonify(services.trip_not_found_response(trip_id)), 404

    return jsonify(result), 200


@trip_bp.post("/<int:trip_id>/travelers")
def add_traveler_to_trip(trip_id: int):
    result = services.add_traveler_to_trip(
        trip_id, TravelerCreate.model_validate(request.get_json())
    )
    if not result:
        return jsonify(services.trip_not_found_response(trip_id)), 404

    return jsonify(result), 201


@trip_bp.delete("/<int:trip_id>/travelers/<int:traveler_id>")
def remove_traveler_from_trip(trip_id: int, traveler_id: int):
    result = services.remove_traveler_from_trip(trip_id, traveler_id)

    if not result:
        return jsonify(services.trip_not_found_response(trip_id)), 404

    return jsonify(result), 200


@trip_bp.post("/<int:trip_id>/expenses")
def add_expense_to_trip(trip_id: int):
    result = services.add_expense_to_trip(
        trip_id,
        ExpenseCreate.model_validate(request.get_json()),
    )

    if not result:
        return jsonify(services.trip_not_found_response(trip_id)), 404

    return jsonify(result), 201
