"""Reflex custom component Monaco."""

# For wrapping react guide, visit https://reflex.dev/docs/wrapping-react/overview/
# Taken and modified from https://github.com/Lendemor/reflex-monaco

import reflex as rx

from enum import Enum
from typing import Any, Optional

class MessageRole(str, Enum):
    """The role of a chat message."""
    SYSTEM = "system" 
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    DATA = "data"
    TOOL = "tool"

class Message(rx.Base):
    """A chat message."""
    content: str
    role: MessageRole = MessageRole.USER
    annotations: Optional[Any] = None


class BaseChatComponent(rx.Component):
    """Base Monaco component."""

    library = "@llamaindex/chat-ui@0.0.6"


class ChatMessage(BaseChatComponent):
    # The name of the component to use from the package.
    tag = "ChatMessage"

    is_default = False

    message: rx.Var[Message]
    class_name: Optional[rx.Var[str]] = None
   


chat_message = ChatMessage.create
