
import json
import tempfile
from pathlib import Path
import pytest
from trinitygov.registry import AgentRegistry
from trinitygov.identity import AgentIdentity
from trinitygov.exceptions import AgentNotFoundError, DuplicateAgentError


class TestAgentRegistry:
    def _make_agent(self, agent_id="KAE-001", name="Kael", role="developer"):
        return AgentIdentity(agent_id=agent_id, name=name, role=role)

    def test_register_and_get(self):
        reg = AgentRegistry()
        agent = self._make_agent()
        reg.register(agent)
        fetched = reg.get("KAE-001")
        assert fetched.name == "Kael"

    def test_duplicate_raises(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        with pytest.raises(DuplicateAgentError):
            reg.register(self._make_agent())

    def test_overwrite_allowed(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        agent2 = AgentIdentity(agent_id="KAE-001", name="Kael-Updated", role="developer")
        reg.register(agent2, overwrite=True)
        assert reg.get("KAE-001").name == "Kael-Updated"

    def test_get_missing_raises(self):
        reg = AgentRegistry()
        with pytest.raises(AgentNotFoundError):
            reg.get("NOBODY")

    def test_contains(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        assert "KAE-001" in reg
        assert "NOBODY" not in reg

    def test_activate_deactivate(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        reg.deactivate("KAE-001")
        assert not reg.get("KAE-001").active
        reg.activate("KAE-001")
        assert reg.get("KAE-001").active

    def test_active_agents(self):
        reg = AgentRegistry()
        reg.register(self._make_agent("KAE-001", "Kael", "developer"))
        reg.register(self._make_agent("COD-001", "CODA", "orchestrator"))
        reg.deactivate("COD-001")
        active = reg.active_agents()
        assert len(active) == 1
        assert active[0].agent_id == "KAE-001"

    def test_grant_capability(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        reg.grant_capability("CODE", "KAE-001", "joshua")
        assert reg.agent_can("KAE-001", "CODE")

    def test_revoke_capability(self):
        reg = AgentRegistry()
        reg.register(self._make_agent())
        reg.grant_capability("CODE", "KAE-001", "joshua")
        reg.revoke_capability("CODE", "KAE-001")
        assert not reg.agent_can("KAE-001", "CODE")

    def test_genesis(self):
        reg = AgentRegistry.genesis()
        assert len(reg) == 4
        assert "KAE-001" in reg
        assert "COD-001" in reg
        assert "REN-001" in reg
        assert "ECH-001" in reg

    def test_genesis_capabilities_granted(self):
        reg = AgentRegistry.genesis()
        assert reg.agent_can("KAE-001", "CODE")
        assert reg.agent_can("REN-001", "TRADE")
        assert reg.agent_can("COD-001", "ORCHESTRATE")
        assert reg.agent_can("ECH-001", "BRIDGE")
        assert reg.agent_can("KAE-001", "GOVERNANCE")

    def test_save_and_load(self):
        reg = AgentRegistry.genesis()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        reg.save(path)
        reg2 = AgentRegistry.load(path)
        assert len(reg2) == 4
        assert "KAE-001" in reg2
        Path(path).unlink()

    def test_by_role(self):
        reg = AgentRegistry.genesis()
        traders = reg.by_role("trader")
        assert len(traders) == 1
        assert traders[0].agent_id == "REN-001"
