import socket
from threading import Thread
from nodes.node import Node, Address
from nodes.merkle_tree import MerkleTree

class CdnNode(Node, MerkleTree, Thread):
    def __init__(self, ip: str, port: int, neighbour_addr: Address = None):
        super().__init__(ip, port)
        self._neighbour_addr: Address = neighbour_addr
        self._communicate_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._bootstrap_addr = bootstrap_addr
    
    def _initialize(self):
        super()._initialize()

    def _connect_to_neighbour(self):
        self._communicate_socket.connect(self._neighbour_addr)
        with self._connections_lock:
            self._connections[self._communicate_socket] = self._neighbour_addr
    
    def start(self) -> None:
        # neighbours = self.bootstrap_node.get_nodes()
        # self.spreader = GossipSpreader(neighbours)
        self._initialize()
        #TODO: Add gossipSpreader
        self._new_data_handler.start()
        self._new_connections_handler.start()
        
        if self._neighbour_addr:
            self._connect_to_neighbour()

        while not self._stop_event.is_set():
            self._stop_event.wait(self._stop_timeout)
        
        self._new_data_handler.join()
        self._new_connections_handler.join()

    def dispose(self) -> None:
        self.spreader.dispose()
