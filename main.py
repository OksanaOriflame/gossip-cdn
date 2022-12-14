import os
from merkle_tree.Pages.page_repository import PageRepository
from merkle_tree.persistence.pages_updater import PagesUpdater
from nodes.cdn_node import CdnNode
from argparse import ArgumentParser
from nodes.models.operation import AddOp

from nodes.models.queries import Meta, UpdatePageRequest


# TODO:
# Определить входные аргументы аргументы (не помню, что там за библиотека была):
# - Адрес бутстрапа в формате {IP}:{PORT}
# - Где взять данные, которые этот узел поместит в cdn. Достаточно директории?
# - Возможно нужно ещё передавать свой адрес, потому что чаще всего мы будем
# запускать что-то на своих домашних машинках, а их адрес провайдер скорее всего
# прячет за своими натами, и к ним будет не достучаться извне.
# Возможно, следует сделать этот параметр опциональным, но нужно будет написать код,
# который на другом хостинге сможет понять свой адрес

def parse_args():
    parser = ArgumentParser()

    parser.add_argument('host', type=str, default='localhost')
    parser.add_argument('port', type=int, default=3228)
    parser.add_argument('--is-sharing', action='store_true')
    parser.add_argument('--cdn-folder', type=str, default=os.path.join(os.getcwd(), "cdn_data"))

    return parser.parse_args()

def main():
    args = parse_args()
    pages_updater = PagesUpdater(args.cdn_folder)
    node = CdnNode(args.host, args.port, pages_updater, args.is_sharing)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()

if __name__ == '__main__':
    main()

# updater = PagesUpdater("C:/000/MM/DCS/gossip-cdn/cdn_data")



# id = "sukkkaaaa"
# meta = Meta(page_id=id, page_name="page333")
# ops = [
#     AddOp(file_name="index.txt", data="<script>Boooooooooba<script/>".encode("utf-8")),
#     AddOp(file_name="index.css", data="{\ndddsadasdasdasd:popa\n}".encode("utf-8"))
# ]
# request = UpdatePageRequest(page_id=id, prev_version="none", root_hash="sdoihsglk", meta=meta, operations=ops)

# updater.update_page(request)

# for page in updater.page_repository.pages:
#     print(page.merkle_tree.versions[-1].root_node)