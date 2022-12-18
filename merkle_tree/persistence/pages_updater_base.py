import json
import os
from typing import Dict
from merkle_tree.Pages.page import Page
from merkle_tree.Pages.page_repository import PageRepository
from nodes.models.operation import AddOp
from nodes.models.queries import Status, UpdatePageRequest, UpdatePageResponse


class PagesUpdaterBase:
    def __init__(self, cdn_node_directory: str) -> None:
        page_repository = PageRepository(cdn_node_directory)
        page_repository.build()
        self.pages: Dict[str, Page] = {x.merkle_tree.pageId: x.merkle_tree for x in page_repository.pages}
        self.page_repository = page_repository
    
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

    def _get_update_operations(self, prev_version_hash: str, next_version_hash: str) -> UpdatePageRequest:
        
        pass