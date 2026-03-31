# api/dispatch.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import DispatchRequest
from services.dispatch_service import dispatch_fg

router = APIRouter()

@router.post("/api/dispatch")
def dispatch_endpoint(request: DispatchRequest, db: Session = Depends(get_db)):
    try:
        return dispatch_fg(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
