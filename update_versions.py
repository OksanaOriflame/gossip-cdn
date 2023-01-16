import os
from merkle_tree.persistence.pages_updater import PagesUpdater
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--cdn-folder', type=str, default=os.path.join(os.getcwd(), "cdn_data"))

    return parser.parse_args()

def main():
    args = parse_args()
    PagesUpdater(args.cdn_folder)
    print("Up to date")
    

if __name__ == '__main__':
    main()
