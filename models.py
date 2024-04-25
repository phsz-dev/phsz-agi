from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from sqlmodel import Field, SQLModel

class ChatDocument(SQLModel, table=True):
    __tablename__ = "chat_document"
    id: int = Field(primary_key=True)
    page_content: str

# export default interface Page<T> {
#   content: T[]
#   totalElements: number
#   totalPages: number
#   pageNumber: number
#   pageSize: number
#   orderColumn?: string
#   orderType?: string
# }

T = TypeVar('T')

class SimplePage(BaseModel, Generic[T]):
    content: List[T]
    totalElements: int
    totalPages: int
    pageNumber: int
    pageSize: int
    orderColumn: Optional[str] = None
    orderType: Optional[str] = None

class Result(BaseModel, Generic[T]):
    code: int
    msg: str
    data: T | None

    @staticmethod
    def success(data: T | None = None, msg: str = "success") -> "Result":
        return Result(code=0, msg=msg, data=data)
    
    @staticmethod
    def error(code: int, msg: str) -> "Result":
        return Result(code=code, msg=msg)