from threading import Event, Thread
from typing import List
from gossip.spread.spread import spread
from nodes.node import Node



class GossipSpreader():
    def __init__(self, neighbours: List[Node]) -> None:
        self.neighbours = neighbours

    def start(self) -> None:
        self.shutdown_event = Event()
        self.thread = Thread(target=spread(self.neighbours, self.shutdown_event))
        self.thread.start()

    def dispose(self) -> None:
        self.shutdown_event.set()
        self.thread.join()
        print("disposed")
    