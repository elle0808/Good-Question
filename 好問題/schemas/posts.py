from pydantic import BaseModel, ConfigDict,Field
from typing import Optional,List

class PostBase(BaseModel):
    """Post 的基本結構"""
    slug: str
    title: str
    author: str
    content: str
    image_url: Optional[str] = None
    tags: List[str] = Field(..., example=["前端開發", "Tailwind CSS", "問答"])
    
class CommentCreate(BaseModel):
    user: str
    content: str
    
class PostResponse(PostBase):
    """回應用的 Post 結構，包含 ID"""
    # 支援 ORM 模式
    model_config = ConfigDict(from_attributes=True)  
    
    id: int

class CommentResponse(BaseModel):
    """用於回應前端的留言結構"""
    author: str = Field(..., alias="user") # 統一作者名稱，使用 user 欄位
    content: str
    time: str = Field(..., example="2025/11/10 17:01") # 新增時間欄位，方便前端顯示
    
    # 支援 ORM 模式
    model_config = ConfigDict(from_attributes=True)