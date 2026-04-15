from src.books.service import BookService
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models import Tag
from src.tags.schemas import TagAdd, TagCreate
from src.exceptions.book.exceptions import BookNotFound
from src.exceptions.tags.exceptions import TagNotFound, TagAlreadyExists


book_service = BookService()

server_error = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong"
)

class TagService:
    async def get_tags(self, session : AsyncSession):  # get all tags
        statement = select(Tag)
        result = await session.execute(statement)

        return result.scalars().all()

    async def add_tags_to_book(self, book_uid : str, tag_data : TagAdd, session: AsyncSession):
        book = await book_service.get_book(book_uid=book_uid, session=session)

        if not book:
            raise BookNotFound()


        for tag_item in tag_data.tags:  # user ne jitne tags bheje proccess kro
            result = await session.execute(
                select(Tag).where(Tag.name == tag_item.name)  # chekc if tag exist pele se
            )

            tag = result.scalar_one_or_none()  # if tag exist=  object, else none
            if not tag:  # if tag dont exist = create it
                tag = Tag(name=tag_item.name)

            book.tags.append(tag)  # book me tags daal diy
        session.add(book)
        await session.commit()
        await session.refresh(book)

        return book

#flow : book uid lo jo user ne bheji, dhundo db me wo book, har tag keliye db check kro tag exist he ya nhi, if not, create new tag, else use that tag and book ke sath link krdo

    async def get_tag_by_uid(self, tag_uid : str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def add_tag(self, tag_data : TagCreate, session : AsyncSession):  #create a tag
        # watch if tag exists already

        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.execute(statement)
        tag = result.scalar_one_or_none()

        if tag:
            raise TagAlreadyExists()


        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()

        return new_tag

    async def update_tag(self, tag_uid, tag_update_data : TagCreate, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)
        update_tag_dict = tag_update_data.model_dump()  # sare tag ke name agye

        for k, v in update_tag_dict.items():
            setattr(tag,k,v)

        await session.commit()
        await session.refresh(tag)
        return tag

    async def delete_tag(self, tag_uid : str, session : AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()

        await session.delete(tag)
        await session.commit()

        return {"message": "successfully deleted a tag"}
