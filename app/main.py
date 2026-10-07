from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware

from app.database.database import engine
from app.database.models import Base
from app.dependencies.auth import get_docs_admin

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
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/openapi.json", include_in_schema=False)
async def openapi_json(
    current_admin=Depends(get_docs_admin),
):
    return app.openapi()


@app.get("/docs", include_in_schema=False)
async def docs(
    current_admin=Depends(get_docs_admin),
):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Философский камень — API Docs",
    )
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(comments.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)