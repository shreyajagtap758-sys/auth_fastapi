from http.client import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from src.models import Book
from datetime import datetime
from src.books.schemas import BookUpdate, BookCreate
from sqlalchemy.orm import selectinload

class BookService:

    async def get_all_books(self,session: AsyncSession):
        result = await session.execute(select(Book))
        return result.scalars().all()


    async def get_users_books(self, user_uid : str, session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.author))

        result = await session.execute(statement)

        return result.scalars().all()


    async def get_book(self, book_uid : str, session : AsyncSession):
        result = await session.execute(
            select(Book).options(selectinload(Book.tags)).where(Book.uid == book_uid)
        )
        return result.scalar_one_or_none()

    async def create_book(self, data : BookCreate, user_uid:str, session : AsyncSession):
        book_data_dict = data.model_dump()

        new_book = Book(**book_data_dict)
        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book

    async def update_book(self, book_uid : str, data : BookUpdate, session : AsyncSession):
        book = await self.get_book(book_uid, session)
        if not book:
            return None

        updated_book = data.model_dump(exclude_unset=True)

        for key, value in updated_book.items():
            setattr(book, key, value)

        book.updated_at = datetime.now()

        await session.commit()
        await session.refresh(book)
        return book

    async def delete_book(self, book_uid : str, session : AsyncSession):
        book = await self.get_book(book_uid, session)
        if not book:
            return False

        await session.delete(book)
        await session.commit()
        return True

    async def get_book_with_tags(self, book_uid: str, session: AsyncSession):
        result = await session.execute(select(Book).options(selectinload(Book.tags)).where(Book.uid == book_uid))

        return result.scalar_one_or_none()

