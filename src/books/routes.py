from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from src.books.schemas import BookCreate, BookUpdate, BookDetailModel
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select   # sqlalchemy select works better with async
from src.models import Book
from src.auth.dependencies import accesstokenbearer, rolechecker
from src.db.database import get_session

books_router = APIRouter(prefix="/books", tags=["books"])
service = BookService()
access_token_bearer = accesstokenbearer()  # token ko validate krke token data yaha use kr sakte
role_checker = Depends(rolechecker(['admin', "user"]))

@books_router.get("/", dependencies=[role_checker])
async def get_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
):
    books = await service.get_all_books(session)
    return books

@books_router.get("/user/{user_uid}", dependencies=[role_checker])
async def get_user_submissions(
    user_uid : str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer)
):
    books = await service.get_users_books(user_uid, session)
    return books


@books_router.get("/search", dependencies=[role_checker])
async def search_books(
        min_price: float = 0,
        session: AsyncSession = Depends(get_session),
        token_details : dict =Depends(access_token_bearer)
):
    result = await session.exec(
        select(Book).where(Book.price >= min_price)

    )
    return result.scalars().all()

# GET BY ID

@books_router.get("/{book_id}",response_model = BookDetailModel ,dependencies=[role_checker])
async def get_a_book(book_id: UUID, session: AsyncSession = Depends(get_session),
                   token_details : dict =Depends(access_token_bearer)) -> dict:
    book = await service.get_book(book_id, session)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


# CREATE
@books_router.post("/", dependencies=[role_checker])
async def create_book(
        data: BookCreate,
        session: AsyncSession = Depends(get_session),
        token_details : dict =Depends(access_token_bearer)
):
    user_id = token_details.get("user")["user_uid"]
    new_book = await service.create_book(data, user_id, session)
    return new_book

# UPDATE
@books_router.put("/{book_id}", dependencies=[role_checker])
async def update_book(
        book_id: UUID,
        data: BookUpdate,
        session: AsyncSession = Depends(get_session),
        token_details : dict =Depends(access_token_bearer)) -> dict:

    user_id = token_details.get('user')['user_uid']

    book = await service.update_book(book_id, data, session)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# DELETE

@books_router.delete("/{book_id}", dependencies=[role_checker])
async def delete_book(
        book_id: UUID,
        session: AsyncSession = Depends(get_session),
        token_details : dict =Depends(access_token_bearer)
):
    success = await service.delete_book(book_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

