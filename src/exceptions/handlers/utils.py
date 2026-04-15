from typing import Callable, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse

# factory function jo use hota he har custom error me
def create_exception_handler(status_code: int, initial_detail: Any) -> Callable:
# outer func= order do from registry(statuscode, detail), inner func= handler banake do

    async def exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status_code,
            content=initial_detail
        )

    return exception_handler

# ye global handler he(500), agar custom error nhi he toh ye dega
async def internal_server_error(request: Request, exc: Exception):

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "someeething went wrong!",
            "error_code": "server_error"
        }
    )
