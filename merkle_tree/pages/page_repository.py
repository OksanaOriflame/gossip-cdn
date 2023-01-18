from glob import glob
import os
import shutil
from typing import List
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