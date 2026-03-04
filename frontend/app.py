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
        theme = st.session_state.get("theme", "Dark Mode")
        
        # Theme overrides
        theme_vars = ""
        if theme == "Light Mode":
            theme_vars = """
            <style>
            :root {
                --bg-deep: #f8fafc;
                --bg-dark: #ffffff;
                --bg-elevated: #f1f5f9;
                --text-main: #0f172a;
                --text-muted: #475569;
                --text-dim: #64748b;
                --border: rgba(0, 0, 0, 0.1);
                --primary-glow: rgba(99, 102, 241, 0.15);
            }
            .lf-navbar { background: rgba(248, 250, 252, 0.8) !important; }
            .lf-bubble-ai { background: #ffffff !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .lf-hero-title { background: linear-gradient(135deg, #0f172a 0%, #475569 100%); -webkit-background-clip: text; }
            .lf-fbadge { background: rgba(0, 0, 0, 0.05); }
            [data-testid="stSidebar"] { background-color: #ffffff !important; }
            .stButton button { color: #0f172a !important; }
            </style>
            """
        
        st.markdown(theme_vars, unsafe_allow_html=True)
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
