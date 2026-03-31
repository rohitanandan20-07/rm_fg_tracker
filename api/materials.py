# api/materials.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from models.orm_models import Material, ScanEvent, ProductionOrder

router = APIRouter()

@router.get("/api/materials")
def get_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).order_by(Material.created_at.desc()).all()
    return [
        {
            "material_id": m.material_id,
            "material_name": m.material_name,
            "material_type": m.material_type,
            "unit": m.unit,
            "current_qty": float(m.current_qty) if m.current_qty else 0,
            "location": m.location,
            "status": m.status,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in materials
    ]


@router.get("/api/scan-events")
def get_scan_events(limit: int = 20, db: Session = Depends(get_db)):
    events = (
        db.query(ScanEvent)
        .order_by(ScanEvent.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "material_id": e.material_id,
            "batch_id": e.batch_id,
            "quantity": float(e.quantity) if e.quantity else None,
            "from_location": e.from_location,
            "to_location": e.to_location,
            "production_order_id": e.production_order_id,
            "worker_id": e.worker_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "blockchain_block_index": e.blockchain_block_index
        }
        for e in events
    ]


@router.get("/api/production-orders")
def get_production_orders(db: Session = Depends(get_db)):
    orders = db.query(ProductionOrder).all()
    return [
        {
            "order_id": o.order_id,
            "product_name": o.product_name,
            "planned_qty": float(o.planned_qty) if o.planned_qty else 0,
            "status": o.status
        }
        for o in orders
    ]
