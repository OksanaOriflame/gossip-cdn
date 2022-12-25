from enum import Enum
from pydantic import BaseModel


class Operation(Enum):
    ADD = "add"
    MODIFY = "modify"
    REMOVE = "remove"

class Op(BaseModel):
    operation: Operation
    file_name: str

class AddOp(Op):
    operation = Operation.ADD
    data: bytes

class ModifyOp(Op):
    operation = Operation.MODIFY
    hash: str
    data: bytes

class RemoveOp(Op):
    operation = Operation.REMOVE
    hash: str
