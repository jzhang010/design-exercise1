import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('10.250.170.49', 12345))
    print("Connected to server")

    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        print(data.decode(), end="")

        command = input("> ").strip()
        client_socket.sendall(command.encode() + b"\n")

    client_socket.close()
    print("Disconnected from server")

if __name__ == "__main__":
    start_client()
