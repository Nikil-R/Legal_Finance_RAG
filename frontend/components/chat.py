"""
Chat interface component.
"""
import streamlit as st
from datetime import datetime
from frontend.utils.api_client import api_client
from frontend.utils.state import add_message, get_messages, get_domain
from frontend.components.sources import render_sources


def render_chat_history():
    """Render the chat message history."""
    
    messages = get_messages()
    
    if not messages:
        # Show welcome message
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem; color: #888;">
                <h3>👋 Welcome!</h3>
                <p>Ask any question about Indian tax laws, financial regulations, or legal provisions.</p>
                <p style="font-size: 0.9rem;">
                    <strong>Example questions:</strong><br>
                    • What are the deductions available under Section 80C?<br>
                    • What are the KYC requirements for banks as per RBI?<br>
                    • What constitutes free consent under the Contract Act?
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Render each message
    for idx, message in enumerate(messages):
        if message.role == "user":
            render_user_message(message, idx)
        else:
            render_assistant_message(message, idx)


def render_user_message(message, idx: int):
    """Render a user message."""
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(message.content)
        
        # Show domain badge
        domain_badge = f"*{message.domain.upper()}*" if message.domain != "all" else ""
        if domain_badge:
            st.caption(f"Domain: {domain_badge}")


def render_assistant_message(message, idx: int):
    """Render an assistant message."""
    
    with st.chat_message("assistant", avatar="⚖️"):
        # Main answer
        st.markdown(message.content)
        
        # Sources (if available)
        if message.sources and st.session_state.get("show_sources", True):
            render_sources(message.sources, idx)
        
        # Metadata (if enabled)
        if message.metadata and st.session_state.get("show_metadata", False):
            render_metadata(message.metadata, idx)


def render_metadata(metadata: dict, idx: int):
    """Render query metadata."""
    
    with st.expander("📊 Query Metadata", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Retrieval Time", f"{metadata.get('retrieval_time_ms', 0):.0f}ms")
            st.metric("Candidates Found", metadata.get('retrieval_candidates', 0))
        
        with col2:
            st.metric("Generation Time", f"{metadata.get('generation_time_ms', 0):.0f}ms")
            st.metric("Chunks Used", metadata.get('reranked_chunks', 0))
        
        with col3:
            st.metric("Total Time", f"{metadata.get('total_time_ms', 0):.0f}ms")
            token_usage = metadata.get('token_usage', {})
            st.metric("Tokens Used", token_usage.get('total_tokens', 0))
        
        st.caption(f"Model: {metadata.get('model', 'N/A')} | Prompt Version: {metadata.get('prompt_version', 'N/A')}")


def render_chat_input():
    """Render the chat input box."""
    
    # Chat input
    if prompt := st.chat_input("Ask a question about Indian tax, finance, or legal matters..."):
        process_query(prompt)


def process_query(question: str):
    """Process a user query."""
    
    domain = get_domain()
    
    # Add user message
    add_message("user", question, domain=domain)
    
    # Show user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)
    
    # Show thinking indicator
    with st.chat_message("assistant", avatar="⚖️"):
        with st.spinner("Searching documents and generating answer..."):
            session_id = st.session_state.get("session_id")
            # Call API
            result = api_client.query(
                question=question,
                domain=domain,
                include_sources=st.session_state.get("show_sources", True),
                session_id=session_id
            )
    
        if result.success:
            # Display answer
            st.markdown(result.answer)
            
            # Add to history
            add_message(
                "assistant",
                result.answer,
                sources=result.sources,
                metadata=result.metadata,
                domain=domain
            )
            
            # Show sources
            if result.sources and st.session_state.get("show_sources", True):
                render_sources(result.sources, len(get_messages()) - 1)
            
            # Show metadata if enabled
            if result.metadata and st.session_state.get("show_metadata", False):
                render_metadata(result.metadata, len(get_messages()) - 1)
        
        else:
            # Display error
            error_msg = f"❌ **Error:** {result.error}"
            st.error(error_msg)
            add_message("assistant", error_msg, domain=domain)
    
    # Rerun to update chat history
    st.rerun()
