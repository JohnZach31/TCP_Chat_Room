import socket
import threading

print("Welcome to the TCP Chatroom!")
print("Created by: Eylon Edri & Johnathan Zachevsky.")

# Choosing Nickname
nickname = input("Please Choose a nickname: ")

# Welcome Message and Info
print(f"Welcome {nickname}!")
print(f"You can send public and/or private messages to other users in the chat.")
print(f"To send a private message, use the format: '/msg <user> <text>'.")
print(f"To quit the chat, use the '/quit' command, or close the window.")

# Connecting to Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # Close Connection with Error
            print("An error occurred!")
            client.close()
            break

#The Client writes a message
def write():
    while True:
        input_message = input("")        

        #A /quit message
        if input_message.lower() == "/quit":
            client.close()
            print("You have left the chat.")
            break
        
        #A normal message
        message = input_message
        client.send(message.encode('ascii'))

# Starting threads for Listening and Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
