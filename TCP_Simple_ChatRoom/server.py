import threading
import socket

# Server Info
host = '127.0.0.1'  # localhost
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#Clients and Nicknames Lists
clients = []        # List of all client sockets
nicknames = []      # List of all nicknames corresponding to those sockets

def broadcast(message: bytes):
    """
    Send 'message' to all connected clients.
    """
    for client in clients:
        client.send(message)

# Send a private message from a client to a client
def private_message(sender_client, sender_nickname, target_nickname, message):
    # Check if target nickname exists
    if target_nickname in nicknames:
        # Find the index of the target nickname in the nicknames list
        target_index = nicknames.index(target_nickname)
        target_client = clients[target_index]

        # Format the private message
        pm_msg = f"/{sender_nickname}: {message}"
        target_client.send(pm_msg.encode('ascii'))
    else:
        # If the target nickname does not exist, let the sender know
        error_msg = f"User '{target_nickname}' not found."
        sender_client.send(error_msg.encode('ascii'))

# Handle messages from a specific client.
def handle(client):
    while True:
        try:
            # We receive raw bytes, then decode
            message = client.recv(1024).decode('ascii')
            if not message:
                # If we received an empty message (connection closed),
                # handle the disconnection
                raise ConnectionResetError
            
            # Identify the nickname of whoever sent this message
            index = clients.index(client)
            sender_nickname = nicknames[index]
            
            # Check if this is a private message by looking for a special command
            # e.g. / <target> <text...>
            if message.startswith("/"):
                # We'll assume the format is "/ targetNickname message..."
                parts = message.split(' ', 2)  # split into at most 3 parts
                # e.g. "/ Bob Hello there"
                # parts[0] = "/"
                # parts[1] = "Bob"
                # parts[2] = "Hello there"

                if len(parts) >= 3:
                    target_nickname = parts[1]
                    actual_message = parts[2]
                    private_message(client, sender_nickname, target_nickname, actual_message)
                else:
                    # Invalid format. Let the sender know.
                    error_msg = (
                        "Invalid private message format.\n"
                        "Use: / <nickname> <your message> (for private messages)"
                    )
                    client.send(error_msg.encode('ascii'))
            else:
                # Otherwise, it's a normal broadcast
                broadcast(f"{sender_nickname}: {message}".encode('ascii'))
        
        except:
            # Means the client has disconnected or we had an error
            disconnect_client(client)
            break

# Remove a disconnected client and broadcast an announcement
def disconnect_client(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]

        clients.remove(client)
        nicknames.remove(nickname)
        broadcast(f"{nickname} left the chat!".encode('ascii'))
        print(f"{nickname} has left the chat!")
        client.close()

# Accept new connections and start a thread to handle each.
def receive():
    while True:
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            
            # Store in our data structures
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}!")
            broadcast(f"{nickname} joined the chat!".encode('ascii'))
            client.send('Connected to the server!'.encode('ascii'))

            # Start a thread for each client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except ConnectionResetError as e:
            print(f"Connection reset: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

print("Server is listening...")
receive()
