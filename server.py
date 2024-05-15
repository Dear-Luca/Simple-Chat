from socket import AF_INET, socket, SOCK_STREAM, SO_REUSEPORT, SOL_SOCKET
from threading import Thread

HOST = "localhost"
PORT = 8080
BUFFER = 1024
addresses = {}
users = {}
server_socket = socket(AF_INET, SOCK_STREAM)
#bind the socket to the server address
server_socket.bind((HOST, PORT))
server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)

def accept_client_connection():
    while True:
        connection_socket, client_address = server_socket.accept()
        print("Connection occured:", client_address)
        #associate the corrispondent client with each socket
        addresses[connection_socket] = client_address
        #start a new Thread to manage each client 
        manage_client_thread = Thread(target=manage_client, args=(connection_socket, ))
        manage_client_thread.start()

def manage_client(connection_socket):
    connection_socket.send("Hi! type your username and then Enter".encode())
    
    user_name = connection_socket.recv(BUFFER).decode()
    while user_name in users.values():
        ask_username(connection_socket)
        user_name = connection_socket.recv(BUFFER).decode()
    welcome_message = "Welcome! " + user_name + " type 'quit' to leave the chat"
    connection_socket.send(welcome_message.encode())
    message = user_name + " join the chat!"
    broadcast(message)
    users[connection_socket] = user_name 

    #wait for other messages
    while True:
        message = connection_socket.recv(BUFFER).decode()
        if message == "quit":
            connection_socket.close()
            del users[connection_socket]
            broadcast(user_name + " left the chat.")
            break
        else:
            broadcast(user_name + ": "+ message)

def ask_username(connection_socket):
    connection_socket.send("There is already a user with this name".encode())
    connection_socket.send("Type another username".encode())

def broadcast(message):
    for user in users:
        user.send(message.encode())



if __name__ == "__main__":
    server_socket.listen(5)
    print("The server is up on port: ",PORT)
    print("Waiting for connections")
    #start a thread to accepting each client connection
    accept_thread = Thread(target=accept_client_connection)
    accept_thread.start()
    #Wait until the thread terminates.
    accept_thread.join()
    server_socket.close()
