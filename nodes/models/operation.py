from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class Operation(Enum):
    ADD = "add"
    MODIFY = "modify"
    REMOVE = "remove"

class Op(BaseModel):
    op: Operation
    name: str

class AddOp(Op):
    op = Operation.ADD
    data: bytes

class ModifyOp(Op):
    op = Operation.MODIFY
    hash: str
    data: bytes

class RemoveOp(Op):
    op = Operation.REMOVE
    hash: str
