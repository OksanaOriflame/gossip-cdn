import os

from ..Pages.page import Page


class PageVersionRepository:
    def __init__(self, directory, page: Page) -> None:
        self.directory = directory
        versions_dir = os.path.join(directory, ".versions")
        if not os.path.isdir(versions_dir):
            os.mkdir(versions_dir)
        self.versions_dir = versions_dir

    
    def commit(self, operations):
        