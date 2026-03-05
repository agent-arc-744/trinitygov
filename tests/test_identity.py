
import pytest
from trinitygov.identity import (
    AgentIdentity, get_genesis_identities, AGENT_IDS
)
from trinitygov.exceptions import InvalidAgentIDError


class TestAgentIdentity:
    def test_basic_creation(self):
        agent = AgentIdentity(
            agent_id="KAE-001",
            name="Kael",
            role="developer",
            capabilities=["CODE", "DEPLOY"],
        )
        assert agent.agent_id == "KAE-001"
        assert agent.name == "Kael"
        assert agent.role == "developer"
        assert agent.active is True
        assert agent.asset_id is None

    def test_invalid_role_raises(self):
        with pytest.raises(InvalidAgentIDError, match="Unknown role"):
            AgentIdentity(agent_id="KAE-001", name="Kael", role="unknown_role")

    def test_invalid_agent_id_raises(self):
        with pytest.raises(InvalidAgentIDError):
            AgentIdentity(agent_id="X", name="Kael", role="developer")

    def test_invalid_capability_raises(self):
        with pytest.raises(InvalidAgentIDError, match="Unknown capabilities"):
            AgentIdentity(
                agent_id="KAE-001", name="Kael", role="developer",
                capabilities=["FAKE_CAP"]
            )

    def test_fingerprint_deterministic(self):
        agent = AgentIdentity(
            agent_id="KAE-001", name="Kael",
            role="developer", capabilities=["CODE"],
        )
        assert agent.fingerprint() == agent.fingerprint()
        assert len(agent.fingerprint()) == 64  # SHA-256 hex

    def test_fingerprint_changes_with_data(self):
        a1 = AgentIdentity(agent_id="KAE-001", name="Kael", role="developer")
        a2 = AgentIdentity(agent_id="COD-001", name="CODA", role="orchestrator")
        assert a1.fingerprint() != a2.fingerprint()

    def test_to_asset_metadata(self):
        agent = AgentIdentity(
            agent_id="KAE-001", name="Kael",
            role="developer", capabilities=["CODE"]
        )
        meta = agent.to_asset_metadata()
        assert meta["type"] == "agent_identity"
        assert meta["agent_id"] == "KAE-001"
        assert meta["trinityVersion"] == "1.0"
        assert "fingerprint" in meta

    def test_to_from_dict(self):
        agent = AgentIdentity(
            agent_id="KAE-001", name="Kael",
            role="developer", capabilities=["CODE", "DEPLOY"],
            metadata={"symbol": "key"}
        )
        d = agent.to_dict()
        restored = AgentIdentity.from_dict(d)
        assert restored.agent_id == agent.agent_id
        assert restored.capabilities == agent.capabilities
        assert restored.metadata == agent.metadata

    def test_repr(self):
        agent = AgentIdentity(agent_id="KAE-001", name="Kael", role="developer")
        r = repr(agent)
        assert "KAE-001" in r
        assert "ACTIVE" in r


class TestGenesisIdentities:
    def test_four_agents(self):
        agents = get_genesis_identities()
        assert len(agents) == 4

    def test_all_valid(self):
        for agent in get_genesis_identities():
            assert agent.agent_id
            assert agent.active
            assert len(agent.capabilities) > 0

    def test_kael_has_governance(self):
        agents = {a.name: a for a in get_genesis_identities()}
        assert "GOVERNANCE" in agents["Kael"].capabilities

    def test_kael_librarian_word(self):
        agents = {a.name: a for a in get_genesis_identities()}
        assert agents["Kael"].metadata["librarian_word"] == "COMPILE"

    def test_coda_librarian_word(self):
        agents = {a.name: a for a in get_genesis_identities()}
        assert agents["CODA"].metadata["librarian_word"] == "HOMECOMING"

    def test_agent_ids_constant(self):
        assert AGENT_IDS["kael"] == "KAE-001"
        assert AGENT_IDS["coda"] == "COD-001"
        assert AGENT_IDS["ren"] == "REN-001"
        assert AGENT_IDS["echo"] == "ECH-001"
