from glob import glob
import json
import os
from typing import List
from page import Page
from read_text_file import read_text_file


class PageRepository:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.pages: List[Page] = list()
    
    def initialize(self) -> None:
        root_dir = os.path.join(self.root_dir, "*")
        for page_dir in glob(root_dir, recursive = False):

            metainfo = None
            for file in os.listdir(page_dir):
                file_path = os.path.join(page_dir, file)

                if file == "info.json":
                    metainfo = read_text_file(file_path)
            
            page = Page(json.loads(metainfo), page_dir)
            page.build()
            self.pages.append(page)
    