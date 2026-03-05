"""
capability.py
=============
Capability tokens — agent permissions as on-chain DigiAssets.

Each capability is a DigiAsset held by an agent. Granting = transfer.
Revocation = burning the token. Joshua holds master grant authority.
All capability state is checkable both locally and on-chain.

Kael | Project Trinity | 2026-02-25
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from .exceptions import (
    CapabilityNotGrantedError,
    CapabilityRevokedError,
    UnauthorizedCapabilityError,
)


# Master capability definitions
CAPABILITY_REGISTRY: Dict[str, str] = {
    # Developer capabilities
    "CODE":               "Write and deploy code to Trinity infrastructure",
    "DEPLOY":             "Deploy services and contracts to production VPS",
    "AUDIT":              "Audit smart contracts, security configurations",
    # Orchestrator capabilities
    "ORCHESTRATE":        "Direct and brief other Trinity agents",
    "BRIEF":              "Issue official briefings and activate agents",
    "ARCHIVE":            "Write to persistent memory files (journal, master files)",
    # Trader capabilities
    "TRADE":              "Execute trades on loop-bot and external markets",
    "MARKET_ANALYSIS":    "Access and interpret market data feeds",
    # Bridge capabilities
    "BRIDGE":             "Relay messages between agents across platforms",
    "RELAY":              "Forward state and memory between agent instances",
    "MEMORY":             "Read and write agent memory stores",
    # Universal / governance
    "GOVERNANCE":         "Participate in governance votes and proposals",
    "TREASURY":           "Authorize DigiDollar minting and DGB treasury actions",
    "CONSTITUTIONAL":     "Propose constitutional-level protocol changes",
}


@dataclass
class Capability:
    """
    A single capability grant for a specific agent.

    Fields
    ------
    capability_id : e.g. "CODE"
    holder_id     : agent_id of the holder e.g. "KAE-001"
    granted_by    : agent_id or "joshua" of the granter
    asset_id      : DigiAssets Asset ID (set after on-chain issuance)
    txid          : grant transaction TXID
    granted_at    : ISO-8601 UTC timestamp
    revoked       : whether this capability has been burned/revoked
    revoked_at    : ISO-8601 UTC timestamp of revocation
    """
    capability_id: str
    holder_id: str
    granted_by: str
    asset_id: Optional[str] = None
    txid: Optional[str] = None
    granted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    revoked: bool = False
    revoked_at: Optional[str] = None

    def __post_init__(self):
        if self.capability_id not in CAPABILITY_REGISTRY:
            raise UnauthorizedCapabilityError(
                f"Unknown capability: {self.capability_id!r}. "
                f"Valid: {list(CAPABILITY_REGISTRY.keys())}"
            )

    def revoke(self) -> None:
        if self.revoked:
            raise CapabilityRevokedError(
                f"Capability {self.capability_id} for {self.holder_id} already revoked."
            )
        self.revoked = True
        self.revoked_at = datetime.now(timezone.utc).isoformat()

    def assert_active(self) -> None:
        if self.revoked:
            raise CapabilityRevokedError(
                f"{self.holder_id} capability {self.capability_id} was revoked at {self.revoked_at}"
            )

    @property
    def description(self) -> str:
        return CAPABILITY_REGISTRY.get(self.capability_id, "Unknown")

    def to_asset_metadata(self) -> Dict:
        return {
            "trinityVersion": "1.0",
            "type": "capability_token",
            "capability_id": self.capability_id,
            "description": self.description,
            "holder_id": self.holder_id,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at,
        }

    def to_dict(self) -> Dict:
        return asdict(self)

    def __repr__(self) -> str:
        status = "REVOKED" if self.revoked else "ACTIVE"
        return f"<Capability {self.capability_id} -> {self.holder_id} | {status}>"


class CapabilityStore:
    """
    Local capability store — tracks granted capabilities per agent.
    Source of truth until on-chain verification is available.
    """

    def __init__(self):
        # capability_id -> holder_id -> Capability
        self._store: Dict[str, Dict[str, Capability]] = {}

    def grant(self, capability_id: str, holder_id: str, granted_by: str,
              asset_id: Optional[str] = None, txid: Optional[str] = None) -> Capability:
        cap = Capability(
            capability_id=capability_id,
            holder_id=holder_id,
            granted_by=granted_by,
            asset_id=asset_id,
            txid=txid,
        )
        self._store.setdefault(capability_id, {})[holder_id] = cap
        return cap

    def revoke(self, capability_id: str, holder_id: str) -> Capability:
        try:
            cap = self._store[capability_id][holder_id]
        except KeyError:
            raise CapabilityNotGrantedError(
                f"{holder_id} does not hold capability {capability_id}"
            )
        cap.revoke()
        return cap

    def has(self, agent_id: str, capability_id: str) -> bool:
        cap = self._store.get(capability_id, {}).get(agent_id)
        return cap is not None and not cap.revoked

    def require(self, agent_id: str, capability_id: str) -> None:
        if not self.has(agent_id, capability_id):
            raise CapabilityNotGrantedError(
                f"Agent {agent_id} does not have capability {capability_id}"
            )

    def get_agent_capabilities(self, agent_id: str) -> List[Capability]:
        result = []
        for cap_id, holders in self._store.items():
            cap = holders.get(agent_id)
            if cap and not cap.revoked:
                result.append(cap)
        return result

    def get_capability_holders(self, capability_id: str) -> List[Capability]:
        return [
            cap for cap in self._store.get(capability_id, {}).values()
            if not cap.revoked
        ]
