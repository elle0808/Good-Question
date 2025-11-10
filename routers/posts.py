from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from db.engine import get_db
from models.posts import PostDB
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
@router.post("/{slug}/comment", status_code=201, response_model=CommentResponse, summary="新增留言")
def add_comment(
    slug: str, 
    comment_data: CommentCreate, 
    db: Session = Depends(get_db)
):
    post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 1. 【TODO】新增留言到資料庫的邏輯
    
    # 2. 創建新留言的響應物件
    new_comment = CommentResponse(
        author=comment_data.user, 
        content=comment_data.content, 
        time="剛剛" # 這裡應該是數據庫記錄的真實時間
    )
    
    # 3. 返回新建立的留言物件 (前端只需將此物件添加到列表中即可)
    return new_comment
    
    # 注意：您的前端要求返回的數據中包含 likes 和 comments
    # 所以我們返回一個包含兩者的結構，或者只返回 comments 讓前端自己更新
    
    # 為了符合前端的 data.comments 和 data.likes 邏輯，我們返回完整結構：
    return {
        "likes": post.likes or 0, 
        "comments": updated_comments # 替換成從資料庫獲取的所有留言
    }

@router.get("/{slug}/comments", response_model=List[CommentResponse], summary="獲取文章的留言列表")
def list_comments_for_post(slug: str, db: Session = Depends(get_db)):
    # 1. 查找文章 (可選，用於確保 slug 有效)
    # post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    # if not post:
    #     raise HTTPException(status_code=404, detail="Post not found")
        
    # 2. 【TODO】從資料庫查詢與該 slug 相關的所有留言
    #    例如：db.query(CommentDB).filter(CommentDB.post_slug == slug).all()
    
    # 為了方便您測試前端，這裡返回模擬數據：
    mock_comments = [
        CommentResponse(author="專業人士", content="這是第一條真正的回答！", time="2025/11/10 18:00"),
        CommentResponse(author="熱心網友", content="這個問題很有趣，我的看法是...", time="2025/11/10 19:15"),
    ]
    
    return mock_comments