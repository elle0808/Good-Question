from pydantic import BaseModel, ConfigDict,Field,EmailStr
from typing import Optional,List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    account: str # 可能是 username 或 email
    password: str

class PostBase(BaseModel):
    """Post 的基本結構"""
    id: int
    slug: str
    title: str
    content: str
    image_url: Optional[str] = None
    tags: List[str] = Field(..., example=["生活", "化學", "學習"])
    is_anonymous: bool = False
    
class CommentCreate(BaseModel):
    content: str
    
class PostResponse(PostBase):
    """回應用的 Post 結構，包含 ID"""
    # 支援 ORM 模式
    id: int
    author: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)  

class CommentResponse(BaseModel):
    """用於回應前端的留言結構"""
    id: int
    is_anonymous: bool
    author: UserResponse
    content: str
    time: datetime
    # 支援 ORM 模式
    model_config = ConfigDict(from_attributes=True)