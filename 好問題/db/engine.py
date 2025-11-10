from sqlalchemy import create_engine
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

def get_db():
    """取得資料庫連線的生成器函數"""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()