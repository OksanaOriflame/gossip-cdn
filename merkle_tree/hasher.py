import hashlib

from .exceptions.null_node_exception import NullNodeException
from .tree_nodes.merkle_node import MerkleNode


class Hasher:
    @staticmethod
    def get_hash(data: str):
        return hashlib.sha256(data.encode()).hexdigest()

    @staticmethod
    def concat_node_hashes(left: MerkleNode, right: MerkleNode):
        left_hash = left.hash
        if not right:
            right_hash = ""
        else:
            right_hash = right.hash
        if not left:
            raise NullNodeException()
        full_str = f"{left_hash}{right_hash}"
        return hashlib.sha256(full_str.encode()).hexdigest()