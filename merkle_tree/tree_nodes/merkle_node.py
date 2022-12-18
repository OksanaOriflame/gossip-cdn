import json


class MerkleNode:
    def __init__(self, hash: str, left, right) -> None:
        self.hash = hash
        self.right = right
        self.left = left
    
    def is_leaf(self):
        return False

    def __repr__(self) -> str:
        if not self.left:
            left = "null"
        else:
            left = self.left

        if not self.right:
            right = "null"
        else:
            right = self.right
          
        return json.dumps(json.loads(f'{{"hash":"{self.hash}", "is_leaf":"{self.is_leaf()}", "left":{left}, "right":{right}}}'), indent=4)