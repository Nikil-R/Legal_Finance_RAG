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
                --primary: #6366f1;
                --accent: #8b5cf6;
                --radius-xl: 20px;
                --radius-lg: 12px;
            }
            .lf-navbar { background: rgba(248, 250, 252, 0.8) !important; }
            .lf-bubble-ai { background: #ffffff !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .lf-hero-title { background: linear-gradient(135deg, #0f172a 0%, #475569 100%); -webkit-background-clip: text; }
            .lf-fbadge { background: rgba(0, 0, 0, 0.05); }
            [data-testid="stSidebar"] { background-color: #ffffff !important; }
            .stButton button { color: #0f172a !important; }
            </style>
            """
        else:
            # Default to Dark Mode
            theme_vars = """
            <style>
            :root {
                --bg-deep: #080c14;
                --bg-dark: #0d1117;
                --bg-elevated: #161b22;
                --primary: #6366f1;
                --primary-glow: rgba(99, 102, 241, 0.4);
                --accent: #8b5cf6;
                --text-main: #e2e8f0;
                --text-muted: #94a3b8;
                --text-dim: #475569;
                --border: rgba(255, 255, 255, 0.1);
                --radius-xl: 20px;
                --radius-lg: 12px;
            }
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
    init_session_state()
    _css()

    render_sidebar()  # left panel
    render_navbar()  # sticky top bar
    render_file_upload()  # badge bar (only when files exist)
    render_chat_history()  # main content
    render_chat_input()  # input row at bottom


if __name__ == "__main__":
    main()
