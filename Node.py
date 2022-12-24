# METU CENG435 Take-Home-Exam-3  Fall2022  
# Kasım Pamuk 2375657
import select
import threading
import socket
import time
import sys

MAX = 10000000 #max value like inf

host = socket.gethostname()
arguments = sys.argv
port = int(arguments[1])

with open(str(port) +".costs") as f: #get info from costs file
    lines = f.readlines()
lines = [line.rstrip() for line in lines]

node_count = int(lines[0]) #no of nodes in graph
lines.pop(0)

costs = [] #list to keep distance informations. 0 for 3000, 1 for 3001,etc
neighbors = {} #dictionary to keep neighbors(dictionary is good to show relations in our case)
sockets = {} #dictionary to keep connection sockets

for line in lines:
    n_port, dist = line.split()
    neighbors[int(n_port)] = int(dist)

for k in range(node_count):
    costs.append(MAX) #initilize costs with inf values

costs[port-3000] = 0 #cost to itself, nothing

for n_port in neighbors.keys():
    costs[n_port-3000] = neighbors[n_port] #costs to neighbors

lock = threading.Lock() #lock

def broadcast(): #func to broadcast cost table to all neighbors
    messg = '/' #initialize a message to send all neighbors
    for n in range(node_count): #add all rows of cost table to message string
        n_port = n+3000
        row = str(port) + ' ' + str(n_port) + ' ' + str(costs[n]) + '#'
        messg += row

    for sock in sockets: #send the created messages to all neighbors
        sockets[sock].send(messg.encode())

# thread to connect bigger port numbers
def connect_thread(port):
    for n_port in neighbors.keys():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if(n_port > port):
            while True: # loop to try connecting until success
                try:
                    sock.connect((host, int(n_port)))
                    lock.acquire()
                    sockets[n_port] = sock
                    #print("sockets: port=" +str(port) +str(sockets)+"\n")
                    #print(str(port)+ " CONNECTED TO: "+ str(n_port) + "\n")
                    lock.release()
                    break
                except:
                    pass

# thread to get connection from smaller ports
def get_conn_thread(port):
    #create socket to listen in defined node port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #reuse ports if still not closed
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    sock.bind((host, port)) #bind to defined port

    sock.listen() #listen

    for n_port in neighbors.keys(): #accept connections and store them in sockets dictionary
        if(n_port < port):
            conn, addr = sock.accept()
            lock.acquire() 
            sockets[n_port] = conn
            # print(n_port)
            lock.release()

recieve_thread = threading.Thread(target=get_conn_thread, args=(port,)) #thread to get conections
send_thread = threading.Thread(target=connect_thread, args=(port,)) #thread to connect others

recieve_thread.start()  #start threads
send_thread.start()

recieve_thread.join()   #join threads
send_thread.join()

broadcast() #start by broadcasting costs to all neighbors
    
start = time.time()
while True: #main loop
    smt_new = False

    for s_index in sockets: #for each connection check for new data
        data = '' #initialize data

        is_new_data = select.select([sockets[s_index]], [], [], 0.05) #store the info if any new data arrived

        if(is_new_data[0]): #if there is a new data arrived store it in data variable
            data = sockets[s_index].recv(1024).decode()
        # print('Received data: ', data)

        if(data != ''): #if data is not empty

            data = data.split("/") #split data if two messages collapsed
            data.pop(0) #ignore first element

            for i in range(len(data)): #for every message taken inside data
                if data[i] != '':
                    data[i] = data[i].split("#") #split data into rows
            #print("data = " + str(data) + "\n")
        else:
            continue
        
        for k in range(len(data)):
            for i in range(len(data[k])):
                if(data[k] != '' and data[k][i] != ''):
                    m_data = data[k][i].split(' ') #split each message to neighbor port, node port, and cost of neighbor to that node
                    m_nport = int(m_data[0])
                    m_node = int(m_data[1])
                    m_cost = int(m_data[2])

                    if(m_cost + costs[m_nport-3000] < costs[m_node-3000]): #update costs table if cheaper
                        costs[m_node-3000] = m_cost + costs[int(m_nport)-3000] 
                        start = time.time()
                        smt_new = True

    if(smt_new): #broadcast if anything updated in the costs table
        broadcast()
    
    smt_new = False

    if(time.time() > start +5): #end the main loop if nothing new in 5 seconds
        break

for node_index in range(len(costs)): #print output in desired format
    n_port = node_index+3000
    cost = str(costs[node_index])
    if(costs[node_index] == MAX):
        cost = 'inf'
    print(str(port) + ' - ' + str(n_port) + ' | ' + cost)  