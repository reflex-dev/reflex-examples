import datetime

from sqlmodel import Column, DateTime, Field, func

import reflex as rx


class AuthSession(
    rx.Model,
    table=True,  # type: ignore
):
    """Correlate a session_id with an arbitrary user_id."""

    user_id: int = Field(index=True, nullable=False)
    session_id: str = Field(unique=True, index=True, nullable=False)
    expiration: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
