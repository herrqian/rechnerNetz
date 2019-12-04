import socket
import base64


def prompt(prompt):
    return input(prompt)


fromaddr = prompt("From: ")
print(fromaddr)
toaddrs = prompt("To: ")
print(toaddrs)

Server_IP = 'asmtp.htwg-konstanz.de'
Server_PORT = 25
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((Server_IP, Server_PORT))

login_name = (base64.b64encode('rnetin'.encode('utf-8'))).decode('utf-8') + '\r\n'
login_passwd = (base64.b64encode('ntsmobil'.encode('utf-8'))).decode('utf-8') + '\r\n'
print(login_name)
print(login_passwd)
print(sock.recv(1024))
sock.send(b'EHLO htwg-konstanz.de\r\n')
print(sock.recv(1024))
sock.send(b'AUTH LOGIN\r\n')
print(sock.recv(1024))
sock.send(str.encode(login_name))
print(sock.recv(1024))
sock.send(str.encode(login_passwd))
print(sock.recv(1024))
mail_from = 'MAIL FROM:<' + fromaddr + '>\r\n'
mail_to = 'RCPT TO:<' + toaddrs + '>\r\n'
sock.send(str.encode(mail_from))
sock.recv(1024)
sock.send(str.encode(mail_to))
sock.recv(1024)
sock.send(b'DATA\r\n')
print(sock.recv(1024))
msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, toaddrs))
print("Enter message, end with ^D (Unix) or ^Z (Windows):")
while True:
    try:
        line = input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line
msg = msg + '\r\n.\r\n'
sock.send(str.encode(msg))
print(sock.recv(1024))
sock.send(b'QUIT\r\n')