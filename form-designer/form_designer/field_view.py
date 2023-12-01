import reflex as rx
import reflex.components.radix.themes as rdxt

from . import common as cm
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
        rdxt.selectroot(
            rdxt.selecttrigger(placeholder="Select an option"),
            rdxt.selectcontent(
                rx.cond(
                    field.options,
                    foreach_field_options(field.options, rdxt.selectitem),
                    rdxt.selectitem("No options defined", value=""),
                ),
            ),
            name=field.name,
        ),
        fallback,
    )


def radio_item(*children: rx.Component, value: rx.Var[str], **props) -> rx.Component:
    return rx.el.label(
        rdxt.radiogroupitem(value=value, margin_left="2em", **props),
        *children,
    )


def field_radio(field: Field, fallback: rx.Component | None = None) -> rx.Component:
    return rx.cond(
        field.type_ == FieldType.radio.value,
        rx.cond(
            field.options,
            rdxt.radiogrouproot(
                foreach_field_options(field.options, radio_item),
                name=field.name,
            ),
            rdxt.text("No options defined"),
        ),
        fallback,
    )


def checkbox_item(field: Field, option: Option):
    value = rx.cond(option.value != "", option.value, option.label)
    return rx.el.label(
        rdxt.checkbox(
            value=value,
            name=f"{field.name}___{value}",
            margin_left="2em",
        ),
        option.label,
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
            rdxt.text("No options defined"),
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
                    rdxt.textarea(
                        placeholder=field.prompt,
                        name=field.name,
                    ),
                    rdxt.textfieldinput(
                        placeholder=field.prompt,
                        type=field.type_.to(str),
                        name=field.name,
                    ),
                ),
            ),
        ),
    )


def field_prompt(field: Field, show_name: bool = False):
    name = f" ({field.name})" if show_name else ""
    return rx.cond(
        field,
        rx.cond(
            field.prompt != "", rdxt.text(f"{field.prompt}{name}"), rdxt.text(field.name)
        ),
    )


def field_view(field: Field):
    return rdxt.box(
        cm.hstack(
            field_prompt(field),
            rdxt.text(rx.cond(field.required, "*", "")),
        ),
        field_input(field),
        border="1px solid var(--gray-8)",
        padding="5px",
        width="100%",
    )
