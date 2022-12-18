from glob import glob
import os
from typing import List
from .page import Page


class PageRepository:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.pages: List[Page] = list()
    
    def initialize(self) -> None:
        root_dir = os.path.join(self.root_dir, "*")
        for page_dir in glob(root_dir, recursive = False):
            page = Page(os.path.join(page_dir, "info.json"), page_dir)
            page.build()
            self.pages.append(page)
    