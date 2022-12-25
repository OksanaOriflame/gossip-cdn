from threading import Thread, Event, Lock
import socket 
from typing import Tuple, List, Dict
from abc import ABC, abstractmethod

Host = str
Port = int
Address = Tuple[Host, Port]
Connection = Tuple[socket.socket, Address]


class BaseNode:
    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port


class Node(BaseNode, ABC):
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._stop_event = Event()
        self._stop_timeout = 1
        self._new_connections_handler: Thread = None
    
    @abstractmethod
    def _handle_new_connection(self, connection: Connection):
        pass

    def _new_connections_reciver(self):
        print(f'Started to listen for new connections on {self._ip}:{self._port}')
        while not self._stop_event.is_set():
            try:
                connection = self._server_socket.accept()
                self._handle_new_connection(connection)
            except BlockingIOError:
                self._stop_event.wait(self._stop_timeout)
                continue

    def _initialize(self):
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen(1)
        # To use ctrl + c and can stop node
        self._server_socket.setblocking(0)
        self._new_connections_handler = Thread(target=self._new_connections_reciver)
    
    def _finish(self):
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()

    def stop(self):
        self._stop_event.set()

