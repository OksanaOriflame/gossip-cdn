import json
from .merkle_node import MerkleNode


class MerkleLeaf(MerkleNode):
    def __init__(self, hash: str, file_name: str) -> None:
        self.file_name = file_name
        super().__init__(hash, None, None)
    
    def is_leaf(super):
        return True

    def __repr__(self) -> str:
        return json.dumps(json.loads(f'{{"hash":"{self.hash}", "is_leaf":"{self.is_leaf()}", "file_name":"{self.file_name}"}}'), indent=4)
