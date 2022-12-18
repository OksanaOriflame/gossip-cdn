from pydantic import BaseModel
from typing import List, Optional, Union
from nodes.models.operation import AddOp, RemoveOp, ModifyOp
from enum import Enum

class BaseQuery(BaseModel):
    page_id: str

class GetPageVersionRequest(BaseQuery):
    pass

class GetPageVersionResponse(BaseQuery):
    version: Optional[str] = None

class Meta(BaseModel):
    page_id: str
    page_name: str

class UpdatePageRequest(BaseQuery):
    prev_version: str
    operations: List[Union[AddOp, RemoveOp, ModifyOp]]
    root_hash: str
    meta: Meta

class Status(Enum):
    OK = 'ok'

class UpdatePageResponse(BaseModel):
    status: Status
