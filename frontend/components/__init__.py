from frontend.components.navbar import render_navbar
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import (
    render_chat_history,
    render_chat_input,
    render_file_upload,
)
from frontend.components.sources import render_sources

# Legacy compat shims
def render_header(): pass
def render_domain_tabs(): pass
def render_upload_section(): pass

__all__ = [
    "render_navbar",
    "render_sidebar",
    "render_chat_history",
    "render_chat_input",
    "render_file_upload",
    "render_sources",
    # legacy
    "render_header",
    "render_domain_tabs",
    "render_upload_section",
]
