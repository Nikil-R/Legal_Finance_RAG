from chromadb import PersistentClient
import os

db_path = os.path.join("chroma_db")
try:
    client = PersistentClient(path=db_path)
    collection = client.get_collection("legal_finance_docs")
    print(f"COUNT: {collection.count()}")
except Exception as e:
    print(f"ERROR: {e}")
