import json
import os
import shutil
from typing import List, Tuple
from merkle_tree.hasher import Hasher
from merkle_tree.merkle_tree import MerkleTree
from merkle_tree.pages.read_text_file import read_text_file
from merkle_tree.tree_nodes.merkle_leaf import MerkleLeaf

from nodes.models.queries import UpdatePageRequest


class PageVersions:
    def __init__(self, directory) -> None:
        self.directory = directory
        versions_dir = os.path.join(directory, ".versions")
        if not os.path.isdir(versions_dir):
            os.mkdir(versions_dir)
        self.versions_dir = versions_dir
    
    def check_inited(self) -> List[MerkleTree]:
        versions_file = os.path.join(self.versions_dir, "versions.json")
        if not os.path.isfile(versions_file):
            return []
        with open(versions_file, "r") as outfile:
            versions = json.load(outfile)
        result: List[MerkleTree] = []
        for version_hash in versions["versions"]:
            version_file = os.path.join(self.versions_dir, f"{version_hash}.version.json")
            with open(version_file, "r") as outfile:
                version = json.load(outfile)
            merkle_tree = MerkleTree()
            merkle_leafs = list(map(lambda x: MerkleLeaf(x["hash"], x["file_name"]), version["leafs"]))
            merkle_tree.build_from_leafs(merkle_leafs)
            result.append(merkle_tree)
        return result

    def init_commit(self, merkle_tree: MerkleTree):
        self._create_versions_file(merkle_tree)
        self._create_new_version_file(merkle_tree)
        self._commit_leafs(merkle_tree)
    
    def add_file(self, file_data) -> Tuple[bool, str]:
        hash = self.hash_hack(file_data)
        new_file = os.path.join(self.versions_dir, hash)
        if os.path.isfile(new_file):
            return True, hash
        with open(new_file, 'wb+') as outfile:
            outfile.write(file_data)
        return False, hash
    
    def hash_hack(self, data) -> str:
        temp_file_name = os.path.join(self.versions_dir, "temp_file")
        with open(temp_file_name, "wb+") as output_file:
            output_file.write(data)
        hash = Hasher.get_hash(read_text_file(temp_file_name))
        os.remove(temp_file_name)
        return hash
    
    def remove_file(self, hash) -> None:
        file_path = os.path.join(self.versions_dir, hash)
        if os.path.isfile(file_path):
            os.remove(file_path)
        
    def get_file_content_bytes(self, hash: str) -> bytes:
        file_location = os.path.join(self.versions_dir, hash)
        if not os.path.isfile(file_location):
            raise FileNotFoundError(f"No file {file_location}")
        with open(file_location, "rb") as outfile:
            return outfile.read()

    def append_version(self, tree: MerkleTree):
        self._create_new_version_file(tree)

        versions_file = os.path.join(self.versions_dir, "versions.json")
        with open(versions_file, "r") as outfile:
            versions = json.load(outfile)
        versions["versions"].append(tree.root_node.hash)
        with open(versions_file, 'w+') as outfile:
            json.dump(versions, outfile, indent=4)
        
        self.commit_new_files(tree, versions["versions"])
        print(f"Updated page version. New commit - {tree.root_node.hash}")

    def commit_new_files(self, merkle_tree: MerkleTree, versions: List[str]):
        last_version = versions[-1]
        prev_version = None if len(versions) == 1 else versions[-2]

        with open(os.path.join(self.versions_dir, f'{last_version}.version.json'), 'r') as f:
            last_version_leafs = json.load(f)["leafs"]
        
        if not prev_version:
            prev_version_leafs = []
        else:
            with open(os.path.join(self.versions_dir, f'{prev_version}.version.json'), 'r') as f:
                prev_version_leafs = set([leaf["hash"] for leaf in json.load(f)["leafs"]])
        
        leafs_to_append = [last_version_leaf for last_version_leaf in last_version_leafs if last_version_leaf["hash"] not in prev_version_leafs]

        for leaf in leafs_to_append:
            shutil.copy(leaf['file_name'], os.path.join(self.versions_dir, f'{leaf["hash"]}'))

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
            content_file_name = leaf.file_location
            blob_name = os.path.join(self.versions_dir, leaf.hash)
            shutil.copy(content_file_name, blob_name)
            

    def commit(self, operations: UpdatePageRequest):
        pass
