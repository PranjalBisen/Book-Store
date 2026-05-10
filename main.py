from fastapi import FastAPI
from app.api.router import api_router
from app.models.base import Base
from app.db.session import engine
import app.models 
Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="Book Store API",
    description="API for managing a book store",
    version="1.0.0",
)

app.include_router(api_router,prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message":"Welcome to the Book Store API"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)
