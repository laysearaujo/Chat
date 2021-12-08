import socket
import common

ip = "127.0.0.1"

myPort   = 12121
destPort = 13132

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((ip, myPort))

print("Cliente Ligado!")

feeder = common.feeder("base_client.jpg",300)
saver = common.saver("client.png")

common.Rdt(udp, feeder, saver, True, (ip, destPort), 100, 2048).transmit()