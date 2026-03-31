# init_db.py
"""
Run this ONCE to:
1. Create all database tables
2. Insert the genesis block
3. Insert seed data for testing

Command: python init_db.py
"""
import hashlib
import json
from datetime import datetime, timezone, date

from database.connection import engine, SessionLocal
from models.orm_models import (
    Base, Material, Batch, ProductionOrder,
    BlockchainLog, ScanEvent, FinishedGood
)


def compute_genesis_hash():
    genesis_content = {
        "block_index": 1,
        "event_type": "GENESIS",
        "data": {"message": "RM-FG Tracker Genesis Block", "system": "initialized"},
        "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "timestamp": "2026-01-01T00:00:00Z"
    }
    content_string = json.dumps(genesis_content, sort_keys=True)
    return hashlib.sha256(content_string.encode("utf-8")).hexdigest()


def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")


def insert_genesis_block(db):
    existing = db.query(BlockchainLog).filter(BlockchainLog.block_index == 1).first()
    if existing:
        print("⚠️  Genesis block already exists, skipping")
        return

    genesis_hash = compute_genesis_hash()
    genesis = BlockchainLog(
        block_index=1,
        event_type="GENESIS",
        data_json={"message": "RM-FG Tracker Genesis Block", "system": "initialized"},
        previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
        block_hash=genesis_hash,
        created_at=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db.add(genesis)
    db.commit()
    print(f"✅ Genesis block inserted. Hash: {genesis_hash[:20]}...")


def insert_seed_data(db):
    # ── Seed Materials ─────────────────────────────────────────
    materials = [
        Material(
            material_id="RM001",
            material_name="Chemical X",
            material_type="RM",
            unit="kg",
            current_qty=100,
            location="Rack A-1",
            status="AVAILABLE"
        ),
        Material(
            material_id="RM002",
            material_name="Chemical Y",
            material_type="RM",
            unit="litres",
            current_qty=200,
            location="Rack B-2",
            status="AVAILABLE"
        ),
    ]
    for m in materials:
        if not db.query(Material).filter(Material.material_id == m.material_id).first():
            db.add(m)
    db.flush()

    # ── Seed Batches ───────────────────────────────────────────
    batches = [
        Batch(
            batch_id="BATCH101",
            material_id="RM001",
            batch_type="RM",
            supplier_id="SUP-ABC",
            supplier_name="ABC Corporation",
            quantity=100,
            unit="kg",
            grn_date=date(2026, 3, 1),
            expiry_date=date(2027, 3, 1),
            quality_status="PASSED"
        ),
        Batch(
            batch_id="BATCH102",
            material_id="RM002",
            batch_type="RM",
            supplier_id="SUP-XYZ",
            supplier_name="XYZ Chemicals",
            quantity=200,
            unit="litres",
            grn_date=date(2026, 3, 5),
            expiry_date=date(2027, 3, 5),
            quality_status="PASSED"
        ),
    ]
    for b in batches:
        if not db.query(Batch).filter(Batch.batch_id == b.batch_id).first():
            db.add(b)

    # ── Seed Production Orders ─────────────────────────────────
    orders = [
        ProductionOrder(
            order_id="PO-2026-01",
            product_name="Product Alpha",
            planned_qty=500,
            status="OPEN"
        ),
        ProductionOrder(
            order_id="PO-2026-02",
            product_name="Product Beta",
            planned_qty=300,
            status="OPEN"
        ),
    ]
    for o in orders:
        if not db.query(ProductionOrder).filter(ProductionOrder.order_id == o.order_id).first():
            db.add(o)

    db.commit()
    print("✅ Seed data inserted (2 materials, 2 batches, 2 production orders)")


if __name__ == "__main__":
    print("=" * 50)
    print("Initializing RM-FG Tracker Database")
    print("=" * 50)

    create_tables()

    db = SessionLocal()
    try:
        insert_genesis_block(db)
        insert_seed_data(db)
    finally:
        db.close()

    print("=" * 50)
    print("✅ Database initialization complete")
    print("Run: python main.py")
    print("=" * 50)
