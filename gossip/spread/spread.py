import sys
from random import randint
from threading import Event
from time import sleep
from typing import List

from nodes.node import Node

SLEEP_TIME_SECONDS = 2


def spread(neighbours: List[Node], shutdown_event: Event) -> None:
    def _spread() -> None:
        while(not shutdown_event.is_set()):
            target_node = neighbours[randint(0, len(neighbours) - 1)]
            print(f"sent to {target_node.ip}:{target_node.port}")
            sleep(SLEEP_TIME_SECONDS)
        sys.exit()
    return _spread
