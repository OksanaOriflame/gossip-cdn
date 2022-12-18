from enum import Enum
from pydantic import BaseModel
from typing import Optional


class Operation(Enum):
    ADD = "add"
    MODIFY = "modify"
    REMOVE = "remove"


class Op(BaseModel):
    op: Operation
    name: str
    data: Optional[bytes]
    hash: Optional[str]
