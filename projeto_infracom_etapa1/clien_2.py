import socket
#import time
#import os

# UDP Client
address = ("localhost", 20001)
buffersize = 1024
filename = "dariodoclient.jpg"
# filename = "teste.txt"
#filesize = os.stat(filename).st_size
#print(filesize)

# Socket UDP do client
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviando arquivo
f = open(filename, "rb")
data = f.read(buffersize)
#udp.sendto(data, address)

while(data):
    if(udp.sendto(data, address)):
        print("Enviando...")
    data = f.read(buffersize)
    #udp.sendto(data, address)

udp.sendto('\x18'.encode(), address)

f.close()
#udp.close()

# Recebendo o mesmo arquivo do client
print("Client is creating a UDP socket.")
address = ("localhost", 20001)
#udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#udp.bind(address)
print("Up and running!")

filename = "outrodariodoclient.jpg"
ff = open(filename, "wb")
data, address = udp.recvfrom(buffersize)

while(data != '\x18'.encode()):
    ff.write(data)
    data, address = udp.recvfrom(buffersize)
    print("Recebendo...")

ff.close()
udp.close()