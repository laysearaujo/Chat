import socket

# UDP Client
address = ("localhost", 20001)
buffersize = 1024
filename = "dariodoclient.jpg"

# Socket UDP do client
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Enviando arquivo
f = open(filename, "rb")
data = f.read(buffersize)

while(data):
    if(udp.sendto(data, address)):
        print("Enviando...")
    data = f.read(buffersize)

udp.sendto('\x18'.encode(), address)
f.close()

# Recebendo o mesmo arquivo do client
address = ("localhost", 20001)
print("Client is creating a UDP socket.")
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