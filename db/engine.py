import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from contextlib import contextmanager
from dotenv import load_dotenv
# from sqlalchemy.orm import sessionmaker # 移除 SessionLocal，直接使用 Session(engine)

load_dotenv()

# 1. 移除硬編碼的 DATABASE_URL 和硬性檢查
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. 軟化錯誤處理：如果沒有設定環境變數，設置一個無效的 URL。
# 這樣程式碼在啟動時不會崩潰，而是在嘗試連接時才會報錯 (更容易被 Vercel 捕獲)
if not DATABASE_URL:
    print("WARNING: DATABASE_URL not found in environment! Using placeholder.")
    DATABASE_URL = "postgresql://invalid:invalid@localhost/invalid" 
    
# 3. 創建 Engine
# 移除 connect_args={"check_same_thread": False} (SQLite 專用)
# 加入 pool_pre_ping=True (推薦用於 Serverless Functions)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True 
)

# 4. 重新定義 get_db() 函數
# 這是 FastAPI 依賴注入的標準模式
def get_db():
    """取得資料庫連線的生成器函數，用於 FastAPI 依賴注入"""
    # 使用 with Session(engine) 確保連線被安全管理和關閉
    with Session(engine) as session:
        try:
            yield session
        finally:
            # Session(engine) 在 with 結束時會自動 close/rollback
            pass
