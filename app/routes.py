from datetime import date

from flask import Blueprint, jsonify, request

trip_bp = Blueprint("trip", __name__)

from app import db
from app.models import Trip


@trip_bp.post("/")
def create_trip():
    data = request.get_json()

    trip = Trip(
        destination=data["destination"],
        start_date=date.fromisoformat(data["start_date"]),
        end_date=date.fromisoformat(data["end_date"]),
        budget=data["budget"],
        max_travelers=data["max_travelers"],
    )

    db.session.add(trip)
    db.session.commit()

    return jsonify({"message": "Trip created successfully", "trip_id": trip.id}), 201
