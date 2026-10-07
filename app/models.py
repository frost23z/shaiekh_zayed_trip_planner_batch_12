from datetime import date

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

trip_travelers = Table(
    "trip_travelers",
    db.metadata,
    Column(
        "trip_id",
        ForeignKey("trips.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "traveler_id",
        ForeignKey("travelers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Trip(db.Model):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    destination: Mapped[str] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    budget: Mapped[int] = mapped_column(nullable=False)
    max_travelers: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="PLANNED")

    travelers: Mapped[list["Traveler"]] = relationship(
        secondary=trip_travelers,
        back_populates="trips",
    )

    def __repr__(self) -> str:
        return f"<Trip id={self.id}, destination={self.destination}, start_date={self.start_date}, end_date={self.end_date}, budget={self.budget}, max_travelers={self.max_travelers}, status={self.status}>"


class Traveler(db.Model):
    __tablename__ = "travelers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)

    trips: Mapped[list["Trip"]] = relationship(
        secondary=trip_travelers,
        back_populates="travelers",
    )
