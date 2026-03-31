# services/dispatch_service.py
import uuid
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session

from models.schemas import DispatchRequest
from models.orm_models import Material, ScanEvent, FinishedGood, DispatchRecord
from blockchain.block import create_block


def dispatch_fg(db: Session, request: DispatchRequest) -> dict:
    # ── STEP 1: VALIDATE ──────────────────────────────────────
    fg = db.query(FinishedGood).filter(FinishedGood.fg_id == request.fg_id).first()
    if not fg:
        raise ValueError(f"Finished Good '{request.fg_id}' not found")
    if fg.status != "IN_STOCK":
        raise ValueError(f"Finished Good status is '{fg.status}'. Cannot dispatch.")
    if float(fg.quantity) < request.quantity:
        raise ValueError(
            f"Insufficient quantity. Available: {fg.quantity}, Requested: {request.quantity}"
        )

    # ── STEP 2: UPDATE FG STATUS ──────────────────────────────
    fg.status = "DISPATCHED"
    fg_material = db.query(Material).filter(Material.material_id == request.fg_id).first()
    if fg_material:
        fg_material.status = "DISPATCHED"
        fg_material.current_qty = float(fg_material.current_qty) - request.quantity
    db.flush()

    # ── STEP 3: CREATE DISPATCH RECORD ───────────────────────
    dispatch_id = "DISP-" + str(uuid.uuid4())[:8].upper()
    dispatch = DispatchRecord(
        dispatch_id=dispatch_id,
        fg_id=request.fg_id,
        customer_name=request.customer_name,
        customer_id=request.customer_id,
        quantity=request.quantity,
        dispatch_date=date.today(),
        vehicle_number=request.vehicle_number
    )
    db.add(dispatch)
    db.flush()

    # ── STEP 4: CREATE SCAN EVENT ─────────────────────────────
    event_id = "EVT-" + str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now(timezone.utc).isoformat()

    scan_event = ScanEvent(
        event_id=event_id,
        event_type="DISPATCHED",
        material_id=request.fg_id,
        quantity=request.quantity,
        from_location="FG Warehouse",
        to_location=f"Customer: {request.customer_name}",
        customer_id=request.customer_id,
        worker_id=request.worker_id
    )
    db.add(scan_event)
    db.flush()

    # ── STEP 5: CREATE BLOCKCHAIN BLOCK ───────────────────────
    blockchain_data = {
        "event_id": event_id,
        "dispatch_id": dispatch_id,
        "fg_id": request.fg_id,
        "customer_id": request.customer_id,
        "customer_name": request.customer_name,
        "quantity": request.quantity,
        "vehicle_number": request.vehicle_number,
        "worker_id": request.worker_id,
        "timestamp": timestamp
    }
    block_info = create_block(db, "DISPATCHED", blockchain_data)
    scan_event.blockchain_block_index = block_info["block_index"]

    db.commit()

    return {
        "success": True,
        "event_id": event_id,
        "dispatch_id": dispatch_id,
        "message": f"{request.quantity} units of {request.fg_id} dispatched to {request.customer_name}",
        "blockchain": {
            "block_index": block_info["block_index"],
            "block_hash": block_info["block_hash"],
            "status": "LOGGED"
        }
    }
