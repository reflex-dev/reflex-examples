from __future__ import annotations

import datetime
import os

import pytz
import reflex as rx
from openai import OpenAI

# Import open-telemetry dependencies
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from sqlalchemy import or_, select
from together import Together

from .chat_messages.model_chat_interaction import ChatInteraction

AI_MODEL: str | None = None
OTEL_HEADERS: str | None = None
OTEL_ENDPOINT: str | None = None


def get_ai_client() -> OpenAI | Together:
    ai_provider = os.environ.get("AI_PROVIDER")
    match ai_provider:
        case "openai":
            return OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY"),
            )

        case "together":
            return Together(
                api_key=os.environ.get("TOGETHER_API_KEY"),
            )

        case _:
            raise ValueError("Invalid AI provider")


def get_ai_model() -> None:
    global AI_MODEL
    ai_model = os.environ.get("AI_PROVIDER")
    match ai_model:
        case "openai":
            AI_MODEL = "gpt-3.5-turbo"

        case "together":
            AI_MODEL = "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo"

        case _:
            raise ValueError("Invalid AI provider. Please set AI_PROVIDER environment variable")


def get_otel_headers() -> None:
    global OTEL_HEADERS
    global OTEL_ENDPOINT
    otel_provider = os.environ.get("OTEL_PROVIDER")
    match otel_provider:
        case "arize":
            OTEL_HEADERS = f"space_id={os.environ.get('ARIZE_SPACE_ID')},api_key={os.environ.get('ARIZE_API_KEY')}"
            OTEL_ENDPOINT = "https://otlp.arize.com/v1"

        case _:
            raise ValueError(
                "Invalid OTEL provider. Please set OTEL_PROVIDER environment variable",
            )


get_ai_model()
get_otel_headers()
trace_attributes = {
    "app_id": "chat_app",
    "app_version": "v3",
    "model_id": AI_MODEL,
    "model_version": "v3",  # You can filter your spans by model version in Arize
}

# Set the tracer provider
os.environ["OTEL_EXPORTER_OTLP_TRACES_HEADERS"] = OTEL_HEADERS
tracer_provider = trace_sdk.TracerProvider(
    resource=Resource(
        attributes=trace_attributes,
    ),
)
tracer_provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=OTEL_ENDPOINT,
        ),
    ),
)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace_api.set_tracer_provider(
    tracer_provider=tracer_provider,
)

# To get your tracer
tracer = trace_api.get_tracer(__name__)


MAX_QUESTIONS = 10
INPUT_BOX_ID = "input-box"


