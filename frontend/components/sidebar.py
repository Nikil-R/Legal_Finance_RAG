"""
Professional Sidebar — Executive Dashboard Panel
Clean, organized navigation with premium styling.
"""

import requests
import streamlit as st

from frontend.config import config
from frontend.utils.state import (
    get_session_id,
    get_uploaded_files,
    reset_session,
)


def _api_ok() -> bool:
    return bool(st.session_state.get("api_healthy"))


def _render_section_header(icon: str, title: str):
    """Renders a clean section header."""
    st.markdown(
        f"""<div style="display: flex; align-items: center; gap: 8px; margin: 1.5rem 0 0.75rem;">
            <span style="font-size: 0.9rem; opacity: 0.7;">{icon}</span>
            <span style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
                        letter-spacing: 0.08em; color: var(--text-dim);">{title}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def _domain_button(label: str, icon: str, value: str, current: str, count: int = 0):
    """Renders a professional domain selector button."""
    is_active = value == current
    if st.button(
        f"{icon} {label}",
        key=f"dom_{value}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        st.session_state.current_domain = value
        st.rerun()


def _file_card(filename: str, chunks: int):
    """Renders a professional file card."""
    st.markdown(
        f"""<div style="background: linear-gradient(135deg, rgba(13, 148, 136, 0.05), transparent);
                    border: 1px solid rgba(13, 148, 136, 0.15); border-radius: 8px;
                    padding: 0.75rem 1rem; margin: 0.5rem 0; display: flex;
                    align-items: center; gap: 10px; transition: all 0.2s ease; cursor: pointer;">
            <span style="font-size: 1.1rem;">📎</span>
            <div style="flex-grow: 1; overflow: hidden;">
                <div style="font-weight: 500; font-size: 0.9rem; color: var(--text-main);
                            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{filename}</div>
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px;">{chunks} chunks indexed</div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        # ── Brand Header ──────────────────────────────────────────────
        st.markdown(
            """<div style="padding: 0.5rem 0 1rem; border-bottom: 1px solid var(--border); margin-bottom: 1rem;">
                <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.4rem; font-weight: 600;
                            background: linear-gradient(135deg, var(--primary) 0%, #e8c96a 100%);
                            -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
                            letter-spacing: 0.02em;">
                    ⚖️ LegalFinance AI
                </div>
                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px; letter-spacing: 0.02em;">
                    Enterprise Research Assistant
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # New Chat Button
        if st.button(
            "✦ New Conversation",
            use_container_width=True,
            key="new_chat_sb",
            type="primary",
        ):
            reset_session()
            st.rerun()

        # ── Research Domain ─────────────────────────────────────────
        _render_section_header("🎯", "Research Domain")
        current = st.session_state.get("current_domain", "all")
        domains = [
            ("All Domains", "🔍", "all"),
            ("Tax Laws", "💰", "tax"),
            ("Finance", "🏦", "finance"),
            ("Legal", "📜", "legal"),
        ]
        for label, icon, val in domains:
            _domain_button(label, icon, val, current)

        # ── Knowledge Base ───────────────────────────────────────────
        uploads = get_uploaded_files()
        if uploads:
            _render_section_header("📚", "Knowledge Base")
            st.markdown(
                f"""<div style="background: linear-gradient(135deg, rgba(212, 175, 55, 0.05), transparent);
                            border: 1px solid rgba(212, 175, 55, 0.1); border-radius: 8px;
                            padding: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
                        <span style="font-size: 0.85rem;">📁</span>
                        <span style="font-size: 0.8rem; font-weight: 500; color: var(--text-muted);">
                            {len(uploads)} document{'s' if len(uploads) > 1 else ''}
                        </span>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            for f in uploads[:3]:  # Show max 3 files
                _file_card(f.filename, f.chunks)

            if len(uploads) > 3:
                st.caption(f"+ {len(uploads) - 3} more files")

            if st.button(
                "🗑  Clear Documents",
                use_container_width=True,
                key="rm_files",
                type="secondary",
            ):
                _clear_files()

        # ── Display Settings ────────────────────────────────────────
        _render_section_header("👁️", "Display")

        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown('<div style="padding-top: 2px;">Sources</div>', unsafe_allow_html=True)
        with col2:
            st.session_state.show_sources = st.toggle(
                "Show Sources",
                value=st.session_state.get("show_sources", True),
                key="toggle_sources",
                label_visibility="collapsed",
            )

        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown('<div style="padding-top: 2px;">Metadata</div>', unsafe_allow_html=True)
        with col2:
            st.session_state.show_metadata = st.toggle(
                "Show Metadata",
                value=st.session_state.get("show_metadata", False),
                key="toggle_metadata",
                label_visibility="collapsed",
            )

        # ── System Status ───────────────────────────────────────────
        _render_section_header("🔌", "System")
        status = st.session_state.get("api_status", "offline")
        
        # Status configurations
        status_configs = {
            "healthy": {
                "color": "#10b981",
                "bg": "rgba(16, 185, 129, 0.1)",
                "border": "rgba(16, 185, 129, 0.2)",
                "text": "System Healthy",
                "dot": "🟢"
            },
            "degraded": {
                "color": "#f59e0b",
                "bg": "rgba(245, 158, 11, 0.1)",
                "border": "rgba(245, 158, 11, 0.2)",
                "text": "System Degraded",
                "dot": "🟡"
            },
            "offline": {
                "color": "#f87171",
                "bg": "rgba(248, 113, 113, 0.1)",
                "border": "rgba(248, 113, 113, 0.2)",
                "text": "System Down",
                "dot": "🔴"
            },
            "unhealthy": {
                "color": "#f87171",
                "bg": "rgba(248, 113, 113, 0.1)",
                "border": "rgba(248, 113, 113, 0.2)",
                "text": "System Down",
                "dot": "🔴"
            }
        }
        
        cfg = status_configs.get(status, status_configs["offline"])
        api_error = st.session_state.get("api_error", "")

        # Build the HTML string cleanly to avoid f-string/HTML nesting issues
        api_latency = st.session_state.get('api_latency', 0)
        
        status_html_parts = [
            f'<div style="background: {cfg["bg"]}; border: 1px solid {cfg["border"]};',
            '            border-radius: 8px; padding: 0.75rem 1rem; margin: 0.5rem 0;">',
            '    <div style="display: flex; align-items: center; gap: 8px;">',
            f'        <span>{cfg["dot"]}</span>',
            f'        <span style="font-weight: 500; color: {cfg["color"]}; font-size: 0.9rem;">{cfg["text"]}</span>',
            '    </div>',
            '    <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px; margin-left: 24px;">',
            f'        API v1.0 &bull; Latency: {api_latency}ms',
            '    </div>',
        ]
        
        if status not in ["healthy", "degraded"] and api_error:
            status_html_parts.append(
                f'    <div style="font-size: 0.65rem; color: #f87171; margin-top: 4px; margin-left: 24px;">{api_error}</div>'
            )
        
        status_html_parts.append('</div>')
        
        st.markdown("\n".join(status_html_parts), unsafe_allow_html=True)

        sid = get_session_id()
        st.markdown(
            f"""<div style="font-size: 0.7rem; color: var(--text-dim); text-align: center;
                        margin-top: 0.5rem; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace;">
                Session: {sid[:8]}…
            </div>""",
            unsafe_allow_html=True,
        )

        # ── User Profile ──────────────────────────────────────────────
        st.markdown("""<div style="margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1rem;"></div>""", unsafe_allow_html=True)

        st.markdown(
            """<div style="background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(13, 148, 136, 0.03));
                        border: 1px solid rgba(212, 175, 55, 0.15); border-radius: 12px;
                        padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 44px; height: 44px; border-radius: 50%;
                                background: linear-gradient(135deg, var(--primary), var(--accent));
                                display: flex; align-items: center; justify-content: center;
                                color: var(--bg-deep); font-weight: 700; font-size: 1.1rem;
                                box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);">
                        N
                    </div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight: 600; font-size: 0.95rem; color: var(--text-main);">Nikil</div>
                        <div style="display: flex; align-items: center; gap: 4px; margin-top: 2px;">
                            <span style="font-size: 0.7rem;">👑</span>
                            <span style="font-size: 0.75rem; color: var(--primary); font-weight: 500;">Pro Member</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; margin-top: 12px;">
                    <button onclick="alert('Settings coming soon')"
                            style="flex: 1; padding: 8px; background: rgba(255,255,255,0.05); border: 1px solid var(--border);
                                   border-radius: 6px; color: var(--text-muted); font-size: 0.8rem; cursor: pointer;">
                        ⚙️ Settings
                    </button>
                    <button onclick="window.location.reload()"
                            style="flex: 1; padding: 8px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2);
                                   border-radius: 6px; color: #f87171; font-size: 0.8rem; cursor: pointer;">
                        🚪 Exit
                    </button>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Version
        st.markdown(
            """<div style="text-align: center; padding-top: 0.5rem;">
                <span style="font-size: 0.7rem; color: var(--text-dim); letter-spacing: 0.05em;">
                    v2.0.1 Enterprise
                </span>
            </div>""",
            unsafe_allow_html=True,
        )


def _clear_files():
    sid = get_session_id()
    try:
        requests.delete(f"{config.API_BASE_URL}/api/v1/user/documents/{sid}", timeout=5)
    except Exception:
        pass
    st.session_state.uploaded_files = []
    st.session_state.last_uploaded_name = None
    st.rerun()
