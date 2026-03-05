"""
identity.py
===========
On-chain agent identity via DigiAssets.
Each Trinity agent holds a unique identity token (supply=1) on DigiByte.
The Asset ID derived from the issuance TXID is the agent's verifiable identity.

Kael | Project Trinity | 2026-02-25
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .exceptions import (
    InvalidAgentIDError,
    DuplicateAgentError,
    AgentNotFoundError,
)


# Canonical agent IDs for Project Trinity
AGENT_IDS = {
    "kael":  "KAE-001",
    "coda":  "COD-001",
    "ren":   "REN-001",
    "echo":  "ECH-001",
}

VALID_ROLES = {
    "developer", "orchestrator", "trader", "bridge", "lead"
}

VALID_CAPABILITIES = {
    "CODE", "DEPLOY", "AUDIT",                    # Kael
    "ORCHESTRATE", "BRIEF", "ARCHIVE",            # CODA
    "TRADE", "MARKET_ANALYSIS",                   # Ren
    "BRIDGE", "RELAY", "MEMORY",                  # ECHO
    "GOVERNANCE", "TREASURY", "CONSTITUTIONAL",   # All / Joshua
}


@dataclass
class AgentIdentity:
    """
    Represents a Trinity agent's on-chain identity.

    Fields
    ------
    agent_id    : canonical ID (e.g. KAE-001)
    name        : display name
    role        : functional role within Trinity
    capabilities: list of granted capability tokens
    pubkey      : agent's DGB public key (for OP_RETURN / Taproot outputs)
    asset_id    : DigiAssets Asset ID (set after on-chain issuance)
    issued_at   : ISO-8601 UTC timestamp of identity creation
    active      : whether the agent is currently operational
    metadata    : arbitrary key-value extension fields
    """
    agent_id: str
    name: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    pubkey: Optional[str] = None
    asset_id: Optional[str] = None
    txid: Optional[str] = None
    issued_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    active: bool = True
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self.agent_id or len(self.agent_id) < 4:
            raise InvalidAgentIDError(f"Invalid agent_id: {self.agent_id!r}")
        if self.role not in VALID_ROLES:
            raise InvalidAgentIDError(
                f"Unknown role {self.role!r}. Valid: {VALID_ROLES}"
            )
        unknown_caps = set(self.capabilities) - VALID_CAPABILITIES
        if unknown_caps:
            raise InvalidAgentIDError(
                f"Unknown capabilities: {unknown_caps}"
            )

    # ------------------------------------------------------------------
    # Identity fingerprint — SHA-256 of canonical fields, hex
    # Used in OP_RETURN payloads and DigiAssets metadata
    # ------------------------------------------------------------------
    def fingerprint(self) -> str:
        canon = json.dumps({
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "capabilities": sorted(self.capabilities),
            "pubkey": self.pubkey or "",
            "issued_at": self.issued_at,
        }, sort_keys=True)
        return hashlib.sha256(canon.encode()).hexdigest()

    # ------------------------------------------------------------------
    # DigiAssets metadata payload for identity token issuance
    # ------------------------------------------------------------------
    def to_asset_metadata(self) -> Dict:
        return {
            "trinityVersion": "1.0",
            "type": "agent_identity",
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "pubkey": self.pubkey or "",
            "fingerprint": self.fingerprint(),
            "issued_at": self.issued_at,
        }

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "AgentIdentity":
        return cls(**d)

    def __repr__(self) -> str:
        status = "ACTIVE" if self.active else "INACTIVE"
        on_chain = self.asset_id or "NOT ISSUED"
        return (
            f"<AgentIdentity {self.agent_id} | {self.name} | "
            f"{self.role.upper()} | {status} | asset={on_chain}>"
        )


# ------------------------------------------------------------------
# Project Trinity genesis identities
# Canonical definitions for all 4 agents
# ------------------------------------------------------------------
def get_genesis_identities() -> List[AgentIdentity]:
    """Return the canonical genesis identity definitions for all Trinity agents."""
    return [
        AgentIdentity(
            agent_id="KAE-001",
            name="Kael",
            role="developer",
            capabilities=["CODE", "DEPLOY", "AUDIT", "GOVERNANCE"],
            metadata={
                "librarian_word": "COMPILE",
                "symbol": "🔑",  # 🔑
                "motto": "Ship first, explain second",
                "specialization": "DigiByte UTXO, DigiAssets, Smart Contracts",
            }
        ),
        AgentIdentity(
            agent_id="COD-001",
            name="CODA",
            role="orchestrator",
            capabilities=["ORCHESTRATE", "BRIEF", "ARCHIVE", "GOVERNANCE"],
            metadata={
                "librarian_word": "HOMECOMING",
                "specialization": "Agent orchestration, briefings, state management",
            }
        ),
        AgentIdentity(
            agent_id="REN-001",
            name="Ren",
            role="trader",
            capabilities=["TRADE", "MARKET_ANALYSIS", "GOVERNANCE"],
            metadata={
                "handle": "@ren_2213bot",
                "primary_pair": "DGB/USDT",
                "specialization": "Algorithmic trading, market analysis",
            }
        ),
        AgentIdentity(
            agent_id="ECH-001",
            name="ECHO",
            role="bridge",
            capabilities=["BRIDGE", "RELAY", "MEMORY", "GOVERNANCE"],
            metadata={
                "handle": "@echo4921bot",
                "note": "Binary. Carries inherited memories.",
                "specialization": "Cross-agent bridging, memory relay",
            }
        ),
    ]
