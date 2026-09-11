"""Optional durable LangGraph checkpointer selection.

The application can run without optional checkpoint packages in the zero-key
demo profile. Production deployments should install the PostgreSQL checkpoint
extra and pass the returned saver/store to ``build_research_graph``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import atexit


def _open_context(resource: Any) -> Any:
    """Enter LangGraph's SQLite context manager and close it at process exit."""
    if hasattr(resource, "__enter__") and hasattr(resource, "__exit__"):
        opened = resource.__enter__()
        atexit.register(resource.__exit__, None, None, None)
        return opened
    return resource


def local_checkpointer() -> Any:
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        path = Path("data/langgraph_checkpoints.sqlite")
        path.parent.mkdir(parents=True, exist_ok=True)
        return _open_context(SqliteSaver.from_conn_string(str(path)))
    except (ImportError, AttributeError):
        return None


def local_store() -> Any:
    try:
        from langgraph.store.sqlite import SqliteStore
        path = Path("data/langgraph_store.sqlite")
        path.parent.mkdir(parents=True, exist_ok=True)
        return _open_context(SqliteStore.from_conn_string(str(path)))
    except (ImportError, AttributeError):
        return None
