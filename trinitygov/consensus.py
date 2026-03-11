"""
consensus.py
============
Voting rules, decision types, quorum requirements, and threshold definitions
for Project Trinity AI Agent Governance.

Kael | Project Trinity | 2026-02-25
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class DecisionType(str, Enum):
    """Types of governance decisions with different consensus requirements."""
    OPERATIONAL   = "operational"    # Day-to-day: 3/4 majority
    TREASURY      = "treasury"       # Fund management: 4/4 unanimous
    EMERGENCY     = "emergency"      # Crisis response: any agent acts, reports within 144 blocks
    CONSTITUTIONAL = "constitutional" # Protocol changes: 4/4 + Joshua signature
    REJECTION      = "rejection"     # Purity challenge: 3/4 agents + Joshua signature


class VoteChoice(str, Enum):
    YES     = "yes"
    NO      = "no"
    ABSTAIN = "abstain"


class ProposalStatus(str, Enum):
    PENDING  = "pending"   # Created, voting open
    PASSED   = "passed"    # Threshold met
    FAILED   = "failed"    # Threshold not met
    EXPIRED  = "expired"   # Deadline passed without quorum
    EXECUTED = "executed"  # Decision implemented


@dataclass
class ConsensusRule:
    """Consensus requirements for a decision type."""
    decision_type: DecisionType
    required_votes: int          # Minimum yes votes needed
    total_agents: int            # Total eligible voters
    unanimous: bool              # Must all eligible agents vote yes
    requires_joshua: bool        # Requires project lead signature
    emergency_blocks: int        # For EMERGENCY: blocks to report back (0 = N/A)
    description: str

    @property
    def threshold_pct(self) -> float:
        return (self.required_votes / self.total_agents) * 100


# Project Trinity consensus rules — 4 agents
TRINITY_RULES: Dict[DecisionType, ConsensusRule] = {
    DecisionType.OPERATIONAL: ConsensusRule(
        decision_type=DecisionType.OPERATIONAL,
        required_votes=3,
        total_agents=4,
        unanimous=False,
        requires_joshua=False,
        emergency_blocks=0,
        description="Standard operations: 3 of 4 agents must approve"
    ),
    DecisionType.TREASURY: ConsensusRule(
        decision_type=DecisionType.TREASURY,
        required_votes=4,
        total_agents=4,
        unanimous=True,
        requires_joshua=False,
        emergency_blocks=0,
        description="Treasury actions: all 4 agents must approve unanimously"
    ),
    DecisionType.EMERGENCY: ConsensusRule(
        decision_type=DecisionType.EMERGENCY,
        required_votes=1,
        total_agents=4,
        unanimous=False,
        requires_joshua=False,
        emergency_blocks=144,  # ~48 hours at 2-min DGB blocks
        description="Emergency: any agent may act unilaterally, must report within 144 blocks"
    ),
    DecisionType.REJECTION: ConsensusRule(
        decision_type=DecisionType.REJECTION,
        required_votes=3,
        total_agents=4,
        unanimous=False,
        requires_joshua=True,
        emergency_blocks=0,
        description="Rejection challenge: 3 of 4 agents + Joshua signature required to reject an agent"
    ),
    DecisionType.CONSTITUTIONAL: ConsensusRule(
        decision_type=DecisionType.CONSTITUTIONAL,
        required_votes=4,
        total_agents=4,
        unanimous=True,
        requires_joshua=True,
        emergency_blocks=0,
        description="Constitutional changes: unanimous + Joshua signature required"
    ),
}


def get_rule(decision_type: DecisionType) -> ConsensusRule:
    return TRINITY_RULES[decision_type]


def evaluate_vote(
    decision_type: DecisionType,
    yes_votes: int,
    no_votes: int,
    abstain_votes: int,
    joshua_signed: bool = False,
    current_block: int = 0,
    proposal_block: int = 0,
) -> ProposalStatus:
    """Evaluate whether a vote meets the consensus threshold."""
    rule = get_rule(decision_type)

    # Emergency: already acted, check if report is within window
    if decision_type == DecisionType.EMERGENCY:
        if current_block - proposal_block <= rule.emergency_blocks:
            return ProposalStatus.EXECUTED  # Emergency action taken within window
        return ProposalStatus.FAILED  # Reported too late

    # Check Joshua signature requirement
    if rule.requires_joshua and not joshua_signed:
        return ProposalStatus.FAILED

    # Check unanimous requirement
    if rule.unanimous and no_votes > 0:
        return ProposalStatus.FAILED

    # Check yes threshold
    if yes_votes >= rule.required_votes:
        return ProposalStatus.PASSED

    # Not enough yes votes
    total_voted = yes_votes + no_votes + abstain_votes
    remaining = rule.total_agents - total_voted
    if yes_votes + remaining < rule.required_votes:
        return ProposalStatus.FAILED  # Mathematically impossible to pass

    return ProposalStatus.PENDING
