"""
Collapsible sidebar — system stats, doc stats, chat controls.
"""
import streamlit as st
import requests
from frontend.config import config
from frontend.utils.state import (
    clear_messages, get_uploaded_files, reset_session,
)


def _get_stats():
    if st.session_state.get("stats"):
        return st.session_state.stats
    try:
        r = requests.get(f"{config.API_BASE_URL}/api/v1/documents/stats", timeout=5)
        if r.status_code == 200:
            st.session_state.stats = r.json()
            return st.session_state.stats
    except Exception:
        pass
    return None


def render_sidebar():
    with st.sidebar:
        st.markdown("---")

        # ── SYSTEM STATUS ──────────────────────────────────────────────
        st.markdown(
            '<div class="lf-sidebar-section-title">System Status</div>',
            unsafe_allow_html=True,
        )
        healthy = st.session_state.get("api_healthy")

        def _dot(ok): return "🟢" if ok else "🔴"

        st.markdown(
            f"""<div class="lf-indicator">{_dot(healthy)} FastAPI Backend</div>
            <div class="lf-indicator">{_dot(healthy)} Vector Database</div>
            <div class="lf-indicator">{_dot(healthy)} LLM Connected</div>""",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── DOCUMENT STATS ─────────────────────────────────────────────
        st.markdown(
            '<div class="lf-sidebar-section-title">Document Stats</div>',
            unsafe_allow_html=True,
        )
        stats = _get_stats()
        if stats:
            col1, col2 = st.columns(2)
            col1.metric("Chunks", stats.get("total_chunks", "—"))
            domains = stats.get("domains", {})
            col2.metric("Domains", len(domains))
            for dom, cnt in domains.items():
                icon = {"tax": "💰", "finance": "🏦", "legal": "📜"}.get(dom, "📄")
                st.markdown(
                    f'<div class="lf-stat-row">{icon} {dom.title()} <strong>{cnt}</strong></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Stats unavailable — ingest documents first.")

        if st.button("🔄 Refresh Stats", use_container_width=True, key="refresh_stats"):
            st.session_state.stats = None
            st.rerun()

        st.markdown("---")

        # ── UPLOADED FILES ────────────────────────────────────────────
        uploads = get_uploaded_files()
        if uploads:
            st.markdown(
                '<div class="lf-sidebar-section-title">Your Files</div>',
                unsafe_allow_html=True,
            )
            for f in uploads:
                st.markdown(
                    f'<div class="lf-stat-row">📄 {f.filename} <strong>{f.chunks}ck</strong></div>',
                    unsafe_allow_html=True,
                )
            if st.button("🗑️ Clear Files", use_container_width=True, key="clear_files_sidebar"):
                _clear_user_files()
            st.markdown("---")

        # ── CHAT CONTROLS ─────────────────────────────────────────────
        st.markdown(
            '<div class="lf-sidebar-section-title">Chat Controls</div>',
            unsafe_allow_html=True,
        )
        st.session_state.show_sources = st.toggle(
            "Show sources", value=st.session_state.get("show_sources", True), key="toggle_sources"
        )
        st.session_state.show_metadata = st.toggle(
            "Show metadata", value=st.session_state.get("show_metadata", False), key="toggle_meta"
        )

        st.markdown("---")
        if st.button("🆕 New Conversation", use_container_width=True, key="new_chat"):
            reset_session()
            st.rerun()

        if st.button("🗑️ Clear Chat Only", use_container_width=True, key="clear_chat"):
            clear_messages()
            st.rerun()

        # ── SESSION INFO ──────────────────────────────────────────────
        st.markdown("---")
        sid = st.session_state.get("session_id", "")
        st.caption(f"Session: `{sid[:8]}…`")


def _clear_user_files():
    """Delete user collection from ChromaDB and reset local state."""
    sid = st.session_state.get("session_id", "")
    try:
        requests.delete(
            f"{config.API_BASE_URL}/api/v1/user/documents/{sid}", timeout=5
        )
    except Exception:
        pass
    st.session_state.uploaded_files = []
    st.session_state.last_uploaded_name = None
    st.rerun()
