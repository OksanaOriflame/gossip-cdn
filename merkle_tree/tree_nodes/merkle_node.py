class MerkleNode:
    def __init__(self, hash: str, left, right) -> None:
        self.hash = hash
        self.right = right
        self.left = left
    
    def is_leaf(self):
        return False

    def __repr__(self) -> str:
        return f"hash:{self.hash}\nis_leaf={self.is_leaf()}\n\n{self.left}\n\n{self.right}"