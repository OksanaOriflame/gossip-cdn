from pydantic import BaseModel
from typing import List, Union
from nodes.models.operation import AddOp, RemoveOp, ModifyOp
from enum import Enum

class BaseQuery(BaseModel):
    id: str

class GetPageVersionRequest(BaseQuery):
    pass

class GetPageVersionResponse(BaseQuery):
    version: str

class Meta(BaseModel):
    id: str
    name: str

class UpdatePageRequest(BaseQuery):
    prev_version: str
    hash: str
    patches: List[Union[AddOp, RemoveOp, ModifyOp]]
    root_hash: str
    meta: Meta

class Status(Enum):
    OK = 'ok'

class UpdatePageResponse(BaseModel):
    status: Status
