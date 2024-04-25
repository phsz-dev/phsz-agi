import os
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.docstore.document import Document
from langchain_community.vectorstores import Milvus
from sqlmodel import SQLModel, Session, create_engine, desc, select, func

from models import ChatDocument

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_db = Milvus(
    embeddings,
    collection_name="mihoyo",
    connection_args={
        "host": os.getenv("MILVUS_HOST"),
        "port": os.getenv("MILVUS_PORT"),
        "user": os.getenv("MILVUS_USER"),
        "password": os.getenv("MILVUS_PASSWORD")
    },
    auto_id=True
)

def milvus_upsert(id: int, page_content: str):
    pks = vector_db.get_pks(f"id == {id}")
    docs = [Document(page_content=page_content, metadata={"id": id})]
    vector_db.upsert(pks, docs)

def milvus_search(query: str):
    return vector_db.search(query, "similarity")

def upsert_chat_document(page_content: str, id: int = None) -> int:
    with Session(engine) as session:
        if id:
            chat_document = session.get(ChatDocument, id)
            if not chat_document:
                chat_document = ChatDocument(id=id, page_content=page_content)
            else:
                chat_document.page_content = page_content
        else:
            chat_document = ChatDocument(page_content=page_content)
        session.add(chat_document)
        session.flush()
        milvus_upsert(chat_document.id, chat_document.page_content)
        session.commit()
        return chat_document.id

def delete_chat_document(id: int):
    with Session(engine) as session:
        chat_document = session.get(ChatDocument, id)
        if chat_document:
            session.delete(chat_document)
        session.commit()

def get_chat_document(id: int):
    with Session(engine) as session:
        chat_document = session.get(ChatDocument, id)
        return chat_document
    
def get_chat_documents(page_number: int, page_size: int, order_by: str = "id", order: Literal["ASC", "DESC"] = "ASC") -> tuple[list[ChatDocument], int]:
    with Session(engine) as session:
        # 计算总记录数
        total_elements = session.exec(select(func.count()).select_from(ChatDocument)).one()
        stmt = select(ChatDocument)
        if order.upper() == "ASC":
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(desc(order_by))
        stmt = stmt.offset(page_number * page_size).limit(page_size)
        chat_documents = session.exec(stmt).all()
        return chat_documents, total_elements

if __name__ == "__main__":
    upsert_chat_document("星穹铁道当前版本为 2.1", 5)
    # upsert_chat_document("星穹铁道最火爆的角色是流萤", 2)
    # upsert_chat_document("明日方舟是鹰角网络开发的一款策略游戏")
    print(milvus_search("星穹铁道版本"))