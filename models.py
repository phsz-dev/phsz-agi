from sqlmodel import Field, SQLModel

class ChatDocument(SQLModel, table=True):
    __tablename__ = "chat_document"
    id: int = Field(primary_key=True)
    page_content: str