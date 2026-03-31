# api/blockchain_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
