# services/grn_service.py
import uuid
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session

from models.schemas import CreateGRNRequest
from models.orm_models import Material, Batch, ScanEvent
from blockchain.block import create_block


def create_grn(db: Session, request: CreateGRNRequest) -> dict:
    """
    Handles GRN (Goods Receipt Note).
    Creates or updates material, creates batch, logs scan event, creates blockchain block.
    """
    # ── STEP 1: UPSERT MATERIAL ───────────────────────────────
    material = db.query(Material).filter(Material.material_id == request.material_id).first()

    if material:
        # Material exists — add to quantity
        material.current_qty = float(material.current_qty) + request.quantity
        material.status = "AVAILABLE"
        material.location = request.location
    else:
        # New material
        material = Material(
            material_id=request.material_id,
            material_name=request.material_name,
            material_type="RM",
            unit=request.unit,
            current_qty=request.quantity,
            location=request.location,
            status="AVAILABLE"
        )
        db.add(material)

    db.flush()

    # ── STEP 2: UPSERT BATCH ──────────────────────────────────
    batch = db.query(Batch).filter(Batch.batch_id == request.batch_id).first()

    if not batch:
        batch = Batch(
            batch_id=request.batch_id,
            material_id=request.material_id,
            batch_type="RM",
            supplier_id=request.supplier_id,
            supplier_name=request.supplier_name,
            quantity=request.quantity,
            unit=request.unit,
            grn_date=date.today(),
            quality_status=request.quality_status
        )
        db.add(batch)
        db.flush()

    # ── STEP 3: CREATE SCAN EVENT ─────────────────────────────
    event_id = "EVT-" + str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now(timezone.utc).isoformat()

    scan_event = ScanEvent(
        event_id=event_id,
        event_type="GRN_RECEIVED",
        material_id=request.material_id,
        batch_id=request.batch_id,
        quantity=request.quantity,
        to_location=request.location,
        worker_id=request.worker_id
    )
    db.add(scan_event)
    db.flush()

    # ── STEP 4: CREATE BLOCKCHAIN BLOCK ───────────────────────
    blockchain_data = {
        "event_id": event_id,
        "material_id": request.material_id,
        "batch_id": request.batch_id,
        "quantity": request.quantity,
        "supplier_id": request.supplier_id,
        "supplier_name": request.supplier_name,
        "worker_id": request.worker_id,
        "location": request.location,
        "timestamp": timestamp
    }
    block_info = create_block(db, "GRN_RECEIVED", blockchain_data)

    # ── STEP 5: LINK SCAN EVENT TO BLOCK ──────────────────────
    scan_event.blockchain_block_index = block_info["block_index"]

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "message": f"GRN recorded: {request.quantity} {request.unit} of {request.material_id} received",
        "blockchain": {
            "block_index": block_info["block_index"],
            "block_hash": block_info["block_hash"],
            "status": "LOGGED"
        }
    }
