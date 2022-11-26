import socket
from threading import Thread
from nodes.bootstrap_node import BootstrapNode
from nodes.node import Node, Address, Connection
from nodes.merkle_tree import MerkleTree
from typing import Optional, List, Callable

class CdnNode(Node, Thread):
    def __init__(
        self, 
        ip: str, 
        port: int, 
        web_folder: Optional[str] = None
    ):
        super().__init__(ip, port)
        self._merkle_tree = MerkleTree()
        self._update_timeout = 2
        self._bootstrap_node = BootstrapNode('localhost', 3333)
        self._neighbours: List[Address] = None
        self._updater: Thread = None
        
    def _handle_new_data(self, data: bytes, sender: socket.socket):
        print(data)
        data_str = data.decode('utf-8')

        #Впервые общается с этим соседом
        if 'I\'m' in data_str:
            ip, port = data_str.split(' ')[1].split(':')
            port = int(port)
            self._curr_communication_node = (sender, (ip, port))

    def _handle_new_connection(self, connection: Connection):
        print('New connection', connection[1])
    
    def _choose_neighbour(self) -> Address:
        return [nb for nb in self._neighbours if nb != (self._ip, self._port)][0]
    
    def _try_create_curr_neighbour(self):
        neighbour_to_send_addr = self._choose_neighbour()   
        nb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            nb_socket.connect(neighbour_to_send_addr)
            nb_socket.sendall(f'I\'m {self._ip}:{self._port}'.encode('utf-8'))
            self._curr_communication_node = (nb_socket, neighbour_to_send_addr)
        except:
            print(f'Failed to connect to {neighbour_to_send_addr}')

    def _updater_func(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._update_timeout)
            if not self._curr_communication_node:
                self._try_create_curr_neighbour()
                continue
            
            try:
                self._curr_communication_node[0] \
                    .sendall(f'Some data from {self._ip}:{self._port}' \
                    .encode('utf-8'))

            except Exception:
                self._curr_communication_node = None
    
    def _initialize(self):
        super()._initialize()
        self._neighbours = self._bootstrap_node.get_neighbours()
        self._updater = Thread(target=self._updater_func)
    
    def start(self) -> None:
        # neighbours = self.bootstrap_node.get_nodes()
        # self.spreader = GossipSpreader(neighbours)
        self._initialize()
        #TODO: Add gossipSpreader
        self._new_data_handler.start()
        self._new_connections_handler.start()
        self._updater.start()

        while not self._stop_event.is_set():
            self._stop_event.wait(self._stop_timeout)
        
        self._new_data_handler.join()
        self._new_connections_handler.join()
        self._updater.join()

    def dispose(self) -> None:
        self.spreader.dispose()
