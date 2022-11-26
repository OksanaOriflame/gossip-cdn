import hashlib

from exceptions.null_node_exception import NullNodeException
from tree_nodes.merkle_node import MerkleNode


class Hasher:
    @staticmethod
    def get_hash(page):
        full_str = "".join(page.get_pages_content())
        return hashlib.sha256(full_str.encode()).hexdigest()

    @staticmethod
    def concat_node_hashes(left: MerkleNode, right: MerkleNode):
        if not right:
            right = ""
        if not left:
            raise NullNodeException()
        full_str = f"{left.hash}{right.hash}"
        return hashlib.sha256(full_str.encode()).hexdigest()