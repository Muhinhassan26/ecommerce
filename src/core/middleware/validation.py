from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.core.error.codes import REGISTRATION_FAILED

from core.error.exceptions import ValidationException
from core.error.format_error import field_error_format


async def validation_exception_handler(
    _: Request,
    exc: Exception,
) -> JSONResponse:
    if isinstance(exc, RequestValidationError):
        details = exc.errors()
        errros = field_error_format(details, is_pydantic_validation_error=True)
        ve = ValidationException(errors=errros, error_code=REGISTRATION_FAILED)

        return JSONResponse(
            status_code=ve.code,
            content={
                "error_code": ve.error_code,
                "message": ve.message,
                "errors": ve.errors,
            },
        )

    raise exc
