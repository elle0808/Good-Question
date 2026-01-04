import os
from fastapi import APIRouter, HTTPException, Depends , Header
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from jose import jwt,JWTError
from dotenv import load_dotenv
from pydantic import BaseModel

from db.engine import get_db
from models.posts import PostDB,CommentDB,UserDB
from schemas.posts import PostResponse, CommentCreate,CommentResponse,UserCreate

load_dotenv()

router = APIRouter(
   prefix='/api/posts',
   tags=['blog posts']
)

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# === 註冊 ===
@router.post("/sync_user")
def sync_user(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == data.id).first()
    
    if user:
        user.username = data.username
        user.email = data.email
    else:
        user = UserDB(**data.model_dump(), hashed_password="managed_by_supabase")
        db.add(user)
    
    db.commit()
    return {"status": "success", "username": user.username}

# === 登入 ===
def get_current_user_id(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供登入資訊")
    
    try:
        # 移除 "Bearer " 前綴
        token = authorization.replace("Bearer ", "")
        
        # 解碼 Token
        # 注意：options={"verify_aud": False} 很重要，因為 Supabase 的 aud (audience) 
        # 預設是 "authenticated"，有時候解碼器會因為這個報錯
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            options={"verify_aud": False}
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="無效的使用者資訊")
            
        return user_id
        
    except JWTError as e:
        print(f"JWT 解碼錯誤: {str(e)}") # 可以在後端終端機看到具體原因
        raise HTTPException(status_code=401, detail="通行證已過期或無效")

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
def add_comment(slug: str, comment_data: CommentCreate, db: Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    # 1. 驗證文章是否存在
    post = db.scalar(select(PostDB).where(PostDB.slug == slug))
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 🌟 關鍵補丁：檢查 users 表格裡有沒有這個 user_id
    user_exists = db.scalar(select(UserDB).where(UserDB.id == user_id))
    if not user_exists:
        # 如果不存在，幫他在本地資料庫建立一筆資料（同步 Supabase 身份）
        # 這裡因為 JWT 沒給 username，我們先用 "Supabase User" 暫代
        new_user = UserDB(
            id=user_id, 
            username=f"用戶_{user_id[:5]}", 
            email="supabase_user@example.com", # 實際應用可從 JWT 拿 email
            hashed_password="external_auth" 
        )
        db.add(new_user)
        db.flush() # 先流進資料庫，確保下面的 ForeignKey 能抓到
    
    # 2. 建立新留言 (假設我們現在還沒做登入，先暫時掛在 ID 1 帳號下測試)
    # 如果你已經有登入功能，這裡應該用 current_user.id
    new_comment = CommentDB(
        content=comment_data.content,
        post_id=post.id,
        author_id=user_id,  
        is_anonymous=False # 這裡可以根據 comment_data 調整
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment) # 重新整理以獲取關聯的作者資料
    
    return new_comment