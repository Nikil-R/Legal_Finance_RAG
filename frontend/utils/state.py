"""
Session state management for Streamlit.
"""
import streamlit as st
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from frontend.config import config


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    domain: str = "all"


def init_session_state():
    """Initialize session state variables."""
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Current domain
    if "current_domain" not in st.session_state:
        st.session_state.current_domain = "all"
    
    # API status
    if "api_healthy" not in st.session_state:
        st.session_state.api_healthy = None
    
    # Stats cache
    if "stats" not in st.session_state:
        st.session_state.stats = None
    
    # Settings
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = config.SHOW_SOURCES
    
    if "show_metadata" not in st.session_state:
        st.session_state.show_metadata = config.SHOW_METADATA


def add_message(role: str, content: str, sources: list = None, metadata: dict = None, domain: str = "all"):
    """Add a message to chat history."""
    message = ChatMessage(
        role=role,
        content=content,
        sources=sources or [],
        metadata=metadata or {},
        domain=domain
    )
    st.session_state.messages.append(message)
    
    # Trim history if too long
    if len(st.session_state.messages) > config.MAX_HISTORY:
        st.session_state.messages = st.session_state.messages[-config.MAX_HISTORY:]


def get_messages() -> list[ChatMessage]:
    """Get all messages in history."""
    return st.session_state.messages


def clear_messages():
    """Clear chat history."""
    st.session_state.messages = []


def set_domain(domain: str):
    """Set current domain."""
    st.session_state.current_domain = domain


def get_domain() -> str:
    """Get current domain."""
    return st.session_state.current_domain
