from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

from .error_schema import ErrorResponse

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None

    model_config = {
        "arbitrary_types_allowed": True
    }
