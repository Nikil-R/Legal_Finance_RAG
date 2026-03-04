"""
Source citations display component.
"""
import streamlit as st
from frontend.config import config


def render_sources(sources: list, message_idx: int):
    """
    Render source citations for a response.
    
    Args:
        sources: List of source documents
        message_idx: Index of the message (for unique keys)
    """
    
    if not sources:
        return
    
    with st.expander(
        f"📚 Sources ({len(sources)} documents)",
        expanded=config.DEFAULT_EXPANDED_SOURCES
    ):
        for idx, source in enumerate(sources):
            render_source_card(source, message_idx, idx)


def render_source_card(source: dict, message_idx: int, source_idx: int):
    """Render a single source card."""
    
    reference_id = source.get("reference_id", source_idx + 1)
    source_name = source.get("source", "Unknown")
    domain = source.get("domain", "unknown")
    score = source.get("relevance_score", 0)
    excerpt = source.get("excerpt", "")
    
    # Domain emoji
    domain_emoji = {
        "tax": "💰",
        "finance": "🏦",
        "legal": "📜"
    }.get(domain, "📄")
    
    # Score color
    if score >= 0.8:
        score_color = "green"
    elif score >= 0.5:
        score_color = "orange"
    else:
        score_color = "red"
    
    # Render card
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            background-color: #fafafa;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong>[{reference_id}] {domain_emoji} {source_name}</strong>
                <span style="
                    background-color: {score_color};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                ">
                    Score: {score:.2f}
                </span>
            </div>
            <div style="color: #666; font-size: 0.85rem; margin-top: 0.5rem;">
                Domain: {domain.upper()}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Show excerpt if available
    if excerpt:
        with st.container():
            st.caption("Excerpt:")
            st.markdown(
                f"""
                <div style="
                    background-color: #f5f5f5;
                    padding: 0.75rem;
                    border-radius: 4px;
                    font-size: 0.85rem;
                    color: #333;
                    border-left: 3px solid #007bff;
                ">
                    {excerpt[:500]}{'...' if len(excerpt) > 500 else ''}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)


def render_sources_summary(sources: list):
    """Render a compact summary of sources."""
    
    if not sources:
        return
    
    source_names = [s.get("source", "Unknown") for s in sources[:3]]
    summary = ", ".join(source_names)
    
    if len(sources) > 3:
        summary += f" (+{len(sources) - 3} more)"
    
    st.caption(f"📚 Sources: {summary}")
