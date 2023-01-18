import json
import os
from typing import Dict, List, Optional, Tuple
from merkle_tree.merkle_tree import MerkleTree
from merkle_tree.pages.page import Page
from merkle_tree.pages.page_repository import PageRepository
from merkle_tree.persistence.update_transaction import UpdateTransaction
from merkle_tree.tree_nodes.merkle_leaf import MerkleLeaf
from nodes.models.operation import AddOp, ModifyOp, RemoveOp
from nodes.models.queries import Meta, Status, UpdatePageRequest, UpdatePageResponse


class PagesUpdaterBase:
    def __init__(self, cdn_node_directory: str) -> None:
        page_repository = PageRepository(cdn_node_directory)
        page_repository.build()
        self.pages: Dict[str, Page] = {x.merkle_tree.pageId: x for x in page_repository.pages}
        self.page_repository = page_repository
    
    def _create_page(self, request: UpdatePageRequest) -> UpdatePageResponse:
        repo = self.page_repository
        dir_name = os.path.join(repo.root_dir, request.meta.page_name)
        os.mkdir(dir_name)
        meta = {
            "id": request.meta.page_id,
            "name": request.meta.page_name
        }
        meta_file = os.path.join(dir_name, "info.json")
        with open(meta_file, "w+") as output:
            json.dump(meta, output, indent=4)
        
        for op in filter(lambda x: isinstance(x, AddOp), request.operations):
            op: AddOp = op
            file_location = os.path.join(dir_name, op.file_name)
            with open(file_location, "wb+") as output_file:
                output_file.write(op.data)
        
        try:
            repo.append_requested_page(dir_name, request.root_hash)
        except Exception as e:
            return UpdatePageResponse(status=Status.ERROR)
        return UpdatePageResponse(status=Status.OK)

    def _update_page(self, operations: UpdatePageRequest) -> UpdatePageResponse:
        page = self.pages[operations.page_id]
        update_transaction = UpdateTransaction(page, operations)
        return update_transaction.apply()

    def _get_update_operations(self, page: Page, prev_version_hash: Optional[str], next_version_tree: MerkleTree) -> UpdatePageRequest:
        next_version_hash = next_version_tree.root_node.hash
        prev_version_leafs = [] if not prev_version_hash else  page.merkle_tree.get_version(prev_version_hash).leafs
        next_version_leafs = next_version_tree.leafs

        both_has_leafs = []
        for prev_leaf in prev_version_leafs:
            for next_leaf in next_version_leafs:
                if prev_leaf.hash == next_leaf.hash and prev_leaf.file_location == next_leaf.file_location:
                    both_has_leafs.append(prev_leaf)
        
        extra_prev_leafs = [x for x in prev_version_leafs if x not in both_has_leafs]
        extra_next_leafs = [x for x in next_version_leafs if x not in both_has_leafs]

        same_names_leafs = [(prev, next) for prev in extra_prev_leafs for next in extra_next_leafs if prev.file_name == next.file_name]
        
        leafs_to_remove = []
        for prev_leaf in extra_prev_leafs:
            is_next_has = False
            for next_leaf in extra_next_leafs:
                if prev_leaf.file_name == next_leaf.file_name:
                    is_next_has = True
                    break
            if not is_next_has:
                leafs_to_remove.append(prev_leaf)
        
        leafs_to_append = []
        for next_leaf in extra_next_leafs:
            is_prev_has = False
            for prev_leaf in extra_prev_leafs:
                if prev_leaf.file_name == next_leaf.file_name:
                    is_prev_has = True
                    break
            if not is_prev_has:
                leafs_to_append.append(next_leaf)
        
        add_ops = self._to_add_ops(leafs_to_append, page)
        remove_ops = self._to_remove_ops(leafs_to_remove)
        modify_ops = self._to_modify_ops(same_names_leafs, page)
        meta = Meta(page_id=page.id, page_name=page.name)

        return UpdatePageRequest(
            page_id=page.id, 
            prev_version=prev_version_hash, 
            operations=[*remove_ops, *add_ops, *modify_ops], 
            root_hash=next_version_hash,
            meta=meta)

    def _to_add_ops(self, leafs: List[MerkleLeaf], page: Page) -> List[AddOp]:
        ops = []
        for leaf in leafs:
            data_bytes = page.merkle_tree.versions_repository.get_file_content_bytes(leaf.hash)
            new_op = AddOp(file_name=leaf.file_name, data=data_bytes)
            ops.append(new_op)

        return ops

    def _to_remove_ops(self, leafs: List[MerkleLeaf]) -> List[RemoveOp]:
        ops = [RemoveOp(file_name=leaf.file_name, hash=leaf.hash) for leaf in leafs]
        return ops
    
    def _to_modify_ops(self, leafs: List[Tuple[MerkleLeaf, MerkleLeaf]], page: Page) -> List[ModifyOp]:
        ops = []
        for prev, next in leafs:
            data_bytes = page.merkle_tree.versions_repository.get_file_content_bytes(next.hash)
            new_op = ModifyOp(file_name=prev.file_name, hash=prev.hash, data=data_bytes)
            ops.append(new_op)
        
        return ops
