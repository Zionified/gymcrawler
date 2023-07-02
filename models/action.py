import datetime
from .base import MongoBaseModel


class Action(MongoBaseModel):
    __tablename__ = "action"

    _id: int
    name: str
    source: str
    source_hash: str

    difficulty_level: str

    category: str

    muscle_type: list[str]
    other_muscle_types: list[str]

    equipment: list[str]

    cover: str
    action_pictures: list[str]
    muscle_pictures: list[str]

    video: str
    instruction: str
    create_time: datetime.datetime
