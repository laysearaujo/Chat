import json
import socket
import threading
from datetime import datetime

class Server:
    def __init__(self,ip='127.0.0.1',port=699):
        self.ip=ip
        self.port=port
        self.sock=socket.socket(type=socket.SOCK_DGRAM)
        self.sock.bind((self.ip,self.port))
        self.client=set()
        self.event=threading.Event()
        self.dic={}

    def start(self):
        print('Server Ligado!')
        threading.Thread(target=self.__recv,daemon=True).start()

    def stop(self):
        self.event.set()
        self.sock.close()

    def get_str(self,t):
        if t < 10:
            return '0' + str(t)
        
        return str(t)
    
    def __recv(self):
        while not self.event.is_set():
            data,ipinfo=self.sock.recvfrom(1024)
            self.client.add(ipinfo)
            
            ip,port = ipinfo
            info = str(ip) + ':' + str(port)
            
            cmd = data[:16]
            if cmd == b'hi, meu nome eh ':
                name = data[16:]
                self.dic[info] = name.decode()
                message = data = '---- ' + name.decode() + ' entrou no chat. ----'
                print(message)
                self.send(message.encode())
            elif cmd == b'list':
                print('lista')
                print(self.dic)
                dct = json.dumps(self.dic)
                self.send(dct.encode())
            elif cmd==b'bye':
                msg =  '--- ' + self.dic[info] + ' saiu ---'
                print(msg)
                self.send(msg.encode())
                self.dic.pop(info)
            else:
                n = datetime.now()
                t = n.timetuple()
                y, m, d, h, mi, sec, wd, yd, i = t
                time = self.get_str(h) + ':' + self.get_str(mi) + ':' + self.get_str(sec)

                msg =  str(time) + ' ' + self.dic[info] + ': ' + data.decode()
                # print(msg)
                self.send(msg.encode())

    def send(self,data):
        for client in self.client:
            self.sock.sendto(data,client)

class Client:
    def __init__(self,ip='127.0.0.1',port=699):
        self.ip=ip
        self.port=port
        self.sock=socket.socket(type=socket.SOCK_DGRAM)
        self.event=threading.Event()

    def start(self):
        print("Client ligado!")
        while True:
            msg = input("Escreva algo: ")
            
            cmd = msg[:16]
            if cmd == 'hi, meu nome eh ':
                self.send(msg)
                threading.Thread(target=self.__recv).start()
                break
    
    def stop(self):
        self.event.set()
        self.sock.close()
    
    def __recv(self):
        while not self.event.is_set():
            data=self.sock.recv(1024)
            print(data.decode())
            if data == b'bye':
                print('--- saiu ---')

    def send(self,cmd):
        cmd=cmd.encode()
        self.sock.sendto(cmd,(self.ip,self.port))
    