from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api import api_v1_router
from app.core import settings
from app.exceptions import AppException, app_exception_handler
from app.schemas import ErrorCode, ResponseModel, ErrorResponse

app = FastAPI(title=settings.PROJECT_NAME)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {"success": True, "data": {"message": "Server is running!"}, "errors": None}


# ERROR HANDLER FOR AppException (404, 403, dll)
app.add_exception_handler(AppException, app_exception_handler)


# ERROR HANDLER FOR VALIDATION ERROR
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ResponseModel(
            success=False,
            error=ErrorResponse(
                code=ErrorCode.VALIDATION_ERROR,
                message="Invalid request data",
                details={"errors": exc.errors()},
            ),
        ).model_dump(),
    )


# ERROR HANDLER FOR
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseModel(
            success=False,
            error=ErrorResponse(
                code=ErrorCode.SERVER_ERROR, message=str(exc), details={}
            ),
        ).model_dump(),
    )


app.include_router(api_v1_router, prefix="/api/v1")
