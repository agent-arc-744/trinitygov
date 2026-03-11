"""
chain.py
========
DGB RPC client and OP_RETURN broadcaster for TrinityGov.

Handles:
  - JSON-RPC communication with DigiByte Core node
  - 80-byte Trinity OP_RETURN payload construction
  - Transaction broadcast (v8 legacy path + v9 PSBT path)
  - Node version detection and path selection
  - Block height querying for governance timestamps

Trinity OP_RETURN 80-byte layout:
  [0:4]   Magic     0x54524e47  ('TRNG')
  [4]     Version   0x01
  [5]     ActionID  ActionType compressed to 1 byte (see ACTION_BYTE_MAP)
  [6:8]   Flags     reserved, zeroed
  [8:40]  Hash      SHA-256 content hash (32 bytes)
  [40:80] Padding   reserved for future fields

Environment variables (mirrored from dgb_broadcaster.py):
  DGB_RPC_HOST    node hostname/IP  (default: 127.0.0.1)
  DGB_RPC_PORT    RPC port          (default: 12022 = testnet)
  DGB_RPC_USER    RPC username      (default: digibyte)
  DGB_RPC_PASS    RPC password      (default: '')

Kael | Project Trinity | 2026-02-28
"""
from __future__ import annotations

import base64
import json
import os
import struct
from typing import Any, Dict, Optional, Tuple

from .log import ActionType
from .exceptions import ChainError, BroadcastError


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RPC_HOST: str = os.environ.get("DGB_RPC_HOST", "127.0.0.1")
RPC_PORT: int = int(os.environ.get("DGB_RPC_PORT", "12022"))   # testnet default
RPC_USER: str = os.environ.get("DGB_RPC_USER", "digibyte")
RPC_PASS: str = os.environ.get("DGB_RPC_PASS", "")

# Node version at which PSBT path becomes available
PSBT_MIN_VERSION: Tuple[int, int, int] = (9, 26, 0)

# sendrawtransaction maxfeerate (DGB/kB)
_SEND_MAX_FEERATE: float = 0.10

# Cached node version
_NODE_VERSION_CACHE: Optional[Tuple[int, int, int]] = None


# ---------------------------------------------------------------------------
# Trinity OP_RETURN schema constants
# ---------------------------------------------------------------------------

TRINITY_MAGIC: bytes = bytes.fromhex("54524e47")   # 'TRNG'
TRINITY_SCHEMA_VERSION: int = 0x01
OP_RETURN_SIZE: int = 80

# ActionType -> single byte encoding for on-chain embedding
ACTION_BYTE_MAP: Dict[ActionType, int] = {
    ActionType.IDENTITY_ISSUED:    0x01,
    ActionType.IDENTITY_REVOKED:   0x02,
    ActionType.CAPABILITY_GRANTED: 0x03,
    ActionType.CAPABILITY_REVOKED: 0x04,
    ActionType.PROPOSAL_CREATED:   0x05,
    ActionType.VOTE_CAST:          0x06,
    ActionType.PROPOSAL_PASSED:    0x07,
    ActionType.PROPOSAL_FAILED:    0x08,
    ActionType.PROPOSAL_EXECUTED:  0x09,
    ActionType.EMERGENCY_ACTION:   0x0A,
    ActionType.AGENT_ACTIVATED:    0x0B,
    ActionType.AGENT_DEACTIVATED:  0x0C,
    ActionType.REGISTRY_GENESIS:   0x0D,
    ActionType.AGENT_FLAGGED:       0x0E,
    ActionType.AGENT_REJECTED:      0x0F,
    ActionType.AGENT_CLEARED:       0x10,
    ActionType.COMPILER_REJECT:     0x11,
}

ACTION_BYTE_REVERSE: Dict[int, ActionType] = {
    v: k for k, v in ACTION_BYTE_MAP.items()
}


# ---------------------------------------------------------------------------
# Trinity OP_RETURN payload builder
# ---------------------------------------------------------------------------

