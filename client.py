from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import sys, signal

BUFFER = 1024


def receive(socket, message_list):
    while True:
        try:
            msg = socket.recv(BUFFER).decode()
            if not msg:
                break
            message_list.insert(tkinter.END, msg)
        except OSError:
            break


def send(message, socket, window):
    msg = message.get()
    message.set("")
    if msg: 
        socket.send(msg.encode())
    if msg == "quit":
        socket.close()
        window.quit()


def close(message, socket, window):
    message.set("quit")
    send(message, socket, window)
    socket.close()
    window.quit()


def signal_handler(signal, frame, message, socket, window):
    print("\nProgram terminated.")
    close(message, socket, window)
    sys.exit(0)

def main():
    PORT = 8080
    try:
        HOST = input("Type the address of the server: ")
    except KeyboardInterrupt:
        sys.exit(0)

    window = tkinter.Tk()
    window.title("MyChat")
    frame = tkinter.Frame(window)
    message = tkinter.StringVar()
    message.set("Write here your message!")
    scrollbar = tkinter.Scrollbar(frame)
    message_list = tkinter.Listbox(
        frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    message_list.pack()
    frame.pack()
    entry_field = tkinter.Entry(window, textvariable=message)
    entry_field.pack()
    entry_field.bind("<Return>", lambda event: send(
        message, client_socket, window))
    send_button = tkinter.Button(
        window, text="Enter", command=lambda: send(message, client_socket, window))
    send_button.pack()
    window.protocol("WM_DELETE_WINDOW", lambda event=None: close(
        message, client_socket, window))

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, message, client_socket, window))
        receive_thread = Thread(
            target=receive, args=(client_socket, message_list), daemon=True)

        receive_thread.start()
        tkinter.mainloop()

        receive_thread.join()
        client_socket.close()
    except ConnectionRefusedError:
        print("Connections refused")
    except KeyboardInterrupt:
        print("\nProgram terminated.")
        client_socket.close()


if __name__ == "__main__":
    main()
