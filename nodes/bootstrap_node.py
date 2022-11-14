from typing import List
from nodes.node import Node


class BootstrapNode(Node):
    def __init__(self, ip: str, port: str) -> None:
        super().__init__(ip, port)
        self.nodes = None
        
    def insert(self, node: Node) -> None:
        # send node to bootstrap
        ...
    
    def sync_nodes(self) -> None:
        #send request to ip:port
        self.nodes = [Node("127.0.0.1", "5555"), 
                 Node("127.0.0.1", "5556"), 
                 Node("127.0.0.1", "5557")]
    
    def get_nodes(self) -> List[Node]:
        if not self.nodes or len(self.nodes) == 0:
            self.sync_nodes()
            
        return self.nodes