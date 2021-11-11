import socket

localIP    = "127.0.0.1"
localPort  = 20001
bufferSize = 1024

# Crie um socket de datagrama
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Vincular ao endereço e ip
UDPServerSocket.bind((localIP, localPort))
print("Servido ligado e ouvindo")

# Escutando os dados de entrada
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    
    print(address, message)

    # Sending a reply to client
    UDPServerSocket.sendto(message, address)
