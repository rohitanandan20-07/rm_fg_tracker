# api/trace.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.orm_models import ScanEvent, BlockchainLog, Material

router = APIRouter()

@router.get("/api/trace/{material_id}")
def trace_material(material_id: str, db: Session = Depends(get_db)):
    """
    Returns the complete event history for a material or FG.
    Each event includes its corresponding blockchain block for verification.
    """
    # Get all scan events for this material
    events = (
        db.query(ScanEvent)
        .filter(ScanEvent.material_id == material_id)
        .order_by(ScanEvent.timestamp.asc())
        .all()
    )

    if not events:
        # Also check if it's an FG and trace back its RM
        raise HTTPException(
            status_code=404,
            detail=f"No events found for material '{material_id}'"
        )

    # Get material info
    material = db.query(Material).filter(Material.material_id == material_id).first()

    result_events = []
    for event in events:
        block = None
        if event.blockchain_block_index:
            block = db.query(BlockchainLog).filter(
                BlockchainLog.block_index == event.blockchain_block_index
            ).first()

        result_events.append({
            "event_id": event.event_id,
            "event_type": event.event_type,
            "material_id": event.material_id,
            "batch_id": event.batch_id,
            "quantity": float(event.quantity) if event.quantity else None,
            "from_location": event.from_location,
            "to_location": event.to_location,
            "production_order_id": event.production_order_id,
            "worker_id": event.worker_id,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "blockchain": {
                "block_index": block.block_index if block else None,
                "block_hash": block.block_hash[:20] + "..." if block else None,
                "status": "VERIFIED" if block else "NOT_LOGGED"
            }
        })

    return {
        "material_id": material_id,
        "material_name": material.material_name if material else "Unknown",
        "material_type": material.material_type if material else "Unknown",
        "current_status": material.status if material else "Unknown",
        "total_events": len(result_events),
        "events": result_events
    }
