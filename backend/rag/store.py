# rag/store.py
from langchain_postgres import PGEngine, PGVectorStore
from langchain_voyageai import VoyageAIEmbeddings

from core.config import CONNECTION_STRING, EMBEDDING_MODEL


def get_store(table_name:str) -> PGVectorStore:
    engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
    return PGVectorStore.create_sync(
        engine=engine,
        table_name=table_name,
        embedding_service=VoyageAIEmbeddings(model=EMBEDDING_MODEL),
    )


