from sqlalchemy import create_engine
from core.config import CONNECTION_STRING
from langchain_postgres import PGEngine

def get_engine():
    return create_engine(CONNECTION_STRING)

def get_pg_engine():
    return PGEngine.from_connection_string(CONNECTION_STRING)