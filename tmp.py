import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 3333))
s.sendall(b'localhost:3228')

while True:
    print(s.recv(1024))
    s.sendall(b'pong')
    time.sleep(3)