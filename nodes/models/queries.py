from pydantic import BaseModel
from typing import List
from nodes.models.operation import Op
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
    patches: List[Op]
    root_hash: str
    meta: Meta

class Status(Enum):
    OK = 'ok'

class UpdatePageResponse(BaseModel):
    status: Status
