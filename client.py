from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread, Timer
import tkinter
import tkinter.font
import sys
import signal
import subprocess
import platform

BUFFER = 1024


def receive(socket, message_list, window):
    # waiting for messages
    while True:
        try:
            msg = socket.recv(BUFFER).decode()
            if not msg:
                break
            # if server closes the client has to quit
            if msg == "SHUTDOWN":
                socket.close()
                window.quit()
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


def signal_handler(signal, frame, message, socket, window):
    print("\nProgram terminated.")
    close(message, socket, window)
    sys.exit(0)


def ping_ip(HOST, PORT, client_socket, window):
    Timer(5.0, ping_ip, args=(HOST, PORT, client_socket, window)).start()
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', HOST]
    result = subprocess.run(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        print("Ping to " + HOST + " was successful")
    else:
        print("Ping to " + HOST + " failed")
        client_socket.close()
        window.quit()
        sys.exit()


def main():
    PORT = 8080
    try:
        HOST = input("Type the address of the server: ")
    except KeyboardInterrupt:
        sys.exit(0)

    window = tkinter.Tk()
    window.title("MyChat")
    window.configure(bg="cornflower blue")

    # Setting custom fonts
    header_font = tkinter.font.Font(family="Helvetica", size=16, weight="bold")
    default_font = tkinter.font.Font(family="Helvetica", size=12)

    # Creating frames
    top_frame = tkinter.Frame(window, bg="blue")
    top_frame.pack(pady=10)

    middle_frame = tkinter.Frame(window, bg="blue")
    middle_frame.pack(pady=5)

    bottom_frame = tkinter.Frame(window, bg="blue")
    bottom_frame.pack(pady=10)

    # Title
    title = tkinter.Label(top_frame, text="MyChat",
                          font=header_font, fg="black", bg="cornflower blue")
    title.pack()

    # Message list with scrollbar
    message = tkinter.StringVar()
    scrollbar = tkinter.Scrollbar(middle_frame)
    message_list = tkinter.Listbox(
        middle_frame, height=15, width=50, yscrollcommand=scrollbar.set, bg="SkyBlue1", fg="black", font=default_font)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=5, pady=5)
    scrollbar.config(command=message_list.yview)

    # Message entry field
    entry_field = tkinter.Entry(bottom_frame, textvariable=message,
                                width=40, font=default_font, bg="SkyBlue1", fg="black")
    entry_field.pack(side=tkinter.LEFT, padx=5, pady=5)
    entry_field.bind("<Return>", lambda event: send(
        message, client_socket, window))

    # Send button
    send_button = tkinter.Button(bottom_frame, text="Enter", command=lambda: send(message, client_socket, window),
                                 fg="black", font=default_font, width=10)
    send_button.pack(side=tkinter.LEFT, padx=5, pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: close(
        message, client_socket, window))

    try:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        # send a signal if ctrl-c is pressed
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(
            sig, frame, message, client_socket, window))
        # starting the thread to receive the messages
        receive_thread = Thread(
            target=receive, args=(client_socket, message_list, window), daemon=True)
        # starting the thead that check the connection with the server
        ping_thread = Timer(5.0, ping_ip, args=(
            HOST, PORT, client_socket, window))
        ping_thread.daemon = True
        ping_thread.start()
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
