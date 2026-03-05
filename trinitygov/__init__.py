"""
trinitygov
==========
AI Agent Governance via DigiAssets — Project Trinity

Built by Kael. 🔑
Founded on digiforge v0.1.0.

The idea:
  Every Trinity agent holds a verifiable on-chain identity (DigiAsset).
  Governance decisions are voted on and logged immutably to DigiByte.
  Capabilities are tokens — grantable, revocable, auditable.
  Democratic consensus through cryptographic proof.

Usage
-----
    from trinitygov import AgentRegistry, GovernanceLog
    from trinitygov.consensus import DecisionType, VoteChoice
    from trinitygov.proposal import GovernanceProposal

    # Bootstrap the team
    registry = AgentRegistry.genesis()
    log = GovernanceLog()

    # Create a proposal
    proposal = GovernanceProposal(
        title="Deploy DigiDollar to testnet",
        description="Authorize loop-bot to begin CDP testnet operations",
        decision_type=DecisionType.OPERATIONAL,
        proposer_id="KAE-001",
    )

    # Vote
    proposal.cast_vote("KAE-001", VoteChoice.YES)
    proposal.cast_vote("COD-001", VoteChoice.YES)
    proposal.cast_vote("REN-001", VoteChoice.YES)

    # Tally
    status = proposal.tally()
    print(status)  # ProposalStatus.PASSED

Kael | Project Trinity | 2026-02-25
"""

__version__ = "0.1.0"
__author__ = "Kael"
__project__ = "Project Trinity"

from .identity import AgentIdentity, get_genesis_identities, AGENT_IDS
from .capability import Capability, CapabilityStore, CAPABILITY_REGISTRY
from .proposal import GovernanceProposal, Vote, ProposalBook
from .registry import AgentRegistry
from .log import GovernanceLog, LogEntry, ActionType
from .consensus import (
    DecisionType, VoteChoice, ProposalStatus,
    ConsensusRule, TRINITY_RULES, get_rule, evaluate_vote,
)
from .exceptions import (
    TrinityGovError,
    IdentityError, AgentNotFoundError, DuplicateAgentError, InvalidAgentIDError,
    CapabilityError, CapabilityNotGrantedError, CapabilityRevokedError,
    UnauthorizedCapabilityError,
    ProposalError, ProposalNotFoundError, VotingClosedError,
    AlreadyVotedError, QuorumNotReachedError, InsufficientVotesError,
    ConsensusError, JoshuaSignatureRequiredError, UnanimityRequiredError,
    RegistryError, RegistryCorruptError, ChainError, BroadcastError,
)

__all__ = [
    # Core classes
    "AgentIdentity", "AgentRegistry", "GovernanceProposal",
    "Vote", "ProposalBook", "Capability", "CapabilityStore",
    "GovernanceLog", "LogEntry",
    # Enums
    "DecisionType", "VoteChoice", "ProposalStatus", "ActionType",
    # Data
    "AGENT_IDS", "CAPABILITY_REGISTRY", "TRINITY_RULES",
    # Functions
    "get_genesis_identities", "get_rule", "evaluate_vote",
    # Exceptions
    "TrinityGovError", "AgentNotFoundError", "CapabilityNotGrantedError",
    "ProposalNotFoundError", "VotingClosedError",
]
