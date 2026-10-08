from datetime import date
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    PositiveInt,
    StringConstraints,
    model_validator,
)


class TripCreate(BaseModel):
    destination: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
    ]
    start_date: date
    end_date: date
    budget: PositiveInt
    max_travelers: PositiveInt

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("trip end_date must be later than start_date.")

        return self


class TripUpdate(BaseModel):
    destination: Annotated[
        str | None,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
    ] = None
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


class TravelerCreate(BaseModel):
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)
    ]
    email: Annotated[
        EmailStr, BeforeValidator(lambda v: v.lower() if isinstance(v, str) else v)
    ]


class ExpenseCreate(BaseModel):
    title: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=100,
        ),
    ]
    amount: PositiveInt


class TravelerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    amount: int


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    destination: str
    start_date: date
    end_date: date
    budget: int
    max_travelers: int
    status: str
    travelers: list[TravelerResponse] = []
    expenses: list[ExpenseResponse] = []


class TripStatusUpdate(BaseModel):
    status: Literal["PLANNED", "ONGOING", "COMPLETED", "CANCELLED"]
