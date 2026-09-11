"""
FinSight AI - Agent Permissions & Security Policy
Codifies role-based access control (RBAC), least privilege, and separation of duties for logical agents.
"""

from typing import Set, Dict, Any
from enum import Enum

class AgentRole(str, Enum):
    RESEARCH_AGENT = "research_agent"
    DEVELOPER_AGENT = "developer_agent"
    QA_AGENT = "qa_agent"
    SUPERVISOR = "supervisor"
    HUMAN_OPERATOR = "human_operator"

class AgentAction(str, Enum):
    READ_MARKET_DATA = "read_market_data"
    SEARCH_DOCUMENTS = "search_documents"
    WRITE_RESEARCH_BRIEF = "write_research_brief"
    GENERATE_STRATEGY_SPEC = "generate_strategy_spec"
    CREATE_CANDIDATE_CODE = "create_candidate_code"
    EXECUTE_STATIC_QA = "execute_static_qa"
    EXECUTE_SANDBOX_TESTS = "execute_sandbox_tests"
    REJECT_ARTIFACT = "reject_artifact"
    APPROVE_CODE = "approve_code"
    RUN_BACKTEST = "run_backtest"
    PROMOTE_TO_SHADOW = "promote_to_shadow"
    EXECUTE_REAL_TRADE = "execute_real_trade"
    ROUTE_WORKFLOW = "route_workflow"
    BYPASS_GATES = "bypass_gates"


ROLE_PERMISSIONS: Dict[AgentRole, Set[AgentAction]] = {
    AgentRole.RESEARCH_AGENT: {
        AgentAction.READ_MARKET_DATA,
        AgentAction.SEARCH_DOCUMENTS,
        AgentAction.WRITE_RESEARCH_BRIEF,
        AgentAction.GENERATE_STRATEGY_SPEC
    },
    AgentRole.DEVELOPER_AGENT: {
        AgentAction.READ_MARKET_DATA,
        AgentAction.CREATE_CANDIDATE_CODE
    },
    AgentRole.QA_AGENT: {
        AgentAction.EXECUTE_STATIC_QA,
        AgentAction.EXECUTE_SANDBOX_TESTS,
        AgentAction.REJECT_ARTIFACT
    },
    AgentRole.SUPERVISOR: {
        AgentAction.ROUTE_WORKFLOW
    },
    AgentRole.HUMAN_OPERATOR: {
        AgentAction.APPROVE_CODE,
        AgentAction.PROMOTE_TO_SHADOW,
        AgentAction.REJECT_ARTIFACT,
        AgentAction.RUN_BACKTEST
    }
}

class PermissionEnforcer:
    """Enforces least privilege and blocks forbidden financial operations."""

    @staticmethod
    def check_permission(role: AgentRole, action: AgentAction) -> bool:

        if action == AgentAction.EXECUTE_REAL_TRADE:
            raise PermissionError("CRITICAL SAFETY VIOLATION: Execution of real-money trades is strictly prohibited.")


        if action == AgentAction.BYPASS_GATES:
            raise PermissionError("GATE VIOLATION: Deterministic validation gates cannot be bypassed.")

        allowed = ROLE_PERMISSIONS.get(role, set())
        if action not in allowed:
            raise PermissionError(f"Permission denied: Agent role '{role.value}' lacks permission for action '{action.value}'.")
        return True

    @staticmethod
    def check_separation_of_duties(requested_by: str, reviewed_by: str):
        """Ensures that the creator of an artifact cannot approve it."""
        if requested_by.strip().lower() == reviewed_by.strip().lower():
            raise PermissionError(
                f"Separation of duties violation: Creator '{requested_by}' cannot approve their own artifact."
            )
        return True
