# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from db.engine import engine
from db.init_data import init_database
from models.base import Base
from routers.posts import router as posts_router

# 設定日誌 - 更詳細的格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    # 啟動時執行
    try:
        logger.info("正在初始化資料庫...")
        Base.metadata.create_all(engine)
        logger.info("資料庫結構初始化完成")
        
        # 初始化資料
        init_database()
        
    except Exception as e:
        logger.error(f"應用程式初始化失敗: {e}")
        raise
    
    yield
    
    # 關閉時執行（可以在這裡添加清理邏輯）
    logger.info("應用程式正在關閉...")
    
app = FastAPI(title="Blog API", version="1.0.0", lifespan=lifespan)

# CORS：視需求收斂 allow_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修正 2: 設定靜態檔案服務
app.mount("/img", StaticFiles(directory="img"), name="img")

# 註冊路由
app.include_router(posts_router)

if __name__ == "__main__":
    # 運行在 8000 埠
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)