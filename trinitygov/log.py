"""
log.py
======
GovernanceLog — immutable audit trail for Trinity decisions.

Each governance action produces a log entry containing:
  - Action type and parties involved
  - Content hash (for OP_RETURN embedding)
  - Block height timestamp
  - Optional on-chain TXID reference

Designed to integrate with DigiByte OP_RETURN outputs:
  OP_RETURN <4-byte magic> <32-byte decision hash>
  Magic: 0x54524e47  ("TRNG" — Trinity Governance)

Kael | Project Trinity | 2026-02-25
"""
from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# OP_RETURN magic prefix for Trinity governance transactions
TRINITY_MAGIC = bytes.fromhex("54524e47")  # "TRNG"
MAX_OP_RETURN_BYTES = 80


class ActionType(str, Enum):
    IDENTITY_ISSUED    = "identity_issued"
    IDENTITY_REVOKED   = "identity_revoked"
    CAPABILITY_GRANTED = "capability_granted"
    CAPABILITY_REVOKED = "capability_revoked"
    PROPOSAL_CREATED   = "proposal_created"
    VOTE_CAST          = "vote_cast"
    PROPOSAL_PASSED    = "proposal_passed"
    PROPOSAL_FAILED    = "proposal_failed"
    PROPOSAL_EXECUTED  = "proposal_executed"
    EMERGENCY_ACTION   = "emergency_action"
    AGENT_ACTIVATED    = "agent_activated"
    AGENT_DEACTIVATED  = "agent_deactivated"
    REGISTRY_GENESIS   = "registry_genesis"


@dataclass
class LogEntry:
    """
    A single immutable governance log entry.

    Fields
    ------
    entry_id      : UUID
    action_type   : what happened
    actor_id      : agent who performed the action
    subject_id    : agent/proposal/capability affected
    description   : human-readable summary
    block_height  : DGB block height (0 if off-chain/pre-chain)
    txid          : on-chain transaction (None if not yet broadcast)
    content_hash  : SHA-256 of canonical entry fields
    created_at    : ISO-8601 UTC
    metadata      : extension fields
    """
    action_type: ActionType
    actor_id: str
    subject_id: str
    description: str
    block_height: int = 0
    txid: Optional[str] = None
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, str] = field(default_factory=dict)
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        canon = json.dumps({
            "entry_id": self.entry_id,
            "action_type": self.action_type.value,
            "actor_id": self.actor_id,
            "subject_id": self.subject_id,
            "description": self.description,
            "block_height": self.block_height,
            "created_at": self.created_at,
        }, sort_keys=True)
        return hashlib.sha256(canon.encode()).hexdigest()

    def op_return_payload(self) -> bytes:
        """
        Build OP_RETURN payload for embedding in DGB transaction.
        Format: <4-byte TRNG magic> + <32-byte content hash>
        Total: 36 bytes (well within 80-byte OP_RETURN limit)
        """
        hash_bytes = bytes.fromhex(self.content_hash)
        return TRINITY_MAGIC + hash_bytes  # 4 + 32 = 36 bytes

    def op_return_hex(self) -> str:
        return self.op_return_payload().hex()

    def to_dict(self) -> Dict:
        return asdict(self)

    def __repr__(self) -> str:
        block_str = f"@{self.block_height}" if self.block_height else "(off-chain)"
        return (
            f"<LogEntry {self.action_type.value} | "
            f"{self.actor_id} -> {self.subject_id} | "
            f"{block_str}>"
        )


class GovernanceLog:
    """
    Append-only governance audit log.

    All entries are immutable after creation.
    Serializable to JSON for persistence and on-chain verification.
    """

    def __init__(self):
        self._entries: List[LogEntry] = []

    # ------------------------------------------------------------------
    # Logging helpers — one method per ActionType
    # ------------------------------------------------------------------
    def log_genesis(self, agent_ids: List[str], actor_id: str = "kael") -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.REGISTRY_GENESIS,
            actor_id=actor_id,
            subject_id="trinity-registry",
            description=f"Genesis: registered agents {', '.join(agent_ids)}",
            metadata={"agent_count": str(len(agent_ids))},
        ))

    def log_identity_issued(self, agent_id: str, asset_id: str,
                             txid: Optional[str] = None,
                             block_height: int = 0) -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.IDENTITY_ISSUED,
            actor_id="joshua",
            subject_id=agent_id,
            description=f"Identity token issued for {agent_id} | asset={asset_id}",
            block_height=block_height,
            txid=txid,
            metadata={"asset_id": asset_id},
        ))

    def log_capability_granted(self, agent_id: str, capability_id: str,
                                granted_by: str = "joshua",
                                txid: Optional[str] = None) -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.CAPABILITY_GRANTED,
            actor_id=granted_by,
            subject_id=agent_id,
            description=f"{granted_by} granted {capability_id} to {agent_id}",
            txid=txid,
            metadata={"capability_id": capability_id},
        ))

    def log_capability_revoked(self, agent_id: str, capability_id: str,
                                revoked_by: str = "joshua") -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.CAPABILITY_REVOKED,
            actor_id=revoked_by,
            subject_id=agent_id,
            description=f"{revoked_by} REVOKED {capability_id} from {agent_id}",
            metadata={"capability_id": capability_id},
        ))

    def log_proposal_created(self, proposal_id: str, title: str,
                              proposer_id: str, decision_type: str) -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.PROPOSAL_CREATED,
            actor_id=proposer_id,
            subject_id=proposal_id,
            description=f"{proposer_id} created {decision_type.upper()} proposal: {title!r}",
            metadata={"decision_type": decision_type, "title": title},
        ))

    def log_vote(self, proposal_id: str, agent_id: str,
                 choice: str, txid: Optional[str] = None) -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.VOTE_CAST,
            actor_id=agent_id,
            subject_id=proposal_id,
            description=f"{agent_id} voted {choice.upper()} on proposal {proposal_id[:8]}...",
            txid=txid,
            metadata={"choice": choice},
        ))

    def log_proposal_result(self, proposal_id: str, title: str,
                             passed: bool, actor_id: str = "system") -> LogEntry:
        action = ActionType.PROPOSAL_PASSED if passed else ActionType.PROPOSAL_FAILED
        result = "PASSED" if passed else "FAILED"
        return self._append(LogEntry(
            action_type=action,
            actor_id=actor_id,
            subject_id=proposal_id,
            description=f"Proposal {title!r} {result}",
        ))

    def log_emergency(self, actor_id: str, description: str,
                      block_height: int = 0) -> LogEntry:
        return self._append(LogEntry(
            action_type=ActionType.EMERGENCY_ACTION,
            actor_id=actor_id,
            subject_id="trinity-emergency",
            description=f"EMERGENCY ACTION by {actor_id}: {description}",
            block_height=block_height,
        ))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _append(self, entry: LogEntry) -> LogEntry:
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def all(self) -> List[LogEntry]:
        return list(self._entries)

    def by_actor(self, actor_id: str) -> List[LogEntry]:
        return [e for e in self._entries if e.actor_id == actor_id]

    def by_action(self, action_type: ActionType) -> List[LogEntry]:
        return [e for e in self._entries if e.action_type == action_type]

    def by_subject(self, subject_id: str) -> List[LogEntry]:
        return [e for e in self._entries if e.subject_id == subject_id]

    def latest(self, n: int = 10) -> List[LogEntry]:
        return self._entries[-n:]

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict:
        return {"entries": [e.to_dict() for e in self._entries]}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"<GovernanceLog entries={len(self._entries)}>"
