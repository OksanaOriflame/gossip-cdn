from ..hasher import Hasher
from .read_text_file import read_text_file


class PageFile:
    def __init__(self, location: str, name: str) -> None:
        self.location = location
        self.name = name
        self.hash = Hasher.get_hash(read_text_file(self.location))
