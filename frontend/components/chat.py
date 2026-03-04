"""
Chat component — premium AI-assistant style.
"""

from datetime import datetime

import requests
import streamlit as st

from frontend.components.sources import render_sources
from frontend.config import config
from frontend.utils.api_client import api_client
from frontend.utils.state import (
    add_message,
    add_uploaded_file,
    get_domain,
    get_messages,
    get_session_id,
    get_uploaded_files,
)

# ─── Welcome Page ────────────────────────────────────────────────────────────

_EXAMPLES = [
    (
        "💰 TAX",
        "Section 80C deductions",
        "What are all deductions available under Section 80C of the Income Tax Act?",
    ),
    (
        "🏦 RBI",
        "KYC compliance",
        "What are the KYC requirements for banks per RBI Master Directions?",
    ),
    (
        "📜 CONTRACT",
        "Free consent",
        "What constitutes free consent under the Indian Contract Act, 1872?",
    ),
    (
        "⚡ GST",
        "E-commerce rates",
        "What is the GST rate applicable on e-commerce operators in India?",
    ),
]


def render_welcome():
    st.markdown(
        """<div class="lf-welcome-wrap">
          <div class="lf-hero-icon">⚖️</div>
          <h1 class="lf-hero-title">Your Legal &amp; Finance AI</h1>
          <p class="lf-hero-sub">
            Ask questions about Indian tax laws, RBI regulations, and legal provisions.
            Upload your own documents to get answers grounded in both official rules and your files.
          </p>
        </div>""",
        unsafe_allow_html=True,
    )

    # Central Upload Box for Landing Page
    st.markdown('<div class="lf-upload-container">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop research papers, contracts, or circulars to start analyzing",
        type=["pdf", "txt", "docx"],
        key="welcome_uploader",
    )
    if uploaded and uploaded.name != st.session_state.get("last_uploaded_name"):
        _handle_upload(uploaded)
    st.markdown("</div>", unsafe_allow_html=True)

    # Example cards (Grid)
    st.markdown(
        '<p style="font-size:0.7rem; color:#475569; text-transform:uppercase; letter-spacing:0.1em; font-weight:700; margin:2rem auto 1rem; text-align:center;">Suggested Topics</p>',
        unsafe_allow_html=True,
    )

    with st.container():
        cols = st.columns(2)
        for i, (tag, title, full_q) in enumerate(_EXAMPLES):
            with cols[i % 2]:
                st.markdown(f'<p style="font-size:0.65rem; color:#6366f1; font-weight:800; margin-bottom:0.4rem; margin-left:0.5rem; text-transform:uppercase;">{tag}</p>', unsafe_allow_html=True)
                if st.button(
                    title,
                    key=f"ex_btn_{i}",
                    use_container_width=True,
                    help=f"Query: {full_q}",
                ):
                    _process_query(full_q)
                    st.rerun()


# ─── Chat History ─────────────────────────────────────────────────────────────


def render_chat_history():
    messages = get_messages()
    if not messages:
        render_welcome()
        return

    st.markdown(
        '<div style="max-width:800px;margin:0 auto;padding:1.25rem 1rem 0.5rem;">',
        unsafe_allow_html=True,
    )
    for idx, msg in enumerate(messages):
        if msg.role == "user":
            _render_user(msg)
        else:
            _render_assistant(msg, idx)
    st.markdown("</div>", unsafe_allow_html=True)


def _ts(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def _render_user(msg):
    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="lf-bubble-user">{msg.content}</div>'
            f'<div class="lf-ts right">{_ts(msg.timestamp)}'
            + (f" · {msg.domain.upper()}" if msg.domain and msg.domain != "all" else "")
            + "</div>",
            unsafe_allow_html=True,
        )


def _render_assistant(msg, idx: int):
    bubble_cls = "lf-bubble-error" if msg.is_error else "lf-bubble-ai"
    with st.chat_message("assistant", avatar="⚖️"):
        st.markdown(
            f'<div class="{bubble_cls}">{msg.content}</div>'
            f'<div class="lf-ts">{_ts(msg.timestamp)}</div>',
            unsafe_allow_html=True,
        )
        if not msg.is_error:
            if msg.sources and st.session_state.get("show_sources", True):
                render_sources(msg.sources, key_prefix=f"h{idx}")
            if msg.metadata and st.session_state.get("show_metadata", False):
                _render_meta(msg.metadata, idx)


