from sqlalchemy import select

from app import db
from app.dtos import (
    ExpenseCreate,
    TravelerCreate,
    TripCreate,
    TripResponse,
    TripStatusUpdate,
    TripUpdate,
)
from app.errors import AppError
from app.models import Expense, Traveler, Trip

ALLOWED_STATUS_TRANSITIONS = {
    "PLANNED": {"ONGOING", "CANCELLED"},
    "ONGOING": {"COMPLETED", "CANCELLED"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}


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

    if trip.status in ("COMPLETED", "CANCELLED"):
        raise AppError(
            409,
            "INVALID_TRIP_STATUS",
            "Completed or cancelled trips cannot be edited.",
        )

    update_data = data.model_dump(exclude_none=True)

    if "max_travelers" in update_data and update_data["max_travelers"] < len(
        trip.travelers
    ):
        raise AppError(
            409,
            "MAX_TRAVELERS_BELOW_CURRENT",
            "max_travelers cannot be less than the current number of travelers.",
        )

    new_start_date = update_data.get("start_date", trip.start_date)
    new_end_date = update_data.get("end_date", trip.end_date)

    if new_end_date <= new_start_date:
        raise AppError(
            400, "VALIDATION_ERROR", "trip end_date must be later than start_date."
        )

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
        raise AppError(
            409, "INVALID_TRIP_STATUS", "Travelers can only be added to planned trips."
        )

    traveler = db.session.scalar(
        select(Traveler).where(Traveler.email == traveler_data.email)
    )

    if traveler is not None and traveler in trip.travelers:
        raise AppError(
            409, "DUPLICATE_TRAVELER", "Traveler is already added to this trip."
        )

    if len(trip.travelers) >= trip.max_travelers:
        raise AppError(
            409,
            "TRIP_FULL",
            "The trip has reached its maximum traveler capacity.",
        )

    if traveler is None:
        traveler = Traveler(
            name=traveler_data.name,
            email=traveler_data.email,
        )
    else:
        for existing_trip in traveler.trips:
            if (
                existing_trip.start_date < trip.end_date
                and existing_trip.end_date > trip.start_date
            ):
                raise AppError(
                    409,
                    "TRAVELER_OVERLAP",
                    "Traveler already has a trip with overlapping dates.",
                )

    trip.travelers.append(traveler)

    db.session.commit()

    return TripResponse.model_validate(trip).model_dump(mode="json")


def remove_traveler_from_trip(trip_id: int, traveler_id: int):
    trip = db.session.get(Trip, trip_id)

    if not trip:
        return None

    if trip.status in ("COMPLETED", "CANCELLED"):
        raise AppError(
            409,
            "INVALID_TRIP_STATUS",
            "Completed or cancelled trips cannot be edited.",
        )

    traveler = db.session.get(Traveler, traveler_id)

    if not traveler or traveler not in trip.travelers:
        raise AppError(404, "TRAVELER_NOT_FOUND", "Traveler is not part of this trip.")

    trip.travelers.remove(traveler)

    db.session.commit()

    return TripResponse.model_validate(trip).model_dump(mode="json")


def add_expense_to_trip(trip_id: int, expense_data: ExpenseCreate):
    trip = db.session.get(Trip, trip_id)

    if not trip:
        return None

    if trip.status not in ("PLANNED", "ONGOING"):
        raise AppError(
            409,
            "INVALID_TRIP_STATUS",
            "Expenses can only be added to planned or ongoing trips.",
        )

    total_expenses = sum(expense.amount for expense in trip.expenses)

    if total_expenses + expense_data.amount > trip.budget:
        raise AppError(
            409, "BUDGET_EXCEEDED", "Trip expenses cannot exceed the trip budget."
        )

    expense = Expense(
        title=expense_data.title,
        amount=expense_data.amount,
        trip=trip,
    )

    db.session.add(expense)
    db.session.commit()

    return TripResponse.model_validate(trip).model_dump(mode="json")


def get_trip_summary(trip_id: int):
    trip = db.session.get(Trip, trip_id)

    if not trip:
        return None

    traveler_count = len(trip.travelers)
    total_expense = sum(expense.amount for expense in trip.expenses)

    return {
        "traveler_count": traveler_count,
        "available_seats": trip.max_travelers - traveler_count,
        "total_expense": total_expense,
        "remaining_budget": trip.budget - total_expense,
    }


def update_trip_status(trip_id: int, status_data: TripStatusUpdate):
    trip = db.session.get(Trip, trip_id)

    if not trip:
        return None

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[trip.status]

    if status_data.status not in allowed_statuses:
        raise AppError(
            409,
            "INVALID_STATUS_TRANSITION",
            f"Trip cannot transition from {trip.status} to {status_data.status}.",
        )

    trip.status = status_data.status

    db.session.commit()

    return TripResponse.model_validate(trip).model_dump(mode="json")


def trip_not_found_response(trip_id: int):
    return {
        "error": "TRIP_NOT_FOUND",
        "message": f"Trip with ID {trip_id} was not found.",
    }
