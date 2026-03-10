"""
Professional Navbar — Executive Header Bar
Minimal, clean, and authoritative.
"""

import streamlit as st


def render_navbar():
    """Executive header with minimal, professional design."""
    status = st.session_state.get("api_status", "offline")
    ok = st.session_state.get("api_healthy", False)

    # Status styling
    if status == "healthy":
        status_text = "System Healthy"
        status_color = "#10b981"
        status_bg = "rgba(16, 185, 129, 0.1)"
        status_border = "rgba(16, 185, 129, 0.2)"
        pulse_active = True
    elif status == "degraded":
        status_text = "System Degraded"
        status_color = "#f59e0b"
        status_bg = "rgba(245, 158, 11, 0.1)"
        status_border = "rgba(245, 158, 11, 0.2)"
        pulse_active = True
    else:
        status_text = "System Down"
        status_color = "#f87171"
        status_bg = "rgba(248, 113, 113, 0.1)"
        status_border = "rgba(248, 113, 113, 0.2)"
        pulse_active = False

    st.markdown(
        f"""
        <div class="lf-navbar">
            <!-- Left: Brand -->
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; border-radius: 10px;
                            background: linear-gradient(135deg, #d4af37, #0d9488);
                            display: flex; align-items: center; justify-content: center;
                            font-size: 1.2rem; box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);">
                    ⚖️
                </div>
                <div>
                    <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.1rem; font-weight: 600;
                                color: var(--text-main); letter-spacing: 0.01em;">
                        LegalFinance
                    </div>
                    <div style="font-size: 0.7rem; color: var(--text-dim); letter-spacing: 0.05em; text-transform: uppercase;">
                        AI Research Platform
                    </div>
                </div>
            </div>
            <!-- Right: Status -->
            <div style="display: flex; align-items: center; gap: 1rem;">
                <!-- Status Badge -->
                <div style="display: flex; align-items: center; gap: 8px;
                            background: {status_bg}; border: 1px solid {status_border};
                            border-radius: 100px; padding: 6px 14px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background: {status_color};
                                box-shadow: 0 0 8px {status_color}; {'animation: pulse 2s infinite;' if pulse_active else ''}"></div>
                    <span style="font-size: 0.8rem; font-weight: 500; color: {status_color};">{status_text}</span>
                </div>
                <!-- Help Icon -->
                <div style="width: 32px; height: 32px; border-radius: 8px;
                            background: rgba(255,255,255,0.03); border: 1px solid var(--border);
                            display: flex; align-items: center; justify-content: center;
                            cursor: pointer; transition: all 0.2s ease;">
                    <span style="font-size: 0.9rem; opacity: 0.6;">❓</span>
                </div>
            </div>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }}
            70% {{ opacity: 1; box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
            100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
