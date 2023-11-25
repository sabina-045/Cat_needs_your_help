from sqlalchemy import Column, String, Text

from app.core.db import Base
from app.services.constants import STRING_MAX_LENGTH


class CharityProject(Base):
    name = Column(String(STRING_MAX_LENGTH), nullable=False, unique=True)
    description = Column(Text, nullable=False)
