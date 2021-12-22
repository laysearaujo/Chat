from common import Client

client = Client()
client.start()
while True:
    cmd=input()
    client.send(cmd)

    if cmd =='bye':
        break