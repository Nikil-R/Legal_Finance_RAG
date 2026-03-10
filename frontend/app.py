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
from frontend.utils.api import probe_api


def _css():
    p = Path(__file__).parent / "styles" / "modern.css"
    if p.exists():
        theme = st.session_state.get("theme", "Dark Mode")

        # Theme overrides - Executive Precision Design
        if theme == "Light Mode":
            theme_vars = """
            <style>
            :root {
                --bg-deep: #fafaf9;
                --bg-dark: #ffffff;
                --bg-elevated: #f5f5f4;
                --text-main: #1c1917;
                --text-muted: #57534e;
                --text-dim: #78716c;
                --border: rgba(212, 175, 55, 0.2);
                --primary-glow: rgba(212, 175, 55, 0.15);
                --primary: #b45309;
                --accent: #0d9488;
                --radius-xl: 16px;
                --radius-lg: 12px;
                --radius-md: 8px;
            }
            .lf-navbar {
                background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,249,0.9)) !important;
                border-bottom-color: rgba(212, 175, 55, 0.2) !important;
            }
            .lf-bubble-ai {
                background: #ffffff !important;
                box-shadow: 0 2px 15px rgba(0,0,0,0.05), 0 0 0 1px rgba(212, 175, 55, 0.1);
            }
            .lf-hero-title {
                background: linear-gradient(135deg, #1c1917 0%, #78716c 100%);
                -webkit-background-clip: text;
            }
            .lf-fbadge {
                background: rgba(212, 175, 55, 0.08);
                border-color: rgba(212, 175, 55, 0.2);
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff, #fafaf9) !important;
                border-right-color: rgba(212, 175, 55, 0.15) !important;
            }
            .stButton button { color: #1c1917 !important; }
            ::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, rgba(212, 175, 55, 0.3), rgba(212, 175, 55, 0.2));
            }
            </style>
            """
        else:
            # Executive Dark Mode (Default)
            theme_vars = """
            <style>
            :root {
                --bg-deep: #0a1628;
                --bg-dark: #0f1d2e;
                --bg-elevated: #162236;
                --primary: #d4af37;
                --primary-glow: rgba(212, 175, 55, 0.3);
                --accent: #0d9488;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --text-dim: #64748b;
                --border: rgba(212, 175, 55, 0.15);
                --radius-xl: 16px;
                --radius-lg: 12px;
                --radius-md: 8px;
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
    probe_api()
    _css()

    render_sidebar()  # left panel
    render_navbar()  # sticky top bar
    render_file_upload()  # badge bar (only when files exist)
    render_chat_history()  # main content
    render_chat_input()  # input row at bottom


if __name__ == "__main__":
    main()
