import socket
from gossip.spread.gossip_spreader import GossipSpreader
from nodes.bootstrap_node import BootstrapNode
from nodes.node import Node


class CdnNode(Node):
    def __init__(self, bootstrap_node: BootstrapNode, ip: str, port: str) -> None:
        super().__init__(ip, port)
        self.bootstrap_node = bootstrap_node
        
    def start(self) -> None:
        neighbours = self.bootstrap_node.get_nodes()
        self.spreader = GossipSpreader(neighbours)
        self.spreader.start()
    
    def dispose(self) -> None:
        self.spreader.dispose()
