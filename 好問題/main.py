# main.py 的 lifespan 函式片段
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時執行
    try:
        logger.info("正在初始化資料庫...")
        Base.metadata.create_all(engine) # ⬅️ 創建表格
        logger.info("資料庫結構初始化完成")
        
        init_database() # ⬅️ 插入初始資料
        
    except Exception as e:
        logger.error(f"應用程式初始化失敗: {e}")
        raise
    
    yield
