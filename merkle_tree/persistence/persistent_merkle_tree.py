
from merkle_tree.persistence.page_versions import PageVersions
from ..merkle_tree import MerkleTree


class PersistentMerkleTree:
    def __init__(self, page, pageId, directory) -> None:
        self.pageId = pageId
        initial_merkle_tree = MerkleTree(page)
        initial_merkle_tree.build()
        self.versions = [initial_merkle_tree]
        self.directory = directory
        self.versions_repository = PageVersions(directory)
        self.versions_repository.init_commit(initial_merkle_tree)
