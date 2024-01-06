import socket
import sys
def start_firewall_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((ip, port)) 
    except OSError as e:
        print("Bind failed:", e)
        sys.exit(1)
    server_socket.listen(5)
    print(f"Firewall server listening on {ip}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        data = client_socket.recv(1024).decode()
        print(f"Received data: {data} from {address}")

        # Implement your firewall logic here based on the received data
        # For simplicity, this example just prints the received data

        client_socket.send("Firewall processed the data".encode())
        client_socket.close()


if __name__=="__main__":
    start_firewall_server(socket.gethostname(),56236)
