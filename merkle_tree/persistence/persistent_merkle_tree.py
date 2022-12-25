
import os
import shutil
from typing import List
from merkle_tree.persistence.page_versions import PageVersions
from merkle_tree.tree_nodes.merkle_leaf import MerkleLeaf
from nodes.models.queries import UpdatePageRequest
from ..merkle_tree import MerkleTree


class PersistentMerkleTree:
    def __init__(self, files, pageId, directory) -> None:
        self.pageId = pageId
        initial_merkle_tree = MerkleTree()
        initial_merkle_tree.build_from_files(files)
        self.versions = [initial_merkle_tree]
        self.directory = directory
        self.versions_repository = PageVersions(directory)
        self.versions_repository.init_commit(initial_merkle_tree)
    
    def get_last_version(self) -> MerkleTree:
        return self.versions[-1]
    
    def create_new_version(self, merkle_tree: MerkleTree):
        self.versions.append(merkle_tree)
    
    def checkout(self, hash: str, build_directory: str):
        suitable_versions = list(filter(lambda x: x.root_node.hash == hash, self.versions))
        if len(suitable_versions) < 1:
            raise NotImplementedError(f"No commit with {hash} hash")
        target_version = suitable_versions[0]
        
        for file in os.listdir(build_directory):
            file_path = os.path.join(build_directory, file)
            if os.path.isdir(file_path) or file == "info.json":
                continue
            os.remove(file_path)
        
        for leaf in target_version.leafs:
            file_path = os.path.join(build_directory, leaf.file_name)
            blob_path = os.path.join(self.versions_repository.directory, leaf.hash)
            shutil.copy(blob_path, file_path)
