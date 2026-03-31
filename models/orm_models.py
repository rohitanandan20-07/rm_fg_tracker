# models/orm_models.py
from sqlalchemy import (
    Column, String, Numeric, Integer, Text, DateTime, Date, ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database.connection import Base


class Material(Base):
    __tablename__ = "materials"

    material_id     = Column(String(20), primary_key=True)
    material_name   = Column(String(100), nullable=False)
    material_type   = Column(String(5), nullable=False)   # "RM" or "FG"
    unit            = Column(String(10), nullable=False)
    current_qty     = Column(Numeric(10, 2), default=0)
    location        = Column(String(50))
    status          = Column(String(20), default="AVAILABLE")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class Batch(Base):
    __tablename__ = "batches"

    batch_id        = Column(String(30), primary_key=True)
    material_id     = Column(String(20), ForeignKey("materials.material_id"))
    batch_type      = Column(String(5))                   # "RM" or "FG"
    supplier_id     = Column(String(20))
    supplier_name   = Column(String(100))
    quantity        = Column(Numeric(10, 2))
    unit            = Column(String(10))
    grn_date        = Column(Date)
    expiry_date     = Column(Date)
    quality_status  = Column(String(20), default="PENDING")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class ScanEvent(Base):
    __tablename__ = "scan_events"

    event_id                = Column(String(30), primary_key=True)
    event_type              = Column(String(30), nullable=False)
    material_id             = Column(String(20), ForeignKey("materials.material_id"))
    batch_id                = Column(String(30), ForeignKey("batches.batch_id"), nullable=True)
    quantity                = Column(Numeric(10, 2))
    from_location           = Column(String(50))
    to_location             = Column(String(50))
    production_order_id     = Column(String(20), nullable=True)
    worker_id               = Column(String(20))
    customer_id             = Column(String(20))
    notes                   = Column(Text)
    timestamp               = Column(DateTime(timezone=True), server_default=func.now())
    blockchain_block_index  = Column(Integer, nullable=True)


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    order_id        = Column(String(20), primary_key=True)
    product_name    = Column(String(100))
    planned_qty     = Column(Numeric(10, 2))
    status          = Column(String(20), default="OPEN")
    started_at      = Column(DateTime(timezone=True), nullable=True)
    completed_at    = Column(DateTime(timezone=True), nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class FinishedGood(Base):
    __tablename__ = "finished_goods"

    fg_id                   = Column(String(20), primary_key=True)
    production_order_id     = Column(String(20), ForeignKey("production_orders.order_id"))
    fg_name                 = Column(String(100))
    quantity                = Column(Numeric(10, 2))
    unit                    = Column(String(10))
    produced_date           = Column(Date)
    status                  = Column(String(20), default="IN_STOCK")
    created_at              = Column(DateTime(timezone=True), server_default=func.now())


class DispatchRecord(Base):
    __tablename__ = "dispatch_records"

    dispatch_id     = Column(String(20), primary_key=True)
    fg_id           = Column(String(20), ForeignKey("finished_goods.fg_id"))
    customer_name   = Column(String(100))
    customer_id     = Column(String(20))
    quantity        = Column(Numeric(10, 2))
    dispatch_date   = Column(Date)
    vehicle_number  = Column(String(20))
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class BlockchainLog(Base):
    __tablename__ = "blockchain_log"

    block_index     = Column(Integer, primary_key=True, autoincrement=True)
    event_type      = Column(String(30), nullable=False)
    data_json       = Column(JSONB, nullable=False)
    previous_hash   = Column(String(64), nullable=False)
    block_hash      = Column(String(64), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
