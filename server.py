from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


HOST = "localhost"
PORT = "8080"
serverSocket = socket(AF_INET, SOCK_STREAM)
#bind the socket to the server address
serverSocket.bind((HOST, PORT))

def accept_client_connection():
    pass


if __name__ == "__main__":
    serverSocket.listen(2)
    print("The server is up on port: ",PORT)
    print("Waiting for connections")
    #start a thread to accepting each client connection
    accept_thread = Thread(target=accept_client_connection)
    accept_thread.start()
    #Wait until the thread terminates.
    accept_thread.join()
    serverSocket.close()
