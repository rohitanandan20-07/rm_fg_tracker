# models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# ── GRN ───────────────────────────────────────────────────────
class CreateGRNRequest(BaseModel):
    material_id:    str = Field(..., example="RM001")
    material_name:  str = Field(..., example="Chemical X")
    batch_id:       str = Field(..., example="BATCH101")
    quantity:       float = Field(..., gt=0, example=50.0)
    unit:           str = Field(..., example="kg")
    supplier_id:    str = Field(..., example="SUP-ABC")
    supplier_name:  str = Field(..., example="ABC Corporation")
    worker_id:      str = Field(..., example="W007")
    location:       str = Field(..., example="Rack A-1")
    quality_status: str = Field(default="PASSED", example="PASSED")


# ── ISSUE MATERIAL ────────────────────────────────────────────
class IssueMaterialRequest(BaseModel):
    material_id:            str = Field(..., example="RM001")
    batch_id:               str = Field(..., example="BATCH101")
    quantity:               float = Field(..., gt=0, example=50.0)
    production_order_id:    str = Field(..., example="PO-2026-01")
    worker_id:              str = Field(..., example="W012")


# ── CREATE FINISHED GOOD ──────────────────────────────────────
class CreateFGRequest(BaseModel):
    fg_id:                  str = Field(..., example="FG-789")
    fg_name:                str = Field(..., example="Product Alpha")
    production_order_id:    str = Field(..., example="PO-2026-01")
    quantity:               float = Field(..., gt=0, example=200.0)
    unit:                   str = Field(..., example="units")
    worker_id:              str = Field(..., example="W015")
    rm_batches_used:        list[str] = Field(..., example=["BATCH101"])


# ── DISPATCH ──────────────────────────────────────────────────
class DispatchRequest(BaseModel):
    fg_id:          str = Field(..., example="FG-789")
    customer_id:    str = Field(..., example="CUST-XYZ")
    customer_name:  str = Field(..., example="XYZ Industries")
    quantity:       float = Field(..., gt=0, example=200.0)
    vehicle_number: str = Field(..., example="TN-01-AB-1234")
    worker_id:      str = Field(..., example="W020")
