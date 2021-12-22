from common import Server

server = Server()
server.start()

while True:
    cmd=input()
    cmd = cmd.encode()
    server.send(cmd)
    
    if cmd =='bye':
        break
