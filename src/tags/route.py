from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.books.service import BookService
from src.auth.dependencies import rolechecker
from src.books.schemas import BookRead
from src.db.database import get_session
from src.models import Book

from src.tags.schemas import TagAdd, TagCreate, TagModel
from src.tags.service import TagService

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(rolechecker(["user", "admin"]))
book_service = BookService()

# get all tags
@tags_router.get("/", response_model = List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session : AsyncSession=Depends(get_session)):
    tags = await tag_service.get_tags(session)

    return tags

# add a tag
@tags_router.post("/", response_model = TagModel,
                  status_code=status.HTTP_201_CREATED,
                  dependencies=[user_role_checker],
                  )
async def add_a_tag(tag_data : TagCreate, session : AsyncSession=Depends(get_session)) -> TagModel:
    tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)

    return tag_added

# add tags to book
@tags_router.post("/book/{book_uid}/tags", response_model=Book,dependencies=[user_role_checker])
async def add_tags_to_bookie(book_uid : str, tag_data : TagAdd, session: AsyncSession = Depends(get_session)) -> Book:

    book_with_tag = await tag_service.add_tags_to_book(book_uid=book_uid, tag_data=tag_data, session=session)

    return book_with_tag

# update a tag
@tags_router.put("/tag/{tag_uid}", response_model = TagModel, dependencies=[user_role_checker])
async def update_tag(tag_uid : str, tag_update_data : TagCreate, session: AsyncSession=Depends(get_session)) -> TagModel:

    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)

    return updated_tag

# delete a tag
@tags_router.delete(
    "/{tag_uid}",status_code=status.HTTP_410_GONE,dependencies=[user_role_checker])
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)) -> None:
    updated_tag = await tag_service.delete_tag(tag_uid, session)

    return updated_tag


@tags_router.get("/{book_uid}", response_model=BookRead)
async def get_book_with_tag(book_uid: str, user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await book_service.get_book_with_tags(book_uid, session)
# adding user added auth here, it gets current user that is logged in

