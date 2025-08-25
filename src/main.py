from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from src.core.config import settings
from src.core.middleware.error_handler import CustomErrorMiddleware
from src.core.middleware.validation import validation_exception_handler
from src.routers import api_router
from starlette.middleware.cors import CORSMiddleware


class EcommerceApp:
    def __init__(self) -> None:
        self.app = FastAPI(
            title="Ecommerce Application",
            description="An ecommerce application backend built with FastAPI",
            version=settings.APP_VERSION,
            DEBUG=settings.DEBUG,
            openapi_url="/api/openapi.json" if settings.DEBUG else None,
            docs_url="/api/docs" if settings.DEBUG else None,
            redoc_url="/api/redoc" if settings.DEBUG else None,
        )
        self.validation_error_handler()
        self.make_middleware()

    def validation_error_handler(self) -> None:
        self.app.add_exception_handler(
            RequestValidationError,
            validation_exception_handler,
        )

    def make_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )
        self.app.add_middleware(CustomErrorMiddleware)

    def init_routers(self) -> None:
        self.app.include_router(api_router)

    def create_app(self) -> FastAPI:
        self.init_routers()
        return self.app

        # self.app.include_router(, prefix="/api/v1")


ecommerce_app = EcommerceApp()
app = ecommerce_app.create_app()
