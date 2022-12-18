import socket
from threading import Thread
import select
from nodes.bootstrap_node import BootstrapNode
from nodes.node import Node, Address, Connection
from nodes.merkle_tree import MerkleTree
from typing import Optional, List
from nodes.models.queries import UpdatePageRequest, Meta
from nodes.models.operation import AddOp, RemoveOp, ModifyOp
from nodes.node import Node, Address
from merkle_tree.merkle_tree import MerkleTree

class CdnNode(Node, Thread):
    def __init__(
        self, 
        ip: str, 
        port: int, 
        is_sharing: bool = True,
        web_folder: Optional[str] = None
    ):
        super().__init__(ip, port)
        self._merkle_tree = MerkleTree()
        self._update_timeout = 2
        self._bootstrap_node = BootstrapNode('localhost', 3333)
        self._neighbours: List[Address] = None
        self._updater: Thread = None
        self._listener_connection: Connection = None
        self._share_connection: Connection = None
        self._is_sharing = is_sharing
    
    def _process_data(self, data: bytes, sender: socket.socket):
        print(data)
        data_str = data.decode('utf-8')

        #Впервые общается с этим соседом
        if 'I\'m' in data_str:
            ip, port = data_str.split(' ')[1].split(':')
            port = int(port)
                
    # Слушаем кого-то
    def _handle_new_connection(self, connection: Connection):
        print('New connection', connection[1])
        timeout = 1
        while not self._stop_event.is_set():
            rd_sockets, _, _ = select.select([connection[0]], [], [], timeout)
            # Весь процесс взаимодействия: отпправка и получение данных
            for rd_socket in rd_sockets:
                data = rd_socket.recv(1024)

                if not data:
                    print(f'Receiving data from {connection[1]} ended up')
                    return
                data_str = data.decode('utf-8')
                if "I\'m" in data_str:
                    print(data_str)
                    continue
            
                print(UpdatePageRequest.parse_raw(data_str))

    def _choose_neighbour(self) -> Address:
        return tuple([nb for nb in self._neighbours if nb != (self._ip, self._port)][0])
    
    def _connect_to_neighbour(self, addr: Address) -> Connection:  
        nb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nb_socket.connect(addr)
        nb_socket.sendall(f'I\'m {self._ip}:{self._port}'.encode('utf-8'))
        
        return (nb_socket, addr)

    # Делимся информацией 
    def _updater_func(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._update_timeout)
            neighbour_addr = self._choose_neighbour() 
            try:
                neighbour = self._connect_to_neighbour(neighbour_addr)
            except ConnectionError:
                print(f'Failed to connect to neighbour {neighbour_addr}. Trying again...')
                continue
            
            print(f'Connected to {neighbour_addr}')
            upd_page_req = UpdatePageRequest(
                page_id="id1", 
                prev_version="hash1", 
                operations=[
                    AddOp(file_name="index.html", data=b'some data'),
                    RemoveOp(file_name="hello.html", hash="hash3"),
                    ModifyOp(file_name="hello", hash="hash4", data=b'some data 2')
                ],
                root_hash="root_hash",
                meta=Meta(page_id="id2", page_name="name2"))
            
            while not self._stop_event.is_set():
                try:
                    # Весь процесс как мы делимся инфой: отправка данных, получение данных
                    neighbour[0].sendall(upd_page_req.json().encode('utf-8'))
                except ConnectionError as err:
                    print(f'Some error occured during sharing data: {err}')
                    break
                finally:
                    self._stop_event.wait(timeout=1)
    
    def _initialize(self):
        super()._initialize()
        self._neighbours = self._bootstrap_node.get_neighbours()
        self._updater = Thread(target=self._updater_func)
    
    def start(self) -> None:
        # neighbours = self.bootstrap_node.get_nodes()
        # self.spreader = GossipSpreader(neighbours)
        self._initialize()
        #TODO: Add gossipSpreader
        self._new_connections_handler.start()

        #Пока только либо делимся, либо слушаем
        if self._is_sharing:
            self._updater.start()

        while not self._stop_event.is_set():
            self._stop_event.wait(self._stop_timeout)
        
        self._new_connections_handler.join()

        if self._is_sharing:
            self._updater.join()
