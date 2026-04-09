from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.books.schemas import BookCreate, BookUpdate
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.database import engine
from sqlalchemy.future import select   # sqlalchemy select works better with async
from src.books.models import Book
from src.auth.dependencies import accesstokenbearer

books_router = APIRouter(prefix="/books", tags=["books"])
service = BookService()
access_token_bearer = accesstokenbearer()  # token ko validate krke token data yaha use kr sakte

async def get_session():
    async with AsyncSession(engine) as session:
        yield session


@books_router.get("/")
async def get_book(
        limit: int = 10,
        offset: int = 0,
        session: AsyncSession = Depends(get_session),
        user_details=Depends(access_token_bearer)  # token read
):     # user detail accestokenbearer call ko execute krta, header se token niklke verify- valid hua to return krega toen_data in userr_data
    result = await session.exec(
        select(Book).offset(offset).limit(limit)
    )
    return result.scalars().all()

@books_router.get("/search")
async def search_books(
        min_price: float = 0,
        session: AsyncSession = Depends(get_session),
        user_details=Depends(access_token_bearer)
):
    result = await session.exec(
        select(Book).where(Book.price >= min_price)

    )
    return result.scalars().all()

# GET BY ID

@books_router.get("/{book_id}")
async def get_book(book_id: UUID, session: AsyncSession = Depends(get_session),
                   user_details=Depends(access_token_bearer)):
    book = await service.get_book(book_id, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# CREATE
@books_router.post("/")
async def create_book(
        data: BookCreate,
        session: AsyncSession = Depends(get_session),
        user_details=Depends(access_token_bearer)
):
    return await service.create_book(data, session)

# UPDATE
@books_router.put("/{book_id}")
async def update_book(
        book_id: UUID,
        data: BookUpdate,
        session: AsyncSession = Depends(get_session),
        user_details=Depends(access_token_bearer)
):
    book = await service.update_book(book_id, data, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# DELETE

@books_router.delete("/{book_id}")
async def delete_book(
        book_id: UUID,
        session: AsyncSession = Depends(get_session),
        user_details=Depends(access_token_bearer)
):
    success = await service.delete_book(book_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}


# FILTER