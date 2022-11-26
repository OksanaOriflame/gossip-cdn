import os
from typing import List

from exceptions.missing_metainfo_exception import MissingMetainfoException
from read_text_file import read_text_file

REQUIRED_METAINFO: List[str] = ["id", "name"]


class Page:
    def __init__(self, metainfo: dict, directory) -> None:
        self.directory = directory
        self._metainfo = metainfo
        self.info: dict = None
    
    def build(self):
        self.validate()
        
        metainfo = self._metainfo

        self.id = metainfo["id"]
        self.name = metainfo["name"]
    
    def validate(self):
        if self._metainfo is None:
            raise MissingMetainfoException()
        
        for property in REQUIRED_METAINFO:
            if property not in self._metainfo:
                raise MissingMetainfoException()
    
    def get_pages_content(self) -> List[str]:
        page_dir = self.directory
        for file in os.listdir(page_dir):
            file_path = os.path.join(page_dir, file)
            yield read_text_file(file_path)
