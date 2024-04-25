from fastapi import FastAPI
from contextlib import asynccontextmanager
from nacos_utils import nacos_config, nacos_add, nacos_remove
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

print(nacos_config)

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        scheduler.add_job(nacos_add, 'interval', seconds=10, next_run_time=datetime.datetime.now())
        scheduler.start()
        yield
    finally:
        scheduler.shutdown()
        nacos_remove()

from routers import chats, documents

app = FastAPI(lifespan=lifespan)
# app = FastAPI()

app.include_router(chats.router)
app.include_router(documents.router)