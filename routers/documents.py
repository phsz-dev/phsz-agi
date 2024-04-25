from fastapi import APIRouter

from models import ChatDocument, SimplePage, Result
from database import get_chat_documents, get_chat_document, upsert_chat_document, delete_chat_document

router = APIRouter(
    prefix="/api/docs",
    tags=["docs"],
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=Result[SimplePage[ChatDocument]])
async def read_docs(pageNum: int = 0, pageSize: int = 10, orderColumn: str = "id", orderType: str = "ASC"):
    chat_documents, total_elements = get_chat_documents(pageNum, pageSize, orderColumn, orderType)
    total_pages = (total_elements + pageSize - 1) // pageSize  # 计算总页数
    return Result.success(SimplePage(
        content=chat_documents,
        totalElements=total_elements,
        totalPages=total_pages,
        pageNumber=pageNum,
        pageSize=pageSize,
        orderColumn=orderColumn,
        orderType=orderType
    ))

@router.get("/{doc_id}", response_model=Result[ChatDocument])
async def read_doc(doc_id: int):
    return Result.success(get_chat_document(doc_id))

@router.post("", response_model=Result[int])
async def create_doc(doc: ChatDocument):
    return Result.success(upsert_chat_document(doc.page_content, doc.id))

@router.put("/{doc_id}", response_model=Result[int])
async def update_doc(doc_id: int, doc: ChatDocument):
    return Result.success(upsert_chat_document(doc.page_content, doc_id))

@router.delete("/{doc_id}", response_model=Result[int])
async def delete_doc(doc_id: int):
    delete_chat_document(doc_id)
    return Result.success(doc_id)