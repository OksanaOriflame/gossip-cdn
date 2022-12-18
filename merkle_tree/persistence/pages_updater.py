import json
import os
from typing import List, Optional
from merkle_tree.Pages.page_repository import PageRepository
from nodes.models.operation import AddOp
from nodes.models.queries import GetPageVersionRequest, GetPageVersionResponse, Status, UpdatePageRequest, UpdatePageResponse


class PagesUpdater:
    def __init__(self, cdn_node_directory: str) -> None:
        page_repository = PageRepository(cdn_node_directory)
        page_repository.build()
        self.pages = {x.merkle_tree.pageId: x.merkle_tree for x in page_repository.pages}
        self.page_repository = page_repository

    def update_page(self, request: UpdatePageRequest) -> UpdatePageResponse:
        page = self.pages.get(request.page_id)
        if not page:
            return self._create_page(request)
        return self._update_page(request)

    def get_random_page_id(self) -> str:
        pass
    
    def get_latest_version(self, request: GetPageVersionRequest) -> GetPageVersionResponse:
        pass

    def get_next_version(self, page_id: str, current_version: str) -> Optional[UpdatePageRequest]:
        pass

    def _create_page(self, request: UpdatePageRequest) -> UpdatePageResponse:
        repo = self.page_repository
        dir_name = os.path.join(repo.root_dir, request.meta.page_name)
        os.mkdir(dir_name)
        meta = {
            "id": request.meta.page_id,
            "name": request.meta.page_name
        }
        meta_file = os.path.join(dir_name, "info.json")
        with open(meta_file, "w+") as output:
            json.dump(meta, output, indent=4)
        
        for op in filter(lambda x: isinstance(x, AddOp), request.operations):
            op: AddOp = op
            file_location = os.path.join(dir_name, op.file_name)
            with open(file_location, "w+") as output_file:
                output_file.write(op.data.decode("utf-8"))
        
        repo.append(dir_name)
        return UpdatePageResponse(status=Status.OK)

    def _update_page(self, operations: UpdatePageRequest) -> UpdatePageResponse:
        
        pass
