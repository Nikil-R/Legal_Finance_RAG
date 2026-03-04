"""
Lean, clean sidebar — brand, domain filter, your files, controls only.
"""

import requests
import streamlit as st

from frontend.config import config
from frontend.utils.state import (
    get_session_id,
    get_uploaded_files,
    reset_session,
)


def _api_ok() -> bool:
    return bool(st.session_state.get("api_healthy"))


def _domain_pill(label: str, icon: str, value: str, current: str):
    is_active = value == current
    # Use a leading dot or emoji to show active state
    display_label = f"● {icon}  {label}" if is_active else f"　 {icon}  {label}"

    if st.button(
        display_label,
        key=f"dom_{value}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.current_domain = value
        st.rerun()


def render_sidebar():
    with st.sidebar:
        st.title("⚖️ LegalFinance AI")
        if st.button("✦ New Conversation", use_container_width=True, key="new_chat_sb"):
            reset_session()
            st.rerun()

        st.divider()

        # ── Domain Filter ───────────────────────────────────────────
        st.subheader("Domain")
        current = st.session_state.get("current_domain", "all")
        domains = [
            ("All Domains", "🔍", "all"),
            ("Tax Laws", "💰", "tax"),
            ("Finance", "🏦", "finance"),
            ("Legal", "📜", "legal"),
        ]
        for label, icon, val in domains:
            _domain_pill(label, icon, val, current)

        # ── Uploaded Files ──────────────────────────────────────────
        uploads = get_uploaded_files()
        if uploads:
            st.divider()
            st.subheader("Your Files")
            for f in uploads:
                st.info(f"📎 {f.filename} ({f.chunks} chunks)")

            if st.button("🗑  Remove files", use_container_width=True, key="rm_files"):
                _clear_files()

        st.divider()

        # ── Controls ────────────────────────────────────────────────
        st.subheader("Display")
        st.session_state.show_sources = st.toggle(
            "Show sources", value=st.session_state.get("show_sources", True)
        )
        st.session_state.show_metadata = st.toggle(
            "Show metadata", value=st.session_state.get("show_metadata", False)
        )

        st.divider()

        # ── API status ──────────────────────────────────────────────
        ok = _api_ok()
        status_txt = "API connected" if ok else "API offline"
        st.caption(status_txt)

        sid = get_session_id()
        st.caption(f"Session: {sid[:8]}…")


def _clear_files():
    sid = get_session_id()
    try:
        requests.delete(f"{config.API_BASE_URL}/api/v1/user/documents/{sid}", timeout=5)
    except Exception:
        pass
    st.session_state.uploaded_files = []
    st.session_state.last_uploaded_name = None
    st.rerun()
