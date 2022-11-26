from threading import Thread, Event, Lock
import socket 
from typing import Tuple, List, Dict
import select

Host = str
Port = int
Address = Tuple[Host, Port]
Connection = Tuple[socket.socket, Address]
    
class Node:
    def __init__(self, ip: str, port: str) -> None:
        self._ip = ip
        self._port = port
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections: Dict[socket.socket, Address] = {}
        self._connections_lock = Lock()
        self._stop_event = Event()
        self._stop_timeout = 1

    def _handle_new_data(self):
        print('Node started to recieve data')
        while not self._stop_event.is_set():
            if not self._connections.keys():
                self._stop_event.wait(self._stop_timeout)
                continue
            
            rd_sockets, _, _ = select.select(list(self._connections.keys()), [], [], 1)
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
            
                print(data)
            
            with self._connections_lock:
                for rm_socket in sockets_to_remove:
                    addr = self._connections.pop(rm_socket)
                    print(f'Connection {addr} closed')

    def _handle_new_connections(self):
        print(f'Started to listen for new connections on {self._ip}:{self._port}')
        while not self._stop_event.is_set():
            try:
                connection = self._server_socket.accept()
                print('New connection', connection[1])
                with self._connections_lock:
                    self._connections[connection[0]] = connection[1]
            except BlockingIOError:
                self._stop_event.wait(self._stop_timeout)
                continue

    def _initialize(self):
        self._server_socket.bind((self._ip, self._port))
        self._server_socket.listen(10)
        self._server_socket.setblocking(0)
        self._new_data_handler = Thread(target=self._handle_new_data)
        self._new_connections_handler = Thread(target=self._handle_new_connections)
    
    def _finish(self):
        for socket in self._client_sockets:
            socket.close()
        
        self._server_socket.close()

    def stop(self):
        self._stop_event.set()

