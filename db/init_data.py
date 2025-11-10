"""資料庫初始化模組"""
import logging
from sqlalchemy.orm import Session

from .engine import engine
from models.posts import PostDB
from data.init_posts import posts

logger = logging.getLogger(__name__)

def init_posts_data():
    """初始化文章資料"""
    with Session(engine) as session:
        # 檢查資料庫是否已有文章資料
        existing_posts_count = session.query(PostDB).count()
        
        if existing_posts_count > 0:
            logger.info(f"資料庫已有 {existing_posts_count} 筆文章，跳過初始化")
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
                    tags=post_data["tags"]
                )
                session.add(post)
            
            session.commit()
            logger.info(f"成功匯入 {len(posts)} 筆文章資料")
            
        except Exception as e:
            logger.error(f"文章資料匯入失敗: {e}")
            raise

def init_database():
    """初始化整個資料庫（包含所有資料表的初始資料）"""
    logger.info("開始初始化資料庫資料...")    
    # 初始化文章資料
    init_posts_data()

    logger.info("資料庫資料初始化完成")
