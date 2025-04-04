import socket
import threading

# Dictionary to store connected clients:
# Key = client socket, Value = {"nickname": ..., "channel": ...}
clients = {}

# Default channel when a client first connects
DEFAULT_CHANNEL = "general"
"""
    Send a message to all clients in a specific channel.
    Excludes the sender if exclude_socket is provided.
    """
def broadcast(message, channel, exclude_socket=None):

    for client, info in clients.items():
        if info["channel"] == channel and client != exclude_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                 # If send fails, close and remove client
                client.close()
                remove_client(client)

def handle_client(client_socket):
    # Ask for nickname
    client_socket.send("Enter your nickname: ".encode('utf-8'))
    nickname = client_socket.recv(1024).decode('utf-8').strip()
     # Register client with nickname and default channel
    clients[client_socket] = {"nickname": nickname, "channel": DEFAULT_CHANNEL}
    # Broadcast welcome message to other users in the same channel
    welcome = f"{nickname} joined channel #{DEFAULT_CHANNEL}."
    print(welcome)
    broadcast(welcome, DEFAULT_CHANNEL, exclude_socket=client_socket)
# Continuously listen for messages or commands from client
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # Handle channel switch command
            if message.startswith("/join "):
                new_channel = message.split(" ", 1)[1].strip()
                old_channel = clients[client_socket]["channel"]
                clients[client_socket]["channel"] = new_channel
                broadcast(f"{nickname} left #{old_channel}.", old_channel, client_socket)
                broadcast(f"{nickname} joined #{new_channel}.", new_channel, client_socket)
                client_socket.send(f"You joined #{new_channel}.".encode('utf-8'))

            # Handle private message command
            elif message.startswith("/msg "):
                parts = message.split(" ", 2)
                target_nick = parts[1]
                msg = parts[2]
                send_private_message(nickname, target_nick, msg)

            # Handle quit command
            elif message.startswith("/quit"):
                client_socket.send("Goodbye!".encode('utf-8'))
                client_socket.close()
                remove_client(client_socket)
                break
            else:
                broadcast(f"[{nickname}] {message}", clients[client_socket]["channel"], exclude_socket=client_socket)
        except:
            remove_client(client_socket)
            break

def send_private_message(sender_nick, target_nick, msg):
    """
    Send a private message to a user with nickname `target_nick`.
    """
    for client, info in clients.items():
        if info["nickname"] == target_nick:
            try:
                client.send(f"[Private from {sender_nick}] {msg}".encode('utf-8'))
                return
            except:
                client.close()
                remove_client(client)
    # If target user is not found, notify the sender
    for client, info in clients.items():
        if info["nickname"] == sender_nick:
            client.send(f"User {target_nick} not found.".encode('utf-8'))

def remove_client(client_socket):
    """
    Remove the client from the system and notify others in the channel.
    """
    if client_socket in clients:
        nickname = clients[client_socket]["nickname"]
        channel = clients[client_socket]["channel"]
        broadcast(f"{nickname} left the chat.", channel, exclude_socket=client_socket)
        del clients[client_socket]
        client_socket.close()

def start_server():
    """
    Start the TCP server and accept new connections.
    Each client connection is handled in a new thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen(5)
    print("Server started on port 12345...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()
