import socket

import sys

# get the command-line arguments
arguments = sys.argv
port = int(arguments[1])


# create a socket object
s = socket.socket()

# get the local machine name
host = socket.gethostname()

# bind the socket to the host and port
s.bind((host, port))



with open("third/"+ str(port) +".costs") as f:
    lines = f.readlines()
lines = [line.rstrip() for line in lines]
i = 0
for line in lines:
    lines[i] = line.split(" ")
    k=0
    for e in lines[i]:
        lines[i][k] = int(e)
        k = k+1
    i = i+1
print(lines)
node_count = int(lines[0][0])
lines.pop(0)

print(node_count)
nodes = []
nodes.append([port,0])
for k in range(len(lines)):
    nodes.append(lines.pop(0))
print(nodes)


# send some data
data = "Hello, world!"
s.send(data.encode())

# receive data
data = s.recv(1024)
print(data.decode())