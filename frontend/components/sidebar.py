"""
Lean, clean sidebar — brand, domain filter, your files, controls only.
"""
import streamlit as st
import requests
from frontend.config import config
from frontend.utils.state import (
    clear_messages, get_uploaded_files, get_session_id, reset_session,
)


def _api_ok() -> bool:
    return bool(st.session_state.get("api_healthy"))


def _domain_pill(label: str, icon: str, value: str, current: str):
    active = "active" if current == value else ""
    if st.button(
        f"{icon}  {label}",
        key=f"dom_{value}",
        use_container_width=True,
    ):
        st.session_state.current_domain = value
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.title("⚖️ LegalFinance AI")
        st.write("Sidebar verification...")
        st.button("✦ New Chat", use_container_width=True)
        st.divider()
        st.checkbox("Show sources", value=True)
        st.checkbox("Show metadata", value=False)


def _clear_files():
    sid = get_session_id()
    try:
        requests.delete(
            f"{config.API_BASE_URL}/api/v1/user/documents/{sid}", timeout=5
        )
    except Exception:
        pass
    st.session_state.uploaded_files = []
    st.session_state.last_uploaded_name = None
    st.rerun()
