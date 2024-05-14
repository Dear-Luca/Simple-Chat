from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


PORT = 8080
HOST = input("Type the address of the server: ")
BUFFER = 1024

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = client_socket.recv(BUFFER).decode()
            print(msg)
        except OSError:
            break


receive_thread = Thread(target=receive)
receive_thread.start()

while True:
    message = input()
    if message:
        client_socket.send(message.encode())