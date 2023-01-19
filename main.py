import os
from merkle_tree.persistence.pages_updater import PagesUpdater
from nodes.cdn_node import CdnNode
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()

    parser.add_argument('port', type=int, default=3228)
    parser.add_argument('--cdn-folder', type=str, default=os.path.join(os.getcwd(), "cdn_data"))
    parser.add_argument('--bootstrap-addr', type=str, default='localhost:3333')
    return parser.parse_args()

def main():
    args = parse_args()
    pages_updater = PagesUpdater(args.cdn_folder)
    bootstrap_addr = tuple(args.bootstrap_addr.split(':'))
    bootstrap_addr = (bootstrap_addr[0], int(bootstrap_addr[1]))

    node = CdnNode(args.port, pages_updater, bootstrap_addr)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()

if __name__ == '__main__':
    main()
