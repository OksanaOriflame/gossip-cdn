import json
from .merkle_node import MerkleNode


class MerkleLeaf(MerkleNode):
    def __init__(self, hash: str, file_name: str) -> None:
        self.file_name = file_name
        super().__init__(hash, None, None)
    
    def is_leaf(super):
        return True

    def to_dict(self):
        return {
            "hash": self.hash,
            "is_leaf": self.is_leaf(),
            "file_name": self.file_name
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
