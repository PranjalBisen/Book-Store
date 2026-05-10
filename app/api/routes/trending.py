from typing import List
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.trending import TrendingResponse
from app.services import trending_service

router=APIRouter()

@router.get("/",response_model=List[TrendingResponse])
def get_trending(limit:int=10,db:Session=Depends(get_db)):
    return trending_service.get_top_trending(db,limit)
