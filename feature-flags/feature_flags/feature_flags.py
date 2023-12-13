import copy
import re

from fastapi import HTTPException
from typing import Optional

import reflex as rx
from sqlmodel import Field


class FeatureFlags(rx.Model, table=True):
    name: str = Field(primary_key=True)
    value: str = Field()





class FeatureFlagsState(rx.State):
    feature_flags_as_loaded_from_db: Optional[dict[str, str]] = None

    pending_creates_or_updates: dict[str, str] = {}
    pending_deletes: set[str] = set()

    @rx.var
    def save_button_color(self) -> str:
        if self.pending_creates or self.pending_deletes or self.pending_updates:
            return "red"
        else:
            return ""

    def load_feature_flags_from_db(self):
        """Populates self.feature_flags_as_loaded_from_db"""
        with rx.session() as session:
            feature_flags = session.exec(FeatureFlags.select).all()
        self.feature_flags_as_loaded_from_db = {ff.name: ff.value for ff in feature_flags}

    @rx.var
    def feature_flag_name_value_pairs(self) -> list[tuple[str, str]]:
        if self.feature_flags_as_loaded_from_db is None:
            self.load_feature_flags_from_db()

        return sorted([(flag_name, flag_value) for flag_name, flag_value in self.latest_feature_flags_view().items()])

    def latest_feature_flags_view(self) -> dict[str, str]:
        latest = {**(self.feature_flags_as_loaded_from_db or {}), **self.pending_creates_or_updates}
        for k in self.pending_deletes:
            del latest[k]
        return latest

    @rx.var
    def pending_creates(self) -> set[str]:
        result = set(copy.deepcopy(self.latest_feature_flags_view()))
        for k in self.feature_flags_as_loaded_from_db or {}:
            if k in result:
                result.remove(k)
        for k in self.pending_deletes:
            if k in result:
                result.remove(k)
        return result

    @rx.var
    def pending_updates(self) -> set[str]:
        result = set()
        for k in self.feature_flags_as_loaded_from_db or {}:
            if k in self.pending_creates_or_updates:
                result.add(k)
        for k in self.pending_deletes:
            if k in result:
                result.remove(k)
        return result

    def update_feature_flag(self, k: str, val: str):
        self.pending_creates_or_updates[k] = val

    def save_to_db(self):
        with rx.session() as session:
            for k, v in self.pending_creates_or_updates.items():
                if k not in self.pending_deletes:
                    # TODO: Do we have to select the item before updating it?
                    ff = session.exec(FeatureFlags.select.where(FeatureFlags.name == k)).first()
                    if not ff:
                        ff = FeatureFlags(name=k, value=v)
                    else:
                        ff.value = v
                    session.add(ff)

            for k in self.pending_deletes:
                # TODO: Do we have to select the item before deleting it?
                ff = session.exec(FeatureFlags.select.where(FeatureFlags.name == k)).first()
                if ff:
                    session.delete(ff)
            session.commit()
        self.pending_deletes = set()
        self.pending_creates_or_updates = {}
        self.load_feature_flags_from_db()

    def stage_delete_feature_flag(self, k: str):
        self.pending_deletes.add(k)


class CreateFlagModalState(FeatureFlagsState):
    new_flag_modal_is_open: bool = False
    new_flag_modal_error: Optional[str] = None

    new_flag_modal_flag_name: Optional[str] = ""
    new_flag_modal_flag_value: Optional[str] = ""

    def new_flag_modal_stage(self):
        if re.search(r"[^a-zA-Z0-9_]+", self.new_flag_modal_flag_name):
            self.new_flag_modal_error = "Flag name must be contain only one or more alphanumeric or _ chars"
            return
        if self.new_flag_modal_flag_name in self.latest_feature_flags_view():
            self.new_flag_modal_error = "Flag already exists"
            return
        self.pending_creates_or_updates[self.new_flag_modal_flag_name] = self.new_flag_modal_flag_value
        self.reset()

    def new_flag_modal_cancel(self):
        self.reset()


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
            rx.heading("Flex-Flags", font_size="2em"),
            rx.hstack(
                rx.button("Save", on_click=FeatureFlagsState.save_to_db, color=FeatureFlagsState.save_button_color),
                rx.button("Add new", on_click=CreateFlagModalState.set_new_flag_modal_is_open(True)),
            ),
            rx.cond(FeatureFlagsState.pending_deletes,
                    rx.text(f"Pending deletes: {FeatureFlagsState.pending_deletes}", color="red")),
            rx.cond(FeatureFlagsState.pending_creates,
                    rx.text(f"Pending creates: {FeatureFlagsState.pending_creates}", color="red")),
            rx.cond(FeatureFlagsState.pending_updates,
                    rx.text(f"Pending updates: {FeatureFlagsState.pending_updates}", color="red")),
            rx.modal(
                rx.modal_overlay(
                    rx.modal_content(
                        rx.modal_header("Add new feature flag"),
                        rx.modal_body(
                            "Add a new feature flag",
                            rx.hstack(
                                rx.input(value=CreateFlagModalState.new_flag_modal_flag_name, width='30%',
                                         on_change=CreateFlagModalState.set_new_flag_modal_flag_name),
                                rx.input(value=CreateFlagModalState.new_flag_modal_flag_value,
                                         on_change=CreateFlagModalState.set_new_flag_modal_flag_value,
                                         width='70%')),
                            rx.cond(CreateFlagModalState.new_flag_modal_error,
                                    rx.text(CreateFlagModalState.new_flag_modal_error, color="red"))
                        ),
                        rx.modal_footer(
                            rx.button(
                                "Stage", on_click=CreateFlagModalState.new_flag_modal_stage,
                            ),
                            rx.button(
                                "Cancel", on_click=CreateFlagModalState.new_flag_modal_cancel,
                            )
                        ),
                    )
                ),
                is_open=CreateFlagModalState.new_flag_modal_is_open,
            ),
            rx.table(
                rx.thead(
                    rx.tr(
                        rx.th("Flag name"),
                        rx.th("Flag value"),
                    )
                ),
                rx.tbody(
                    rx.cond(
                        # TODO follow up on "flashing" issue (needs is_hydrated cond right now...)
                        # Repro sequence:
                        # 1. Add a new flag X
                        # 2. Save
                        # 3. Open new tab T
                        # 4. from T, delete flag X, save
                        # 5. refresh T (see flash of X in browser)
                        # 6. refresh T again (see flash again!)
                        FeatureFlagsState.is_hydrated,
                        rx.foreach(
                            FeatureFlagsState.feature_flag_name_value_pairs,
                            lambda p: rx.tr(
                                rx.td(p[0]),
                                rx.td(
                                    rx.input(value=p[1],
                                             on_change=lambda v: FeatureFlagsState.update_feature_flag(p[0], v),
                                             width="70%")),
                                rx.td(rx.button("Delete",
                                                on_click=FeatureFlagsState.stage_delete_feature_flag(p[0]),
                                                width="30%"))
                            ),
                        ),
                    )
                ),
            ),
            on_mount=FeatureFlagsState.load_feature_flags_from_db,
        ),
    )


app = rx.App()


async def get_flag(flag_name: str):
    try:
        with rx.session() as session:
            flag = session.exec(FeatureFlags.select.where(FeatureFlags.name == flag_name)).first()
            if flag is None:
                raise ValueError()
    except Exception:
        raise HTTPException(status_code=404, detail="Flag not found")
    return {"flag_value": flag.value}


app.api.add_api_route("/flag/{flag_name}", get_flag)

app.add_page(index)
app.compile()
