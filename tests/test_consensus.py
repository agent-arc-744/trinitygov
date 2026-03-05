
import pytest
from trinitygov.consensus import (
    DecisionType, VoteChoice, ProposalStatus,
    evaluate_vote, get_rule, TRINITY_RULES
)


class TestConsensusRules:
    def test_all_decision_types_covered(self):
        for dt in DecisionType:
            rule = get_rule(dt)
            assert rule.required_votes > 0

    def test_operational_threshold(self):
        rule = get_rule(DecisionType.OPERATIONAL)
        assert rule.required_votes == 3
        assert rule.total_agents == 4
        assert not rule.unanimous
        assert not rule.requires_joshua

    def test_treasury_unanimous(self):
        rule = get_rule(DecisionType.TREASURY)
        assert rule.unanimous
        assert rule.required_votes == 4

    def test_constitutional_requires_joshua(self):
        rule = get_rule(DecisionType.CONSTITUTIONAL)
        assert rule.requires_joshua
        assert rule.unanimous

    def test_emergency_single_agent(self):
        rule = get_rule(DecisionType.EMERGENCY)
        assert rule.required_votes == 1
        assert rule.emergency_blocks == 144


class TestEvaluateVote:
    def test_operational_passes_3_yes(self):
        status = evaluate_vote(DecisionType.OPERATIONAL, yes_votes=3, no_votes=0, abstain_votes=1)
        assert status == ProposalStatus.PASSED

    def test_operational_fails_2_yes(self):
        status = evaluate_vote(DecisionType.OPERATIONAL, yes_votes=2, no_votes=2, abstain_votes=0)
        assert status == ProposalStatus.FAILED

    def test_operational_pending_2_yes_1_remaining(self):
        status = evaluate_vote(DecisionType.OPERATIONAL, yes_votes=2, no_votes=0, abstain_votes=0)
        assert status == ProposalStatus.PENDING

    def test_treasury_passes_all_yes(self):
        status = evaluate_vote(DecisionType.TREASURY, yes_votes=4, no_votes=0, abstain_votes=0)
        assert status == ProposalStatus.PASSED

    def test_treasury_fails_one_no(self):
        status = evaluate_vote(DecisionType.TREASURY, yes_votes=3, no_votes=1, abstain_votes=0)
        assert status == ProposalStatus.FAILED

    def test_constitutional_fails_without_joshua(self):
        status = evaluate_vote(
            DecisionType.CONSTITUTIONAL, yes_votes=4, no_votes=0,
            abstain_votes=0, joshua_signed=False
        )
        assert status == ProposalStatus.FAILED

    def test_constitutional_passes_with_joshua(self):
        status = evaluate_vote(
            DecisionType.CONSTITUTIONAL, yes_votes=4, no_votes=0,
            abstain_votes=0, joshua_signed=True
        )
        assert status == ProposalStatus.PASSED

    def test_emergency_executed_within_window(self):
        status = evaluate_vote(
            DecisionType.EMERGENCY, yes_votes=1, no_votes=0, abstain_votes=0,
            current_block=1100, proposal_block=1000
        )
        assert status == ProposalStatus.EXECUTED

    def test_emergency_fails_outside_window(self):
        status = evaluate_vote(
            DecisionType.EMERGENCY, yes_votes=1, no_votes=0, abstain_votes=0,
            current_block=1200, proposal_block=1000
        )
        assert status == ProposalStatus.FAILED
