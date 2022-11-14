import sys
from signal import Signals, SIGINT, signal
from time import sleep
from nodes.bootstrap_node import BootstrapNode
from nodes.cdn_node import CdnNode

node = None

def interruption_handler(sig: Signals, frame) -> None:
    print("Interrupted")
    node.dispose()
    sys.exit(0)

# TODO:
# Определить входные аргументы аргументы (не помню, что там за библиотека была):
# - Адрес бутстрапа в формате {IP}:{PORT}
# - Где взять данные, которые этот узел поместит в cdn. Достаточно директории?
# - Возможно нужно ещё передавать свой адрес, потому что чаще всего мы будем
# запускать что-то на своих домашних машинках, а их адрес провайдер скорее всего
# прячет за своими натами, и к ним будет не достучаться извне.
# Возможно, следует сделать этот параметр опциональным, но нужно будет написать код,
# который на другом хостинге сможет понять свой адрес

if __name__ == "__main__":
    signal(SIGINT, interruption_handler)

    bootstrap = BootstrapNode("127.0.0.1", "7700")
    node = CdnNode(bootstrap, "127.0.0.1", "7701")
    node.start()
    while(True):
        sleep(2)
