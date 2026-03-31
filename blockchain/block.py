# blockchain/block.py
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy.orm import Session
from models.orm_models import BlockchainLog


def compute_block_hash(
    block_index: int,
    event_type: str,
    data_json: Dict[str, Any],
    previous_hash: str,
    timestamp: str
) -> str:
    """
    Computes SHA-256 of all block fields combined.
    sort_keys=True guarantees identical output regardless of dict key order.
    """
    content = {
        "block_index": block_index,
        "event_type": event_type,
        "data": data_json,
        "previous_hash": previous_hash,
        "timestamp": timestamp
    }
    content_string = json.dumps(content, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(content_string.encode("utf-8")).hexdigest()


def create_block(db: Session, event_type: str, data_json: Dict[str, Any]) -> Dict:
    """
    Called after every successful DB write.
    1. Fetches last block's hash
    2. Computes new block's hash
    3. Inserts new block into blockchain_log
    4. Returns block info

    IMPORTANT: Always call this AFTER PostgreSQL writes succeed.
    """
    # Step 1: Get the last block
    last_block = (
        db.query(BlockchainLog)
        .order_by(BlockchainLog.block_index.desc())
        .first()
    )

    if last_block is None:
        raise RuntimeError(
            "Blockchain not initialized. Run init_db.py first to create the genesis block."
        )

    previous_hash = last_block.block_hash
    # We need to determine the next index manually since we use autoincrement
    # but we need the index value BEFORE insert for hashing
    next_index = last_block.block_index + 1
    timestamp = datetime.now(timezone.utc).isoformat()

    # Step 2: Compute hash
    block_hash = compute_block_hash(
        block_index=next_index,
        event_type=event_type,
        data_json=data_json,
        previous_hash=previous_hash,
        timestamp=timestamp
    )

    # Step 3: Insert new block
    new_block = BlockchainLog(
        block_index=next_index,
        event_type=event_type,
        data_json=data_json,
        previous_hash=previous_hash,
        block_hash=block_hash,
        created_at=datetime.fromisoformat(timestamp)
    )
    db.add(new_block)
    db.flush()   # Write to DB within transaction but don't commit yet
                 # Caller (service) will commit after everything succeeds

    return {
        "block_index": next_index,
        "block_hash": block_hash,
        "previous_hash": previous_hash,
        "timestamp": timestamp,
        "event_type": event_type
    }
