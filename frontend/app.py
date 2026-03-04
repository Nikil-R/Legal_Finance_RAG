"""
LegalFinance AI — app entry point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from frontend.components import (
    render_chat_history,
    render_chat_input,
    render_file_upload,
    render_navbar,
    render_sidebar,
)
from frontend.utils.state import init_session_state


def _css():
    p = Path(__file__).parent / "styles" / "modern.css"
    if p.exists():
        st.markdown(
            f"<style>{p.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True
        )


def main():
    st.set_page_config(
        page_title="LegalFinance AI",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _css()
    init_session_state()

    render_sidebar()  # left panel
    render_navbar()  # sticky top bar
    render_file_upload()  # badge bar (only when files exist)
    render_chat_history()  # main content
    render_chat_input()  # input row at bottom


if __name__ == "__main__":
    main()
