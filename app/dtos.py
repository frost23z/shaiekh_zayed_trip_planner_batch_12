from datetime import date

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator


class TripCreate(BaseModel):
    destination: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    budget: PositiveInt
    max_travelers: PositiveInt

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("trip end_date must be later than start_date.")

        return self


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destination: str
    start_date: date
    end_date: date
    budget: int
    max_travelers: int
    status: str


class TripUpdate(BaseModel):
    destination: str | None = Field(default=None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    budget: PositiveInt | None = None
    max_travelers: PositiveInt | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one field must be provided for update.")

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date <= self.start_date
        ):
            raise ValueError("trip end_date must be later than start_date.")

        return self
