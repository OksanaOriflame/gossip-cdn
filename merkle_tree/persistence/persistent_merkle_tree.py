import os
import shutil
from typing import Optional, Tuple
from merkle_tree.persistence.page_versions import PageVersions
from ..merkle_tree import MerkleTree


class PersistentMerkleTree:
    def __init__(self, files, pageId, directory) -> None:
        self.pageId = pageId

        initial_merkle_tree = MerkleTree()
        initial_merkle_tree.build_from_files(files)

        self.directory = directory
        versions_repository = PageVersions(directory)
        self.versions_repository = versions_repository
        self.versions = versions_repository.check_inited()

        if len(self.versions) == 0:
            self.versions.append(initial_merkle_tree)
            self.versions_repository.init_commit(initial_merkle_tree)
        elif self.versions[-1].root_node.hash != initial_merkle_tree.root_node.hash:
            self.versions.append(initial_merkle_tree)
            self.versions_repository.append_version(initial_merkle_tree)
    
    def get_version(self, hash: str):
        versions = self.versions
        suitable_versions = list(filter(lambda x: x.root_node.hash == hash, versions))
        if len(suitable_versions) < 1:
            raise Exception(f"Version {hash} not found")
        return suitable_versions[0]

    def determine_next_version(self, prev_version_hash: Optional[str]) -> Optional[MerkleTree]:
        versions = self.versions
        next_version = None
        if not prev_version_hash:
            return versions[0]
        for i in range(len(versions)):
            version = versions[i]
            if version.root_node.hash == prev_version_hash and i != len(versions) - 1:
                next_version = versions[i + 1]
                break
        
        if not next_version:
            return None
        
        return next_version
    
    def get_last_version(self) -> MerkleTree:
        return self.versions[-1]
    
    def create_new_version(self, merkle_tree: MerkleTree):
        self.versions_repository.append_version(merkle_tree)
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
            file_path = os.path.join(build_directory, leaf.file_location)
            blob_path = os.path.join(self.versions_repository.versions_dir, leaf.hash)
            shutil.copy(blob_path, file_path)
