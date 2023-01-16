from nodes.bootstrap_node import BootstrapNode
from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()

    parser.add_argument('--port', type=int, default=3333)

    return parser.parse_args()

def main():
    args = parse_args()

    node = BootstrapNode(args.port)

    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()

if __name__ == '__main__':
    main()
