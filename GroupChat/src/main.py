import socket
import threading

print("IP: ")
serverIP = input()

print("Port: ")
serverPort = int(input())

print("Name: ")
name = input()

SOCKET_TIMEOUT = 10
#
# serverIP = socket.gethostbyname(socket.gethostname())
print("IP: " + serverIP)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((serverIP, serverPort))
sock.listen(10)

# List to store the clients
clients = {}
clients_lock = threading.Lock()

shutdown = False


def add_client(client_name, client_sock):
    clients_lock.acquire()
    clients[client_sock] = client_name
    clients_lock.release()


def remove_client(client_name):
    c = get_client(client_name)
    clients_lock.acquire()
    clients.pop(c)
    clients_lock.release()


def has_client(client_name):
    if get_client(client_name) is None:
        return False
    else:
        return True


def get_client_by_sock(client_sock):
    clients_lock.acquire()
    c = clients[client_sock]
    clients_lock.release()
    return c


def get_client(client_name):
    clients_lock.acquire()
    for s, n in clients.items():
        if client_name == n:
            clients_lock.release()
            return s


def connect_to(ip, port):
    new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sock.settimeout(SOCKET_TIMEOUT)
    try:
        new_sock.connect((ip, port))
    except socket.timeout:
        print(f"Connect-Request to {ip}:{port} timed out.")
        new_sock.close()
        return
    except ConnectionRefusedError:
        print(f"Connect-Refused from {ip}:{port}.")
        return
    new_sock.send(str.encode(f"name : {name}"))
    threading.Thread(target=handle_message, args=(new_sock,)).start()


def send_ack(client_socket):
    client_socket.send(str.encode(f"ack : {name}"))


def send_end():
    clients_lock.acquire()
    for client_sock, client_name in clients.items():
        client_sock.send(str.encode(f"quit : quit"))
    clients_lock.release()


def send_sm(client_socket, message):
    client_socket.send(str.encode(f"sm : {message}"))


def send_gm(message):
    clients_lock.acquire()
    for client_socket, client_name in clients.items():
        client_socket.send(str.encode(f"gm : {message}"))
    clients_lock.release()


def handle_message(client_socket):
    while not shutdown:
        try:
            data = client_socket.recv(1024)
            if not data:
                continue
        except socket.timeout:
            continue
        except OSError:
            data = b'end'

        data_as_string = data.decode('utf-8')
        data_split = data_as_string.split(' ', 2)
        keyword = data_split[0]
        if keyword != "quit":
            message = data_split[2]

        if keyword == 'name':
            print(f"{message} joined.")
            add_client(message, client_socket)
            send_ack(client_socket)

        elif keyword == 'ack':
            add_client(message, client_socket)
            print(f"{message} joined.")

        elif keyword == 'quit':
            client_name = get_client_by_sock(client_socket)
            remove_client(client_name)
            client_socket.close()
            print(f"{client_name} left.")
            return

        elif keyword == 'sm':
            print(f"S: {get_client_by_sock(client_socket)}\n{message}")

        elif keyword == 'gm':
            print(f"G: {get_client_by_sock(client_socket)}\n{message}")

        else:
            print(f"received unknown command '{keyword}' from {get_client_by_sock(client_socket)}")


def wait_for_peers():
    print("Waiting for peers")
    while not shutdown:
        (client_socket, addr) = sock.accept()
        client_socket.settimeout(SOCKET_TIMEOUT)
        t = threading.Thread(target=handle_message, args=(client_socket,))
        t.start()


laborpc = {"127.0.1.1": 50000, "127.0.1.2": 50000, "127.0.1.3": 50000}


def scan():
    for ip, port in laborpc.items():
        connect_to(ip, port)


main_thread = threading.Thread(target=wait_for_peers)
main_thread.start()

command = ""

while command != "exit":
    print("> ", end="")
    line = input()
    split = line.split(" ", 2)
    command = split[0]

    if command in ["message"]:
        client_name = split[1]
        if has_client(client_name):
            send_sm(get_client(client_name), split[2])
        else:
            print(f"No such client: {client_name}")

    elif command in ['group']:
        send_gm(line.split(" ", 1)[1])

    elif command == 'connect':
        connect_to(split[1], int(split[2]))
        print(f"send connect")

    elif command in ['list']:
        clients_lock.acquire()
        if len(clients) == 0:
            print("There are no clients yet.")
        else:
            for client_sock, client_name in clients.items():
                print(f"{client_sock}:{client_name}")
        clients_lock.release()

    elif command in ["scan"]:
        print("Scanning for peers.")
        scan()

    elif command in ["quit"]:
        shutdown = True
        send_end()
        # Connect to the the accept socket to kill the thread
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_sock.connect((serverIP, serverPort))
        new_sock.close()
        sock.close()

    elif command.__eq__("exit"):
        break

    else:
        print(f"received unknown command: {command}")
