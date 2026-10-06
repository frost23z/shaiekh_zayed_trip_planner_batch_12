from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from app import db


class Trip(db.Model):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    destination: Mapped[str] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    budget: Mapped[int] = mapped_column(nullable=False)
    max_travelers: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="PLANNED")

    def __repr__(self) -> str:
        return f"<Trip id={self.id}, destination={self.destination}, start_date={self.start_date}, end_date={self.end_date}, budget={self.budget}, max_travelers={self.max_travelers}, status={self.status}>"