class ChatState(rx.State):
    """The app state."""

    filter: str = ""

    _ai_client_instance: OpenAI | Together | None = None
    _ai_chat_instance = None

    has_checked_database: bool = False
    chat_history: list[ChatInteraction] = [
        ChatInteraction(
            prompt="What is the meaning of life?",
            answer="The meaning of life is a deep philosophical question that has been debated for centuries. It is a question that is often asked by people who are not philosophers.",
            chat_participant_user_name="Mauro Sicard",
            chat_participant_user_avatar_url="/avatar-default.png",
        ),
    ]
    has_token: bool = True
    username: str = "Mauro Sicard"
    prompt: str = ""
    result: str = ""
    ai_loading: bool = False
    timestamp: datetime.datetime = datetime.datetime.now(
        tz=pytz.timezone(
            "US/Pacific",
        ),
    )

    @rx.var
    def timestamp_formatted(
        self,
    ) -> str:
        return self.timestamp.strftime("%I:%M %p")

    @tracer.start_as_current_span("get_client_instance")
    def _get_client_instance(
        self,
    ) -> OpenAI | Together:
        if self._ai_client_instance is not None:
            return self._ai_client_instance

        return get_ai_client()

    @tracer.start_as_current_span("fetch_messages")
    def _fetch_messages(
        self,
    ) -> list[ChatInteraction]:
        if not self.has_checked_database:
            with rx.session() as session:
                self.has_checked_database = True
                query = select(ChatInteraction)
                if self.filter:
                    query = query.where(
                        or_(
                            ChatInteraction.prompt.ilike(f"%{self.filter}%"),
                            ChatInteraction.answer.ilike(f"%{self.filter}%"),
                        ),
                    )

                return (
                    session.exec(
                        query.distinct(ChatInteraction.prompt)
                        .order_by(ChatInteraction.timestamp.desc())
                        .limit(MAX_QUESTIONS),
                    )
                    .scalars()
                    .all()
                )

        return []

    @rx.var
    def messages(
        self,
    ) -> list[ChatInteraction]:
        """Get the users saved questions and answers from the database."""
        if self.has_checked_database:
            return self.chat_history

        results: list[ChatInteraction] = self._fetch_messages()
        if results:
            self.chat_history = results

        return self.chat_history

    def set_prompt(
        self,
        prompt: str,
    ) -> None:
        self.prompt = prompt

    def create_new_chat(
        self,
    ) -> None:
        pass

    @tracer.start_as_current_span("save_resulting_chat_interaction")
    def _save_resulting_chat_interaction(
        self,
        chat_interaction: ChatInteraction,
    ) -> None:
        with rx.session() as session:
            session.add(
                chat_interaction,
            )
            session.commit()
            session.refresh(chat_interaction)

    @tracer.start_as_current_span("check_saved_chat_interactions")
    async def _check_saved_chat_interactions(
        self,
        username: str,
        prompt: str,
    ) -> None:
        with rx.session() as session:
            if (
                session.exec(
                    select(ChatInteraction)
                    .where(
                        ChatInteraction.chat_participant_user_name == username,
                    )
                    .where(
                        ChatInteraction.prompt == prompt,
                    ),
                ).first()
                or len(
                    session.exec(
                        select(ChatInteraction)
                        .where(
                            ChatInteraction.chat_participant_user_name == username,
                        )
                        .where(
                            ChatInteraction.timestamp
                            > datetime.datetime.now()
                            - datetime.timedelta(
                                days=1,
                            ),
                        ),
                    ).all(),
                )
                > MAX_QUESTIONS
            ):
                raise ValueError(
                    "You have already asked this question or have asked too many questions in the past 24 hours.",
                )

    @rx.background
    async def submit_prompt(
        self,
    ):
        @tracer.start_as_current_span("fetch_chat_completion_session")
        async def _fetch_chat_completion_session(
            prompt: str,
        ):
            def _create_messages_for_chat_completion():
                messages = [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are a helpful assistant. Respond in markdown.",
                            },
                        ],
                    },
                ]
                for chat_interaction in self.chat_history:
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": chat_interaction.prompt,
                                },
                            ],
                        },
                    )
                    messages.append(
                        {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": chat_interaction.answer,
                                },
                            ],
                        },
                    )

                messages.append(
                    {
                        "role": "user",
                        "content": prompt,
                    },
                )
                return messages

            messages = _create_messages_for_chat_completion()
            ai_client_instance = self._get_client_instance()
            stream = ai_client_instance.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.7,
                top_k=50,
                repetition_penalty=1,
                stop=["<|eot_id|>", "<|eom_id|>"],
                truncate=130560,
                stream=True,
            )
            if stream is None:
                raise Exception("Session is None")

            return stream

        @tracer.start_as_current_span("set_ui_loading_state")
        def set_ui_loading_state() -> None:
            self.ai_loading = True

        @tracer.start_as_current_span("clear_ui_loading_state")
        def clear_ui_loading_state() -> None:
            self.result = ""
            self.ai_loading = False

        @tracer.start_as_current_span("add_new_chat_interaction")
        def add_new_chat_interaction() -> None:
            self.chat_history.append(
                ChatInteraction(
                    prompt=prompt,
                    answer="",
                    chat_participant_user_name=self.username,
                ),
            )
            self.prompt = ""

        # Get the question from the form
        if self.prompt == "":
            return

        prompt = self.prompt
        if self.username == "":
            raise ValueError("Username is required")

        await self._check_saved_chat_interactions(
            prompt=prompt,
            username=self.username,
        )
        async with self:
            set_ui_loading_state()

            yield

            stream = await _fetch_chat_completion_session(prompt)
            clear_ui_loading_state()
            add_new_chat_interaction()
            yield

            try:
                for item in stream:
                    if item.choices and item.choices[0] and item.choices[0].delta:
                        answer_text = item.choices[0].delta.content
                        # Ensure answer_text is not None before concatenation
                        if answer_text is not None:
                            self.chat_history[-1].answer += answer_text

                        else:
                            answer_text = ""
                            self.chat_history[-1].answer += answer_text

                        yield rx.scroll_to(
                            elem_id=INPUT_BOX_ID,
                        )

            except StopAsyncIteration:
                raise

            self.result = self.chat_history[-1].answer

        self._save_resulting_chat_interaction(
            chat_interaction=self.chat_history[-1],
        )
