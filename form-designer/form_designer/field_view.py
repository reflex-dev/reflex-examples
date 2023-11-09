from functools import partial

import reflex as rx

from .models import Field, FieldType, Option


class OptionItemCallable:
    def __call__(
        self, *children: rx.Component, value: rx.Var[str], **props
    ) -> rx.Component:
        ...


def foreach_field_options(
    options: list[Option], component: OptionItemCallable
) -> rx.Component:
    return rx.foreach(
        options,
        lambda option: component(
            option.label,
            value=rx.cond(option.value != "", option.value, option.label),
        ),
    )


def field_select(field: Field, fallback: rx.Component | None = None) -> rx.Component:
    return rx.cond(
        field.type_ == FieldType.select.value,
        rx.select(
            rx.cond(
                field.options,
                foreach_field_options(field.options, rx.option),
                rx.option("No options defined", value=""),
            ),
            name=field.name,
        ),
        fallback,
    )


def field_radio(field: Field, fallback: rx.Component | None = None) -> rx.Component:
    return rx.cond(
        field.type_ == FieldType.radio.value,
        rx.cond(
            field.options,
            rx.radio_group(
                foreach_field_options(field.options, rx.radio),
                name=field.name,
            ),
            rx.text("No options defined"),
        ),
        fallback,
    )


def checkbox_item(field: Field, option: Option):
    value = rx.cond(option.value != "", option.value, option.label)
    return rx.checkbox(
        option.label,
        value=value,
        name=f"{field.name}___{value}",
    )


def field_checkbox(field: Field, fallback: rx.Component | None = None) -> rx.Component:
    return rx.cond(
        field.type_ == FieldType.checkbox.value,
        rx.cond(
            field.options,
            rx.foreach(
                field.options,
                lambda option: checkbox_item(field, option),
            ),
            rx.text("No options defined"),
        ),
        fallback,
    )


def field_input(field: Field):
    return field_checkbox(
        field,
        field_radio(
            field,
            field_select(
                field,
                rx.cond(
                    field.type_ == FieldType.textarea.value,
                    rx.text_area(
                        placeholder=field.prompt,
                        name=field.name,
                    ),
                    rx.input(
                        placeholder=field.prompt,
                        type_=field.type_.to(str),
                        name=field.name,
                    ),
                ),
            ),
        ),
    )


def field_prompt(field: Field, show_name: bool = False):
    name = f" ({field.name})" if show_name else ""
    return rx.cond(
        field.prompt != "", rx.text(f"{field.prompt}{name}"), rx.text(field.name)
    )


def field_view(field: Field):
    return rx.box(
        rx.hstack(
            field_prompt(field),
            rx.text(rx.cond(field.required, "*", "")),
        ),
        field_input(field),
        border="1px solid black",
        padding="5px",
        width="100%",
    )
