from fastapi import FastAPI, status
from starlette.responses import JSONResponse

from src.exceptions.handlers.utils import create_exception_handler

from src.exceptions.auth.exceptions import (
    InvalidCredentials,
    UserNotFound, UserAlreadyExists,
    InvalidToken, InsufficientPermission,
    AccessTokenRequired, RefreshTokenRequired,
    RevokedToken, AccountNotVerified
)
from src.exceptions.book.exceptions import BookNotFound
from src.exceptions.tags.exceptions import TagNotFound, TagAlreadyExists
from src.exceptions.handlers.utils import internal_server_error

# yaha sirf app.utils wala function likhenge
def register_exception_handler(app: FastAPI):

    # AUTH
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid email or password",
                "resolution": "enter correct email/pass",
                "error_code": "invalid_credentials"
            }
        )
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "User already exists",
                "error_code": "user_exists"
            }
        )
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token",
                "error_code": "invalid_token"
            }
        )
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Insufficient permissions",
                "error_code": "permission_denied"
            }
        )
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token required",
                "error_code": "access_token_required"
            }
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Refresh token required",
                "error_code": "refresh_token_required"
            }
        )
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked",
                "error_code": "revoked_token"
            }
        )
    )

    # BOOK
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found"
            }
        )
    )

    # TAGS
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "tag_not_found"
            }
        )
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Tag already exists",
                "error_code": "tag_exists"
            }
        )
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "account not verified",
                "error_code": "account_not_verified",
                "resolution": "check your email for verification details"
            }
        )
    )

    app.add_exception_handler(
        Exception,
        internal_server_error # ye utils me pass hogi
    ) # ye global error he, mtlab agar custom error na ho or kuch error ayega, to ye dikhega)