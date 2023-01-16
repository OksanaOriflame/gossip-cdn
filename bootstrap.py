from nodes.bootstrap_node import BootstrapNode


def main():
    node = BootstrapNode(3333)

    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()

if __name__ == '__main__':
    main()
