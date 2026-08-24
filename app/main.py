from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api import router as api_router
from app.core.config import settings
from app.core.deps import set_session_factory
from app.exceptions import BusinessError, InvalidParameterError, NotFoundError


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": False, "error": {"message": message}})


def _validation_error_message(exc: RequestValidationError) -> str:
    for error in exc.errors():
        if error.get("type") == "missing":
            return "必要參數未提供"
        loc = error.get("loc", ())
        # "amount" 命中 amount 欄位本身；也涵蓋 monthlyAmount（budget）等以 amount 結尾的欄位，
        # 不逐一列舉每個新 schema 的金額欄位名稱。
        is_amount_field = any(isinstance(part, str) and part.lower().endswith("amount") for part in loc)
        if is_amount_field and error.get("type") in {"greater_than", "greater_than_equal"}:
            return "金額必須為正數"
    return "必要參數未提供"


def create_app() -> FastAPI:
    app = FastAPI(title="ledger-app API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.on_event("startup")
    def init_session_factory() -> None:
        engine = create_engine(settings.DATABASE_URL)
        set_session_factory(sessionmaker(bind=engine))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.exception_handler(RequestValidationError)
    def handle_validation_error(request: Request, exc: RequestValidationError):
        return _error_response(400, _validation_error_message(exc))

    @app.exception_handler(InvalidParameterError)
    def handle_invalid_parameter(request: Request, exc: InvalidParameterError):
        return _error_response(400, exc.message)

    @app.exception_handler(NotFoundError)
    def handle_not_found(request: Request, exc: NotFoundError):
        return _error_response(404, exc.message)

    @app.exception_handler(BusinessError)
    def handle_business_error(request: Request, exc: BusinessError):
        return _error_response(422, exc.message)

    return app


app = create_app()
