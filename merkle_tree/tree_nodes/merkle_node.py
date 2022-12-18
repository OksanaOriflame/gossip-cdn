import json


class MerkleNode:
    def __init__(self, hash: str, left, right) -> None:
        self.hash = hash
        self.right = right
        self.left = left
    
    def is_leaf(self):
        return False

    def to_dict(self):
        if not self.left:
            left = "null"
        else:
            left = self.left.to_dict()

        if not self.right:
            right = "null"
        else:
            right = self.right.to_dict()

        return {
            "hash": self.hash,
            "is_leaf": self.is_leaf(), 
            "left":left,
            "right":right
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
