"""
Top navigation bar component.
"""
import streamlit as st
import requests
from frontend.config import config
from frontend.utils.state import get_domain, set_domain


def _check_api_health() -> bool:
    """Quick non-blocking health probe (cached per rerun)."""
    if st.session_state.get("api_healthy") is not None:
        return st.session_state.api_healthy
    try:
        r = requests.get(f"{config.API_BASE_URL}/health", timeout=3)
        healthy = r.status_code == 200 and r.json().get("status") == "healthy"
    except Exception:
        healthy = False
    st.session_state.api_healthy = healthy
    return healthy


def render_navbar():
    """Render the sticky top navigation bar."""
    healthy = _check_api_health()
    current_domain = get_domain()

    domain_options = {
        "all": "🔍 All Domains",
        "tax": "💰 Tax Laws",
        "finance": "🏦 Finance",
        "legal": "📜 Legal",
    }

    # Build the navbar via columns
    st.markdown('<div class="lf-navbar">', unsafe_allow_html=True)

    left, center, right = st.columns([2, 3, 3])

    with left:
        st.markdown(
            '<div class="lf-brand">⚖️ <span>LegalFinance</span> AI</div>',
            unsafe_allow_html=True,
        )

    with center:
        selected = st.selectbox(
            "domain_nav",
            options=list(domain_options.keys()),
            format_func=lambda k: domain_options[k],
            index=list(domain_options.keys()).index(current_domain),
            label_visibility="collapsed",
            key="nav_domain_select",
        )
        if selected != current_domain:
            set_domain(selected)
            st.rerun()

    with right:
        rc1, rc2 = st.columns([1, 1])
        with rc1:
            status_class = "online" if healthy else "offline"
            status_text = "API Online" if healthy else "API Offline"
            st.markdown(
                f"""<div class="lf-status {status_class}">
                  <span class="lf-status-dot"></span>{status_text}
                </div>""",
                unsafe_allow_html=True,
            )
        with rc2:
            if st.button("🔄 Refresh Status", use_container_width=True, key="refresh_health"):
                st.session_state.api_healthy = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
