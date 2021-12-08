import socket
import common

ip = "127.0.0.1"

myPort   = 13132
destPort = 12121

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((ip, myPort))

print("Servidor ligado!")

feeder = common.feeder("base_server.png",300)
saver = common.saver("server.jpg")

common.Rdt(udp, feeder, saver, False, (ip, destPort), 100, 2048).transmit()