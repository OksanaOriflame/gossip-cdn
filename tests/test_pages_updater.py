from merkle_tree.persistence.pages_updater import PagesUpdater
from nodes.models.queries import (
    GetPageVersionResponse, 
    GetPageVersionRequest, 
    UpdatePageRequest, 
    Meta, 
    UpdatePageResponse,
    Status
)
from nodes.models.operation import AddOp
import pytest
from tempfile import TemporaryDirectory
import os
from distutils.dir_util import copy_tree

@pytest.fixture
def cdn_dir() -> str:
    return 'tests\\resources\\pages'

@pytest.fixture
def page_meta() -> Meta:
    return Meta(
        page_id='index1',
        page_name='index1'
    )

@pytest.fixture
def tmp_cdn_dir(cdn_dir: str) -> str:
    with TemporaryDirectory(prefix='test_pages_updater_') as tmp_dir:
        cdn_dir = os.path.join(os.getcwd(), cdn_dir)
        copy_tree(cdn_dir, tmp_dir)
        yield tmp_dir


@pytest.fixture
def pages_updater(tmp_cdn_dir: str) -> PagesUpdater:
    return PagesUpdater(tmp_cdn_dir)


def test_pages_updater(pages_updater: PagesUpdater, page_meta: Meta):
    assert len(pages_updater.page_repository.pages) == 1
    assert pages_updater.get_random_page_id() == 'Not realized'

    get_page_version_request = GetPageVersionRequest(page_id="page_id_1")
    assert pages_updater.get_latest_version(get_page_version_request) == GetPageVersionResponse(page_id='page id mock', version='hash test')
    assert pages_updater.get_next_version("page_id", "version_hash") == None
    
    ops = [
        AddOp(file_name="index.txt", data="<script>Boooooooooba<script/>".encode("utf-8")),
        AddOp(file_name="index.css", data="{\ndddsadasdasdasd:popa\n}".encode("utf-8"))
    ]
    request = UpdatePageRequest(page_id=page_meta.page_id, prev_version="none", root_hash="sdoihsglk", meta=page_meta, operations=ops)
    response = pages_updater.update_page(request)
    assert response == None

    request = UpdatePageRequest(
        page_id="index2",
        prev_version="none",
        root_hash="sdoihsglk",
        meta=Meta(page_id="index2", page_name="index2"),
        operations=ops
    )
    response = pages_updater.update_page(request)
    assert response == UpdatePageResponse(status=Status.OK)
    assert len(pages_updater.page_repository.pages) == 2

