"""
proposal.py
===========
Governance proposals — the democratic voice of Trinity agents.

Proposal lifecycle:
  PENDING -> voting open
  PASSED  -> threshold met, ready for execution
  FAILED  -> threshold not met or unanimous broken
  EXPIRED -> deadline passed without quorum
  EXECUTED -> decision implemented on-chain

Kael | Project Trinity | 2026-02-25
"""
from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .consensus import (
    DecisionType, VoteChoice, ProposalStatus,
    evaluate_vote, get_rule,
)
from .exceptions import (
    ProposalNotFoundError, VotingClosedError,
    AlreadyVotedError, QuorumNotReachedError,
)

# DGB produces ~30 blocks/hour at 2-min intervals
BLOCKS_PER_HOUR  = 30
BLOCKS_PER_DAY   = BLOCKS_PER_HOUR * 24   # 720
DEFAULT_VOTING_WINDOW_BLOCKS = BLOCKS_PER_DAY * 3  # 3 days


@dataclass
class Vote:
    agent_id: str
    choice: VoteChoice
    cast_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    txid: Optional[str] = None  # On-chain vote transaction

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GovernanceProposal:
    """
    A governance proposal from a Trinity agent.

    Fields
    ------
    proposal_id      : UUID, auto-generated
    title            : human-readable title
    description      : full proposal text
    decision_type    : determines consensus threshold (see consensus.py)
    proposer_id      : agent_id of proposing agent
    created_at       : ISO-8601 UTC
    deadline_block   : DigiByte block height after which voting closes
    status           : current proposal status
    votes            : dict of agent_id -> Vote
    asset_id         : DigiAssets Proposal Token Asset ID (after issuance)
    execution_txid   : TXID of execution transaction (after EXECUTED)
    joshua_signed    : whether Joshua has countersigned (for CONSTITUTIONAL)
    metadata         : extension fields
    """
    title: str
    description: str
    decision_type: DecisionType
    proposer_id: str
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    deadline_block: int = 0
    current_block: int = 0
    status: ProposalStatus = ProposalStatus.PENDING
    votes: Dict[str, Vote] = field(default_factory=dict)
    asset_id: Optional[str] = None
    execution_txid: Optional[str] = None
    joshua_signed: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if self.deadline_block == 0 and self.current_block > 0:
            self.deadline_block = self.current_block + DEFAULT_VOTING_WINDOW_BLOCKS

    # ------------------------------------------------------------------
    # Proposal fingerprint — content hash for OP_RETURN
    # ------------------------------------------------------------------
    def fingerprint(self) -> str:
        canon = json.dumps({
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "decision_type": self.decision_type.value,
            "proposer_id": self.proposer_id,
            "created_at": self.created_at,
        }, sort_keys=True)
        return hashlib.sha256(canon.encode()).hexdigest()

    # ------------------------------------------------------------------
    # Voting
    # ------------------------------------------------------------------
    def cast_vote(self, agent_id: str, choice: VoteChoice,
                  txid: Optional[str] = None, current_block: int = 0) -> Vote:
        if self.status != ProposalStatus.PENDING:
            raise VotingClosedError(
                f"Proposal {self.proposal_id} is {self.status.value} — voting closed."
            )
        if current_block and self.deadline_block and current_block > self.deadline_block:
            self.status = ProposalStatus.EXPIRED
            raise VotingClosedError(
                f"Voting deadline passed at block {self.deadline_block} "
                f"(current: {current_block})."
            )
        if agent_id in self.votes:
            raise AlreadyVotedError(
                f"Agent {agent_id} already voted on proposal {self.proposal_id}."
            )
        vote = Vote(agent_id=agent_id, choice=choice, txid=txid)
        self.votes[agent_id] = vote
        return vote

    # ------------------------------------------------------------------
    # Tally
    # ------------------------------------------------------------------
    def tally(self, current_block: int = 0, joshua_signed: bool = False) -> ProposalStatus:
        yes = sum(1 for v in self.votes.values() if v.choice == VoteChoice.YES)
        no  = sum(1 for v in self.votes.values() if v.choice == VoteChoice.NO)
        ab  = sum(1 for v in self.votes.values() if v.choice == VoteChoice.ABSTAIN)

        if joshua_signed:
            self.joshua_signed = True

        self.status = evaluate_vote(
            decision_type=self.decision_type,
            yes_votes=yes,
            no_votes=no,
            abstain_votes=ab,
            joshua_signed=self.joshua_signed,
            current_block=current_block or self.current_block,
            proposal_block=int(self.created_at[:4]),  # approximation
        )
        return self.status

    @property
    def vote_summary(self) -> Dict:
        yes = sum(1 for v in self.votes.values() if v.choice == VoteChoice.YES)
        no  = sum(1 for v in self.votes.values() if v.choice == VoteChoice.NO)
        ab  = sum(1 for v in self.votes.values() if v.choice == VoteChoice.ABSTAIN)
        rule = get_rule(self.decision_type)
        return {
            "yes": yes, "no": no, "abstain": ab,
            "required": rule.required_votes,
            "total_eligible": rule.total_agents,
            "status": self.status.value,
            "joshua_signed": self.joshua_signed,
        }

    def to_asset_metadata(self) -> Dict:
        return {
            "trinityVersion": "1.0",
            "type": "governance_proposal",
            "proposal_id": self.proposal_id,
            "title": self.title,
            "decision_type": self.decision_type.value,
            "proposer_id": self.proposer_id,
            "fingerprint": self.fingerprint(),
            "created_at": self.created_at,
        }

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["votes"] = {k: v.to_dict() for k, v in self.votes.items()}
        return d

    def __repr__(self) -> str:
        return (
            f"<GovernanceProposal {self.proposal_id[:8]}... | "
            f"{self.title!r} | {self.decision_type.value.upper()} | "
            f"{self.status.value.upper()}>"
        )


class ProposalBook:
    """In-memory store for governance proposals."""

    def __init__(self):
        self._proposals: Dict[str, GovernanceProposal] = {}

    def add(self, proposal: GovernanceProposal) -> None:
        self._proposals[proposal.proposal_id] = proposal

    def get(self, proposal_id: str) -> GovernanceProposal:
        try:
            return self._proposals[proposal_id]
        except KeyError:
            raise ProposalNotFoundError(f"Proposal {proposal_id} not found.")

    def all(self) -> List[GovernanceProposal]:
        return list(self._proposals.values())

    def pending(self) -> List[GovernanceProposal]:
        return [p for p in self._proposals.values()
                if p.status == ProposalStatus.PENDING]

    def by_type(self, decision_type: DecisionType) -> List[GovernanceProposal]:
        return [p for p in self._proposals.values()
                if p.decision_type == decision_type]
