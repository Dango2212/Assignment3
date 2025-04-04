import socket
import threading

def receive_messages(sock):
    """
    This function runs in a separate thread.
    It continuously listens for messages from the server and prints them.
    """
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                print("Disconnected from server.")
                break
            print(message)
        except:
            print("Connection closed.")
            break

def main():
    host = input("Enter server IP (e.g. 127.0.0.1): ")
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except:
        print("Connection failed.")
        return


    initial_msg = client_socket.recv(1024).decode('utf-8')
    print(initial_msg)
    nickname = input(">> ")
    client_socket.send(nickname.encode('utf-8'))

 
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.daemon = True
    recv_thread.start()

    print("=== Welcome to the chat ===")
    print("Commands:")
    print("/join [channel] - switch channel")
    print("/msg [nickname] [message] - private message")
    print("/quit - exit chat")
    print("===========================")

    while True:
        try:
            msg = input()
            if msg:
                client_socket.send(msg.encode('utf-8'))
                if msg.strip() == "/quit":
                    break
        except:
            break

    client_socket.close()

if __name__ == "__main__":
    main()
