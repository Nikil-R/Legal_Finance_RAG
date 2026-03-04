"""
LegalFinance AI — Streamlit frontend entry point.
Modern redesign: dark mode, chat-centric, multi-source RAG.

Run with:
    streamlit run frontend/app.py
"""
import sys
import os
from pathlib import Path

# Allow `from frontend.xxx import ...` from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from frontend.config import config
from frontend.utils.state import init_session_state
from frontend.components import (
    render_navbar,
    render_sidebar,
    render_chat_history,
    render_chat_input,
    render_file_upload,
)


def _load_css():
    css_path = Path(__file__).parent / "styles" / "modern.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    # ── Page config (must be first Streamlit call) ─────────────────────────────
    st.set_page_config(
        page_title="LegalFinance AI",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── CSS & state ───────────────────────────────────────────────────────────
    _load_css()
    init_session_state()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    render_sidebar()

    # ── Navbar ────────────────────────────────────────────────────────────────
    render_navbar()

    # ── Uploaded files badge bar ──────────────────────────────────────────────
    render_file_upload()

    # ── Chat area ─────────────────────────────────────────────────────────────
    # Use a container that fills the remaining viewport height with scroll
    chat_area = st.container()
    with chat_area:
        render_chat_history()

    # ── Input row (pinned visually at bottom via CSS) ─────────────────────────
    render_chat_input()


if __name__ == "__main__":
    main()
