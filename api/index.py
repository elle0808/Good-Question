# =========================================================
# **請將以下內容暫時替換到您的 api/index.py 中**
# =========================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os 
from routers import posts as post_router # 保持路由導入，但它們的 DB 依賴可能仍會失敗

# 獲取當前文件所在的目錄 (確保靜態檔案路徑正確)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Vercel Test Startup: DB REMOVED ---")
    # 這裡不再進行任何資料庫操作
    yield
    print("--- Vercel Test Shutdown ---")

app = FastAPI(lifespan=lifespan)

# 註冊路由
app.include_router(post_router.router)


# --- 靜態檔案服務 (使用修正過的路徑) ---
@app.get("/")
async def read_index():
    # 確保這裡的路徑是修正過的
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))

# 註冊靜態檔案掛載
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# =========================================================
