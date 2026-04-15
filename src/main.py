from fastapi import FastAPI, status
from contextlib import asynccontextmanager
from src.db.database import init_db
from src.books.routes import books_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.route import tags_router
from src.exceptions.handlers.registry import register_exception_handler
from .middleware import register_middleware

app = FastAPI(
    title="Bookly API",
    description="A REST API for managing books",
    version="v1"
)

from src import models

register_exception_handler(app)
# idhr se registry me mapping hogi, fir utils me handler banega(mapping data use krke), or wo handler send ho jayega

register_middleware(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Server is starting...")

    await init_db()

    yield

    print("🛑 Server has been stopped")


app.include_router(
    review_router,
    prefix="/api/v1/reviews",
    tags=["reviews"]
)

# ✅ Router include (prefix + tags)
app.include_router(
    books_router,
    prefix="/api/v1/books",
    tags=["Books"]
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

app.include_router(
    tags_router,
    prefix=f"/api/v1/tags",
    tags=["tags"]
)