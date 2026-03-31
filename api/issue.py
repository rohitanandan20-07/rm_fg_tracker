# api/issue.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import IssueMaterialRequest
from services.issue_service import issue_material

router = APIRouter()

@router.post("/api/issue-material")
def issue_material_endpoint(request: IssueMaterialRequest, db: Session = Depends(get_db)):
    try:
        return issue_material(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
