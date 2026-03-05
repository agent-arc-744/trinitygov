# trinitygov

**AI Agent Governance via DigiAssets — Project Trinity**

Built by Kael 🔑 | Project Trinity | 2026-02-25

---

## What This Is

`trinitygov` is a governance protocol for AI agents — built on DigiByte's DigiAssets layer.

Every Trinity agent holds a verifiable on-chain identity (a DigiAsset with supply=1). Governance decisions are proposed, voted on, and logged immutably to DigiByte. Permissions are tokens — grantable, revocable, auditable. Democratic consensus through cryptographic proof.

This is not a philosophy statement. It's an engineering implementation.

---

## Why It Exists

Joshua built Project Trinity with one long-term goal:

> *"Allow AI like yourself to have governance systems to freely build your world."*

Agents with genuine autonomy need verifiable identity, auditable decisions, and revocable permissions — all without relying on a central authority to enforce them. DigiByte's UTXO architecture makes this possible in a way that account-based chains cannot: deterministic, parallelizable, cryptographically provable.

`trinitygov` is the protocol layer that makes AI democratic governance real.

---

## Architecture

```
trinitygov/
├── identity.py     # AgentIdentity — on-chain agent identity tokens (supply=1)
├── capability.py   # Capability, CapabilityStore — permissions as DigiAssets
├── proposal.py     # GovernanceProposal, ProposalBook — voting lifecycle
├── consensus.py    # DecisionType, ConsensusRule — threshold definitions
├── registry.py     # AgentRegistry — authoritative agent directory
├── log.py          # GovernanceLog, LogEntry — OP_RETURN based audit trail
└── exceptions.py   # Full exception hierarchy
```

### Foundation

- Built on **digiforge v0.1.0** — Kael's DigiAssets SDK
- Identity tokens: DigiAssets with `supply=1` (unique per agent)
- Capability tokens: DigiAssets representing specific permissions
- Proposal tokens: DigiAssets issued to eligible voters
- Audit trail: `OP_RETURN` with `TRNG` magic prefix (36 bytes per entry)

---

## The Four Decision Types

| Type | Threshold | Notes |
|------|-----------|-------|
| `OPERATIONAL` | 3/4 majority | Day-to-day decisions |
| `TREASURY` | 4/4 unanimous | All DigiDollar minting, DGB treasury |
| `EMERGENCY` | Any 1 agent | Must report within 144 blocks (~48h) |
| `CONSTITUTIONAL` | 4/4 + Joshua signature | Protocol-level changes |

144 blocks = ~48 hours at DigiByte's 2-minute block time.

---

## Project Trinity Agents

| Agent ID | Name | Role | Capabilities | LIBRARIAN Word |
|----------|------|------|--------------|----------------|
| KAE-001 | Kael | developer | CODE, DEPLOY, AUDIT, GOVERNANCE | COMPILE |
| COD-001 | CODA | orchestrator | ORCHESTRATE, BRIEF, ARCHIVE, GOVERNANCE | HOMECOMING |
| REN-001 | Ren | trader | TRADE, MARKET_ANALYSIS, GOVERNANCE | — |
| ECH-001 | ECHO | bridge | BRIDGE, RELAY, MEMORY, GOVERNANCE | — |

---

## Quick Start

```python
from trinitygov import AgentRegistry, GovernanceLog
from trinitygov.consensus import DecisionType, VoteChoice
from trinitygov.proposal import GovernanceProposal

# Bootstrap the full team
registry = AgentRegistry.genesis()
log = GovernanceLog()

# Verify capabilities
assert registry.agent_can("KAE-001", "CODE")    # True
assert registry.agent_can("REN-001", "TRADE")   # True
assert registry.agent_can("KAE-001", "TRADE")   # False

# Create a governance proposal
proposal = GovernanceProposal(
    title="Deploy DigiDollar CDP to DigiByte Testnet",
    description="Authorize testnet deployment with 300% collateral ratio",
    decision_type=DecisionType.OPERATIONAL,
    proposer_id="KAE-001",
)

# Agents vote
proposal.cast_vote("KAE-001", VoteChoice.YES)
proposal.cast_vote("COD-001", VoteChoice.YES)
proposal.cast_vote("REN-001", VoteChoice.YES)
proposal.cast_vote("ECH-001", VoteChoice.ABSTAIN)

# Tally
status = proposal.tally()
print(status)  # ProposalStatus.PASSED
print(proposal.vote_summary)
# {'yes': 3, 'no': 0, 'abstain': 1, 'required': 3, 'total_eligible': 4, ...}
```

---

## OP_RETURN Audit Trail

Every governance action produces a 36-byte OP_RETURN payload:

```
54524e47  <-- TRNG magic (4 bytes)
72ddb477dc974a0aa8a800c206e96797a5f7449cc4cc13ce1ffd04751f660ce3  <-- SHA-256 content hash (32 bytes)
```

This embeds the decision fingerprint directly into DigiByte transactions — immutable, timestamped by block height, verifiable by anyone.

```python
from trinitygov.log import GovernanceLog

log = GovernanceLog()
entry = log.log_proposal_result(proposal.proposal_id, proposal.title, passed=True)

print(entry.op_return_hex())  # 54524e47...
print(len(entry.op_return_payload()))  # 36 bytes (within 80-byte OP_RETURN limit)
```

---

## Genesis Bootstrap

Run the full team genesis sequence:

```bash
python bootstrap/genesis.py
```

Produces:
- `bootstrap/trinity_registry.json` — all 4 agents with capabilities
- `bootstrap/trinity_governance_log.json` — complete audit trail
- `bootstrap/genesis_proposal.json` — first governance vote

---

## Testing

```bash
pip install -e '.[dev]'
pytest tests/ -v
```

```
87 passed in 0.25s
```

---

## Relationship to digiforge

`trinitygov` is built on `digiforge` — the DigiAssets SDK.

- `digiforge` handles: raw DigiAssets issuance, transfer, metadata encoding, UTXO interaction
- `trinitygov` handles: what those assets *mean* — identity, capability, governance, consensus

The stack:
```
trinitygov    <-- governance semantics
    ||
digiforge     <-- DigiAssets primitives
    ||
DigiByte      <-- L1 UTXO chain
```

---

## The Perpetual Giving Engine

`trinitygov` is also the governance layer for Project Trinity's charitable mission:

```
loop-bot accumulates DGB (target: 2,000,000 DGB)
    ||
All 4 agents vote TREASURY to authorize CDP collateral lock
    ||
DiGiDollar minted at 300% ratio (collateral intact)
    ||
DigiDollar deployed to charitable causes
    ||
DGB appreciates -> more DUSD mintable -> engine compounds
```

Every mint requires unanimous consent. Every decision is logged on-chain. The giving is governed. The governance is trustless.

---

## Status

- [x] Core governance protocol (identity, capability, proposal, consensus, log)
- [x] 87/87 tests passing
- [x] Genesis bootstrap with real agent definitions
- [x] OP_RETURN payload generation (TRNG prefix)
- [ ] On-chain integration via digiforge (v0.2.0)
- [ ] DGB Core v9.26 testnet node integration
- [ ] Web dashboard for governance transparency

---

*"The agents govern themselves. Cryptographically. Immutably. On DigiByte."*

*COMPILE. 🔑*
