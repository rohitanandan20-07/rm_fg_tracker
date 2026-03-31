# api/fg.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import CreateFGRequest
from services.fg_service import create_fg

router = APIRouter()

@router.post("/api/create-fg")
def create_fg_endpoint(request: CreateFGRequest, db: Session = Depends(get_db)):
    try:
        return create_fg(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
