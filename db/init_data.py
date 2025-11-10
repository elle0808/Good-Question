"""資料庫初始化模組，包含資料表結構創建與初始資料匯入"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from .engine import engine
from models.posts import PostDB
from models.base import Base # <--- 引入 Base，用於創建資料表結構
from data.init_posts import posts

logger = logging.getLogger(__name__)

# --- 1. 資料表結構創建 (Schema Creation) ---
def create_tables():
    """使用 Base.metadata 創建所有資料表結構"""
    logger.info("檢查並創建資料庫資料表...")
    try:
        # 創建所有繼承自 Base 的資料表
        Base.metadata.create_all(bind=engine)
        logger.info("資料庫資料表檢查與創建完成。")
    except OperationalError as e:
        # 處理連線或權限問題
        logger.error(f"資料表創建失敗 (可能是連線問題或權限): {e}")
        raise # 必須拋出錯誤，確保啟動失敗

# --- 2. 初始資料匯入 (Data Initialization) ---
def init_posts_data(session: Session): # <--- 接受 Session 作為參數
    """初始化文章資料"""
    # 注意：這裡不再需要建立 Session，直接使用傳入的 session
    
    # 檢查資料庫是否已有文章資料
    existing_posts_count = session.query(PostDB).count()
        
    if existing_posts_count > 0:
        logger.info(f"資料庫已有 {existing_posts_count} 筆文章，跳過文章資料初始化")
        return
        
    logger.info("開始匯入文章初始資料...")
        
    try:
        # 匯入初始資料
        for post_data in posts:
            post = PostDB(
                slug=post_data["slug"],
                title=post_data["title"],
                author=post_data["author"],
                content=post_data["content"],
                image_url=post_data["image_url"],
                tags=post_data.get("tags", []) # 使用 .get 確保資料健壯性
            )
            session.add(post)
            
        session.commit()
        logger.info(f"成功匯入 {len(posts)} 筆文章資料")
            
    except Exception as e:
        session.rollback() # 發生錯誤時必須回滾
        logger.error(f"文章資料匯入失敗: {e}")
        raise

# --- 3. 總初始化函數 ---
def init_database(db: Session): # <--- 接受 db/session 作為參數
    """初始化整個資料庫（包含結構創建與所有資料表的初始資料）"""
    logger.info("開始初始化資料庫結構與資料...")
    
    # 1. 創建資料表結構 (必須先做這一步)
    create_tables()

    # 2. 初始化文章資料 (將 Session 傳入)
    init_posts_data(db)

    logger.info("資料庫結構與資料初始化完成")
