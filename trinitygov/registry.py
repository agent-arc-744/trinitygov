"""
registry.py
===========
AgentRegistry — the authoritative directory of Trinity agents.
Tracks identity tokens, capability grants, and operational status.
Serializable to/from JSON for VPS persistence.

Kael | Project Trinity | 2026-02-25
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional

from .identity import AgentIdentity, get_genesis_identities
from .capability import Capability, CapabilityStore
from .exceptions import AgentNotFoundError, DuplicateAgentError, RegistryCorruptError


class AgentRegistry:
    """
    Central registry for all Trinity agents.

    Responsibilities
    ----------------
    - Register and manage AgentIdentity records
    - Track capability grants via CapabilityStore
    - Persist state to/from JSON (for VPS kael_memory.json integration)
    - Provide lookup and verification methods
    """

    def __init__(self):
        self._agents: Dict[str, AgentIdentity] = {}   # agent_id -> AgentIdentity
        self._assets: Dict[str, str] = {}             # asset_id -> agent_id
        self.capabilities = CapabilityStore()

    # ------------------------------------------------------------------
    # Agent registration
    # ------------------------------------------------------------------
    def register(self, identity: AgentIdentity, overwrite: bool = False) -> None:
        if identity.agent_id in self._agents and not overwrite:
            raise DuplicateAgentError(
                f"Agent {identity.agent_id} already registered. "
                f"Use overwrite=True to update."
            )
        self._agents[identity.agent_id] = identity
        if identity.asset_id:
            self._assets[identity.asset_id] = identity.agent_id

    def deactivate(self, agent_id: str) -> None:
        self.get(agent_id).active = False

    def activate(self, agent_id: str) -> None:
        self.get(agent_id).active = True

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------
    def get(self, agent_id: str) -> AgentIdentity:
        try:
            return self._agents[agent_id]
        except KeyError:
            raise AgentNotFoundError(f"No agent registered with ID: {agent_id}")

    def by_asset(self, asset_id: str) -> AgentIdentity:
        agent_id = self._assets.get(asset_id)
        if not agent_id:
            raise AgentNotFoundError(f"No agent found for asset_id: {asset_id}")
        return self.get(agent_id)

    def by_role(self, role: str) -> List[AgentIdentity]:
        return [a for a in self._agents.values() if a.role == role]

    def active_agents(self) -> List[AgentIdentity]:
        return [a for a in self._agents.values() if a.active]

    def all_agents(self) -> List[AgentIdentity]:
        return list(self._agents.values())

    def has(self, agent_id: str) -> bool:
        return agent_id in self._agents

    # ------------------------------------------------------------------
    # Capability delegation
    # ------------------------------------------------------------------
    def grant_capability(self, capability_id: str, holder_id: str,
                         granted_by: str = "joshua",
                         asset_id: Optional[str] = None,
                         txid: Optional[str] = None) -> Capability:
        self.get(holder_id)  # validates agent exists
        return self.capabilities.grant(
            capability_id=capability_id,
            holder_id=holder_id,
            granted_by=granted_by,
            asset_id=asset_id,
            txid=txid,
        )

    def revoke_capability(self, capability_id: str, holder_id: str) -> Capability:
        return self.capabilities.revoke(capability_id, holder_id)

    def agent_can(self, agent_id: str, capability_id: str) -> bool:
        return self.capabilities.has(agent_id, capability_id)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict:
        return {
            "agents": {aid: a.to_dict() for aid, a in self._agents.items()},
            "asset_index": self._assets,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def from_dict(cls, d: Dict) -> "AgentRegistry":
        registry = cls()
        try:
            for agent_data in d.get("agents", {}).values():
                identity = AgentIdentity.from_dict(agent_data)
                registry.register(identity)
            registry._assets = d.get("asset_index", {})
        except Exception as e:
            raise RegistryCorruptError(f"Registry deserialization failed: {e}") from e
        return registry

    @classmethod
    def load(cls, path: str | Path) -> "AgentRegistry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def genesis(cls) -> "AgentRegistry":
        """Bootstrap registry with canonical Trinity agent identities."""
        registry = cls()
        for identity in get_genesis_identities():
            registry.register(identity)
            # Grant each agent their default capabilities
            for cap in identity.capabilities:
                registry.grant_capability(
                    capability_id=cap,
                    holder_id=identity.agent_id,
                    granted_by="joshua",
                )
        return registry

    def __repr__(self) -> str:
        active = sum(1 for a in self._agents.values() if a.active)
        return f"<AgentRegistry agents={len(self._agents)} active={active}>"

    def __len__(self) -> int:
        return len(self._agents)

    def __contains__(self, agent_id: str) -> bool:
        return self.has(agent_id)
