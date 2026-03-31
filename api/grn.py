# api/grn.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import CreateGRNRequest
from services.grn_service import create_grn

router = APIRouter()

@router.post("/api/create-grn")
def create_grn_endpoint(request: CreateGRNRequest, db: Session = Depends(get_db)):
    try:
        return create_grn(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
