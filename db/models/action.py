import datetime
from sqlalchemy import BigInteger, DateTime, String, Text, UniqueConstraint, func, null
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Action(Base):
    __tablename__ = "action"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        primary_key=True,
        autoincrement=True,
        comment="id",
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="name")

    source: Mapped[str] = mapped_column(String(1024), comment="url")
    source_hash: Mapped[str] = mapped_column(
        String(32), comment="shorter url"
    )

    difficulty_level: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="difficulty level"
    )

    category: Mapped[str] = mapped_column(
        String(32), default="''", comment="workout category"
    )
    
    muscle_type: Mapped[str] = mapped_column(
        Text(), default="[]", nullable=False, comment="primary muscle involved"
    )
    other_muscle_types: Mapped[str] = mapped_column(
        Text(), default="[]", comment="other muscles involved"
    )

    equipment: Mapped[str] = mapped_column(
        Text(), default="[]", nullable=False, comment="equipment used"
    )

    cover: Mapped[str] = mapped_column(Text(), nullable=False, comment="action cover")
    action_pictures: Mapped[str] = mapped_column(
        Text(), default="[]", comment="action instruction pictures"
    )
    muscle_pictures: Mapped[str] = mapped_column(
        Text(), default="[]", comment="muscle pictures"
    )

    video: Mapped[str] = mapped_column(
        String(1024), default="''", comment="video instruction"
    )
    instruction: Mapped[str] = mapped_column(
        Text(), default="''", comment="action instructions"
    )

    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="create time"
    )

    # __table_args__ = (UniqueConstraint("id", "name", name="unix_id_name"),)