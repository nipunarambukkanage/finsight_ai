"""
FinSight AI - Memory Storage & Privacy Policies
Enforces tenant isolation, user isolation, and prevents secret/credential leakage into long-term memory.
"""

import re
from typing import Dict, Any

class MemoryPolicyViolation(Exception):
    pass

class MemoryPolicyEnforcer:
    FORBIDDEN_PATTERNS = [
        re.compile(r"(api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}['\"]?)", re.IGNORECASE),
        re.compile(r"(bearer\s+[a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE),
        re.compile(r"(password\s*[:=]\s*['\"]?[^\s'\"]{6,}['\"]?)", re.IGNORECASE),
        re.compile(r"(secret\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{16,}['\"]?)", re.IGNORECASE),
        re.compile(r"(broker[_-]?(account|token|key|secret)\s*[:=])", re.IGNORECASE),
        re.compile(r"(sk-[a-zA-Z0-9]{20,})", re.IGNORECASE)
    ]

    @classmethod
    def sanitize_and_verify(cls, content: str, metadata: Dict[str, Any]) -> str:
        """Verifies that memory content does not contain credentials, API keys, or forbidden secrets."""
        for pat in cls.FORBIDDEN_PATTERNS:
            if pat.search(content):
                raise MemoryPolicyViolation(
                    "SECURITY POLICY VIOLATION: Memory storage rejected because content contains sensitive credentials, API keys, or secrets."
                )

        # Check metadata keys
        meta_str = str(metadata).lower()
        for pat in cls.FORBIDDEN_PATTERNS:
            if pat.search(meta_str):
                raise MemoryPolicyViolation(
                    "SECURITY POLICY VIOLATION: Memory metadata contains sensitive credentials or keys."
                )

        return content

    @staticmethod
    def verify_tenant_access(request_tenant: str, item_tenant: str, request_user: str, item_user: str) -> bool:
        """Enforces tenant isolation and user privacy boundaries."""
        if request_tenant != item_tenant:
            return False
        # If user is not admin, ensure user isolation
        if request_user != item_user and request_user != "admin":
            return False
        return True
