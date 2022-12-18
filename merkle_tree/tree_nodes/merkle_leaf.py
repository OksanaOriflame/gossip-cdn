from .merkle_node import MerkleNode


class MerkleLeaf(MerkleNode):
    def __init__(self, hash: str, page_id) -> None:
        self.id = page_id
        super().__init__(hash, None, None)
    
    def is_leaf(super):
        return True
