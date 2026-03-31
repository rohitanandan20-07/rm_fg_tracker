# services/issue_service.py
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from models.schemas import IssueMaterialRequest
from models.orm_models import Material, ScanEvent, ProductionOrder
from blockchain.block import create_block


def issue_material(db: Session, request: IssueMaterialRequest) -> dict:
    # ── STEP 1: VALIDATE ──────────────────────────────────────
    material = db.query(Material).filter(Material.material_id == request.material_id).first()
    if not material:
        raise ValueError(f"Material '{request.material_id}' not found")
    if float(material.current_qty) < request.quantity:
        raise ValueError(
            f"Insufficient quantity. Available: {material.current_qty} {material.unit}, "
            f"Requested: {request.quantity}"
        )
    if material.status not in ("AVAILABLE",):
        raise ValueError(f"Material status is '{material.status}'. Cannot issue.")

    order = db.query(ProductionOrder).filter(
        ProductionOrder.order_id == request.production_order_id
    ).first()
    if not order:
        raise ValueError(f"Production order '{request.production_order_id}' not found")
    if order.status not in ("OPEN", "IN_PROGRESS"):
        raise ValueError(f"Production order status is '{order.status}'. Cannot issue to it.")

    # ── STEP 2: UPDATE MATERIAL ───────────────────────────────
    original_location = material.location
    material.current_qty = float(material.current_qty) - request.quantity
    if float(material.current_qty) == 0:
        material.status = "ISSUED"
    material.location = "Production Floor"
    db.flush()

    # ── STEP 3: UPDATE PRODUCTION ORDER ──────────────────────
    if order.status == "OPEN":
        order.status = "IN_PROGRESS"
        order.started_at = datetime.now(timezone.utc)
    db.flush()

    # ── STEP 4: CREATE SCAN EVENT ─────────────────────────────
    event_id = "EVT-" + str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now(timezone.utc).isoformat()

    scan_event = ScanEvent(
        event_id=event_id,
        event_type="MATERIAL_ISSUED",
        material_id=request.material_id,
        batch_id=request.batch_id,
        quantity=request.quantity,
        from_location=original_location,
        to_location="Production Floor",
        production_order_id=request.production_order_id,
        worker_id=request.worker_id
    )
    db.add(scan_event)
    db.flush()

    # ── STEP 5: CREATE BLOCKCHAIN BLOCK ───────────────────────
    blockchain_data = {
        "event_id": event_id,
        "material_id": request.material_id,
        "batch_id": request.batch_id,
        "quantity": request.quantity,
        "production_order_id": request.production_order_id,
        "from_location": original_location,
        "worker_id": request.worker_id,
        "timestamp": timestamp
    }
    block_info = create_block(db, "MATERIAL_ISSUED", blockchain_data)
    scan_event.blockchain_block_index = block_info["block_index"]

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "message": f"{request.quantity} {material.unit} of {request.material_id} issued to {request.production_order_id}",
        "blockchain": {
            "block_index": block_info["block_index"],
            "block_hash": block_info["block_hash"],
            "status": "LOGGED"
        }
    }
