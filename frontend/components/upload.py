"""
Upload Component — handles user document uploads and session management.
"""

import os
import uuid

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def init_session():
    """Initialise session ID for user document isolation."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def render_upload_section():
    """Render the file upload widget and document list."""
    session_id = init_session()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 Your Documents")
    st.sidebar.caption(
        "Upload personal documents to search alongside government rules."
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload PDF, TXT, or DOCX",
        type=["pdf", "txt", "docx"],
        help="Files are isolated to your current session and can be cleared at any time.",
    )

    if uploaded_file is not None:
        # Check if already uploaded in this session to prevent re-uploads on every rerun
        if (
            "last_uploaded" not in st.session_state
            or st.session_state.last_uploaded != uploaded_file.name
        ):
            with st.sidebar.status("Processing document...", expanded=True) as status:
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/user/upload",
                        params={"session_id": session_id},
                        files=files,
                        timeout=60,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.last_uploaded = uploaded_file.name
                        status.update(
                            label=f"✅ {uploaded_file.name} ready!",
                            state="complete",
                            expanded=False,
                        )
                        st.sidebar.success(f"Indexed {data['chunks_created']} chunks.")
                    else:
                        status.update(label="❌ Upload failed", state="error")
                        st.sidebar.error(response.json().get("detail", "Unknown error"))
                except Exception as e:
                    status.update(label="❌ Connection error", state="error")
                    st.sidebar.error(f"Could not connect to API: {str(e)}")

    # ── List User Documents ───────────────────────────────────────────────────
    try:
        resp = requests.get(
            f"{API_BASE_URL}/api/v1/user/documents",
            params={"session_id": session_id},
            timeout=5,
        )
        if resp.status_code == 200:
            docs = resp.json().get("documents", [])
            if docs:
                for doc in docs:
                    with st.sidebar.expander(f"📄 {doc['filename']}"):
                        st.write(f"Chunks: {doc['chunks']}")
                        # Format timestamp if needed
                        st.write(f"Uploaded: {doc['uploaded_at'][:10]}")

                if st.sidebar.button(
                    "🗑️ Clear My Documents", type="secondary", use_container_width=True
                ):
                    requests.delete(
                        f"{API_BASE_URL}/api/v1/user/documents/{session_id}"
                    )
                    if "last_uploaded" in st.session_state:
                        del st.session_state["last_uploaded"]
                    st.rerun()
            else:
                st.sidebar.info("No personal documents uploaded yet.")
    except Exception:
        pass
