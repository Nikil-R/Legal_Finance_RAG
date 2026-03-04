"""
Session state management — extended for multi-source RAG.
"""
import uuid
import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime
from frontend.config import config


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str           # "user" | "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    domain: str = "all"
    is_error: bool = False


@dataclass
class UploadedFile:
    """Tracks a user-uploaded file within this session."""
    filename: str
    chunks: int
    timestamp: datetime = field(default_factory=datetime.now)


def init_session_state():
    """Initialise all session state variables with safe defaults."""
    defaults = {
        "messages": [],
        "current_domain": "all",
        "api_healthy": None,
        "stats": None,
        "show_sources": config.SHOW_SOURCES,
        "show_metadata": config.SHOW_METADATA,
        # Multi-source RAG
        "session_id": str(uuid.uuid4()),
        "uploaded_files": [],          # list[UploadedFile]
        "last_uploaded_name": None,    # dedupe guard
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Messages ──────────────────────────────────────────────────────────────────

def add_message(role: str, content: str, *, sources=None,
                metadata=None, domain="all", is_error=False):
    msg = ChatMessage(
        role=role, content=content,
        sources=sources or [], metadata=metadata or {},
        domain=domain, is_error=is_error,
    )
    st.session_state.messages.append(msg)
    if len(st.session_state.messages) > config.MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-config.MAX_HISTORY:]


def get_messages() -> list[ChatMessage]:
    return st.session_state.messages


def clear_messages():
    st.session_state.messages = []


# ── Domain ────────────────────────────────────────────────────────────────────

def set_domain(domain: str):
    st.session_state.current_domain = domain


def get_domain() -> str:
    return st.session_state.current_domain


# ── Uploads ───────────────────────────────────────────────────────────────────

def add_uploaded_file(filename: str, chunks: int):
    st.session_state.uploaded_files.append(UploadedFile(filename, chunks))


def get_uploaded_files() -> list[UploadedFile]:
    return st.session_state.uploaded_files


def get_session_id() -> str:
    return st.session_state.session_id


def reset_session():
    """Clear chat + uploads + generate a new session_id."""
    st.session_state.messages = []
    st.session_state.uploaded_files = []
    st.session_state.last_uploaded_name = None
    st.session_state.session_id = str(uuid.uuid4())
