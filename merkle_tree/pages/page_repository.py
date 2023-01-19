from glob import glob
import os
import shutil
from typing import List, Optional
from .page import Page


class PageRepository:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.pages: List[Page] = list()
    
    def build(self) -> None:
        root_dir = os.path.join(self.root_dir, "*")
        for page_dir in glob(root_dir, recursive = False):
            self.append(page_dir)
    
    def append(self, page_dir: str):
        meta_file = os.path.join(page_dir, "info.json")
        page = Page(meta_file, page_dir)
        page.build()
        self.pages.append(page)
    
    def append_requested_page(self, page_dir: str, hash: str) -> str:
        meta_file = os.path.join(page_dir, "info.json")
        page = Page(meta_file, page_dir)
        page.build()
        if page.merkle_tree.get_last_version().root_node.hash != hash:
            shutil.rmtree(page_dir)
            del page
            raise Exception
        self.pages.append(page)
    
    def get_page(self, page_id: str) -> Optional[Page]:
        pages = list(filter(lambda x: x.id == page_id, self.pages))
        if len(pages) > 1:
            raise Exception(f"Pages repository contains multiple pages with id {page_id}")
        if len(pages) == 0:
            return None
        return pages[0]