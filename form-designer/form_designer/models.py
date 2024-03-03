from enum import Enum

import sqlmodel

import reflex as rx
from reflex.utils.serializers import serializer


class FieldType(Enum):
    text = "text"
    number = "number"
    email = "email"
    password = "password"
    checkbox = "checkbox"
    radio = "radio"
    select = "select"
    textarea = "textarea"


@serializer
def serialize_field_type(value: FieldType) -> str:
    return value.value


class Option(rx.Model, table=True):
    label: str = ""
    value: str = ""

    field_id: int = sqlmodel.Field(foreign_key="field.id")


class Field(rx.Model, table=True):
    name: str = ""
    type_: FieldType = FieldType.text
    required: bool = False
    prompt: str = ""

    form_id: int = sqlmodel.Field(foreign_key="form.id")
    options: list[Option] = sqlmodel.Relationship(
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"},
    )
    field_values: list["FieldValue"] = sqlmodel.Relationship(
        back_populates="field",
        sa_relationship_kwargs={"lazy": "noload", "cascade": "all, delete"},
    )


class Form(rx.Model, table=True):
    name: str = ""

    fields: list[Field] = sqlmodel.Relationship(
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"},
    )
    responses: list["Response"] = sqlmodel.Relationship(
        back_populates="form",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )


class FieldValue(rx.Model, table=True):
    field_id: int = sqlmodel.Field(foreign_key="field.id")
    response_id: int = sqlmodel.Field(foreign_key="response.id")
    value: str

    field: Field = sqlmodel.Relationship(sa_relationship_kwargs={"lazy": "selectin"})


class Response(rx.Model, table=True):
    client_token: str
    form_id: int = sqlmodel.Field(foreign_key="form.id")
    form: Form = sqlmodel.Relationship(back_populates="responses")

    field_values: list[FieldValue] = sqlmodel.Relationship(
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )
