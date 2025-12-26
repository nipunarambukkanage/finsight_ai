import pytest
from backend.app.memory.service import memory_service
from backend.app.memory.models import MemoryCategory
from backend.app.memory.policies import MemoryPolicyViolation
from backend.app.providers.manager import provider_manager, DemoProvider, OllamaProvider

def test_memory_storage_and_deduplication():
    """Verify storing duplicate content increments version instead of creating redundant rows."""
    title = "Key Quantitative Rule"
    content = "Always verify zero look-ahead bias before promoting strategy to backtest."

    item1 = memory_service.store_memory(
        tenant_id="tenant_a",
        user_id="analyst_1",
        category=MemoryCategory.LESSON_LEARNED,
        title=title,
        content=content
    )
    assert item1.version == 1

    # Store identical memory
    item2 = memory_service.store_memory(
        tenant_id="tenant_a",
        user_id="analyst_1",
        category=MemoryCategory.LESSON_LEARNED,
        title=title,
        content=content
    )
    assert item2.version == 2
    assert item2.id == item1.id

def test_memory_policy_blocks_secrets():
    """Verify security policy blocks storing API keys, tokens, and passwords."""
    with pytest.raises(MemoryPolicyViolation):
        memory_service.store_memory(
            tenant_id="tenant_a",
            user_id="analyst_1",
            category=MemoryCategory.WORKFLOW_CONTEXT,
            title="Leaked API Key",
            content="Use this api_key: sk-1234567890abcdef1234567890"
        )

def test_memory_tenant_isolation():
    """Verify memories from tenant_b are not visible to tenant_a."""
    memory_service.store_memory(
        tenant_id="tenant_b",
        user_id="analyst_b",
        category=MemoryCategory.CLIENT_INSTRUCTION,
        title="Confidential Client Mandate B",
        content="Allocate only to large-cap equities with market cap over 200B."
    )

    results = memory_service.retrieve_relevant_memories(
        query="Confidential Client Mandate B",
        tenant_id="tenant_a",
        user_id="analyst_a"
    )
    assert not any(r.title == "Confidential Client Mandate B" for r in results)

@pytest.mark.asyncio
async def test_provider_manager_fallback_and_telemetry():
    """Verify provider gateway executes and records telemetry with fallback."""
    text, telemetry = await provider_manager.execute_with_telemetry(
        prompt="Synthesize Apple performance metrics.",
        provider_name="OLLAMA",
        prompt_version="v2.1"
    )
    assert text is not None
    assert len(text) > 20
    assert "latency_ms" in telemetry
    assert telemetry["prompt_version"] == "v2.1"
    assert telemetry["status"] in ["success", "fallback"]
