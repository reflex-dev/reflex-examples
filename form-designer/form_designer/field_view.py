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


def field_select(field: Field) -> rx.Component:
    return rdxt.select_root(
        rdxt.select_trigger(placeholder="Select an option"),
        rdxt.select_content(
            rx.cond(
                field.options,
                foreach_field_options(field.options, rdxt.select_item),
            ),
        ),
        name=field.name,
    )


def radio_item(*children: rx.Component, value: rx.Var[str], **props) -> rx.Component:
    return rx.el.label(
        cm.hstack(
            rdxt.radio_group_item(value=value, **props),
            *children,
        )
    )


def field_radio(field: Field) -> rx.Component:
    return rx.cond(
        field.options,
        rdxt.radio_group_root(
            cm.vstack(
                foreach_field_options(field.options, radio_item),
                align="start",
            ),
            name=field.name,
        ),
        rdxt.text("No options defined"),
    )


def checkbox_item(field: Field, option: Option):
    value = rx.cond(option.value != "", option.value, option.label)
    return rx.el.label(
        cm.hstack(
            rdxt.checkbox(
                value=value,
                name=f"{field.name}___{value}",
            ),
            option.label,
            margin_right="2em",
        )
    )


def field_checkbox(field: Field) -> rx.Component:
    return rx.cond(
        field.options,
        rx.foreach(
            field.options,
            lambda option: checkbox_item(field, option),
        ),
        rdxt.text("No options defined"),
    )


def field_input(field: Field):
    return rx.match(
        field.type_,
        (FieldType.checkbox.value, field_checkbox(field)),
        (FieldType.radio.value, field_radio(field)),
        (FieldType.select.value, field_select(field)),
        (
            FieldType.textarea.value,
            rdxt.textarea(
                placeholder=field.prompt,
                name=field.name,
            ),
        ),
        rdxt.textfield_input(
            placeholder=field.prompt,
            type=field.type_.to(str),
            name=field.name,
        ),
    )


def field_prompt(field: Field, show_name: bool = False):
    name = f" ({field.name})" if show_name else ""
    return rx.cond(
        field,
        rx.cond(
            field.prompt != "",
            rdxt.text(f"{field.prompt}{name}"),
            rx.cond(
                field.name != "",
                rdxt.text(field.name),
                rdxt.text("[unnamed field]"),
            ),
        ),
    )


def field_view(field: Field):
    return rdxt.card(
        cm.hstack(
            field_prompt(field),
            rdxt.text(rx.cond(field.required, "*", "")),
        ),
        field_input(field),
        width="100%",
    )
