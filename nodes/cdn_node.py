import socket
from threading import Thread
import select
from merkle_tree.persistence.pages_updater import PagesUpdater
from nodes.bootstrap_node import BootstrapNode
from nodes.node import Node, Address, Connection
from typing import List
from nodes.models.queries import GetPageVersionRequest, GetPageVersionResponse, UpdatePageRequest

class CdnNode(Node, Thread):
    def __init__(
        self, 
        ip: str, 
        port: int, 
        pages_updater: PagesUpdater,
        is_sharing: bool = True
    ):
        super().__init__(ip, port)
        self._update_timeout = 2
        self._bootstrap_node = BootstrapNode('localhost', 3333)
        self._neighbours: List[Address] = None
        self._updater: Thread = None
        self._is_sharing = is_sharing
        self._pages_updater = pages_updater
    
    # Слушаем кого-то
    def _handle_new_connection(self, connection: Connection):
        pages_updater = self._pages_updater
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

                try:    
                    request = GetPageVersionRequest.parse_raw(data_str)
                    version_response = pages_updater.get_latest_version(request)
                    rd_socket.sendall(version_response.json().encode('utf-8'))
                    data = rd_socket.recv(1024)
                    if data:
                        update_page_request = UpdatePageRequest(data.decode('utf-8'))
                        update_page_response = pages_updater.update_page(update_page_request)
                        rd_socket.sendall(update_page_response.json().encode('utf-8'))
                except Exception as e:
                    print('Some error occured while recieving data ', e)

    def _choose_neighbour(self) -> Address:
        return tuple([nb for nb in self._neighbours if nb != (self._ip, self._port)][0])
    
    def _connect_to_addr(self, addr: Address) -> Connection:  
        nb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nb_socket.connect(addr)
        
        return (nb_socket, addr)

    def _share_with_neighbour(self, neighbour: Connection):
        pages_updater = self._pages_updater
        page_id = pages_updater.get_random_page_id()
        request = GetPageVersionRequest(page_id=page_id)
        neighbour[0].sendall(request.json().encode('utf-8'))

        data = neighbour[0].recv(1024)
        page_version_response = GetPageVersionResponse.parse_raw(data.decode('utf-8'))
        next_version = pages_updater.get_next_version(
            page_id=page_version_response.page_id,
            current_version=page_version_response.version
        )

        # За один раз происходит обновления до актуальной версии (while next_version)
        # Или на +1 версию?
        if not next_version:
            # its actual version, nothing to do
            neighbour[0].sendall(b'')
            return

        neighbour[0].sendall(next_version.json().encode('utf-8'))
    
    # Делимся информацией 
    def _updater_func(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._update_timeout)
            neighbour_addr = self._choose_neighbour() 
            try:
                neighbour = self._connect_to_addr(neighbour_addr)
            except ConnectionError:
                print(f'Failed to connect to neighbour {neighbour_addr}. Trying again...')
                continue
            
            print(f'Connected to {neighbour_addr}')
            
            try:
                self._share_with_neighbour(neighbour)
            except ConnectionError as err:
                print(f'Some error occured during sharing data: {err}')
                continue
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
