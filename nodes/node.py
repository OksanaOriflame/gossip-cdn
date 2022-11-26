from threading import Thread, Event, Lock
import socket 
from typing import Tuple, List, Dict
import select
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from  typing import Optional, Callable

Host = str
Port = int
Address = Tuple[Host, Port]
Connection = Tuple[socket.socket, Address]

class NodeType(Enum):
    Bootstrap = 0
    CDNNode = 1

@dataclass
class NodeInfo:
    addr: Address
    type: Optional[NodeType]


class Node(ABC):
    def __init__(self, ip: str, port: str) -> None:
        self._ip = ip
        self._port = port
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._curr_communication_node: Connection = None
        self._stop_event = Event()
        self._stop_timeout = 1
        self._new_data_handler: Thread = None
        self._new_connections_handler: Thread = None

    @abstractmethod
    def _handle_new_data(self, data: bytes, sender: socket.socket):
        pass
    
    @abstractmethod
    def _handle_new_connection(self, connection: Connection):
        pass

    def _new_data_reciver(self):
        print('Node started to recieve data')
        while not self._stop_event.is_set():
            if not self._curr_communication_node:
                self._stop_event.wait(self._stop_timeout)
                continue
            
            rd_sockets, _, _ = select.select([self._curr_communication_node[0]], [], [], 1)
            sockets_to_remove = []
            for rd_socket in rd_sockets:
                try:
                    data = rd_socket.recv(1024)
                except ConnectionResetError:
                    sockets_to_remove.append(rd_socket)
                    continue

                if not data:
                    sockets_to_remove.append(rd_socket)
                    continue
            
                self._handle_new_data(data, rd_socket)

    def _new_connections_reciver(self):
        print(f'Started to listen for new connections on {self._ip}:{self._port}')
        while not self._stop_event.is_set():
            try:
                connection = self._server_socket.accept()
                if self._curr_communication_node:
                    connection[0].close()
                    self._stop_event.wait(self._stop_timeout)
                    continue
                self._handle_new_connection(connection)

                self._curr_communication_node = connection
            except BlockingIOError:
                self._stop_event.wait(self._stop_timeout)
                continue

    def _initialize(self):
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen(1)
        self._server_socket.setblocking(0)
        self._new_data_handler = Thread(target=self._new_data_reciver)
        self._new_connections_handler = Thread(target=self._new_connections_reciver)
    
    def _finish(self):
        if self._curr_communication_node:
            self._curr_communication_node[0].close()
        
        self._server_socket.close()

    def stop(self):
        self._stop_event.set()