def build_op_return_payload(action_type: ActionType, content_hash: str) -> bytes:
    """
    Build an 80-byte Trinity OP_RETURN payload.

    Layout:
      [0:4]   TRNG magic
      [4]     schema version (0x01)
      [5]     action type byte
      [6:8]   flags (reserved, zeroed)
      [8:40]  SHA-256 content hash (32 bytes)
      [40:80] reserved padding (40 bytes, zeroed)

    Args:
        action_type:  ActionType enum value
        content_hash: 64-char hex SHA-256 hash string from LogEntry

    Returns:
        80-byte payload ready for OP_RETURN broadcast.

    Raises:
        ValueError: if content_hash is not a valid 32-byte hex string
    """
    hash_bytes = bytes.fromhex(content_hash)
    if len(hash_bytes) != 32:
        raise ValueError(
            f"content_hash must be 32 bytes (64 hex chars), got {len(hash_bytes)}"
        )

    action_byte = ACTION_BYTE_MAP.get(action_type, 0x00)

    payload = (
        TRINITY_MAGIC           +  # [0:4]  4 bytes
        bytes([TRINITY_SCHEMA_VERSION]) +  # [4]    1 byte
        bytes([action_byte])    +  # [5]    1 byte
        bytes(2)                +  # [6:8]  2 bytes flags (reserved)
        hash_bytes              +  # [8:40] 32 bytes
        bytes(40)                  # [40:80] 40 bytes padding
    )

    assert len(payload) == OP_RETURN_SIZE, f"Payload size error: {len(payload)}"
    return payload


def build_op_return_hex(action_type: ActionType, content_hash: str) -> str:
    """Return hex string of 80-byte Trinity OP_RETURN payload."""
    return build_op_return_payload(action_type, content_hash).hex()


def decode_op_return_payload(payload: bytes) -> Dict:
    """
    Decode a Trinity 80-byte OP_RETURN payload.

    Returns:
        dict with keys: magic, version, action_type, flags, content_hash, valid

    Raises:
        ValueError: on magic mismatch, wrong size, or unknown action byte
    """
    if len(payload) != OP_RETURN_SIZE:
        raise ValueError(f"Expected {OP_RETURN_SIZE} bytes, got {len(payload)}")

    magic   = payload[0:4]
    version = payload[4]
    action_byte = payload[5]
    flags   = payload[6:8]
    content_hash = payload[8:40].hex()

    if magic != TRINITY_MAGIC:
        raise ValueError(
            f"Magic mismatch: expected {TRINITY_MAGIC.hex()}, got {magic.hex()}"
        )
    if version != TRINITY_SCHEMA_VERSION:
        raise ValueError(f"Unknown schema version: 0x{version:02X}")

    action_type = ACTION_BYTE_REVERSE.get(action_byte)

    return {
        "magic":        magic.hex(),
        "version":      version,
        "action_type":  action_type,
        "action_byte":  action_byte,
        "flags":        flags.hex(),
        "content_hash": content_hash,
        "valid":        action_type is not None,
    }


# ---------------------------------------------------------------------------
# RPC client
# ---------------------------------------------------------------------------

class RPCError(ChainError):
    """Raised when the DGB node returns a JSON-RPC error."""
    def __init__(self, code: int, message: str):
        self.code    = code
        self.message = message
        super().__init__(f"RPC error {code}: {message}")


def _rpc_url() -> str:
    return f"http://{RPC_HOST}:{RPC_PORT}/"


def _rpc(method: str, params: list = None) -> Any:
    """
    Execute a JSON-RPC 2.0 call against the DGB node.
    Returns the 'result' field on success.
    Raises RPCError on node-level errors.
    Raises ChainError on connection failures.
    """
    import urllib.request
    import urllib.error

    if params is None:
        params = []

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id":      "trinity-gov",
        "method":  method,
        "params":  params,
    }).encode("utf-8")

    credentials = base64.b64encode(
        f"{RPC_USER}:{RPC_PASS}".encode("utf-8")
    ).decode("ascii")

    req = urllib.request.Request(
        _rpc_url(),
        data    = payload,
        headers = {
            "Content-Type":  "application/json",
            "Authorization": f"Basic {credentials}",
        },
        method  = "POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            raise ChainError(
                f"HTTP {e.code} from DGB node — check credentials and port"
            ) from e
    except Exception as e:
        raise ChainError(f"Cannot reach DGB node at {_rpc_url()}: {e}") from e

    if body.get("error") is not None:
        err = body["error"]
        raise RPCError(err.get("code", -1), err.get("message", "unknown error"))

    return body["result"]


# ---------------------------------------------------------------------------
# Node version detection
# ---------------------------------------------------------------------------

