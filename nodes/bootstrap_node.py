import socket
from threading import Lock, Thread
from typing import Dict, List, Set
from nodes.node import Node, Address
from nodes.node import Connection
import select
import time

class BootstrapNode(Node):
    def __init__(self, ip: str, port: str) -> None:
        super().__init__(ip, port)
        self._nodes: Dict[socket.socket, Address] = {}
        self._nodes_lock: Lock = Lock()
        self._nodes_updater_timeout: int = 1

    def _handle_new_connection(self, connection: Connection):
        sock, addr = connection
        print(connection)
        try:
            data = sock.recv(1024).decode('utf-8')
            actual_host, actual_port = data.split(':')
        except Exception as e:
            print(e)

        with self._nodes_lock:
            self._nodes[sock] = (actual_host, int(actual_port))
            print('New node = ', (actual_host, int(actual_port)))

    def insert(self, node: Node) -> None:
        # send node to bootstrap
        pass
    
    def sync_nodes(self) -> None:
        #send request to ip:port
        self.nodes = [Node("127.0.0.1", "5555"), 
                 Node("127.0.0.1", "5556"), 
                 Node("127.0.0.1", "5557")]
    
    def get_nodes(self) -> List[Node]:
        if not self.nodes or len(self.nodes) == 0:
            self.sync_nodes()
            
        return self.nodes
    
    def get_neighbours(self) -> List[Address]:
        return [('localhost', 3228), ['localhost', 3229]]
    
    def _run(self):
        while not self._stop_event.is_set():
            with self._nodes_lock:
                if not self._nodes:
                    self._stop_event.wait(1)
                    continue
                
                start = time.monotonic()
                rd_sockets, _, _ = select.select(list(self._nodes.keys()), [], [], 5)
                end = time.monotonic()
                print(end - start)
                for rd_socket in rd_sockets:
                    data = rd_socket.recv(1024)
                    if not data:
                        removed_node = self._nodes.pop(rd_socket)
                        print('Removed node ', removed_node)
                        continue
                    
                    print(data)
                    # if data == b'alive':
    def start(self):
        self._initialize()
        self._new_connections_handler.start()
        self._run()
        self._new_connections_handler.join()
        # self._alive_nodes_handler.join()