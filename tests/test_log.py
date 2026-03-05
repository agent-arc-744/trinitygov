
import pytest
from trinitygov.log import GovernanceLog, LogEntry, ActionType, TRINITY_MAGIC


class TestLogEntry:
    def test_content_hash_generated(self):
        entry = LogEntry(
            action_type=ActionType.REGISTRY_GENESIS,
            actor_id="kael",
            subject_id="trinity-registry",
            description="Genesis",
        )
        assert len(entry.content_hash) == 64

    def test_op_return_payload_length(self):
        entry = LogEntry(
            action_type=ActionType.IDENTITY_ISSUED,
            actor_id="joshua",
            subject_id="KAE-001",
            description="Issued identity",
        )
        payload = entry.op_return_payload()
        assert len(payload) == 36  # 4 magic + 32 hash
        assert payload[:4] == TRINITY_MAGIC

    def test_op_return_hex_is_72_chars(self):
        entry = LogEntry(
            action_type=ActionType.VOTE_CAST,
            actor_id="KAE-001",
            subject_id="proposal-001",
            description="Voted YES",
        )
        assert len(entry.op_return_hex()) == 72  # 36 bytes * 2

    def test_magic_prefix_in_hex(self):
        entry = LogEntry(
            action_type=ActionType.PROPOSAL_CREATED,
            actor_id="KAE-001",
            subject_id="proposal-001",
            description="Created",
        )
        assert entry.op_return_hex().startswith("54524e47")  # TRNG


class TestGovernanceLog:
    def setup_method(self):
        self.log = GovernanceLog()

    def test_starts_empty(self):
        assert len(self.log) == 0

    def test_log_genesis(self):
        entry = self.log.log_genesis(["KAE-001", "COD-001", "REN-001", "ECH-001"])
        assert entry.action_type == ActionType.REGISTRY_GENESIS
        assert len(self.log) == 1

    def test_log_identity_issued(self):
        entry = self.log.log_identity_issued("KAE-001", "ASSET123", txid="txabc")
        assert entry.action_type == ActionType.IDENTITY_ISSUED
        assert entry.metadata["asset_id"] == "ASSET123"

    def test_log_capability_granted(self):
        entry = self.log.log_capability_granted("KAE-001", "CODE")
        assert entry.action_type == ActionType.CAPABILITY_GRANTED
        assert entry.metadata["capability_id"] == "CODE"

    def test_log_vote(self):
        entry = self.log.log_vote("proposal-001", "KAE-001", "yes")
        assert entry.action_type == ActionType.VOTE_CAST
        assert entry.actor_id == "KAE-001"

    def test_log_proposal_result_passed(self):
        entry = self.log.log_proposal_result("p-001", "Deploy test", passed=True)
        assert entry.action_type == ActionType.PROPOSAL_PASSED

    def test_log_proposal_result_failed(self):
        entry = self.log.log_proposal_result("p-001", "Deploy test", passed=False)
        assert entry.action_type == ActionType.PROPOSAL_FAILED

    def test_log_emergency(self):
        entry = self.log.log_emergency("KAE-001", "Critical patch", block_height=5000)
        assert entry.action_type == ActionType.EMERGENCY_ACTION
        assert entry.block_height == 5000

    def test_by_actor(self):
        self.log.log_vote("p-001", "KAE-001", "yes")
        self.log.log_vote("p-001", "COD-001", "yes")
        self.log.log_vote("p-001", "KAE-001", "yes")
        entries = self.log.by_actor("KAE-001")
        assert len(entries) == 2

    def test_by_action(self):
        self.log.log_genesis(["KAE-001"])
        self.log.log_vote("p-001", "KAE-001", "yes")
        votes = self.log.by_action(ActionType.VOTE_CAST)
        assert len(votes) == 1

    def test_latest(self):
        for i in range(15):
            self.log.log_vote(f"p-{i:03d}", "KAE-001", "yes")
        latest = self.log.latest(5)
        assert len(latest) == 5
        assert latest[-1].subject_id == "p-014"

    def test_save_and_repr(self, tmp_path):
        self.log.log_genesis(["KAE-001"])
        path = tmp_path / "test_log.json"
        self.log.save(str(path))
        assert path.exists()
        assert "GovernanceLog" in repr(self.log)
