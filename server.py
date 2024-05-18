from socket import *
from threading import Thread
import sys
import signal

HOST = "localhost"
PORT = 8080
BUFFER = 1024
addresses = {}
users = {}
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# bind the socket to the server address
server_socket.bind((HOST, PORT))

accepting_connections = True


def accept_client_connection():
    global accepting_connections
    while accepting_connections:
        try:
            connection_socket, client_address = server_socket.accept()
            print("Connection occured:", client_address)
            # associate the corrispondent client with each socket
            addresses[connection_socket] = client_address
            # start a new Thread to manage each client
            manage_client_thread = Thread(
                target=manage_client, args=(connection_socket, ), daemon=True)
            manage_client_thread.start()
        except OSError:
            break


def manage_client(connection_socket):
    connection_socket.send("Hi! type your username and then Enter".encode())

    user_name = connection_socket.recv(BUFFER).decode()
    #users can't have the same user_name
    while user_name in users.values():
        ask_username(connection_socket)
        user_name = connection_socket.recv(BUFFER).decode()
    welcome_message = "Welcome! " + user_name + " type 'quit' to leave the chat"
    connection_socket.send(welcome_message.encode())
    message = user_name + " join the chat!"
    broadcast(message)
    users[connection_socket] = user_name

    # wait for other messages
    while True:
        try:
            message = connection_socket.recv(BUFFER).decode()
            if message == "quit":
                quit_user(connection_socket, user_name)
                break
            else:
                broadcast(user_name + ": " + message)
        except (ConnectionResetError, BrokenPipeError):
            quit_user(connection_socket, user_name)
            break


def quit_user(socket, user_name):
    socket.close()
    del users[socket]
    print(addresses[socket], " disconnected")
    print(user_name)
    broadcast(user_name + " left the chat.")


def ask_username(connection_socket):
    connection_socket.send(
        "There is already a user with this name, type another username".encode())


def broadcast(message):
    for user in users:
        user.send(message.encode())


def quit_server(signal, frame):
    global accepting_connections
    print("Exiting server...")
    accepting_connections = False
    #if server closes connection all clients have to quit
    broadcast("SHUTDOWN")
    server_socket.close()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_server)

    server_socket.listen(5)
    print("The server is up on port: ", PORT)
    print("Waiting for connections")
    # start a thread to accepting each client connection
    accept_thread = Thread(target=accept_client_connection, daemon=True)
    accept_thread.start()

    # Wait until the thread terminates.
    accept_thread.join()
    server_socket.close()
