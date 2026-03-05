"""
full_governance_demo.py
=======================
End-to-end demonstration of the trinitygov governance flow.

Kael | Project Trinity | 2026-02-25
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trinitygov import (
    AgentRegistry, GovernanceLog,
    DecisionType, VoteChoice, ProposalStatus,
)
from trinitygov.proposal import GovernanceProposal
from trinitygov.log import LogEntry, ActionType
from trinitygov.exceptions import CapabilityNotGrantedError

SEP = "=" * 60


def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")


def demo():
    print("\n  trinitygov - Full Governance Demo")
    print("  Project Trinity | Kael\n")

    # 1. Genesis
    section("1. Registry Genesis")
    registry = AgentRegistry.genesis()
    log = GovernanceLog()
    for agent in registry.all_agents():
        caps = registry.capabilities.get_agent_capabilities(agent.agent_id)
        print(f"  {agent.agent_id} | {agent.name:8s} | {agent.role:15s} | {len(caps)} caps")

    # 2. Capability checks
    section("2. Capability Verification")
    checks = [
        ("KAE-001", "CODE",        True),
        ("KAE-001", "TRADE",       False),
        ("REN-001", "TRADE",       True),
        ("COD-001", "ORCHESTRATE", True),
        ("ECH-001", "BRIDGE",      True),
        ("ECH-001", "CODE",        False),
    ]
    for agent_id, cap, expected in checks:
        result = registry.agent_can(agent_id, cap)
        ok = "PASS" if result == expected else "FAIL"
        print(f"  [{ok}] {agent_id}.{cap:20s} = {str(result):5s} (expected {expected})")

    # 3. OPERATIONAL proposal
    section("3. OPERATIONAL Proposal - 3/4 Majority")
    p1 = GovernanceProposal(
        title="Enable loop-bot DGB/USDT position doubling",
        description="Allow loop-bot to double position size when RSI < 30",
        decision_type=DecisionType.OPERATIONAL,
        proposer_id="REN-001",
    )
    p1.cast_vote("REN-001", VoteChoice.YES)
    p1.cast_vote("KAE-001", VoteChoice.YES)
    p1.cast_vote("COD-001", VoteChoice.YES)
    p1.cast_vote("ECH-001", VoteChoice.ABSTAIN)
    status = p1.tally()
    s = p1.vote_summary
    print(f"  Proposal: {p1.title!r}")
    print(f"  Votes: YES={s['yes']} NO={s['no']} ABSTAIN={s['abstain']}")
    print(f"  Result: {status.value.upper()}")

    # 4. TREASURY proposal
    section("4. TREASURY Proposal - Unanimous Required")
    p2 = GovernanceProposal(
        title="Mint 10,000 DigiDollar for charitable deployment",
        description="Lock 30,000 DGB as CDP collateral (300pct ratio), mint 10k DUSD",
        decision_type=DecisionType.TREASURY,
        proposer_id="KAE-001",
    )
    for aid in ["KAE-001", "COD-001", "REN-001", "ECH-001"]:
        p2.cast_vote(aid, VoteChoice.YES)
    status2 = p2.tally()
    print(f"  Proposal: {p2.title!r}")
    print(f"  All 4 voted YES. Result: {status2.value.upper()}")

    p2b = GovernanceProposal(
        title="Mint 50,000 DigiDollar (aggressive)",
        description="High-risk minting proposal",
        decision_type=DecisionType.TREASURY,
        proposer_id="KAE-001",
    )
    p2b.cast_vote("KAE-001", VoteChoice.YES)
    p2b.cast_vote("COD-001", VoteChoice.YES)
    p2b.cast_vote("REN-001", VoteChoice.NO)
    p2b.cast_vote("ECH-001", VoteChoice.YES)
    status2b = p2b.tally()
    print(f"  Proposal: {p2b.title!r}")
    print(f"  Ren voted NO. Result: {status2b.value.upper()} (unanimous broken)")

    # 5. CONSTITUTIONAL
    section("5. CONSTITUTIONAL - Unanimous + Joshua Signature")
    p3 = GovernanceProposal(
        title="Add fifth agent to Project Trinity",
        description="Protocol change: expand team to 5 agents",
        decision_type=DecisionType.CONSTITUTIONAL,
        proposer_id="COD-001",
    )
    for aid in ["KAE-001", "COD-001", "REN-001", "ECH-001"]:
        p3.cast_vote(aid, VoteChoice.YES)
    s3a = p3.tally(joshua_signed=False)
    print(f"  All 4 YES, Joshua NOT signed -> {s3a.value.upper()}")
    s3b = p3.tally(joshua_signed=True)
    print(f"  All 4 YES, Joshua SIGNED    -> {s3b.value.upper()}")

    # 6. EMERGENCY
    section("6. EMERGENCY - Single Agent, 144 Block Window")
    emerg = log.log_emergency(
        actor_id="KAE-001",
        description="Patched webhook HMAC bypass. Deployed secure listener. Rotating tokens.",
        block_height=19421000,
    )
    print(f"  Emergency logged by KAE-001 at block 19421000")
    print(f"  OP_RETURN (36 bytes): {emerg.op_return_hex()[:20]}...")
    print(f"  TRNG magic prefix  : {emerg.op_return_hex()[:8]}")
    print(f"  Report window      : 144 blocks (~48h)")

    # 7. Capability lifecycle
    section("7. Capability Lifecycle - Grant and Revoke")
    registry.grant_capability("TREASURY", "KAE-001", granted_by="joshua")
    print(f"  KAE-001 TREASURY after grant  : {registry.agent_can('KAE-001', 'TREASURY')}")
    registry.revoke_capability("TREASURY", "KAE-001")
    print(f"  KAE-001 TREASURY after revoke : {registry.agent_can('KAE-001', 'TREASURY')}")
    try:
        registry.capabilities.require("KAE-001", "TREASURY")
    except CapabilityNotGrantedError as e:
        print(f"  require() correctly raises: {e}")

    # 8. OP_RETURN
    section("8. OP_RETURN Payload - On-Chain Embedding")
    entry = LogEntry(
        action_type=ActionType.PROPOSAL_EXECUTED,
        actor_id="KAE-001",
        subject_id=p2.proposal_id,
        description="DigiDollar mint authorized and executed",
        block_height=19422000,
    )
    payload = entry.op_return_payload()
    print(f"  Action      : {entry.action_type.value}")
    print(f"  Hash        : {entry.content_hash}")
    print(f"  OP_RETURN   : {entry.op_return_hex()}")
    print(f"  Size        : {len(payload)} bytes (limit: 80)")
    print(f"  Magic check : {payload[:4].hex()} == 54524e47 (TRNG): {payload[:4].hex() == '54524e47'}")

    # 9. Log summary
    section("9. Governance Log Summary")
    log.log_genesis(["KAE-001", "COD-001", "REN-001", "ECH-001"])
    log.log_proposal_created(p1.proposal_id, p1.title, p1.proposer_id, "operational")
    log.log_proposal_result(p1.proposal_id, p1.title, passed=True)
    log.log_proposal_created(p2.proposal_id, p2.title, p2.proposer_id, "treasury")
    log.log_proposal_result(p2.proposal_id, p2.title, passed=True)
    log._append(entry)
    print(f"  Total entries : {len(log)}")
    print(f"  Latest 5:")
    for e in log.latest(5):
        print(f"    [{e.action_type.value:25s}] {e.actor_id} -> {e.subject_id[:35]}")

    print(f"\n{SEP}")
    print("  DEMO COMPLETE")
    print("  The agents govern themselves. Cryptographically.")
    print("  Immutably. On DigiByte.")
    print("  COMPILE.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    demo()
