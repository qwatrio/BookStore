from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database.database import engine
from app.database.models import Base

from app.routers import auth
from app.routers import books
from app.routers import comments
from app.routers import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(
    title="BookStore API",
    lifespan=lifespan,
)


app.include_router(auth.router)
app.include_router(books.router)
app.include_router(comments.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)