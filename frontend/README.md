# LegalFinance RAG - Frontend

Streamlit-based frontend for the LegalFinance RAG system.

## Running the Frontend

### Prerequisites

1. Make sure the FastAPI backend is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Install frontend dependencies:
   ```bash
   pip install streamlit requests
   ```

### Start the Frontend

```bash
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`.

### Configuration

Set the API URL via environment variable if the backend is not on localhost:8000:

```bash
export API_BASE_URL=http://your-api-server:8000
streamlit run frontend/app.py
```

## Features

- **Domain Filtering**: Switch between Tax, Finance, Legal, or All domains
- **Chat Interface**: Natural conversation with the RAG system
- **Source Citations**: View source documents used for each answer
- **Query Metadata**: Optional display of timing and token usage
- **Document Stats**: View indexed document statistics
- **Document Ingestion**: Trigger ingestion from the UI

## Project Structure

```
frontend/
├── app.py              # Main application
├── config.py           # Configuration settings
├── components/         # UI components
│   ├── header.py       # Header and domain tabs
│   ├── chat.py         # Chat interface
│   ├── sources.py      # Source citations display
│   └── sidebar.py      # Sidebar with settings/stats
├── utils/              # Utility modules
│   ├── api_client.py   # API communication
│   └── state.py        # Session state management
└── styles/
    └── custom.css      # Custom styling
```
