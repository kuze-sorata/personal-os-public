from datetime import datetime

from pydantic import BaseModel


class FreeBlock(BaseModel):
    start: datetime
    end: datetime
    minutes: int

