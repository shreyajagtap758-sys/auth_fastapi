from src.exceptions.base import AppException

class InvalidToken(AppException):
    """User has provided an invalid/expired token"""
    pass

class RevokedToken(AppException):
    """User has provided token that has been revoked"""
    pass

class AccessTokenRequired(AppException):
    """RefreshTokenRequired"""
    pass

class RefreshTokenRequired(AppException):
    """refresh token is needed, check for the provided token to be an access token"""
    pass

class InsufficientPermission(AppException):
    """user is not allowed to perform this action"""
    pass

class UserAlreadyExists(AppException):
    """user with this email exists"""
    pass

class UserNotFound(AppException):
    """"""
    pass

class InvalidCredentials(AppException):
    """user provided wrong email/password during login"""
    pass

class AccountNotVerified(AppException):
    """account not yet verified"""
    pass