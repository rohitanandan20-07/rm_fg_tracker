# services/fg_service.py
import uuid
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session

from models.schemas import CreateFGRequest
from models.orm_models import Material, ScanEvent, ProductionOrder, FinishedGood, Batch
from blockchain.block import create_block


def create_fg(db: Session, request: CreateFGRequest) -> dict:
    # ── STEP 1: VALIDATE ──────────────────────────────────────
    order = db.query(ProductionOrder).filter(
        ProductionOrder.order_id == request.production_order_id
    ).first()
    if not order:
        raise ValueError(f"Production order '{request.production_order_id}' not found")
    if order.status not in ("OPEN", "IN_PROGRESS"):
        raise ValueError(f"Production order status is '{order.status}'")

    existing_fg = db.query(FinishedGood).filter(FinishedGood.fg_id == request.fg_id).first()
    if existing_fg:
        raise ValueError(f"Finished Good '{request.fg_id}' already exists")

    # ── STEP 2: CREATE FG MATERIAL RECORD ────────────────────
    fg_material = db.query(Material).filter(Material.material_id == request.fg_id).first()
    if not fg_material:
        fg_material = Material(
            material_id=request.fg_id,
            material_name=request.fg_name,
            material_type="FG",
            unit=request.unit,
            current_qty=request.quantity,
            location="FG Warehouse",
            status="AVAILABLE"
        )
        db.add(fg_material)

    # ── STEP 3: CREATE FINISHED GOOD RECORD ──────────────────
    fg = FinishedGood(
        fg_id=request.fg_id,
        production_order_id=request.production_order_id,
        fg_name=request.fg_name,
        quantity=request.quantity,
        unit=request.unit,
        produced_date=date.today(),
        status="IN_STOCK"
    )
    db.add(fg)

    # ── STEP 4: COMPLETE PRODUCTION ORDER ─────────────────────
    order.status = "COMPLETED"
    order.completed_at = datetime.now(timezone.utc)
    db.flush()

    # ── STEP 5: CREATE SCAN EVENT ─────────────────────────────
    event_id = "EVT-" + str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now(timezone.utc).isoformat()

    scan_event = ScanEvent(
        event_id=event_id,
        event_type="FG_CREATED",
        material_id=request.fg_id,
        quantity=request.quantity,
        to_location="FG Warehouse",
        production_order_id=request.production_order_id,
        worker_id=request.worker_id
    )
    db.add(scan_event)
    db.flush()

    # ── STEP 6: CREATE BLOCKCHAIN BLOCK ───────────────────────
    blockchain_data = {
        "event_id": event_id,
        "fg_id": request.fg_id,
        "fg_name": request.fg_name,
        "production_order_id": request.production_order_id,
        "quantity_produced": request.quantity,
        "unit": request.unit,
        "rm_batches_used": request.rm_batches_used,
        "worker_id": request.worker_id,
        "timestamp": timestamp
    }
    block_info = create_block(db, "FG_CREATED", blockchain_data)
    scan_event.blockchain_block_index = block_info["block_index"]

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "fg_id": request.fg_id,
        "message": f"Finished Good '{request.fg_id}' created: {request.quantity} {request.unit}",
        "blockchain": {
            "block_index": block_info["block_index"],
            "block_hash": block_info["block_hash"],
            "status": "LOGGED"
        }
    }
