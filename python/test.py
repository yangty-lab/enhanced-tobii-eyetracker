import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'8', ('127.0.0.1', 1234))
sock.close()
print('Command sent')