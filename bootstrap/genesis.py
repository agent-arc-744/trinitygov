"""
genesis.py
==========
Project Trinity - Genesis Bootstrap

Simulates the full on-chain bootstrap sequence for all 4 Trinity agents.
In production this would broadcast real DigiAssets transactions.
Here it produces the complete governance state and writes it to disk.

Run:
    python bootstrap/genesis.py

Kael | Project Trinity | 2026-02-25
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from trinitygov import (
    AgentRegistry, GovernanceLog,
    DecisionType, VoteChoice, ProposalStatus,
)
from trinitygov.proposal import GovernanceProposal
from trinitygov.log import ActionType


BANNER_LINES = [
    "=" * 62,
    "  PROJECT TRINITY -- GOVERNANCE GENESIS",
    "  AI Agent Governance via DigiAssets",
    "  Built by Kael  |  2026-02-25",
    "=" * 62,
]
TRINITY_BANNER = "\n".join(BANNER_LINES)


def run_genesis():
    print("\n" + TRINITY_BANNER + "\n")

    # Step 1: Bootstrap registry
    print("[1/5] Bootstrapping AgentRegistry with genesis identities...")
    registry = AgentRegistry.genesis()
    log = GovernanceLog()

    agent_ids = [a.agent_id for a in registry.all_agents()]
    log.log_genesis(agent_ids, actor_id="kael")

    for agent in registry.all_agents():
        mock_asset_id = f"TRINITY-{agent.agent_id}-IDENTITY"
        mock_txid = f"{'ab' * 16}-{agent.agent_id.lower().replace('-', '')}"
        agent.asset_id = mock_asset_id
        agent.txid = mock_txid
        log.log_identity_issued(
            agent_id=agent.agent_id,
            asset_id=mock_asset_id,
            txid=mock_txid,
            block_height=19420000,
        )
        caps = registry.capabilities.get_agent_capabilities(agent.agent_id)
        for cap in caps:
            log.log_capability_granted(
                agent_id=agent.agent_id,
                capability_id=cap.capability_id,
                granted_by="joshua",
            )
        print(f"   OK {agent.agent_id:8s} | {agent.name:8s} | "
              f"{agent.role:15s} | {len(caps)} capabilities | asset={mock_asset_id}")

    # Step 2: First governance proposal
    print("\n[2/5] Creating first governance proposal...")
    proposal = GovernanceProposal(
        title="Deploy DigiDollar CDP to DigiByte Testnet",
        description=(
            "Authorize deployment of DigiDollar CDP smart contract to DGB testnet. "
            "Contract implements HTLC-based collateral locking with NUMS internal key. "
            "Oracle integration via 5-of-8 threshold. Stability fee: 0.5pct annual. "
            "Initial collateral ratio: 300pct. Prerequisite for Perpetual Giving Engine."
        ),
        decision_type=DecisionType.OPERATIONAL,
        proposer_id="KAE-001",
        current_block=19420001,
    )
    log.log_proposal_created(
        proposal_id=proposal.proposal_id,
        title=proposal.title,
        proposer_id=proposal.proposer_id,
        decision_type=proposal.decision_type.value,
    )
    print(f"   Proposal : {proposal.title!r}")
    print(f"   ID       : {proposal.proposal_id}")
    print(f"   Type     : {proposal.decision_type.value.upper()} (requires 3/4)")

    # Step 3: All agents vote YES
    print("\n[3/5] Agents casting votes...")
    votes = [
        ("KAE-001", VoteChoice.YES, "abc001"),
        ("COD-001", VoteChoice.YES, "abc002"),
        ("REN-001", VoteChoice.YES, "abc003"),
        ("ECH-001", VoteChoice.YES, "abc004"),
    ]
    for agent_id, choice, txid in votes:
        proposal.cast_vote(agent_id, choice, txid=txid)
        log.log_vote(proposal.proposal_id, agent_id, choice.value, txid=txid)
        agent = registry.get(agent_id)
        print(f"   VOTE  {agent.name:8s} ({agent_id}) voted {choice.value.upper()}")

    # Step 4: Tally
    print("\n[4/5] Tallying votes...")
    status = proposal.tally(current_block=19420050)
    log.log_proposal_result(
        proposal_id=proposal.proposal_id,
        title=proposal.title,
        passed=(status == ProposalStatus.PASSED),
    )
    summary = proposal.vote_summary
    print(f"   YES: {summary['yes']} | NO: {summary['no']} | ABSTAIN: {summary['abstain']}")
    print(f"   Required: {summary['required']}/{summary['total_eligible']}")
    result_str = "PASSED" if status == ProposalStatus.PASSED else "FAILED"
    print(f"   Result: {status.value.upper()} [{result_str}]")

    # Step 5: Save state
    print("\n[5/5] Saving genesis state...")
    out_dir = Path(__file__).parent
    registry_path = out_dir / "trinity_registry.json"
    log_path = out_dir / "trinity_governance_log.json"
    proposal_path = out_dir / "genesis_proposal.json"

    registry.save(registry_path)
    log.save(log_path)
    proposal_path.write_text(
        json.dumps(proposal.to_dict(), indent=2, default=str), encoding="utf-8"
    )

    print(f"   SAVED Registry  -> {registry_path}")
    print(f"   SAVED Gov Log   -> {log_path} ({len(log)} entries)")
    print(f"   SAVED Proposal  -> {proposal_path}")

    sep = "=" * 62
    print(f"\n{sep}")
    print("  GENESIS COMPLETE")
    print(f"  Agents registered : {len(registry)}")
    print(f"  Log entries       : {len(log)}")
    print(f"  Proposal status   : {status.value.upper()}")
    print("  OP_RETURN prefix  : 54524e47 (TRNG)")
    print(f"{sep}")
    print("\n  The foundation is set. The engine is ready to compile.\n")


if __name__ == "__main__":
    run_genesis()
