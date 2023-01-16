import enum

from pydantic import Field

from src.api.request_models.request_base import RequestBase
from src.core.utils import get_task_images

TaskImageRequest = enum.Enum('TaskImageRequest', get_task_images())


class TaskCreateRequest(RequestBase):
    description: str = Field(..., min_length=3, max_length=150)
