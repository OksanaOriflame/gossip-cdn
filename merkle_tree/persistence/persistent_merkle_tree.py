from typing import List
from ..merkle_tree import MerkleTree


class PersistentMerkleTree:
    def __init__(self, versions: List[MerkleTree], pageId, directory) -> None:
        self.pageId = pageId
        self.versions = versions
        self.directory = directory
    
