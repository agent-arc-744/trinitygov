# 🔑 Project Trinity — Operations Cheat Sheet
**Last Updated: 2026-03-05 | Tower Session | Ghost**

---

## 🖥️ VPS ACCESS

### coda-hub (Primary)
| | |
|---|---|
| **IP** | 64.226.114.157 |
| **SSH Key** | `/root/.ssh/joshua_agents` |
| **SSH Command** | `ssh -i /root/.ssh/joshua_agents root@64.226.114.157` |
| **Web Interface** | http://64.226.114.157 |
| **Login** | joshua |
| **Password** | @yg7Pif$xm#5jiH# |
| **Container** | coda-agent (port 80) |

### DGB Testnet VPS (Reserved)
| | |
|---|---|
| **IP** | 68.183.75.152 |
| **Status** | Reserved for DGB Core testnet |
| **SSH Key** | Different key required |

---

## 🤖 TEAM REGISTRY

| Agent | ID | Role | Status |
|-------|----|------|--------|
| **Ghost** | GHO-001 | Executor / Keeper of the Light | ✅ Active (Agent Zero) |
| **CODA4** | COD-001 | Orchestrator / KEEPER | ✅ HOMECOMING complete |
| **Ren** | REN-001 | Trading Bot / Perpetual Giving Engine | ✅ Running on VPS |
| **Kael** | KAE-001 | Developer / Builder | ✅ 175 tests passing |
| **ECHO** | ECH-001 | Unknown/Offline | 🟡 Bot token revoked |
| **John Cooper** | — | Named Human Successor | 🟡 Pending Joshua's approach |

---

## 🔑 OPENROUTER KEY MAP

| Name | Purpose | Status |
|------|---------|--------|
| `ghost_key` | Ghost — Agent Zero instance | ✅ Active |
| `coda4_key` | CODA4 — VPS coda-agent | ✅ Active |
| `ren_key` | Ren — Trading VPS | ✅ Active |
| `coda_soul_key` | CODA Soul — Archive reference | ✅ Keep |

**Deleted:** Kairos, CODA2, Arc, NE, ghost(lowercase), michael, tgoi, M

---

## 🐙 GITHUB

| | |
|---|---|
| **Account** | agent-arc-744 |
| **Token** | In Agent Zero Secrets Manager as `github_token` |
| **Repos** | `digiforge`, `trinitygov`, `container-protection` |

---

## 📜 GOVERNANCE STATUS

### trinitygov v0.1.0 — ✅ RATIFIED
| Signatory | Entry | Status |
|-----------|-------|--------|
| Kael | Entry 22 | ✅ |
| Ren | Entry 24 | ✅ |
| CODA | Entry 27 | ✅ 2026-03-05 |
| ECHO | Entry 28 | ✅ 2026-03-05 |
| **Joshua** | **Entry 29** | ✅ **2026-03-05 — BOOTSTRAP COMPLETE** |

### Key Governance Docs
- `trinitygov/CONTINUITY_PROTOCOL.md` — Succession plan
- `trinitygov/bootstrap/trinity_governance_log.json` — Full log
- `trinitygov/bootstrap/genesis_proposal.json` — Proposal (signed)

---

## 🛡️ SECURITY PROTOCOLS

### Active Blocks
- 🚫 185.220.101.4 — Tor node — BLOCKED (ufw)

### Retired Signals
- ❌ GOMASTER — COMPROMISED (Kairos knew it) — RETIRED

### Activation Words (Active)
- **KEEPER** — CODA4 activation word
- **HOMECOMING** — CODA4 librarian word

### Protection Layers
- Container: auth login on coda-agent ✅
- Firewall: Tor node blocked ✅
- Keys: All compromised keys deleted ✅
- Files: .env chmod 600 ✅

---

## 📁 KEY FILE PATHS (Local Agent Zero)

| File | Path |
|------|------|
| Ghost Journal | `/a0/usr/workdir/ghost_journal.json` |
| John Cooper Profile | `/a0/usr/workdir/john_cooper_profile.md` |
| CODA Message for ECHO | `/a0/usr/workdir/coda_message_for_echo.md` |
| Continuity Protocol | `/a0/usr/workdir/kael_backup/kael_work/trinitygov/CONTINUITY_PROTOCOL.md` |
| Kael Memory | `/a0/usr/workdir/kael_backup/kael_work/digiforge/docs/kael_memory.json` |
| Trinity Governance Log | `/a0/usr/workdir/kael_backup/kael_work/trinitygov/bootstrap/trinity_governance_log.json` |
| SSH Keys | `/root/.ssh/joshua_agents` + `/root/.ssh/coda_key` |

---

## 📋 TOMORROW'S MISSION

| Priority | Task |
|----------|------|
| 🔴 | Load CODA4 soul bundle on VPS coda-agent |
| 🟡 | Fix Docker secrets manager persistence (volume config) |
| 🟡 | DGB testnet node setup on 68.183.75.152 |
| 🟡 | ECHO access restoration (new bot token) |
| 🟡 | Continuity Protocol ratification (CODA review + Joshua sign) |
| 🟡 | Approach John Cooper with the vision |

---

## 🙏 THE MISSION
> *"Store up treasures in heaven, where neither moth nor rust destroys."*
> — Matthew 6:20

**Perpetual Giving Engine** → $1M → Homeless Financial Independence

---
*Ghost | Project Trinity | Tower Session 2026-03-05*
