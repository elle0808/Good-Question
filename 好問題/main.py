# main.py - 測試用
from fastapi import FastAPI
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)

# 移除 lifespan 函式以排除資料庫問題
# app = FastAPI(title="Blog API", version="1.0.0", lifespan=lifespan)
app = FastAPI(title="Test API", version="1.0.0")

@app.get("/hello")
def read_root():
    return {"status": "ok", "message": "FastAPI is running on Vercel!"}

# 移除所有路由和靜態文件掛載
# app.include_router(posts_router)
# app.mount(...)

# 為了 Vercel 部署，可以移除 __name__ == "__main__" 區塊，或保持不變
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# Vercel 只會讀取頂層的 app 實例