def get_node_version(cached: bool = True) -> Tuple[int, int, int]:
    """
    Return DGB node version as (major, minor, patch).
    e.g. getnetworkinfo().version=9260000 -> (9, 26, 0)
    """
    global _NODE_VERSION_CACHE
    if cached and _NODE_VERSION_CACHE is not None:
        return _NODE_VERSION_CACHE

    info  = _rpc("getnetworkinfo")
    v     = int(info["version"])
    major = v // 1_000_000
    minor = (v // 10_000) % 100
    patch = (v // 100) % 100
    _NODE_VERSION_CACHE = (major, minor, patch)
    return _NODE_VERSION_CACHE


def _use_psbt_path() -> bool:
    """True if node version >= 9.26.0 (PSBT path), else legacy."""
    try:
        return get_node_version() >= PSBT_MIN_VERSION
    except Exception:
        return False  # safe fallback to legacy


def get_block_height() -> int:
    """Return current DGB block height."""
    info = _rpc("getblockchaininfo")
    return int(info["blocks"])


def get_balance() -> float:
    """Return wallet balance in DGB."""
    return float(_rpc("getbalance"))


# ---------------------------------------------------------------------------
# Broadcast paths
# ---------------------------------------------------------------------------

def _broadcast_legacy(hex_payload: str) -> str:
    """
    Legacy broadcast: createrawtransaction -> fundrawtransaction ->
    signrawtransactionwithwallet -> sendrawtransaction.
    Compatible with DGB Core v8.26.x.
    """
    outputs  = [{"data": hex_payload}]
    raw_tx   = _rpc("createrawtransaction", [[], outputs])

    fund_result = _rpc("fundrawtransaction", [
        raw_tx,
        {
            "changePosition":  -1,
            "changeType":      "bech32",
            "includeWatching": False,
        }
    ])
    funded_tx = fund_result["hex"]

    sign_result = _rpc("signrawtransactionwithwallet", [funded_tx])
    if not sign_result.get("complete", False):
        errors = sign_result.get("errors", [])
        raise BroadcastError(f"Transaction signing incomplete: {errors}")
    signed_tx = sign_result["hex"]

    return _rpc("sendrawtransaction", [signed_tx, _SEND_MAX_FEERATE])


def _broadcast_psbt(hex_payload: str) -> str:
    """
    PSBT broadcast: walletcreatefundedpsbt -> walletprocesspsbt ->
    finalizepsbt -> sendrawtransaction.
    Requires DGB Core v9.26+ with descriptor wallet.
    """
    outputs = [{"data": hex_payload}]

    psbt_result = _rpc("walletcreatefundedpsbt", [
        [],
        outputs,
        0,
        {
            "changeType":      "bech32m",
            "includeWatching": False,
            "fee_rate":        10,
        }
    ])
    psbt_b64 = psbt_result["psbt"]

    processed = _rpc("walletprocesspsbt", [psbt_b64, True, "ALL", True])

    finalized = _rpc("finalizepsbt", [processed["psbt"]])
    if not finalized.get("complete", False):
        raise BroadcastError(
            "PSBT finalization incomplete — missing signatures or descriptor wallet"
        )
    signed_hex = finalized["hex"]

    return _rpc("sendrawtransaction", [signed_hex, _SEND_MAX_FEERATE])


# ---------------------------------------------------------------------------
# Public broadcast API
# ---------------------------------------------------------------------------

def broadcast_governance_entry(
    action_type: ActionType,
    content_hash: str,
) -> str:
    """
    Build and broadcast a Trinity governance OP_RETURN transaction.

    Args:
        action_type:  ActionType enum — encoded to 1 byte in payload
        content_hash: 64-char hex SHA-256 from LogEntry.content_hash

    Returns:
        TXID string (64 hex chars)

    Raises:
        BroadcastError: signing or broadcast failure
        ChainError:     connection or RPC failure
        ValueError:     invalid content_hash
    """
    hex_payload = build_op_return_hex(action_type, content_hash)

    if _use_psbt_path():
        return _broadcast_psbt(hex_payload)
    else:
        return _broadcast_legacy(hex_payload)


def health_check() -> Dict:
    """
    Check DGB node connectivity and wallet health.

    Returns:
        dict with keys: ok, version, chain, blocks, balance, psbt_path, error
    """
    try:
        ver     = get_node_version(cached=False)
        info    = _rpc("getblockchaininfo")
        balance = get_balance()
        psbt    = _use_psbt_path()
        return {
            "ok":        True,
            "version":   f"{ver[0]}.{ver[1]}.{ver[2]}",
            "chain":     info.get("chain", "unknown"),
            "blocks":    info.get("blocks", 0),
            "balance":   balance,
            "psbt_path": psbt,
            "error":     None,
        }
    except Exception as e:
        return {
            "ok":    False,
            "error": str(e),
        }
