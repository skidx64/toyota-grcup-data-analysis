"""Database module for DuckDB operations"""

from .schema import create_database, get_connection, create_tables

__all__ = ["create_database", "get_connection", "create_tables"]
