"""
Chat interface — modern AI assistant style.
"""
import streamlit as st
import requests
from datetime import datetime

from frontend.config import config
from frontend.utils.api_client import api_client
from frontend.utils.state import (
    add_message, add_uploaded_file, get_domain, get_messages,
    get_session_id, get_uploaded_files,
)
from frontend.components.sources import render_sources


# ── Welcome Screen ────────────────────────────────────────────────────────────

_EXAMPLES = [
    "What are deductions under Section 80C?",
    "Explain KYC requirements per RBI guidelines",
    "What constitutes free consent in Contract Act?",
    "GST rate on e-commerce transactions?",
]

def render_welcome():
    st.markdown(
        """<div class="lf-welcome">
          <div class="lf-welcome-icon">⚖️</div>
          <h2>LegalFinance AI</h2>
          <p>Ask anything about Indian tax laws, financial regulations, or legal provisions.
          Upload your personal documents to get answers grounded in both official rules and your files.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="text-align:center;margin-bottom:0.5rem;font-size:0.78rem;color:#6b7280;">Try asking:</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, ex in enumerate(_EXAMPLES):
        with cols[i % 2]:
            if st.button(f"💬 {ex}", key=f"ex_{i}", use_container_width=True):
                _process_query(ex)
                st.rerun()


# ── Message Rendering ─────────────────────────────────────────────────────────

def _ts(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def render_chat_history():
    messages = get_messages()
    if not messages:
        render_welcome()
        return

    for idx, msg in enumerate(messages):
        if msg.role == "user":
            _render_user_bubble(msg)
        else:
            _render_assistant_bubble(msg, idx)


def _render_user_bubble(msg):
    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="lf-bubble user">{msg.content}</div>'
            f'<div class="lf-timestamp">{_ts(msg.timestamp)}'
            + (f' · {msg.domain.upper()}' if msg.domain != "all" else '')
            + '</div>',
            unsafe_allow_html=True,
        )


def _render_assistant_bubble(msg, idx: int):
    css_class = "error" if msg.is_error else "assistant"
    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown(
            f'<div class="lf-bubble {css_class}">{msg.content}</div>'
            f'<div class="lf-timestamp">{_ts(msg.timestamp)}</div>',
            unsafe_allow_html=True,
        )
        if not msg.is_error and msg.sources and st.session_state.get("show_sources", True):
            render_sources(msg.sources, key_prefix=f"hist_{idx}")
        if not msg.is_error and msg.metadata and st.session_state.get("show_metadata", False):
            _render_metadata(msg.metadata, idx)


def _render_metadata(meta: dict, idx: int):
    with st.expander("📊 Query Metadata", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Retrieval", f"{meta.get('retrieval_time_ms', 0):.0f} ms")
        c1.metric("Candidates", meta.get("retrieval_candidates", 0))
        c2.metric("Generation", f"{meta.get('generation_time_ms', 0):.0f} ms")
        c2.metric("Chunks Used", meta.get("reranked_chunks", 0))
        c3.metric("Total", f"{meta.get('total_time_ms', 0):.0f} ms")
        tok = meta.get("token_usage", {})
        c3.metric("Tokens", tok.get("total_tokens", 0))
        st.caption(f"Model: {meta.get('model','N/A')} · Prompt: {meta.get('prompt_version','v1')}")


# ── File Upload Bar ───────────────────────────────────────────────────────────

def render_file_upload():
    """Show uploaded file badges; handle new uploads."""
    uploads = get_uploaded_files()

    if uploads:
        badges = "".join(
            f'<span class="lf-file-badge">📎 {f.filename}</span>'
            for f in uploads
        )
        st.markdown(
            f'<div class="lf-files-bar"><span style="color:#6b7280">Uploaded:</span>{badges}</div>',
            unsafe_allow_html=True,
        )


# ── Chat Input Row ────────────────────────────────────────────────────────────

def render_chat_input():
    """Upload column + chat input."""
    col_upload, col_chat = st.columns([1, 6])

    with col_upload:
        uploaded = st.file_uploader(
            "📎",
            type=["pdf", "txt", "docx"],
            label_visibility="collapsed",
            key="chat_uploader",
        )
        if uploaded and uploaded.name != st.session_state.get("last_uploaded_name"):
            _handle_upload(uploaded)

    with col_chat:
        if prompt := st.chat_input(
            "Ask about Indian tax, finance, or legal matters…",
            key="main_chat_input",
        ):
            _process_query(prompt)
            st.rerun()


def _handle_upload(file):
    """POST uploaded file to API, update state."""
    session_id = get_session_id()
    with st.spinner(f"Uploading {file.name}…"):
        try:
            resp = requests.post(
                f"{config.API_BASE_URL}/api/v1/user/upload",
                params={"session_id": session_id},
                files={"file": (file.name, file.getvalue())},
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                add_uploaded_file(file.name, data.get("chunks_created", 0))
                st.session_state.last_uploaded_name = file.name
                # Add confirmation message to chat
                add_message(
                    "assistant",
                    f"📄 **{file.name}** uploaded successfully — "
                    f"{data.get('chunks_created', 0)} chunks indexed. "
                    "You can now ask questions about this document.",
                )
                st.rerun()
            else:
                err = resp.json().get("detail", "Upload failed")
                st.error(f"Upload failed: {err}")
        except Exception as exc:
            st.error(f"Could not connect to API: {exc}")


# ── Query Processing ──────────────────────────────────────────────────────────

def _process_query(question: str):
    """Record user message, call API, record assistant reply."""
    domain = get_domain()
    session_id = get_session_id()

    add_message("user", question, domain=domain)

    # Re-render user bubble immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="lf-bubble user">{question}</div>',
            unsafe_allow_html=True,
        )

    # Typing indicator + API call
    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="lf-bubble assistant">'
            '<div class="typing-indicator">'
            '<span></span><span></span><span></span>'
            "</div></div>",
            unsafe_allow_html=True,
        )

        result = api_client.query(
            question=question,
            domain=domain,
            include_sources=True,
            session_id=session_id,
        )

        placeholder.empty()

        if result.success:
            st.markdown(
                f'<div class="lf-bubble assistant">{result.answer}</div>',
                unsafe_allow_html=True,
            )
            add_message(
                "assistant", result.answer,
                sources=result.sources,
                metadata=result.metadata,
                domain=domain,
            )
            if result.sources and st.session_state.get("show_sources", True):
                render_sources(result.sources, key_prefix="live")
            if result.metadata and st.session_state.get("show_metadata", False):
                _render_metadata(result.metadata, -1)
        else:
            err_text = f"❌ **Error:** {result.error}"
            st.markdown(
                f'<div class="lf-bubble error">{err_text}</div>',
                unsafe_allow_html=True,
            )
            add_message("assistant", err_text, domain=domain, is_error=True)
