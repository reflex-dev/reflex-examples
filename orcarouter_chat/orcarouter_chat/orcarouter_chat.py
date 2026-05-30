"""OrcaRouter chat example for Reflex.

Demonstrates calling OrcaRouter (https://www.orcarouter.ai) -- an OpenAI-compatible
LLM gateway -- from a Reflex app, with a runtime-loaded model dropdown that lets you
switch between adaptive routing (orcarouter/auto) and specific upstream models in
one click.

Run:
    cp .env.example .env  # fill in ORCAROUTER_API_KEY (get one at https://www.orcarouter.ai/console)
    pip install -r requirements.txt
    reflex run
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import httpx
import reflex as rx
from openai import AsyncOpenAI

try:
    from dotenv import load_dotenv

    _here = Path(__file__).resolve().parent
    for candidate in (_here / ".env", _here.parent / ".env"):
        if candidate.exists():
            load_dotenv(candidate, override=False)
            break
except ImportError:
    pass

ORCAROUTER_BASE_URL = "https://api.orcarouter.ai/v1"
ORCAROUTER_PRICING_URL = "https://www.orcarouter.ai/api/pricing"

ATTRIBUTION_HEADERS = {
    "HTTP-Referer": "https://www.orcarouter.ai/",
    "X-Title": "reflex-orcarouter-chat",
}

FALLBACK_MODELS: list[str] = [
    "orcarouter/auto",
    "openai/gpt-5.5",
    "google/gemini-3-flash-preview",
    "anthropic/claude-opus-4.7",
    "grok/grok-4.3",
    "deepseek/deepseek-v4-pro",
    "minimax/minimax-m2.7",
    "qwen/qwen3.6-flash",
]


def is_chat_model(name: str, entry: dict[str, Any]) -> bool:
    """Filter /api/pricing entries down to chat-LLM models.

    Mirrors the rules documented in OrcaRouter's pricing schema: skip image /
    video / embedding / TTS / STT / rerank entries plus models that only live
    on the responses or completions endpoint.
    """
    eps = set(entry.get("supported_endpoint_types") or [])
    n = name.lower()
    if "image-generation" in eps or "openai-video" in eps:
        return False
    if "image" in set(entry.get("output_modalities") or []):
        return False
    if any(k in n for k in ("imagen", "dall-e", "gpt-image", "grok-imagine")):
        return False
    if "embedding" in n or "tts" in n or n.endswith("-speech"):
        return False
    if "whisper" in n or "transcrib" in n or "rerank" in n:
        return False
    if "openai-response" in eps and "openai" not in eps:
        return False
    if "codex" in n:
        return False
    if re.match(r"openai/gpt-5(\.\d+)?-pro", n):
        return False
    return True


def is_reasoning_model(model: str) -> bool:
    """Models that reject `temperature` (and need longer timeouts).

    Detected by the OrcaRouter-documented patterns: Claude Opus reasoning,
    OpenAI gpt-5 / o-series, DeepSeek reasoner / r1, plus the conservative
    catch-all `*-reasoner` / `*-thinking` suffix used by several upstreams.
    The submit handler also retries once without temperature if the upstream
    still rejects it, so this list is a fast path, not a hard contract.
    """
    m = model.lower()
    if m.startswith("anthropic/claude-opus"):
        return True
    if re.match(r"openai/gpt-5(\.\d+)?($|[-/])", m):
        return True
    if re.match(r"openai/o\d+($|[-/])", m):
        return True
    if "deepseek-reasoner" in m or "deepseek-r1" in m:
        return True
    if m.endswith("-reasoner") or m.endswith("-thinking"):
        return True
    return False


def force_stream_model(model: str) -> bool:
    """z-ai/glm-4.5 family rejects non-streaming requests."""
    m = model.lower()
    return m.startswith("z-ai/glm-4.5")


class State(rx.State):
    """Chat state."""

    models: list[str] = list(FALLBACK_MODELS)
    model: str = FALLBACK_MODELS[0]
    pinned_models: list[str] = []
    custom_model: str = ""
    use_fallback_route: bool = False
    fallback_models_csv: str = "openai/gpt-5.5, anthropic/claude-opus-4.7"

    prompt: str = ""
    messages: list[dict[str, str]] = []
    streaming: bool = False
    error: str = ""

    last_model: str = ""
    last_input_tokens: int = 0
    last_output_tokens: int = 0
    models_source: str = "fallback"

    @rx.event(background=True)
    async def load_models(self):
        """Pull the live model catalog from OrcaRouter; fall back to the curated
        flagship list if the network is unavailable so the demo always boots.

        Runs as a background task so the 10s HTTP fetch never holds the state
        lock -- the UI stays responsive while the catalog loads.
        """
        async with self:
            pinned_snapshot = list(self.pinned_models)
            current_model = self.model

        live_merged: list[str] | None = None
        error_msg = ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(ORCAROUTER_PRICING_URL)
                resp.raise_for_status()
                payload = resp.json()
            entries = payload.get("data") or []
            live = [
                e["model_name"]
                for e in entries
                if "model_name" in e and is_chat_model(e["model_name"], e)
            ]
            if live:
                live_merged = [
                    "orcarouter/auto",
                    *sorted(m for m in live if m != "orcarouter/auto"),
                ]
        except Exception as exc:  # noqa: BLE001 - demo path, surface the reason in UI
            error_msg = f"Could not load live model catalog: {exc}. Using fallback list."

        if live_merged is not None:
            merged = live_merged
            source = f"live ({len(merged)} models from https://www.orcarouter.ai/models)"
        else:
            merged = list(FALLBACK_MODELS)
            source = (
                f"fallback ({len(FALLBACK_MODELS)} flagship models; "
                "see https://www.orcarouter.ai/models for the full catalog)"
            )

        for p in pinned_snapshot:
            if p not in merged:
                merged.append(p)

        new_model = current_model if current_model in merged else merged[0]

        async with self:
            self.models = merged
            self.model = new_model
            self.models_source = source
            if error_msg:
                self.error = error_msg

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value

    @rx.event
    def set_model(self, value: str):
        self.model = value

    @rx.event
    def set_custom_model(self, value: str):
        self.custom_model = value

    @rx.event
    def apply_custom_model(self):
        candidate = self.custom_model.strip()
        if not candidate:
            return
        if candidate not in self.pinned_models:
            self.pinned_models = [*self.pinned_models, candidate]
        if candidate not in self.models:
            self.models = [candidate, *self.models]
        self.model = candidate
        self.custom_model = ""

    @rx.event
    def toggle_fallback_route(self, checked: bool):
        self.use_fallback_route = checked

    @rx.event
    def set_fallback_models_csv(self, value: str):
        self.fallback_models_csv = value

    @rx.event
    def clear_chat(self):
        self.messages = []
        self.error = ""
        self.last_model = ""
        self.last_input_tokens = 0
        self.last_output_tokens = 0

    @rx.event
    def submit_from_form(self, _form_data: dict[str, Any]):
        return State.submit

    @rx.event(background=True)
    async def submit(self):
        async with self:
            prompt = self.prompt.strip()
            if not prompt or self.streaming:
                return
            api_key = os.environ.get("ORCAROUTER_API_KEY", "").strip()
            if not api_key:
                cwd = os.getcwd()
                env_here = (Path(cwd) / ".env").exists()
                self.error = (
                    "ORCAROUTER_API_KEY is not set. Create a .env next to rxconfig.py "
                    "(or export the env var before running) and restart `reflex run`. "
                    f"Looked at cwd={cwd}, .env exists there: {env_here}."
                )
                return
            model = self.model
            self.error = ""
            self.streaming = True
            self.messages = [
                *self.messages,
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": ""},
            ]
            self.prompt = ""
            history = list(self.messages[:-1])
            use_fallback = self.use_fallback_route
            fallback_csv = self.fallback_models_csv

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=ORCAROUTER_BASE_URL,
            default_headers=ATTRIBUTION_HEADERS,
        )

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": history,
            "stream": True,
            "stream_options": {"include_usage": True},
            "timeout": 300.0,
        }
        if not is_reasoning_model(model):
            kwargs["temperature"] = 0.7
        if use_fallback:
            fallback_list = [m.strip() for m in fallback_csv.split(",") if m.strip()]
            if fallback_list:
                kwargs["extra_body"] = {"models": fallback_list, "route": "fallback"}

        async def consume(call_kwargs: dict[str, Any]):
            stream = await client.chat.completions.create(**call_kwargs)
            async for chunk in stream:
                if chunk.usage is not None:
                    async with self:
                        self.last_input_tokens = chunk.usage.prompt_tokens or 0
                        self.last_output_tokens = chunk.usage.completion_tokens or 0
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content or ""
                if not delta:
                    continue
                async with self:
                    msgs = list(self.messages)
                    msgs[-1] = {
                        "role": "assistant",
                        "content": msgs[-1]["content"] + delta,
                    }
                    self.messages = msgs

        try:
            try:
                await consume(kwargs)
            except Exception as exc:  # noqa: BLE001
                msg = str(exc).lower()
                if "temperature" in msg and "temperature" in kwargs:
                    retry_kwargs = {k: v for k, v in kwargs.items() if k != "temperature"}
                    async with self:
                        msgs = list(self.messages)
                        msgs[-1] = {"role": "assistant", "content": ""}
                        self.messages = msgs
                    await consume(retry_kwargs)
                else:
                    raise
        except Exception as exc:  # noqa: BLE001 - demo path, surface the reason in UI
            async with self:
                self.error = f"{type(exc).__name__}: {exc}"
                if self.messages and self.messages[-1]["role"] == "assistant":
                    self.messages = self.messages[:-1]
        finally:
            async with self:
                self.streaming = False
                self.last_model = model


def message_bubble(msg: dict[str, str]) -> rx.Component:
    is_user = msg["role"] == "user"
    return rx.box(
        rx.text(msg["content"], white_space="pre-wrap"),
        background=rx.cond(is_user, "var(--accent-3)", "var(--gray-3)"),
        padding="0.75em 1em",
        border_radius="12px",
        max_width="80%",
        align_self=rx.cond(is_user, "flex-end", "flex-start"),
    )


def model_picker() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.select(
                State.models,
                value=State.model,
                on_change=State.set_model,
                width="100%",
            ),
            rx.button(
                "Refresh",
                on_click=State.load_models,
                variant="soft",
            ),
            width="100%",
        ),
        rx.hstack(
            rx.input(
                placeholder="Custom model id (e.g. orcarouter/your-router)",
                value=State.custom_model,
                on_change=State.set_custom_model,
                width="100%",
            ),
            rx.button("Use", on_click=State.apply_custom_model, variant="soft"),
            width="100%",
        ),
        rx.hstack(
            rx.checkbox(
                "Enable fallback route",
                checked=State.use_fallback_route,
                on_change=State.toggle_fallback_route,
            ),
            rx.cond(
                State.use_fallback_route,
                rx.input(
                    value=State.fallback_models_csv,
                    on_change=State.set_fallback_models_csv,
                    placeholder="comma-separated fallback models",
                    width="100%",
                ),
            ),
            width="100%",
        ),
        rx.text(State.models_source, size="1", color="gray"),
        width="100%",
        spacing="2",
    )


def chat_panel() -> rx.Component:
    return rx.vstack(
        rx.foreach(State.messages, message_bubble),
        rx.cond(
            State.streaming,
            rx.text("...", color="gray"),
        ),
        rx.cond(
            State.error != "",
            rx.callout(State.error, icon="triangle_alert", color_scheme="red"),
        ),
        width="100%",
        align="stretch",
        spacing="3",
        min_height="40vh",
    )


def input_bar() -> rx.Component:
    return rx.form(
        rx.hstack(
            rx.input(
                name="prompt",
                placeholder="Ask anything...",
                value=State.prompt,
                on_change=State.set_prompt,
                width="100%",
            ),
            rx.button(
                "Send",
                type="submit",
                loading=State.streaming,
            ),
            rx.button(
                "Clear",
                on_click=State.clear_chat,
                variant="soft",
                type="button",
            ),
            width="100%",
        ),
        on_submit=State.submit_from_form,
        reset_on_submit=False,
        width="100%",
    )


def footer() -> rx.Component:
    return rx.hstack(
        rx.text(
            "Last call: ",
            rx.cond(State.last_model != "", State.last_model, "--"),
            "  |  in/out tokens: ",
            State.last_input_tokens.to_string(),
            "/",
            State.last_output_tokens.to_string(),
            size="1",
            color="gray",
        ),
        rx.spacer(),
        rx.link(
            "OrcaRouter docs",
            href="https://docs.orcarouter.ai",
            is_external=True,
            size="1",
        ),
        width="100%",
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("OrcaRouter chat", size="6"),
            rx.text(
                "OpenAI-compatible chat against ",
                rx.code("api.orcarouter.ai/v1"),
                ". Switch the router/model from the dropdown -- same API key, "
                "same endpoint.",
                size="2",
                color="gray",
            ),
            model_picker(),
            rx.divider(),
            chat_panel(),
            input_bar(),
            footer(),
            spacing="4",
            width="100%",
        ),
        size="3",
        padding_y="2em",
    )


app = rx.App(theme=rx.theme(accent_color="violet"))
app.add_page(index, route="/", on_load=State.load_models)
