from fastapi import APIRouter, Depends
from src.models import User
from src.reviews.schemas import reviewcreatemodel, reviewmodel
from src.db.database import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.service import reviewservice
from src.auth.dependencies import get_current_user

review_router = APIRouter()
review_service = reviewservice()

@review_router.post('/book/{book_uid}',response_model=reviewmodel)
async def add_review_to_books(
        book_uid : str,
        review_data : reviewcreatemodel,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):

    new_review = await review_service.add_review_to_book(
        user_email = current_user.email,
        review_data = review_data,
        book_uid = book_uid,
        session = session
    )

    return new_review
