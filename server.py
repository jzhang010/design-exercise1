import socket

def start_server():
    #starting the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('10.250.77.19', 12345))
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
                if call[1] in accounts and accounts[call[1]] == call[2]:
                    client_socket.send("Login successful\n".encode())
                    client_connected.append(client_socket)
                    if call[1] in messages:
                        for message in messages[call[1]]:
                            client_socket.send(message.encode())
                        messages[call[1]] = []
                else:
                    client_socket.send("Login failed\n".encode())

            elif call[0] == "send":
                recipient = call[1]
                if recipient in accounts:
                    if recipient in client_connected:
                        accounts[recipient].sendall("Message from {}: {}\n".format(call[2], " ".join(call[3:])).encode())
                    else:
                        if recipient in messages:
                            messages[recipient].append("Message from {}: {}\n".format(call[2], " ".join(call[3:])))
                        else:
                            messages[recipient] = ["Message from {}: {}\n".format(call[2], " ".join(call[3:]))]
                else:
                    client_socket.sendall("Recipient not found\n".encode())

            else:
                client_socket.sendall(b"Unknown command\n")

        client_socket.close()
        print(f"Closed connection with {client_address}")

if __name__ == "__main__":
    start_server()