import uuid
from pathlib import Path

import reflex as rx
from fastapi import Request
from reflex.event import EventSpec
from sqlmodel import or_
from webpush import WebPushSubscription

from rxconfig import config
from .models import Subscriber


application_server_key = Path("applicationServerKey").read_text()
register_endpoint = "/register-push"
register_endpoint_url = rx.Var(
    f"getBackendURL('{config.api_url}{register_endpoint}')",
    _var_data=rx.vars.VarData(
        imports={
            "/utils/state": [
                rx.ImportVar(tag="getBackendURL"),
            ],
        }
    ),
)


async def register_push(sub: WebPushSubscription, request: Request):
    try:
        browser_id = request.headers["X-Reflex-Browser-Id"]
        uuid.UUID(browser_id)
    except (KeyError, ValueError):
        return {"status": "error", "message": "Browser ID not provided"}

    with rx.session() as session:
        existing_sub = session.exec(
            Subscriber.select().where(
                or_(
                    Subscriber.browser_id == browser_id,
                    Subscriber.auth_key == sub.keys.auth,
                )
            )
        ).one_or_none()
        if existing_sub is not None:
            existing_sub.browser_id = browser_id
            existing_sub.auth_key = sub.keys.auth
            existing_sub.sub = sub.model_dump_json()
        else:
            session.add(
                Subscriber(
                    browser_id=browser_id,
                    auth_key=sub.keys.auth,
                    sub=sub.model_dump_json(),
                ),
            )
        session.commit()

    return {"status": "ok"}


def add_register_push_endpoint(app: rx.App):
    app.api.post(register_endpoint)(register_push)


def trigger_register(browser_id: rx.Var[str]) -> EventSpec:
    return rx.call_script(
        f"registerForPushNotifications('{register_endpoint_url}', '{application_server_key}', '{browser_id}')"
    )