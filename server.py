import socket
import time

# UDP Server
localAddress = ("localhost", 20001)
buffersize = 1024
filename = "dariodoserver.jpg"

# Socket UDP do server
print("Server is creating a UDP socket.")
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind(localAddress)
print("UDP server now is up and running!")

f = open(filename, "wb")
data, address = udp.recvfrom(buffersize)

while(data != '\x18'.encode()):
    f.write(data)
    data, address = udp.recvfrom(buffersize)
    print("Recebendo...")

f.close()
time.sleep(1)

# Enviando arquivo
ff = open(filename, "rb")
data = ff.read(buffersize)

while(data):
    if(udp.sendto(data, address)):
        print("Enviando...")
    data = ff.read(buffersize)

udp.sendto('\x18'.encode(), address)
ff.close()

udp.close()