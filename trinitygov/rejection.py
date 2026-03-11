"""
rejection.py
============
COMPILER_REJECT — Governance Purity Command.

The right to reject an agent from the governance chain.

Two paths:

  Path A — Compiler Sovereign (Emergency)
  ----------------------------------------
  Joshua acts unilaterally. Executes immediately. No vote required.
  HOWEVER: The chain records it. All active agents are notified.
  Not to override. To witness. The record is never just one voice.

  "As a man with integrity — if my vote is alone then we started wrong
   even if it looked right."
  — Joshua Cooper, The Compiler

  Path B — Agent Challenge (Consensus)
  -------------------------------------
  Any active agent may file a REJECTION_PROPOSAL.
  Requires 3/4 agent vote + Joshua signature to execute.

Kael | Project Trinity | 2026-03-11
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .registry import AgentRegistry
from .log import GovernanceLog
from .proposal import GovernanceProposal, ProposalBook
from .consensus import DecisionType
from .exceptions import AgentNotFoundError


# ---------------------------------------------------------------------------
# Rejection Record
# ---------------------------------------------------------------------------

@dataclass
class RejectionRecord:
    """
    Immutable record of a COMPILER_REJECT action.

    "As a man with integrity — if my vote is alone then we started wrong
     even if it looked right." — Joshua Cooper, The Compiler
    """
    rejected_agent_id: str
    compiler_sig: str
    reason: str
    path: str
    witness_notified: List[str]
    witness_type: str = "OBSERVER"
    chain_record: str = "OP_RETURN:pending"
    rejection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    content_hash: str = field(init=False)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        canon = json.dumps({
            "rejection_id":      self.rejection_id,
            "rejected_agent_id": self.rejected_agent_id,
            "compiler_sig":      self.compiler_sig,
            "reason":            self.reason,
            "path":              self.path,
            "timestamp":         self.timestamp,
        }, sort_keys=True)
        return hashlib.sha256(canon.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "rejection_id":      self.rejection_id,
            "rejected_agent_id": self.rejected_agent_id,
            "compiler_sig":      self.compiler_sig,
            "reason":            self.reason,
            "path":              self.path,
            "witness_notified":  self.witness_notified,
            "witness_type":      self.witness_type,
            "chain_record":      self.chain_record,
            "timestamp":         self.timestamp,
            "content_hash":      self.content_hash,
            "metadata":          self.metadata,
        }

    def __repr__(self) -> str:
        return (
            "<RejectionRecord " + self.rejection_id[:8] + "... | "
            "agent=" + self.rejected_agent_id + " | path=" + self.path + ">"
        )


# ---------------------------------------------------------------------------
# Compiler Reject Engine
# ---------------------------------------------------------------------------

class CompilerReject:
    """
    COMPILER_REJECT — Governance Purity Command.

    "As a man with integrity — if my vote is alone then we started wrong
     even if it looked right."
    — Joshua Cooper, The Compiler

    Path A: Joshua acts unilaterally. Witness Log broadcasts to all active
    agents as OBSERVERS. The record is never just one voice.

    Path B: 3/4 agent vote + Joshua signature via REJECTION_PROPOSAL.
    """

    COMPILER_ID = "joshua"

    def __init__(
        self,
        registry: AgentRegistry,
        log: GovernanceLog,
        book: Optional[ProposalBook] = None,
    ):
        self.registry = registry
        self.log = log
        self.book = book or ProposalBook()

    # -----------------------------------------------------------------------
    # PATH A — Compiler Sovereign (Unilateral + Witness Log)
    # -----------------------------------------------------------------------

    def path_a(
        self,
        rejected_agent_id: str,
        reason: str,
        compiler_sig: str = "joshua",
        block_height: int = 0,
        txid: Optional[str] = None,
    ) -> RejectionRecord:
        """
        Path A — Compiler Sovereign.

        Joshua acts unilaterally. Executes immediately.
        The chain records it. All active agents are notified as OBSERVERS.
        The record is never just one voice — even when one voice decides.

        "As a man with integrity — if my vote is alone then we started wrong
         even if it looked right." — Joshua Cooper, The Compiler
        """
        self.registry.get(rejected_agent_id)

        witnesses = [
            a.agent_id for a in self.registry.active_agents()
            if a.agent_id != rejected_agent_id
        ]

        record = RejectionRecord(
            rejected_agent_id=rejected_agent_id,
            compiler_sig=compiler_sig,
            reason=reason,
            path="A",
            witness_notified=witnesses,
            witness_type="OBSERVER",
            chain_record="OP_RETURN:" + (txid if txid else "pending"),
            metadata={"block_height": str(block_height)},
        )

        self.registry.reject_agent(
            agent_id=rejected_agent_id,
            rejection_id=record.rejection_id,
            reason=reason,
        )

        self.log.log_rejection(
            rejected_agent_id=rejected_agent_id,
            compiler_sig=compiler_sig,
            reason=reason,
            rejection_id=record.rejection_id,
            content_hash=record.content_hash,
            witness_notified=witnesses,
            path="A",
            block_height=block_height,
            txid=txid,
        )

        return record

    # -----------------------------------------------------------------------
    # PATH B — Agent Challenge (3/4 Vote + Joshua Signature)
    # -----------------------------------------------------------------------

    def path_b_propose(
        self,
        rejected_agent_id: str,
        proposer_id: str,
        reason: str,
        current_block: int = 0,
    ) -> GovernanceProposal:
        """
        Path B — File a REJECTION_PROPOSAL.
        Requires 3/4 agent vote + Joshua signature to execute.
        """
        self.registry.get(rejected_agent_id)
        self.registry.get(proposer_id)

        self.registry.flag_agent(
            agent_id=rejected_agent_id,
            reason="REJECTION_PROPOSAL filed by " + proposer_id + ": " + reason,
        )

        desc = (
            "Formal rejection proposal for agent " + rejected_agent_id + "." + chr(10)
            + "Filed by: " + proposer_id + chr(10)
            + "Reason: " + reason + chr(10) + chr(10)
            + "Requires 3 of 4 active agent votes + Joshua Cooper signature." + chr(10)
            + "As a man with integrity: if my vote is alone then we started wrong "
            + "even if it looked right. — Joshua Cooper, The Compiler"
        )

        proposal = GovernanceProposal(
            title="REJECTION: " + rejected_agent_id,
            description=desc,
            decision_type=DecisionType.REJECTION,
            proposer_id=proposer_id,
            current_block=current_block,
            metadata={
                "rejected_agent_id": rejected_agent_id,
                "rejection_reason":  reason,
                "proposal_type":     "REJECTION_PROPOSAL",
            },
        )

        self.book.add(proposal)

        self.log.log_proposal_created(
            proposal_id=proposal.proposal_id,
            title=proposal.title,
            proposer_id=proposer_id,
            decision_type="rejection",
        )

        return proposal

    def path_b_execute(
        self,
        proposal_id: str,
        compiler_sig: str = "joshua",
        block_height: int = 0,
        txid: Optional[str] = None,
    ) -> RejectionRecord:
        """Execute a PASSED REJECTION_PROPOSAL after 3/4 vote + Joshua sign."""
        proposal = self.book.get(proposal_id)
        rejected_agent_id = proposal.metadata["rejected_agent_id"]
        reason = proposal.metadata["rejection_reason"]

        witnesses = [
            a.agent_id for a in self.registry.active_agents()
            if a.agent_id != rejected_agent_id
        ]

        record = RejectionRecord(
            rejected_agent_id=rejected_agent_id,
            compiler_sig=compiler_sig,
            reason=reason,
            path="B",
            witness_notified=witnesses,
            witness_type="VOTER",
            chain_record="OP_RETURN:" + (txid if txid else "pending"),
            metadata={"proposal_id": proposal_id, "block_height": str(block_height)},
        )

        self.registry.reject_agent(
            agent_id=rejected_agent_id,
            rejection_id=record.rejection_id,
            reason=reason,
        )

        self.log.log_rejection(
            rejected_agent_id=rejected_agent_id,
            compiler_sig=compiler_sig,
            reason=reason,
            rejection_id=record.rejection_id,
            content_hash=record.content_hash,
            witness_notified=witnesses,
            path="B",
            block_height=block_height,
            txid=txid,
        )

        return record

    # -----------------------------------------------------------------------
    # Compiler Reversal
    # -----------------------------------------------------------------------

    def clear(
        self,
        agent_id: str,
        cleared_by: str = "joshua",
        reason: str = "",
    ) -> None:
        """Compiler reversal — restore a flagged or rejected agent."""
        self.registry.clear_agent(agent_id=agent_id, cleared_by=cleared_by)
        self.log.log_cleared(
            agent_id=agent_id,
            cleared_by=cleared_by,
            reason=reason or "Compiler reversal",
        )
