"""
API Utilities for health probes and basic connectivity.
"""

import requests
import streamlit as st
import time
from frontend.config import config

def probe_api() -> bool:
    """Health probe — check if API is responsive and at least degraded."""
    urls = [config.API_BASE_URL]
    # If the configured URL is 127.0.0.1, also try localhost as backup (or vice versa)
    if "127.0.0.1" in config.API_BASE_URL:
        urls.append(config.API_BASE_URL.replace("127.0.0.1", "localhost"))
    elif "localhost" in config.API_BASE_URL:
        urls.append(config.API_BASE_URL.replace("localhost", "127.0.0.1"))

    start_time = time.time()
    last_error = None
    
    for url in urls:
        try:
            r = requests.get(f"{url}/health", timeout=15)
            latency = (time.time() - start_time) * 1000
            
            if r.status_code == 200:
                data = r.json()
                status = data.get("status", "unknown")
                st.session_state.api_status = status
                st.session_state.api_latency = round(latency, 1)
                st.session_state.api_healthy = status in ["healthy", "degraded"]
                return True
            elif r.status_code == 503:
                # Backend returned unhealthy — but it may have detail with component info
                try:
                    data = r.json()
                    detail = data.get("detail", {})
                    st.session_state.api_status = detail.get("status", "unhealthy")
                except Exception:
                    st.session_state.api_status = "unhealthy"
                st.session_state.api_healthy = False
                st.session_state.api_latency = round(latency, 1)
                return False
            else:
                last_error = f"Status {r.status_code}"
        except Exception as e:
            last_error = str(e)
            continue
            
    # If we reach here, all URLs failed
    st.session_state.api_status = "offline"
    st.session_state.api_healthy = False
    st.session_state.api_latency = 0
    st.session_state.api_error = last_error
    return False
