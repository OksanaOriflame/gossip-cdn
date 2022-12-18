from typing import List
from hasher import Hasher
from page import Page
from tree_nodes.merkle_node import MerkleNode
from page_repository import PageRepository
from tree_nodes.merkle_leaf import MerkleLeaf


BuildUnit = str

class MerkleTree:
    def __init__(self, root_dir: BuildUnit = "C:/000/MM/DCS/gossip-cdn/cdn_data"):
        self.root_dir = root_dir
        self.page_repository = PageRepository(root_dir)
        self.page_repository.initialize()
        self.root_node = None
        self.root_nodes = list()

    def build(self):
        leafs = [MerkleLeaf(Hasher.get_hash(x), x.id) for x in self.page_repository.pages]
        root_node = self._build_tree(leafs)
        self.root_node = root_node
        self.root_nodes.append(root_node)
        print(root_node)
        
    def _build_tree(self, nodes: List[MerkleNode]) -> MerkleNode:
        node_pairs = list()
        for i in range(0, len(nodes), 2):
            if i + 1 == len(nodes):
                node_pairs.append((nodes[i], None))
            else:
                node_pairs.append((nodes[i], nodes[i + 1]))

        next_layer = list(map(lambda x: MerkleNode(Hasher.concat_node_hashes(x[0], x[1]), x[0], x[1]), node_pairs))
        if len(next_layer) == 1:
            return next_layer
        
        return self._build_tree(next_layer)

mt = MerkleTree()
mt.build()