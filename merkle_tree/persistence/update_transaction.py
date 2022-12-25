import copy
from typing import List
from merkle_tree.Pages.page import Page
from merkle_tree.merkle_tree import MerkleTree
from merkle_tree.tree_nodes.merkle_leaf import MerkleLeaf
from nodes.models.operation import AddOp, RemoveOp, ModifyOp
from nodes.models.queries import Status, UpdatePageRequest, UpdatePageResponse


class UpdateTransaction:
    def __init__(self, page: Page, update_request: UpdatePageRequest) -> None:
        self.page = page
        self.request = update_request
        self.leafs = copy.deepcopy(page.merkle_tree.get_last_version().leafs)
        self.files_to_revert_by_remove: List[str] = []
        
    def apply(self):
        try:
            for op in self.request.operations:
                if isinstance(op, AddOp):
                    self._add(op.data, op.file_name)
                elif isinstance(op, ModifyOp):
                    self._modify(op.data, op.hash, op.file_name)
                elif isinstance(op, RemoveOp):
                    self._remove(op.hash, op.file_name, op.file_name)
                else:
                    raise NotImplementedError(f"op type {type(op)} is unknown")
            new_merkle_tree = MerkleTree()
            new_merkle_tree.build_from_leafs(self.leafs)
            root_hash = new_merkle_tree.root_node.hash
            if root_hash != self.request.root_hash:
                raise Exception()
            self.page.merkle_tree.create_new_version(new_merkle_tree)
        except Exception as e:
            self._revert_changes()
            return UpdatePageResponse(Status.ERROR)
        
        self.page.update_to_last_version()
        return UpdatePageResponse(Status.ERROR)
    
    def _add(self, file_data: str, file_name: str):
        page = self.page
        existed, hash = page.merkle_tree.versions_repository.add_file(file_data)
        if not existed:
            self.files_to_revert_by_remove.append(hash)
        new_leaf = MerkleLeaf(hash, file_name)
        leafs = self.leafs
        leafs.append(new_leaf)
    
    def _remove(self, hash: str, file_name: str):
        leafs_to_remove = list(filter(lambda x: x.hash == hash and x.file_name == file_name, self.leafs))
        if len(leafs_to_remove) != 1:
            raise Exception
        self.leafs = list(filter(lambda x: x.hash != hash and x.file_name != file_name, self.leafs))
    
    def _modify(self, file_data: str, hash: str, file_name: str):
        self._remove(hash, file_name)
        self._add(file_data, file_name)

    def _revert_changes(self):
        for file in self.files_to_revert_by_remove:
            self.page.merkle_tree.versions_repository.remove_file(file)
