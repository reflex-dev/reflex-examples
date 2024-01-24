import json
from typing import Optional

import reflex as rx
import reflex.components.radix.themes as rdxt
import reflex.components.radix.primitives as rdxp

from .fetchers import user_stats


TEAM = [
    "masenf",
    "Lendemor",
    "picklelo",
    "martinxu9",
    "ElijahAhianyo",
    "Alek99",
    "tgberkeley",
    "jackie-pc",
]


class State(rx.State):
    selected_users: list[str]
    user_stats: list[dict] = []
    fetching: bool = False
    selected_users_json: str = rx.LocalStorage()
    user_stats_json: str = rx.LocalStorage()
    username: str = ""
    progress: Optional[int] = None

    def on_load(self):
        if self.selected_users_json:
            self.selected_users = json.loads(self.selected_users_json)
        if self.user_stats_json:
            self.user_stats = json.loads(self.user_stats_json)
        return State.fetch_missing_stats

    def _save_selected_users(self):
        self.selected_users_json = json.dumps(self.get_value(self.selected_users))

    def _save_user_stats(self):
        self.user_stats_json = json.dumps(self.get_value(self.user_stats))

    def _selected_users_lower(self):
        return [u.lower() for u in self.selected_users]

    def _already_fetched_users(self):
        return set(u["login"].lower() for u in self.user_stats)

    def _remove_data_for_deselected_users(self):
        selected_users_lower = self._selected_users_lower()
        remove_data = []
        for user_data in self.user_stats:
            if user_data["login"].lower() not in selected_users_lower:
                remove_data.append(user_data)
        for user_data in remove_data:
            self.user_stats.remove(user_data)

    @rx.background
    async def clear_username(self):
        async with self:
            self.username = ""

    @rx.background
    async def fetch_missing_stats(self):
        async with self:
            if self.fetching:
                return
            self._remove_data_for_deselected_users()
            already_fetched_users = self._already_fetched_users()
            self.fetching = True
        try:
            for user in self._selected_users_lower():
                if user in already_fetched_users:
                    continue
                user_data = await user_stats(user)
                if user_data is None:
                    continue
                async with self:
                    if user_data["login"].lower() in set(self._selected_users_lower()):
                        self.user_stats.append(user_data)
        finally:
            async with self:
                self._save_user_stats()
                self.fetching = False
        async with self:
            # check if any users were added while fetching
            currently_fetched_users = self._already_fetched_users()
            if any(
                user.lower() not in currently_fetched_users
                for user in self.selected_users
            ):
                return State.fetch_missing_stats
            else:
                return State.clear_username

    def remove_user(self, user: str):
        self.selected_users.remove(user)
        self._save_selected_users()
        self._remove_data_for_deselected_users()

    def add_user(self):
        if not self.username:
            return
        if self.username in self.selected_users:
            return
        self.selected_users.append(self.username)
        self._save_selected_users()
        return State.fetch_missing_stats

    @rx.cached_var
    def data_pretty(self) -> str:
        return json.dumps(self.user_stats, indent=2)


def index() -> rx.Component:
    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
        rdxt.heading("Github Stats", font_size="2em"),
            rdxt.flex(
                rx.foreach(
                    State.selected_users,
                    lambda user: rdxt.box(
                        user,
                        rdxt.button(
                            "X",
                            size="2",
                            on_click=State.remove_user(user),
                            margin_left="5px",
                        ),
                        border="1px solid black",
                        margin="10px",
                        padding="5px",
                    ),
                ),
                direction="row",
                wrap="wrap",
            ),
            rx.cond(
                State.fetching,
                rx.vstack(
                    rdxt.text("Fetching Data..."),
                    # TODO use rdxp.progress
                    rx.progress(is_indeterminate=True, width="50vw"),
                ),
            ),
            rdxt.textfield_root(
                rdxt.textfield_input(
                    placeholder="Github Username",
                    value=State.username,
                    on_change=State.set_username,
                    size="2"
                ),
                rdxt.textfield_slot(
                    rdxt.button("Get", size="2",  on_click=State.add_user),
                ),
                direction="horizontal"
            ),
            rdxt.box(
                rx.recharts.bar_chart(
                    rx.recharts.graphing_tooltip(cursor=False),
                    rx.recharts.bar(
                        data_key="repositoriesContributedTo",
                        stroke="#8884d8",
                        fill="#8884d8",
                    ),
                    rx.recharts.bar(
                        data_key="mergedPullRequests", stroke="#82ca9d", fill="#82ca9d"
                    ),
                    rx.recharts.bar(
                        data_key="openIssues", stroke="#ffc658", fill="#ffc658"
                    ),
                    rx.recharts.bar(
                        data_key="closedIssues", stroke="#ff0000", fill="#ff0000"
                    ),
                    rx.recharts.x_axis(data_key="login"),
                    rx.recharts.y_axis(),
                    data=State.user_stats,
                ),
                width="100%",
                height="15em",
            ),
            rdxt.textarea(
                value=State.data_pretty,
            ),
        ),
    )


app = rx.App(
    theme=rdxt.theme(
        appearance="light", has_background=True, radius="medium", high_contrast=True,
    ),
)
app.add_page(index, on_load=State.on_load)
