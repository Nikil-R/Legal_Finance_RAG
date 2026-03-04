"""
Sidebar component with stats, settings, and actions.
"""
import streamlit as st
from frontend.utils.api_client import api_client
from frontend.utils.state import clear_messages
from frontend.config import config


def render_sidebar():
    """Render the sidebar."""
    
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Display settings
        render_display_settings()
        
        st.divider()
        
        # System status
        render_system_status()
        
        st.divider()
        
        # Document stats
        render_document_stats()
        
        st.divider()
        
        # Actions
        render_actions()
        
        st.divider()
        
        # About
        render_about()


def render_display_settings():
    """Render display settings."""
    
    st.markdown("### 📺 Display")
    
    # Show sources toggle
    st.session_state.show_sources = st.toggle(
        "Show source documents",
        value=st.session_state.get("show_sources", True),
        help="Display source citations with each answer"
    )
    
    # Show metadata toggle
    st.session_state.show_metadata = st.toggle(
        "Show query metadata",
        value=st.session_state.get("show_metadata", False),
        help="Display timing and token usage information"
    )


def render_system_status():
    """Render system status indicators."""
    
    st.markdown("### 🔌 System Status")
    
    # Check API health
    try:
        health = api_client.health_check()
        
        if health.get("status") == "healthy":
            st.success("✅ API Connected")
        elif health.get("status") == "degraded":
            st.warning("⚠️ API Degraded")
        else:
            st.error("❌ API Unhealthy")
        
        # Component status
        components = health.get("components", {})
        
        with st.expander("Component Details"):
            for component, status in components.items():
                icon = "✅" if status else "❌"
                st.markdown(f"{icon} {component.replace('_', ' ').title()}")
    
    except Exception as e:
        st.error("❌ API Unreachable")
        st.caption(f"Error: {str(e)[:50]}")


def render_document_stats():
    """Render document statistics."""
    
    st.markdown("### 📊 Document Stats")
    
    try:
        stats = api_client.get_stats()
        
        if stats.get("index_status") == "ready":
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Chunks", stats.get("total_chunks", 0))
            
            with col2:
                st.metric("Documents", stats.get("total_documents", 0))
            
            # Per-domain breakdown
            domains = stats.get("domains", {})
            if domains:
                st.markdown("**By Domain:**")
                for domain, count in domains.items():
                    emoji = {"tax": "💰", "finance": "🏦", "legal": "📜"}.get(domain, "📄")
                    st.caption(f"{emoji} {domain.title()}: {count} chunks")
        
        elif stats.get("index_status") == "empty":
            st.warning("No documents indexed")
            st.caption("Use 'Ingest Documents' to add documents")
        
        else:
            st.error("Index status unknown")
    
    except Exception as e:
        st.error("Could not fetch stats")


def render_actions():
    """Render action buttons."""
    
    st.markdown("### 🔧 Actions")
    
    # Clear chat history
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_messages()
        st.success("Chat history cleared!")
        st.rerun()
    
    # Ingest documents
    with st.expander("📥 Ingest Documents"):
        st.caption("Load documents from data/raw/ into the system")
        
        clear_existing = st.checkbox(
            "Clear existing documents first",
            value=False,
            help="Remove all existing documents before ingesting"
        )
        
        if st.button("Start Ingestion", use_container_width=True):
            with st.spinner("Ingesting documents..."):
                result = api_client.trigger_ingestion(clear_existing=clear_existing)
            
            if result.get("success"):
                st.success(
                    f"✅ Ingested {result.get('documents_loaded', 0)} documents "
                    f"({result.get('chunks_created', 0)} chunks)"
                )
            else:
                st.error(f"❌ Ingestion failed: {result.get('error', 'Unknown error')}")


def render_about():
    """Render about section."""
    
    st.markdown("### ℹ️ About")
    
    st.markdown(
        """
        **LegalFinance RAG** v0.1.0
        
        An AI-powered assistant for Indian:
        - 💰 Tax Laws
        - 🏦 Financial Regulations  
        - 📜 Legal Provisions
        
        Built with:
        - 🦙 Llama 3.1 (via Groq)
        - 🔍 Hybrid Search (Vector + BM25)
        - ⚡ FastAPI + Streamlit
        """
    )
    
    st.caption("⚠️ For educational purposes only. Not legal/financial advice.")
