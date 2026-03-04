"""
Header component with domain tabs.
"""
import streamlit as st
from frontend.config import config
from frontend.utils.state import set_domain, get_domain


def render_header():
    """Render the application header."""
    
    # Title and description
    st.markdown(
        """
        <div style="text-align: center; padding: 1rem 0;">
            <h1>⚖️ LegalFinance RAG</h1>
            <p style="color: #666; font-size: 1.1rem;">
                AI-powered assistant for Indian Tax Laws, Financial Regulations, and Legal Provisions
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_domain_tabs():
    """Render domain selection tabs."""
    
    domains = config.DOMAINS
    current_domain = get_domain()
    
    # Create columns for tabs
    cols = st.columns(len(domains))
    
    for idx, (domain_id, domain_info) in enumerate(domains.items()):
        with cols[idx]:
            # Determine if this tab is active
            is_active = domain_id == current_domain
            
            # Style based on active state
            if is_active:
                button_type = "primary"
            else:
                button_type = "secondary"
            
            # Create button
            if st.button(
                f"{domain_info['icon']} {domain_info['name']}",
                key=f"domain_tab_{domain_id}",
                use_container_width=True,
                type=button_type
            ):
                set_domain(domain_id)
                st.rerun()
    
    # Show description for current domain
    current_info = domains[current_domain]
    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.5rem; color: #888; font-size: 0.9rem;">
            {current_info['description']}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
