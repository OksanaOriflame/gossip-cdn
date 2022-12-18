import json
import os
import shutil
from merkle_tree.merkle_tree import MerkleTree

from nodes.models.queries import UpdatePageRequest


class PageVersions:
    def __init__(self, directory) -> None:
        self.directory = directory
        versions_dir = os.path.join(directory, ".versions")
        if not os.path.isdir(versions_dir):
            os.mkdir(versions_dir)
        self.versions_dir = versions_dir

    def init_commit(self, merkle_tree: MerkleTree):
        self._create_versions_file(merkle_tree)
        self._create_new_version_file(merkle_tree)
        self._commit_leafs(merkle_tree)
    
    def _create_versions_file(self, merkle_tree: MerkleTree):
        versions = {
            "versions": [merkle_tree.root_node.hash]
        }
        versions_file = os.path.join(self.versions_dir, "versions.json")
        with open(versions_file, 'w+') as outfile:
            json.dump(versions, outfile, indent=4)
    
    def _create_new_version_file(self, merkle_tree: MerkleTree):
        new_version_leafs = [leaf.to_dict() for leaf in merkle_tree.leafs]
        new_version = {
            "leafs": new_version_leafs
        }
        version_file = os.path.join(self.versions_dir, f"{merkle_tree.root_node.hash}.version.json")
        with open(version_file, 'w+') as outfile:
            json.dump(new_version, outfile, indent=4)
        
    def _commit_leafs(self, merkle_tree: MerkleTree):
        for leaf in merkle_tree.leafs:
            content_file_name = leaf.file_name
            blob_name = os.path.join(self.versions_dir, leaf.hash)
            shutil.copy(content_file_name, blob_name)
            

    def commit(self, operations: UpdatePageRequest):
        pass