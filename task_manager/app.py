import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from task_manager.routers import auth, todos, users
from task_manager.schemas import Message

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


@app.get(
    '/health',
    status_code=HTTPStatus.OK,
    response_model=Message,
    tags=['Health'],
)
async def health():
    return {'message': 'ok'}
