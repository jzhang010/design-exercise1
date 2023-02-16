import socket

def start_server():
    #starting the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.250.170.49', 12345))
    server_socket.listen(5)
    print("Server started, waiting for clients")

    # keep track of which clients are connected
    client_connected = []

    # create a dictionary called accounts to store all the accounts created by the client
    accounts = {}
    messages = {}

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected to by: {client_address}")
        client_socket.sendall(b"Welcome to the chat server!\n")

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            data = data.decode().strip()
            call = data.split()

            if len(call) == 0:
                continue

            #create an account
            if call[0] == "create":
                username = call[1]
                if username in accounts:
                    client_socket.sendall(f"Username '{username}' is already taken\n".encode())
                else:
                    accounts[username] = []
                    client_socket.sendall(f"Account '{username}' created\n".encode())

            #list an accoutn
            elif call[0] == "list":
                client_socket.sendall("\n".join(accounts.keys()).encode() + b"\n")

            elif call[0] == "login":
                username = call[1]
                if username in accounts:
                    client_connected.append(username)
                    client_socket.sendall(f"Successfully logged in to account '{username}'\n".encode())
                else:
                    client_socket.sendall(f"Account '{username}' not found\n".encode())

            # send message to recipient
            elif call[0] == "send":
                recipient = call[1]
                if recipient in accounts:
                    if recipient in client_connected:
                        accounts[recipient].sendall("Message from {}: {}\n".format(call[2], " ".join(call[3:])).encode())
                        client_socket.sendall(f"Message sent to {recipient}\n".encode())
                    else:
                        if recipient in messages:
                            messages[recipient].append("Message from {}: {}\n".format(call[2], " ".join(call[3:])))
                        else:
                            messages[recipient] = ["Message from {}: {}\n".format(call[2], " ".join(call[3:]))]
                        client_socket.sendall(f"Message sent to {recipient}\n".encode())
                else:
                    client_socket.sendall("Recipient not found\n".encode())

            # deliver undelivered messages to a user
            elif call[0] == "deliver":
                username = call[1]
                if username in messages:
                    client_socket.sendall("\n".join(messages[username]).encode() + b"\n")
                    del messages[username]
                else:
                    client_socket.sendall("No undelivered messages\n".encode())

            # delete an account
            elif call[0] == "delete":
                username = call[1]
                if username in accounts:
                    if username in messages:
                        client_socket.sendall(f"Cannot delete account {username}. It has undelivered messages.\n".encode())
                    else:
                        del accounts[username]
                        client_socket.sendall(f"Account {username} deleted.\n".encode())
                else:
                    client_socket.sendall(f"Account {username} not found.\n".encode())

        client_socket.close()
        print(f"Closed connection with {client_address}")

if __name__ == "__main__":
    start_server()
