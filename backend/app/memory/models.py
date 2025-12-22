"""
FinSight AI - Persistent Memory Models
Defines schema and entities for long-term institutional memory and cross-workflow retrieval.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from backend.app.database.session import Base
from pydantic import BaseModel, Field

class MemoryCategory(str, Enum):
    WORKFLOW_CONTEXT = "WORKFLOW_CONTEXT"
    RESEARCH_SUMMARY = "RESEARCH_SUMMARY"
    CLIENT_INSTRUCTION = "CLIENT_INSTRUCTION"
    DECISION = "DECISION"
    STRATEGY_SUCCESS = "STRATEGY_SUCCESS"
    STRATEGY_REJECTION = "STRATEGY_REJECTION"
    LESSON_LEARNED = "LESSON_LEARNED"

class MemoryItemEntity(Base):
    __tablename__ = "memory_items"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(100), default="default_tenant", index=True, nullable=False)
    user_id = Column(String(100), default="demo_analyst", index=True, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)
    version = Column(Integer, default=1)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class MemoryItemDTO(BaseModel):
    id: Optional[int] = None
    tenant_id: str = "default_tenant"
    user_id: str = "demo_analyst"
    category: MemoryCategory
    title: str
    content: str
    content_hash: Optional[str] = None
    version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
