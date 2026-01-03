from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from db.engine import get_db
from models.posts import PostDB,CommentDB
from schemas.posts import PostResponse, CommentCreate,CommentResponse

router = APIRouter(
   prefix='/api/posts',
   tags=['blog posts']
)

@router.get("", response_model=List[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    rows = (
        db.query(PostDB)
         .order_by(PostDB.id.asc())
         .all()
    )
    return rows

@router.get("/{slug}", response_model=PostResponse)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post




# ----------------------------------------------------
## 留言 (Comment) 路由
# ----------------------------------------------------
@router.get("/{slug}/comments", response_model=List[CommentResponse])
def list_comments_for_post(slug: str, db: Session = Depends(get_db)):
    # 1. 找到對應的文章
    post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
        
    # 2. 從資料庫查詢該文章的所有留言
    # 重點：SQLAlchemy 會自動幫你把 UserDB 的資料關聯進來
    comments = db.query(CommentDB).filter(CommentDB.post_id == post.id).all()
    
    return comments

@router.post("/{slug}/comment", response_model=CommentResponse)
def add_comment(slug: str, comment_data: CommentCreate, db: Session = Depends(get_db)):
    # 1. 驗證文章是否存在
    post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 2. 建立新留言 (假設我們現在還沒做登入，先暫時掛在 ID 1 帳號下測試)
    # 如果你已經有登入功能，這裡應該用 current_user.id
    new_comment = CommentDB(
        content=comment_data.content,
        post_id=post.id,
        author_id=1,  # 先寫死成 1 號 (阿椎伯) 測試
        is_anonymous=False # 這裡可以根據 comment_data 調整
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment) # 重新整理以獲取關聯的作者資料
    
    return new_comment