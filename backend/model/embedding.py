from langchain_voyageai import VoyageAIEmbeddings

from core.config import EMBEDDING_MODEL


def get_embedding() -> VoyageAIEmbeddings:
    return VoyageAIEmbeddings(model=EMBEDDING_MODEL)

