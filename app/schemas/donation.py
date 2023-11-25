from datetime import datetime

from typing import Optional
from pydantic import BaseModel, PositiveInt, Extra


class DonationCreate(BaseModel):
    """Схема для создания пожертвования."""
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class UserDonation(DonationCreate):
    """Схема возвращаемых ответов при создании пожертвования."""
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationGet(UserDonation):
    """Схема возвращаемых ответов
    при получении списка пожертвований."""
    user_id: int
    invested_amount: Optional[int]
    fully_invested: bool
    close_date: Optional[datetime]
    comment: Optional[str]

    class Config:
        orm_mode = True
