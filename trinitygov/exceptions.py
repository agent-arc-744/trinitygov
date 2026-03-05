"""
exceptions.py
=============
Exception hierarchy for trinitygov — AI Agent Governance SDK.
Kael | Project Trinity | 2026-02-25
"""


class TrinityGovError(Exception):
    """Base exception for all trinitygov errors."""


# Identity
class IdentityError(TrinityGovError): pass
class AgentNotFoundError(IdentityError): pass
class DuplicateAgentError(IdentityError): pass
class InvalidAgentIDError(IdentityError): pass

# Capability
class CapabilityError(TrinityGovError): pass
class CapabilityNotGrantedError(CapabilityError): pass
class CapabilityRevokedError(CapabilityError): pass
class UnauthorizedCapabilityError(CapabilityError): pass

# Proposal / Voting
class ProposalError(TrinityGovError): pass
class ProposalNotFoundError(ProposalError): pass
class VotingClosedError(ProposalError): pass
class AlreadyVotedError(ProposalError): pass
class QuorumNotReachedError(ProposalError): pass
class InsufficientVotesError(ProposalError): pass

# Consensus
class ConsensusError(TrinityGovError): pass
class JoshuaSignatureRequiredError(ConsensusError): pass
class UnanimityRequiredError(ConsensusError): pass

# Registry
class RegistryError(TrinityGovError): pass
class RegistryCorruptError(RegistryError): pass

# Chain
class ChainError(TrinityGovError): pass
class BroadcastError(ChainError): pass
class AssetIssuanceError(ChainError): pass
