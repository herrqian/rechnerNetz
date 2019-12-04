import socket
import threading

HOST_SERVER = '141.37.168.26'

counter = 0

def port_scanner(port, host=HOST_SERVER):
    print("trying port " + str(port) + "...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.settimeout(5)
    try:
        sock.connect((host, port))
        sock.send(b'hello')
        print(sock.recv(1024))
    except ConnectionRefusedError as e:
        print(e)
        return
    except ConnectionResetError as e:
        print(e)
        return
    except socket.timeout:
        print('timed out')
        return

def port_scanner2(port, host=HOST_SERVER):
    print("trying port " + str(port) + "...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = 'hello'

    sock.settimeout(1)
    try:
        sock.connect((host, port))
        sock.send(message.encode('utf-8'))
        print(sock.recvfrom(4096))
    except ConnectionRefusedError as e:
        print(e)
        return
    except OSError as e:
        print(e)
        return
    except socket.timeout:
        print('timed out')
        return

print('tcp:')
for i in range(51):
    if i > 0:
        t = threading.Thread(target=port_scanner(i))

print('udp:')
for i in range(51):
    if i > 0:
        t = threading.Thread(target=port_scanner2(i))

