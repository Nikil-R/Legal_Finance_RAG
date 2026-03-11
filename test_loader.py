from app.ingestion.loader import DocumentLoader
loader = DocumentLoader()
docs = loader.load_directory("data/core")
print(f"Loaded {len(docs)} documents")
