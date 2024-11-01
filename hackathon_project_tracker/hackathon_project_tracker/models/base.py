from __future__ import annotations

import datetime  # trunk-ignore(ruff/TCH003)

import reflex as rx
from sqlmodel import Column, DateTime, Field, func


class Base(rx.Model, table=False):
    """Common attributes for all models."""
    timestamp: datetime.datetime = Field(
        sa_column=Column(
            DateTime(
                timezone=True,
            ),
            server_default=func.now(),
        ),
    )
