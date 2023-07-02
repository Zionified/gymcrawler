import datetime
from .base import MongoBaseModel

class SourceHTML(MongoBaseModel):
    __tablename__ = "source_html"

    source: str
    source_hash: str
    content: str
    create_time: datetime.datetime
