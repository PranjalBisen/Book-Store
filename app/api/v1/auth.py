from fastapi import FastAPI, HTTPException

from app.api import router
from psycopg2 import connect, OperationalError
from app.schemas.login import Login
router.app.include_router(router.app)

app = FastAPI(
    title="Book Store API",
    description="API for managing a book store",
    version="1.0.0",
)

@router.post("/login")
async def login(credentials: Login):
    try:
        db = connect(
            dbname="bookstore",
            user="user",
            password="password",
            host="localhost",
            port="5432"
        )
        db.close()
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection failed")
    user_name = db.query(model.User).filter(model.User.username == credentials.username).first()
    user_password = db.query(model.User).filter(model.User.password == credentials.password).first()
    if not user_name or not user_password:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Login successful", "user": user_name}

@router.post("/register")
async def register(credentials: Login):
    try:
        db = connect(
            dbname="bookstore",
            user="user",
            password="password",
            host="localhost",
            port="5432"
        )
        db.close()
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection failed")
    user = db.query(model.User).filter(model.User.username == credentials.username).first()
    if user:
        raise HTTPException(status_code=404, detail="User already exists")
    db.add(model.User(username=credentials.username, password=credentials.password))
    db.commit()
    return {"message": "User registered successfully", "user": credentials.username}