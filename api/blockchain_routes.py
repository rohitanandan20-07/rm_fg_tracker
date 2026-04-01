# api/blockchain_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
from models.orm_models import BlockchainLog
from blockchain.validator import validate_chain as validate_chain_logic

router = APIRouter()

@router.get("/api/validate-chain")
def validate_chain_endpoint(db: Session = Depends(get_db)):
    return validate_chain_logic(db)


@router.get("/api/blockchain-log")
def get_blockchain_log(limit: int = 20, db: Session = Depends(get_db)):
    """Returns the most recent N blocks for dashboard display."""
    blocks = (
        db.query(BlockchainLog)
        .order_by(BlockchainLog.block_index.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "block_index": b.block_index,
            "event_type": b.event_type,
            "data_json": b.data_json,
            "previous_hash": b.previous_hash,
            "block_hash": b.block_hash,
            "created_at": b.created_at.isoformat() if b.created_at else None
        }
        for b in reversed(blocks)  # Return chronological order
    ]


def _flatten_json(value, prefix=""):
    items = {}
    if isinstance(value, dict):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            items.update(_flatten_json(v, key))
        return items
    if isinstance(value, list):
        for i, v in enumerate(value):
            key = f"{prefix}[{i}]"
            items.update(_flatten_json(v, key))
        return items
    items[prefix] = value
    return items


@router.get("/api/blockchain-log-history")
def get_blockchain_log_history(block_index: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns audit history for a specific block index with field-level diffs.

    Note: History exists only after the audit trigger has been installed (on API startup).
    """
    rows = db.execute(
        text(
            """
            SELECT audit_id, changed_at, operation, old_row, new_row
            FROM blockchain_log_audit
            WHERE block_index = :block_index
            ORDER BY changed_at DESC, audit_id DESC
            LIMIT :limit
            """
        ),
        {"block_index": block_index, "limit": limit},
    ).mappings().all()

    out = []
    for r in rows:
        old_row = r["old_row"] or {}
        new_row = r["new_row"] or {}

        old_data = old_row.get("data_json") or {}
        new_data = new_row.get("data_json") or {}

        flat_old = _flatten_json(old_data)
        flat_new = _flatten_json(new_data)

        all_keys = sorted(set(flat_old.keys()) | set(flat_new.keys()))
        changes = []
        for k in all_keys:
            before = flat_old.get(k, None)
            after = flat_new.get(k, None)
            if before != after:
                changes.append({"field": k, "from": before, "to": after})

        out.append(
            {
                "audit_id": int(r["audit_id"]),
                "changed_at": r["changed_at"].isoformat() if r["changed_at"] else None,
                "operation": r["operation"],
                "changes": changes,
            }
        )

    return {
        "block_index": block_index,
        "count": len(out),
        "history": out,
    }
