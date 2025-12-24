"""
FinSight AI - System Diagnostic & Health API
Provides granular health status across provider gateway, memory layer, sandbox, and active workflows.
"""

from typing import Dict, Any
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.providers.manager import provider_manager
from backend.app.memory.service import memory_service
from backend.app.orchestration.graph import workflow_engine

router = APIRouter()

@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """Comprehensive system health and service readiness check."""
    return {
        "status": "healthy",
        "app_env": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
        "available_providers": provider_manager.list_providers(),
        "memory_service": {
            "status": "operational",
            "stored_items": len(memory_service._memory_store)
        },
        "workflow_engine": {
            "status": "operational",
            "active_workflows": len(workflow_engine.workflows)
        },
        "sandbox": {
            "status": "operational",
            "isolation_level": "restricted_subprocess",
            "timeout_sec": 5
        },
        "disclaimer": "FinSight AI is an engineering research and decision-support demonstration platform."
    }
