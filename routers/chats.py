import os
import asyncio
from typing import Annotated, AsyncIterable
from dotenv import load_dotenv

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from models import ChatDocument
from database import get_chat_documents, vector_db

load_dotenv()

router = APIRouter(
    prefix="/api/chats",
    tags=["chats"],
    responses={404: {"description": "Not found"}},
)

retriever = vector_db.as_retriever()

def format_docs(docs: list[ChatDocument]) -> str:
    return "\n\n".join([f"Result {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

# prompt = ChatPromptTemplate(
#     messages=[
#         SystemMessage('''You are an assistant for question-answering tasks.
# Use the following pieces of retrieved context to answer the question.
# If you don't know the answer, just say that you don't know.
# Use three sentences maximum and keep the answer concise.
# Question: {question} 
# Context: {context} 
# Answer:'''),
#     ]
# )
prompt = ChatPromptTemplate.from_messages(
    [("system", """You are a smart QA system for a pet hospital learning system capable of retrieving knowledge from the system's database.
Use the following pieces of retrieved context to answer the question.

Retrieved Context:

{context}
      
!!!Important!!!: If the information is not in the retrieved context, state that it is not available in the knowledge base.
Try keep the answer concise.

Question: {question}
Answer:""")]
)

model = ChatOpenAI(
    model="gpt-4-turbo",
    base_url=os.getenv("OPENAI_API_BASE"), streaming=True, verbose=True
)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
)

async def send_message(content: str) -> AsyncIterable[str]:

    async for chunk in rag_chain.astream(content):
        print(chunk.content)
        yield chunk.content


@router.post("/openai")
async def openai(message: Annotated[str, Body()]):
    return StreamingResponse(send_message(message))

if __name__ == "__main__":

    async def main():
        async for chunk in send_message("Hello"):
            print(chunk)

    asyncio.run(main())
