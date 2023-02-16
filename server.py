import socket
from _thread import *
import threading

# keep track of which clients are connected
client_connected = []

# create a dictionary called accounts to store all the accounts created by the client
accounts = {}
messages = {}

p_lock = threading.Lock()

def threaded(c):

    while True:
        data_list=[]
        # data received from client
        data = c.recv(1024)
        data_str = data.decode('UTF-8')
        if not data:
            print('Bye')
            break
        print(data_str+"\n")
        #data_str = str(data)
        data_list = data_str.split()
        opcode = data_list[0]
        #opcode = opcode_b[2:]
        print("Opcode:" + str(opcode))

        if opcode == "create":
            username = data_list[1]
            if username in accounts:
                c.send(f"Username '{username}' is already taken\n".encode())
            else:
                accounts[username] = []
                c.send(f"Account '{username}' created\n".encode())

            #list an account
        elif opcode == "list":
            c.send("\n".join(accounts.keys()).encode() + b"\n")

        elif opcode == "login":
            username = data_list[1]
            if username in accounts:
                p_lock.acquire()
                client_connected.append(username)
                p_lock.release()
                c.send(f"Successfully logged in to account '{username}'\n".encode())
            else:
                c.sendall(f"Account '{username}' not found\n".encode())

            # send message to recipient
            # send message to recipient
        elif opcode == "send":
            recipient = data_list[1]
            if recipient in accounts:
                if recipient in client_connected:
                    accounts[recipient].sendall("Message from {}: {}\n".format(data_list[2], " ".join(call[3:])).encode())
                    c.sendall(f"Message sent to {recipient}\n".encode())
                else:
                    if recipient in messages:
                        messages[recipient].append("Message from {}: {}\n".format(data_list[2], " ".join(call[3:])))
                    else:
                        messages[recipient] = ["Message from {}: {}\n".format(data_list[2], " ".join(call[3:]))]
                    c.sendall(f"Message sent to {recipient}\n".encode())
            else:
                c.sendall("Recipient not found\n".encode())
            # deliver undel
        elif opcode == "deliver":
            username = data_list[1]
            if username in messages:
                c.send("\n".join(messages[username]).encode() + b"\n")
                del messages[username]
            else:
                c.send("No undelivered messages\n".encode())

            # delete an account
        elif opcode == "delete":
            username = data_list[1]
            if username in accounts:
                if username in messages:
                    c.send(f"Cannot delete account {username}. It has undelivered messages.\n".encode())
                else:
                    del accounts[username]
                    c.send(f"Account {username} deleted.\n".encode())
            else:
                c.send(f"Account {username} not found.\n".encode())

    c.close()

def Main():

    host = "127.0.0.1"
 
    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 2048
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)
 
    # put the socket into listening mode
    s.listen(5)
    print("socket is listening")
 
    # a forever loop until client wants to exit
    while True:
 
        # establish connection with client
        c, addr = s.accept()      
        print('Connected to :', addr[0], ':', addr[1])
 
        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    
    s.close()
 
 
if __name__ == '__main__':
    Main()
