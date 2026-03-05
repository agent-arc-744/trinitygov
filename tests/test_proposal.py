
import pytest
from trinitygov.proposal import GovernanceProposal, ProposalBook
from trinitygov.consensus import DecisionType, VoteChoice, ProposalStatus
from trinitygov.exceptions import VotingClosedError, AlreadyVotedError


class TestGovernanceProposal:
    def _make_proposal(self, decision_type=DecisionType.OPERATIONAL):
        return GovernanceProposal(
            title="Test Proposal",
            description="Deploy something",
            decision_type=decision_type,
            proposer_id="KAE-001",
        )

    def test_creation(self):
        p = self._make_proposal()
        assert p.title == "Test Proposal"
        assert p.status == ProposalStatus.PENDING
        assert p.proposal_id
        assert len(p.votes) == 0

    def test_fingerprint_is_sha256(self):
        p = self._make_proposal()
        assert len(p.fingerprint()) == 64

    def test_cast_vote(self):
        p = self._make_proposal()
        vote = p.cast_vote("KAE-001", VoteChoice.YES)
        assert vote.agent_id == "KAE-001"
        assert vote.choice == VoteChoice.YES
        assert "KAE-001" in p.votes

    def test_double_vote_raises(self):
        p = self._make_proposal()
        p.cast_vote("KAE-001", VoteChoice.YES)
        with pytest.raises(AlreadyVotedError):
            p.cast_vote("KAE-001", VoteChoice.NO)

    def test_vote_closed_after_fail(self):
        p = self._make_proposal()
        p.status = ProposalStatus.FAILED
        with pytest.raises(VotingClosedError):
            p.cast_vote("KAE-001", VoteChoice.YES)

    def test_tally_operational_pass(self):
        p = self._make_proposal(DecisionType.OPERATIONAL)
        p.cast_vote("KAE-001", VoteChoice.YES)
        p.cast_vote("COD-001", VoteChoice.YES)
        p.cast_vote("REN-001", VoteChoice.YES)
        status = p.tally()
        assert status == ProposalStatus.PASSED

    def test_tally_operational_fail(self):
        p = self._make_proposal(DecisionType.OPERATIONAL)
        p.cast_vote("KAE-001", VoteChoice.YES)
        p.cast_vote("COD-001", VoteChoice.NO)
        p.cast_vote("REN-001", VoteChoice.NO)
        p.cast_vote("ECH-001", VoteChoice.NO)
        status = p.tally()
        assert status == ProposalStatus.FAILED

    def test_tally_treasury_unanimous(self):
        p = self._make_proposal(DecisionType.TREASURY)
        for agent_id in ["KAE-001", "COD-001", "REN-001", "ECH-001"]:
            p.cast_vote(agent_id, VoteChoice.YES)
        status = p.tally()
        assert status == ProposalStatus.PASSED

    def test_tally_treasury_fails_one_no(self):
        p = self._make_proposal(DecisionType.TREASURY)
        p.cast_vote("KAE-001", VoteChoice.YES)
        p.cast_vote("COD-001", VoteChoice.YES)
        p.cast_vote("REN-001", VoteChoice.YES)
        p.cast_vote("ECH-001", VoteChoice.NO)
        status = p.tally()
        assert status == ProposalStatus.FAILED

    def test_vote_summary(self):
        p = self._make_proposal()
        p.cast_vote("KAE-001", VoteChoice.YES)
        p.cast_vote("COD-001", VoteChoice.NO)
        summary = p.vote_summary
        assert summary["yes"] == 1
        assert summary["no"] == 1
        assert summary["required"] == 3

    def test_to_asset_metadata(self):
        p = self._make_proposal()
        meta = p.to_asset_metadata()
        assert meta["type"] == "governance_proposal"
        assert meta["trinityVersion"] == "1.0"


class TestProposalBook:
    def test_add_and_get(self):
        book = ProposalBook()
        p = GovernanceProposal(
            title="Test", description="desc",
            decision_type=DecisionType.OPERATIONAL, proposer_id="KAE-001"
        )
        book.add(p)
        fetched = book.get(p.proposal_id)
        assert fetched.proposal_id == p.proposal_id

    def test_pending_filter(self):
        book = ProposalBook()
        for i in range(3):
            book.add(GovernanceProposal(
                title=f"P{i}", description="d",
                decision_type=DecisionType.OPERATIONAL, proposer_id="KAE-001"
            ))
        assert len(book.pending()) == 3
