from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from db.init_data import create_tables, init_db
from db.engine import SessionLocal
from routers import posts as post_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- Lifespan event: startup ---")
    try:
        # 現在 create_tables() 會確保所有模型都已載入
        create_tables()
        
        db = SessionLocal()
        init_db(db)
        db.close()
    except Exception as e:
        print(f"啟動過程中發生嚴重錯誤: {e}")
    
    yield
    
    print("--- Lifespan event: shutdown ---")

app = FastAPI(lifespan=lifespan)

app.include_router(post_router.router)


# --- 靜態檔案服務 (以下不變) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

@app.get("/")
async def read_index():
    # 使用絕對路徑確保檔案被找到
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))

@app.get("/blog.html")
async def read_blog_html():
    return FileResponse(os.path.join(STATIC_DIR, 'list.html')) # 修正為 list.html

@app.get("/post.html")
async def read_post_html():
    return FileResponse(os.path.join(STATIC_DIR, 'post.html'))

# 靜態檔案掛載的部分也確保目錄正確（但這裡保持 'static' 可能沒問題）
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 註冊路由
app.include_router(posts_router)

if __name__ == "__main__":
    # 運行在 8000 埠

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

