from nodes.cdn_node import CdnNode
from argparse import ArgumentParser


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
    parser.add_argument('--nb-host', type=str, default=None)
    parser.add_argument('--nb-port', type=int, default=-1)

    return parser.parse_args()

def main():
    args = parse_args()
    neighbour_addr = None

    if args.nb_host and args.nb_port > 0:
        neighbour_addr = (args.nb_host, args.nb_port)
    
    node = CdnNode(args.host, args.port)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()

if __name__ == '__main__':
    main()
