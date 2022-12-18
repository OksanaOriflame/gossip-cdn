import json
import os
from typing import List

from merkle_tree.persistence.persistent_merkle_tree import PersistentMerkleTree

from ..exceptions.missing_metainfo_exception import MissingMetainfoException
from .page_file import PageFile
from .read_text_file import read_text_file

REQUIRED_METAINFO: List[str] = ["id", "name"]
IGNORED_FILES: List[str] = ["info.json", ".versions"]


class Page:
    def __init__(self, metainfo_file: str, directory: str) -> None:
        self.directory = directory
        self._metainfo_file = metainfo_file
        self.info: dict = None
        self.files: List[PageFile] = []
        self.merkle_tree = None
    
    def build(self) -> None:
        metainfo = json.loads(read_text_file(self._metainfo_file))
        self._metainfo = metainfo
        self.validate()

        self.id = metainfo["id"]
        self.name = metainfo["name"]
        self._fill_files()
        self.merkle_tree = PersistentMerkleTree(self, self.id, self.directory)
    
    def validate(self) -> None:
        if self._metainfo is None:
            raise MissingMetainfoException()
        
        for property in REQUIRED_METAINFO:
            if property not in self._metainfo:
                raise MissingMetainfoException()
    
    def _fill_files(self) -> None:
        page_dir = self.directory
        self.files = []
        for file in os.listdir(page_dir):
            if file in IGNORED_FILES:
                continue
            file_path = os.path.join(page_dir, file)
            self.files.append(PageFile(file_path, file))
    
    def get_files(self) -> List[PageFile]:
        return self.files
