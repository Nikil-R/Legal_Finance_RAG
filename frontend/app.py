"""
LegalFinance RAG - Streamlit Frontend Application

Run with: streamlit run frontend/app.py
"""
import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path so 'frontend' package can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
from frontend.components import (
    render_header,
    render_domain_tabs,
    render_chat_history,
    render_chat_input,
    render_sidebar,
    render_upload_section
)
from frontend.utils.state import init_session_state
from frontend.config import config


def load_css():
    """Load custom CSS styles."""
    css_file = Path(__file__).parent / "styles" / "custom.css"
    
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    render_upload_section()
    
    # Main content area
    main_container = st.container()
    
    with main_container:
        # Header
        render_header()
        
        # Domain tabs
        render_domain_tabs()
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Chat history
            render_chat_history()
        
        # Chat input (always at bottom)
        render_chat_input()


if __name__ == "__main__":
    main()
