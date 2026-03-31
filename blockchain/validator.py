# blockchain/validator.py
import json
from typing import Dict
from sqlalchemy.orm import Session
from models.orm_models import BlockchainLog
from blockchain.block import compute_block_hash


def validate_chain(db: Session) -> Dict:
    """
    Fetches all blocks in order and verifies:
    1. Each block's stored hash matches a fresh recomputation from its data
    2. Each block's previous_hash matches the actual prior block's hash

    Returns a dict with valid: True/False and error details.
    """
    blocks = (
        db.query(BlockchainLog)
        .order_by(BlockchainLog.block_index.asc())
        .all()
    )

    if not blocks:
        return {
            "valid": False,
            "reason": "No blocks found in blockchain_log",
            "total_blocks": 0
        }

    errors = []

    for i in range(1, len(blocks)):
        current = blocks[i]
        previous = blocks[i - 1]

        # Recompute expected hash from stored data
        expected_hash = compute_block_hash(
            block_index=current.block_index,
            event_type=current.event_type,
            data_json=current.data_json,
            previous_hash=current.previous_hash,
            timestamp=current.created_at.isoformat()
        )

        # Check 1: Stored hash matches recomputed hash
        if current.block_hash != expected_hash:
            errors.append({
                "block_index": current.block_index,
                "issue": "HASH_MISMATCH",
                "detail": f"Block {current.block_index} data was altered after logging",
                "stored_hash": current.block_hash[:20] + "...",
                "expected_hash": expected_hash[:20] + "..."
            })

        # Check 2: previous_hash matches actual previous block's hash
        if current.previous_hash != previous.block_hash:
            errors.append({
                "block_index": current.block_index,
                "issue": "CHAIN_BROKEN",
                "detail": f"Block {current.block_index} is not linked to Block {previous.block_index} correctly"
            })

    if errors:
        return {
            "valid": False,
            "total_blocks": len(blocks),
            "error_count": len(errors),
            "errors": errors,
            "message": f"⚠️ Chain INVALID — {len(errors)} issue(s) detected"
        }

    return {
        "valid": True,
        "total_blocks": len(blocks),
        "error_count": 0,
        "errors": [],
        "message": f"✅ Chain VALID — All {len(blocks)} blocks verified"
    }
