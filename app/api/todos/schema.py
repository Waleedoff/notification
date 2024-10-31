from datetime import datetime

from pydantic import BaseModel


class TodoResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    is_chceked: bool

    class Config:
        form_attribute = True


class TodoCreateRequest(BaseModel):
    title: str


class TodoUpdateRequest(BaseModel):
    title: str
