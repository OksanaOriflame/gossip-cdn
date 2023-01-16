import socket
from threading import Lock, Thread
from typing import Dict, List, Optional, Set
from nodes.node import Node, Address
from nodes.node import Connection
import select
import time
from pydantic import BaseModel


class NodesState(BaseModel):
    neighbours: List[Address]

class BootstrapNode(Node):
    def __init__(self, port: str) -> None:
        super().__init__(port)
        self._nodes: Dict[socket.socket, Address] = {}
        self._nodes_lock: Lock = Lock()
        self._nodes_acessable_ttl: int = 4

    def _handle_new_connection(self, connection: Connection):
        sock, addr = connection
        try:
            rd_sockets, _, _ = select.select([sock], [], [], 3)
            if not rd_sockets:
                sock.close()
                return
            
            rd_socket = rd_sockets[0]
            actual_port = rd_socket.recv(1024).decode('utf-8')
        except Exception as e:
            print(e)

        with self._nodes_lock:
            self._nodes[sock] = (addr[0], int(actual_port))
            print('New node = ', (addr[0], int(actual_port)))
    
    def _run(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(1)

            print(self._nodes)
            if not self._nodes:
                continue
            
            nodes_to_remove = []
            nodes = set(self._nodes.keys())
            for node in nodes:
                try:
                    nodes_addrs = [self._nodes[_node] for _node in nodes if _node != node]
                    request = NodesState(neighbours=nodes_addrs)
                    node.sendall(request.json().encode('utf-8'))
                except Exception as e:
                    nodes_to_remove.append(node)
                    print(e)

            self._stop_event.wait(self._nodes_acessable_ttl)

            rd_sockets, _, _ = select.select(list(nodes), [], [], 1)

            for rd_socket in rd_sockets:
                try:
                    data = rd_socket.recv(1024)
                except Exception:
                    nodes_to_remove.append(rd_socket)
                    continue
                
                if not data or not data == b'alive':
                    nodes_to_remove.append(rd_socket)

            nodes_to_remove.extend(nodes - set(rd_sockets))

            with self._nodes_lock:
                for node in nodes_to_remove:
                    self._nodes.pop(node)

    def start(self):
        self._initialize()
        self._new_connections_handler.start()
        self._run()
        self._new_connections_handler.join()