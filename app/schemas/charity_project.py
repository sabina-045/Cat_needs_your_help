from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field, PositiveInt, Extra

from app.services.constants import STRING_MAX_LENGTH, STRING_MIN_LENGTH


class CharityProjectUpdate(BaseModel):
    full_amount: Optional[PositiveInt]
    name: Optional[str] = Field(None, min_length=STRING_MIN_LENGTH, max_length=STRING_MAX_LENGTH)
    description: Optional[str] = Field(None, min_length=STRING_MIN_LENGTH)

    class Config:
        extra = Extra.forbid


class CharityProjectCreate(CharityProjectUpdate):
    """Схема для создания объектов."""
    full_amount: PositiveInt
    name: str = Field(min_length=STRING_MIN_LENGTH, max_length=STRING_MAX_LENGTH)
    description: str = Field(min_length=STRING_MIN_LENGTH)


class CharityProjectDB(CharityProjectCreate):
    """Схема возвращаемых ответов из бд."""
    id: int
    invested_amount: Optional[int]
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
