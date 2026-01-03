"""資料庫初始化模組，包含資料表結構創建與初始資料匯入"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from .engine import engine
from models.posts import PostDB,UserDB
from models.base import Base # <--- 引入 Base，用於創建資料表結構
from data.init_posts import posts
from data.init_users import users

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

def init_all_data(session: Session):
    """初始化使用者與文章資料"""
    
    # A. 先檢查並匯入使用者
    if session.query(UserDB).count() == 0:
        logger.info("開始匯入使用者初始資料...")
        created_users = []
        for u_data in users:
            user = UserDB(
                username=u_data["username"],
                email=u_data["email"],
                hashed_password=u_data["password"] # <--- 暫不加密，直接存明文
            )
            session.add(user)
            created_users.append(user)
        session.commit() # 提交後才能拿到 user.id
    else:
        created_users = session.query(UserDB).all()

    # B. 檢查並匯入文章
    if session.query(PostDB).count() == 0:
        logger.info("開始匯入文章初始資料...")
        try:
            for post_data in posts:
                # 這裡假設所有初始文章都掛在第一個使用者 (admin) 名下
                post = PostDB(
                    slug=post_data["slug"],
                    title=post_data["title"],
                    author_id=created_users[0].id, # <--- 改用 ID 關聯
                    content=post_data["content"],
                    image_url=post_data.get("image_url", ""),
                    is_anonymous=post_data.get("is_anonymous", False),# 新增的欄位
                    tags=post_data.get("tags", [])
                )
                session.add(post)
            session.commit()
            logger.info("成功匯入文章資料")
        except Exception as e:
            session.rollback()
            logger.error(f"文章資料匯入失敗: {e}")
            raise

# --- 3. 總初始化函數 ---
def init_database(db: Session):
    logger.info("開始初始化資料庫結構與資料...")
    create_tables()
    init_all_data(db) # 呼叫新的整合匯入函數
    logger.info("資料庫結構與資料初始化完成")
