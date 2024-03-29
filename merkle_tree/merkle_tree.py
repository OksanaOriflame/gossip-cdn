from typing import List

from merkle_tree.pages.page_file import PageFile
from .hasher import Hasher
from .tree_nodes.merkle_node import MerkleNode
from .tree_nodes.merkle_leaf import MerkleLeaf


BuildUnit = str

class MerkleTree:
    def __init__(self):
        self.root_node: MerkleNode = None
        self.leafs: List[MerkleLeaf] = []

    def build_from_files(self, files: List[PageFile]):
        for file in files:
            leaf = MerkleLeaf(file.hash, file.location)
            self.leafs.append(leaf)
        self.leafs.sort(key=lambda x: x.hash)
        self.root_node = self._build_tree(self.leafs)
    
    def build_from_leafs(self, leafs: List[MerkleLeaf]):
        self.leafs = leafs
        self.leafs.sort(key=lambda x: x.hash)
        self.root_node = self._build_tree(self.leafs)

    def _build_tree(self, nodes: List[MerkleNode]) -> MerkleNode:
        node_pairs = list()
        for i in range(0, len(nodes), 2):
            if i + 1 == len(nodes):
                node_pairs.append((nodes[i], None))
            else:
                node_pairs.append((nodes[i], nodes[i + 1]))

        next_layer = list(map(lambda x: MerkleNode(Hasher.concat_node_hashes(x[0], x[1]), x[0], x[1]), node_pairs))
        if len(next_layer) == 1:
            return next_layer[0]
        
        return self._build_tree(next_layer)
