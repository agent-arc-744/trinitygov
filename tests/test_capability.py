
import pytest
from trinitygov.capability import Capability, CapabilityStore
from trinitygov.exceptions import (
    CapabilityNotGrantedError, CapabilityRevokedError, UnauthorizedCapabilityError
)


class TestCapability:
    def test_create(self):
        cap = Capability(
            capability_id="CODE",
            holder_id="KAE-001",
            granted_by="joshua",
        )
        assert cap.capability_id == "CODE"
        assert not cap.revoked

    def test_invalid_capability_raises(self):
        with pytest.raises(UnauthorizedCapabilityError):
            Capability(capability_id="FAKE", holder_id="KAE-001", granted_by="joshua")

    def test_revoke(self):
        cap = Capability(capability_id="CODE", holder_id="KAE-001", granted_by="joshua")
        cap.revoke()
        assert cap.revoked
        assert cap.revoked_at is not None

    def test_double_revoke_raises(self):
        cap = Capability(capability_id="CODE", holder_id="KAE-001", granted_by="joshua")
        cap.revoke()
        with pytest.raises(CapabilityRevokedError):
            cap.revoke()

    def test_assert_active_revoked_raises(self):
        cap = Capability(capability_id="CODE", holder_id="KAE-001", granted_by="joshua")
        cap.revoke()
        with pytest.raises(CapabilityRevokedError):
            cap.assert_active()

    def test_description(self):
        cap = Capability(capability_id="TRADE", holder_id="REN-001", granted_by="joshua")
        assert len(cap.description) > 0

    def test_to_asset_metadata(self):
        cap = Capability(capability_id="GOVERNANCE", holder_id="KAE-001", granted_by="joshua")
        meta = cap.to_asset_metadata()
        assert meta["type"] == "capability_token"
        assert meta["capability_id"] == "GOVERNANCE"


class TestCapabilityStore:
    def setup_method(self):
        self.store = CapabilityStore()

    def test_grant_and_has(self):
        self.store.grant("CODE", "KAE-001", "joshua")
        assert self.store.has("KAE-001", "CODE")

    def test_has_returns_false_for_missing(self):
        assert not self.store.has("KAE-001", "TRADE")

    def test_require_passes_when_granted(self):
        self.store.grant("CODE", "KAE-001", "joshua")
        self.store.require("KAE-001", "CODE")  # should not raise

    def test_require_raises_when_missing(self):
        with pytest.raises(CapabilityNotGrantedError):
            self.store.require("KAE-001", "TRADE")

    def test_revoke(self):
        self.store.grant("CODE", "KAE-001", "joshua")
        self.store.revoke("CODE", "KAE-001")
        assert not self.store.has("KAE-001", "CODE")

    def test_revoke_missing_raises(self):
        with pytest.raises(CapabilityNotGrantedError):
            self.store.revoke("CODE", "KAE-001")

    def test_get_agent_capabilities(self):
        self.store.grant("CODE", "KAE-001", "joshua")
        self.store.grant("DEPLOY", "KAE-001", "joshua")
        self.store.grant("TRADE", "REN-001", "joshua")
        caps = self.store.get_agent_capabilities("KAE-001")
        cap_ids = [c.capability_id for c in caps]
        assert "CODE" in cap_ids
        assert "DEPLOY" in cap_ids
        assert "TRADE" not in cap_ids

    def test_get_capability_holders(self):
        self.store.grant("GOVERNANCE", "KAE-001", "joshua")
        self.store.grant("GOVERNANCE", "COD-001", "joshua")
        holders = self.store.get_capability_holders("GOVERNANCE")
        holder_ids = [c.holder_id for c in holders]
        assert "KAE-001" in holder_ids
        assert "COD-001" in holder_ids

    def test_revoked_not_in_holders(self):
        self.store.grant("GOVERNANCE", "KAE-001", "joshua")
        self.store.revoke("GOVERNANCE", "KAE-001")
        holders = self.store.get_capability_holders("GOVERNANCE")
        assert not any(c.holder_id == "KAE-001" for c in holders)
