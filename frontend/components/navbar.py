"""
Navbar — glass bar with brand + API status.
"""

import requests
import streamlit as st

from frontend.config import config


def _probe_api() -> bool:
    """Health probe — cached per page run via session_state."""
    if st.session_state.get("api_healthy") is not None:
        return st.session_state.api_healthy
    try:
        r = requests.get(f"{config.API_BASE_URL}/health", timeout=2)
        ok = r.status_code == 200 and r.json().get("status") == "healthy"
    except Exception:
        ok = False
    st.session_state.api_healthy = ok
    return ok


def render_navbar():
    """Slim frosted-glass top bar."""
    ok = _probe_api()
    badge_cls = "on" if ok else "off"
    badge_txt = "API Online" if ok else "API Offline"

    st.markdown(
        f"""<div class="lf-navbar">
          <div class="lf-brand">⚖️ LegalFinance AI</div>
          <div style="display:flex;align-items:center;gap:1.5rem;">
            <div class="lf-api-badge {badge_cls}">
              <span class="lf-api-pulse"></span>{badge_txt}
            </div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )
