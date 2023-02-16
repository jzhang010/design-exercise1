import socket
from _thread import *
import threading

accountName_table = {}
client_connected = {}
accounts = {}
messages = {}

def threaded(c):
    while True:
        data_list = []
        data = c.recv(1024)
        data_str = data.decode('UTF-8')
        if not data:
            print('Bye')
            break
        print(data_str+"\n")
        data_list = data_str.split('|')
        opcode = data_list[0]
        print ("Opcode:" + str(opcode))

        if opcode[0] == "create":
                username = opcode[1]
                if username in accounts:
                    c.sendall(f"Username '{username}' is already taken\n".encode())
                else:
                    accounts[username] = []
                    c.sendall(f"Account '{username}' created\n".encode())

            #list an accoutn
        elif opcode[0] == "list":
                c.sendall("\n".join(accounts.keys()).encode() + b"\n")

        elif opcode[0] == "login":
            username = opcode[1]
            if username in accounts:
                client_connected.add(username)
                c.sendall(f"Successfully logged in to account '{username}'\n".encode())
            else:
                c.sendall(f"Account '{username}' not found\n".encode())

            # send message to recipient
        elif opcode[0] == "send":
            recipient = opcode[1]
            if recipient in accounts:
                if recipient in client_connected:
                    accounts[recipient].sendall("Message from {}: {}\n".format(opcode[2], " ".join(opcode[3:])).encode())                        
                    c.sendall(f"Message sent to {recipient}\n".encode())
                else:
                    if recipient in messages:
                        messages[recipient].append("Message from {}: {}\n".format(opcode[2], " ".join(opcode[3:])))
                    else:
                        messages[recipient] = ["Message from {}: {}\n".format(opcode[2], " ".join(opcode[3:]))]
                        c.sendall(f"Message sent to {recipient}\n".encode())
            else:
                c.sendall("Recipient not found\n".encode())

            # deliver undelivered messages to a user
        elif opcode[0] == "deliver":
            username = opcode[1]
            if username in messages:
                c.sendall("\n".join(messages[username]).encode() + b"\n")
                del messages[username]                
            else:
                c.sendall("No undelivered messages\n".encode())

            # delete an account
        elif opcode[0] == "delete":
            username = opcode[1]
            if username in accounts:
                if username in messages:
                    c.sendall(f"Cannot delete account {username}. It has undelivered messages.\n".encode())
                else:
                    del accounts[username]
                    c.sendall(f"Account {username} deleted.\n".encode())
        else:
            c.sendall(f"Account {username} not found.\n".encode())

def Main():
    host = '10.250.170.49'
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    print("socket binded to port", port)

    s.listen(5)
    print("socket is listning")

    while True:
        c, addr = s.accept()
        print("Connected to :", addr[0], ":", addr[1])

        start_new_thread(threaded, (c,))
        
    s.close()

if __name__ == '__main__':
    Main()
