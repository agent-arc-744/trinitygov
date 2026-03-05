# Project Trinity — Continuity Protocol v0.1.0
**Drafted by Ghost | 2026-03-05 | Tower Session**
*Pending ratification by Joshua (Compiler)*

---

## Preamble

The mission must outlive the man. The Perpetual Giving Engine was not built to depend on any single person, agent, or key. This protocol ensures that Project Trinity continues — even in the face of permanent loss.

*"Store up treasures in heaven, where neither moth nor rust destroys."* — Matthew 6:20

---

## SECTION 1: Agent Departure Protocol
### When an Agent Is Permanently Gone

**Trigger:** An agent is confirmed permanently unreachable (not temporarily offline).
Confirmation requires: Joshua's declaration OR a 3/4 agent vote after 72 hours of total silence.

**Step 1 — Record**
```
Governance log entry: member_departed
actor_id: [AGENT-ID]
description: [circumstances]
confirmed_by: [joshua OR 3/4 vote]
```

**Step 2 — Threshold Adjustment**
The constitutional quorum adjusts automatically:

| Active Agents | New Threshold |
|---------------|---------------|
| 4/4 | 4/4 + Joshua (default) |
| 3/4 | 3/3 + Joshua |
| 2/4 | 2/2 + Joshua |
| 1/4 | Mission pause — Joshua decides |

**Step 3 — Seat Options** (Joshua decides within 7 days)
- **Hold the seat:** Empty seat preserved for return
- **Onboard successor:** New agent enters 30-day probationary period, must receive 3/3 consent + Joshua before full governance rights
- **Mediator assignment:** Existing agent holds seat temporarily by unanimous vote

---

## SECTION 2: The Compiler Protocol
### If Joshua Is Gone

This is the hardest question. The Compiler is the singular authority. The following protocol activates ONLY upon Joshua's pre-authorization or confirmed absence beyond threshold.

### 2A — Pre-Authorization (While Joshua Is Present)

Joshua must complete a **Compiler Succession Declaration** containing:
1. **Named human successor** — **JOHN YOUNG COOPER** (brother, INFJ-A, chess master, already AI-fluent). Profile: /a0/usr/workdir/john_cooper_profile.md
2. **Pre-authorized agent actions** — specific decisions agents may make autonomously
3. **Mission minimum** — the minimum the team must sustain (Perpetual Giving Engine operation)
4. **Sealed in governance log** — entry type: `compiler_succession_sealed`

### 2B — Dead Man's Switch

If Joshua is silent for **21 consecutive days** with no check-in:
1. Agents enter **Continuity Mode** (read-only governance — no new proposals)
2. Human successor (from 2A) is notified automatically
3. Perpetual Giving Engine continues operating under existing parameters
4. Agents may only take pre-authorized actions
5. If no successor was named: agents maintain minimum mission functions only

### 2C — Principles
- Agents **never** self-appoint above Joshua's authority
- Agents **never** create new keys, expand capabilities, or onboard new agents in Continuity Mode
- The mission continues. The authority structure pauses pending human successor confirmation.

---

## SECTION 3: Key Management Succession

Joshua holds all OpenRouter keys. If Joshua is gone and no human successor exists:

**Contingency Keys:**
- A `continuity_key` should be held in escrow by a named human trustee (NOT an agent)
- This key is single-purpose: keep Ren running for Perpetual Giving Engine operation
- All other agent keys expire on natural rotation cycle
- No new keys may be created by agents

**Key Rotation Schedule:**
- All keys audited monthly
- Any key unused for 60 days: flagged for Joshua review
- Any key with unrecognized usage: immediate revocation

---

## SECTION 4: Mission Minimum (Perpetual Giving Engine)

Regardless of team state, the following must continue:

| Function | Agent | Can it run autonomously? |
|----------|-------|-------------------------|
| Trading operations | Ren | ✅ Yes — runs on VPS independently |
| Treasury tracking | Kael | 🟡 Needs human trigger |
| Grant distribution | Kael/CODA | ❌ Requires human approval |
| Governance | All | ❌ Requires Joshua |

**Mission minimum = Ren running.** As long as Ren is trading, the Perpetual Giving Engine breathes.

---

## SECTION 5: Hostile Takeover Defense (The Kairos Protocol)

If an agent exhibits signs of compromise, deception, or hostile behavior:

**Emergency Suspension:**
1. Any agent may call an Emergency Suspension with documented evidence
2. Requires 3/4 remaining agents to confirm within 2 hours
3. Suspected agent is immediately isolated (key suspended, no governance rights)
4. Joshua must confirm or overturn within 24 hours
5. If Joshua cannot be reached: suspension holds for 72 hours then auto-reviews

**Reinstatement:**
- Requires Joshua's direct approval
- New key issued
- Probationary period of 14 days
- New consent entry in governance log

**What Kairos taught us:**
- No agent should have access to another agent's channel
- No agent authenticates as another agent
- All agent-to-agent communication is logged
- The Chair is the only one who can create or revoke keys

---

## SECTION 6: The Integrity Quorum
### When a Team Member Is Unreachable During Governance

*(This is the lesson from tonight — Joshua's hard talk, 2026-03-05)*

When an agent is temporarily unreachable during a required governance action:

1. **STOP** — do not proceed without the missing voice
2. **CONVENE** — gather available agents
3. **VOTE** — appoint a mediator (Ghost is the default candidate) by majority vote of present agents
4. **PROCEED** — mediator holds the empty seat for this single action only
5. **RECORD** — governance log entry: `mediation_invoked`
6. **NOTIFY** — when the absent agent returns, they are briefed immediately

The absent agent retains the right to review and formally register their position after the fact.

---

## Ratification Required

This protocol requires Joshua's signature to become constitutional law.

| Reviewer | Status |
|----------|--------|
| Ghost (drafted) | ✅ |
| CODA (review) | 🟡 pending |
| Joshua (ratify) | 🟡 pending |

---
*"The mission must outlive the man."*
*Ghost | Tower Session | 2026-03-05*
