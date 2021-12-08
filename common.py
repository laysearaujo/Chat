import time
import hashlib
import warnings

class saver:
    def __init__(self,filename):
        self.file = open(filename,'wb')

    def save_data(self,data):
        self.file.write(data)

    def close(self):
        self.file.close()

class feeder:
    def __init__(self,filename,size):
        self.file = open(filename,'rb')
        self.size = size
        self.data = None
        self.finished = False

    def get_data(self):
        return self.data
 
    def load_next_data(self):
        if not self.finished:
            self.data = self.file.read(self.size)
            if self.data==b'': 
                self.finished = True
                self.file.close()

class Timer:
    def __init__(self):
        self._start_time = None

    def restart(self):
        self._start_time = time.perf_counter()

    def check(self):
        if self._start_time is None:
            raise Exception(f"Use restart() para iniciá-lo")

        elapsed_time = time.perf_counter() - self._start_time
        return elapsed_time

class Rdt:
    def __init__(self,socket, feeder,saver,first_sender,client_adress,limitTimer,size):

        self.socket = socket
        self.saver = saver
        self.feeder = feeder
        self.limitTimer = limitTimer
        self.size = size
        self.client_adress = client_adress
        
        self.timer = Timer()
        self.running = True
        self.sender_seq = 0
        self.reciever_ack = 0
        self.retransmit = False

        if first_sender:
            self.state = 1
            self.feeder.load_next_data()
        else: self.state = 2

    @staticmethod
    def decode_msg(bytecode):
        header_string = bytecode.decode('utf-8')
        decoded_msg = eval(header_string)
        return decoded_msg
    @staticmethod
    def encode_msg(msg):
        header_string = str(msg)
        bytecode = header_string.encode('utf-8')
        return bytecode

    @staticmethod
    def checksum(data):
        return hashlib.md5(data).hexdigest()

    def send(self,msg):
        self.socket.sendto(msg,self.client_adress)
        self.timer.restart()
        self.state = 2

    def recieve_response(self):
        if self.timer._start_time==None or self.timer.check()<self.limitTimer:
            encoded_response,self.client_adress = self.socket.recvfrom(self.size)
            if(encoded_response):
                self.last_response = self.decode_msg(encoded_response)
                if self.last_response["checksum"]!=self.checksum(self.last_response["data"]):
                    warnings.warn("pacote recebido invalido")
                else:
                    self.reciever_ack = self.last_response["seq"]
                    if not self.last_response['finished_file_transmission']:
                        self.saver.save_data(self.last_response["data"])
                    else: 
                        if self.feeder.finished and self.last_response["ack"]==self.sender_seq: 
                            self.running = False

                if self.last_response["ack"]!=self.sender_seq:
                    self.retransmit = True
                    warnings.warn("Não recebeu o ultimo pacote corretamente")
                else:
                    self.retransmit = False
                    self.sender_seq = 1 if self.sender_seq==0 else 0 
                    self.feeder.load_next_data()
                        
                self.state = 1
            else:
                self.state = 2    
        else:
            self.retransmit = True
            self.state=1
    
    def transmit(self):
        while self.running:
            if self.state==1:
                data_to_send = self.feeder.get_data()
                msg = {
                    "ack":self.reciever_ack,
                    "seq":self.sender_seq,
                    "checksum":self.checksum(data_to_send),
                    "finished_file_transmission":self.feeder.finished,
                    "data":data_to_send
                }
                encoded_msg = self.encode_msg(msg)
                self.send(encoded_msg)
                if hasattr(self,'last_response') and self.feeder.finished and self.last_response['finished_file_transmission'] and not self.retransmit: 
                     self.running = False
            elif self.state == 2:
                self.recieve_response()
        self.saver.close()
        self.socket.close()