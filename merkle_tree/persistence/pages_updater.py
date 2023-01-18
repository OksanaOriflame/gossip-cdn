from random import Random
from typing import Optional
from merkle_tree.persistence.pages_updater_base import PagesUpdaterBase
from nodes.models.queries import GetPageVersionRequest, GetPageVersionResponse, UpdatePageRequest, UpdatePageResponse


class PagesUpdater(PagesUpdaterBase):
    def __init__(self, cdn_node_directory: str) -> None:
        super().__init__(cdn_node_directory)

    def update_page(self, request: UpdatePageRequest) -> UpdatePageResponse:
        page = self.pages.get(request.page_id)
        if not page:
            return self._create_page(request)
        return self._update_page(request)

    def get_random_page_id(self) -> str:
        version_number = Random().randint(0, len(self.pages) - 1)
        return list(self.pages.keys())[version_number]
    
    def get_latest_version(self, request: GetPageVersionRequest) -> GetPageVersionResponse:
        page = self.pages.get(request.page_id)
        if not page:
            return GetPageVersionResponse(page_id=request.page_id, version=None)
        
        latest_version_hash = page.merkle_tree.versions[-1].root_node.hash
        return GetPageVersionResponse(page_id=request.page_id, version=latest_version_hash)

    def get_next_version(self, page_id: str, current_version: Optional[str]) -> Optional[UpdatePageRequest]:
        page = self.pages.get(page_id)
        if not page:
            raise FileNotFoundError(f"No {page_id} page")
        
        next_version = page.merkle_tree.determine_next_version(current_version)
        if not next_version:
            return None
        
        return self._get_update_operations(page, current_version, next_version)
