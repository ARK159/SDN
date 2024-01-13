# IDS Server

import socket

IDS_SERVER_IP = '0.0.0.0'  # Replace with the actual IP address
IDS_SERVER_PORT = 9999  # Replace with the desired port

def main():
    ids_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ids_server_socket.bind((IDS_SERVER_IP, IDS_SERVER_PORT))
    ids_server_socket.listen()

    print(f"IDS Server listening on {IDS_SERVER_IP}:{IDS_SERVER_PORT}")

    while True:
        client_socket, client_address = ids_server_socket.accept()
        print(f"Accepted connection from {client_address}")

        # Receive message from the client
        data = client_socket.recv(1024)
        print(f"Received message from client: {data.decode()}")

        # Process the message (you can implement IDS logic here)

        # Send a response back to the client
        response = "Message received successfully!"
        client_socket.sendall(response.encode())

        client_socket.close()

if __name__ == "__main__":
    main()
