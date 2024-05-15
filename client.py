from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os

BUFFER = 1024

def receive(socket):
    while True:
        try:
            msg = socket.recv(BUFFER).decode()
            print(msg)
        except OSError:
            break

def send_messages(socket):
    while True:
        message = input()
        socket.send(message.encode())
        if message == "quit":
            socket.close()
            os._exit(0)
            break

def main():    
    PORT = 8080
    HOST = input("Type the address of the server: ")

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        
        receive_thread = Thread(target=receive, args=(client_socket, ), daemon=True)
        send_thread = Thread(target=send_messages, args=(client_socket, ), daemon=True)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()
        client_socket.close()
    except ConnectionRefusedError:
        print("Connections refused")
    except KeyboardInterrupt:
        print("\nProgram terminated.")


if __name__ == "__main__":
    main()