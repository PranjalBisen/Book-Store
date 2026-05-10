import os

class Settings:
    SECRET_KEY=os.getenv("SECRET_KEY","secret")
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    DATABASE_URL=os.getenv("DATABASE_URL","postgresql://user:password@localhost:5432/bookstore")

settings=Settings()