def _render_meta(meta: dict, idx: int):
    with st.expander("📊 Metadata", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("Retrieval", f"{meta.get('retrieval_time_ms',0):.0f} ms")
        c1.metric("Candidates", meta.get("retrieval_candidates", 0))
        c2.metric("Generation", f"{meta.get('generation_time_ms',0):.0f} ms")
        c2.metric("Chunks", meta.get("reranked_chunks", 0))
        c3.metric("Total", f"{meta.get('total_time_ms',0):.0f} ms")
        tok = meta.get("token_usage", {})
        c3.metric("Tokens", tok.get("total_tokens", 0))
        st.caption(
            f"Model: {meta.get('model','N/A')}  ·  Prompt: {meta.get('prompt_version','v1')}"
        )


# ─── File Badge Bar ───────────────────────────────────────────────────────────


def render_file_upload():
    uploads = get_uploaded_files()
    if uploads:
        badges = "".join(
            f'<span class="lf-fbadge">📎 {u.filename}</span>' for u in uploads
        )
        st.markdown(
            f'<div class="lf-filesbar">'
            f'<span class="lf-filesbar-label">Active files</span>{badges}'
            f"</div>",
            unsafe_allow_html=True,
        )


# ─── Chat Input Row ───────────────────────────────────────────────────────────


def render_chat_input():
    # Only show the additional upload zone if we already have messages
    # (The landing page has its own central one)
    messages = get_messages()
    if messages:
        st.markdown('<div class="lf-upload-container">', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Add another document to this research (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"],
            key="chat_uploader",
        )
        if uploaded and uploaded.name != st.session_state.get("last_uploaded_name"):
            _handle_upload(uploaded)
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input centered
    st.markdown('<div style="max-width:800px; margin:0 auto;">', unsafe_allow_html=True)
    if prompt := st.chat_input(
        "Ask about tax, finance, or legal matters…",
        key="main_input",
    ):
        _process_query(prompt)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _handle_upload(file):
    sid = get_session_id()
    with st.spinner(f"Indexing {file.name}…"):
        try:
            resp = requests.post(
                f"{config.API_BASE_URL}/api/v1/user/upload",
                params={"session_id": sid},
                files={"file": (file.name, file.getvalue())},
                timeout=90,
            )
            if resp.status_code == 200:
                data = resp.json()
                add_uploaded_file(file.name, data.get("chunks_created", 0))
                st.session_state.last_uploaded_name = file.name
                add_message(
                    "assistant",
                    f"📄 **{file.name}** uploaded and indexed — "
                    f"**{data.get('chunks_created', 0)} chunks** ready.\n\n"
                    "You can now ask questions that reference this document alongside official regulations.",
                )
                st.rerun()
            else:
                err = resp.json().get("detail", "Upload failed")
                st.error(f"Upload error: {err}")
        except Exception as exc:
            st.error(f"Could not reach API: {exc}")


# ─── Query Processing ─────────────────────────────────────────────────────────


def _process_query(question: str):
    domain = get_domain()
    session_id = get_session_id()

    add_message("user", question, domain=domain)

    with st.chat_message("user", avatar="👤"):
        st.markdown(
            f'<div class="lf-bubble-user">{question}</div>',
            unsafe_allow_html=True,
        )

    with st.chat_message("assistant", avatar="⚖️"):
        placeholder = st.empty()
        placeholder.markdown(
            '<div class="lf-bubble-ai">'
            '<div class="lf-typing"><span></span><span></span><span></span></div>'
            "</div>",
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
                f'<div class="lf-bubble-ai">{result.answer}</div>',
                unsafe_allow_html=True,
            )
            add_message(
                "assistant",
                result.answer,
                sources=result.sources,
                metadata=result.metadata,
                domain=domain,
            )
            if result.sources and st.session_state.get("show_sources", True):
                render_sources(result.sources, key_prefix="live")
            if result.metadata and st.session_state.get("show_metadata", False):
                _render_meta(result.metadata, -1)
        else:
            err = f"❌ **{result.error}**"
            st.markdown(
                f'<div class="lf-bubble-error">{err}</div>', unsafe_allow_html=True
            )
            add_message("assistant", err, domain=domain, is_error=True)
