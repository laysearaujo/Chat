import time
import hashlib
import warnings

class Timer:
    def __init__(self):
        self.start_time = None

    def restart(self):
        self.start_time = time.perf_counter()

    def check(self):
        if self.start_time is None:
            raise Exception(f"Use restart() para iniciá-lo")

        elapsed_time = time.perf_counter() - self.start_time
        return elapsed_time


class saver:
    def __init__(self,filename):
        self.file = open(filename,'wb')

    def save_data(self,data):
        self.file.write(data)

    def close(self):
        self.file.close()


class Rdt:
    def __init__(self,socket, feeder,saver,first_sender,client_adress,timer_limit,size):

        self.socket = socket
        self.saver = saver
        self.feeder = feeder
        self.timer_limit = timer_limit
        self.size = size
        self.client_adress = client_adress
        
        self.timer = Timer()
        self.action = True
        self.sender_sequence = 0
        self.receiver_ack = 0
        self.retransmit = False

        if first_sender:
            self.state = 1
            self.feeder.load_next_data()
        else: self.state = 2

    @staticmethod
    def decode_msg(bytecode):
        string_head = bytecode.decode('utf-8')
        decoded_msg = eval(string_head)
        return decoded_msg
    @staticmethod
    def encode_msg(msg):
        string_head = str(msg)
        bytecode = string_head.encode('utf-8')
        return bytecode

    @staticmethod
    def verify_sum(data):
        return hashlib.md5(data).hexdigest()

    def send(self,msg):
        self.socket.sendto(msg,self.client_adress)
        self.timer.restart()
        self.state = 2

    def recieve_response(self):
        if self.timer.start_time==None or self.timer.check()<self.timer_limit:
            encoded_response,self.client_adress = self.socket.recvfrom(self.size)
            if(encoded_response):
                self.last_response = self.decode_msg(encoded_response)
                if self.last_response["verify_sum"]!=self.verify_sum(self.last_response["data"]):
                    warnings.warn("pacote recebido invalido")
                else:
                    self.receiver_ack = self.last_response["seq"]
                    if not self.last_response['finish_file_transmission']:
                        self.saver.save_data(self.last_response["data"])
                    else: 
                        if self.feeder.finish and self.last_response["ack"]==self.sender_sequence: 
                            self.action = False

                if self.last_response["ack"]!=self.sender_sequence:
                    self.retransmit = True
                    warnings.warn("Não recebeu o ultimo pacote corretamente")
                else:
                    self.retransmit = False
                    self.sender_sequence = 1 if self.sender_sequence==0 else 0 
                    self.feeder.load_next_data()
                        
                self.state = 1
            else:
                self.state = 2    
        else:
            self.retransmit = True
            self.state=1
    
    def transmit(self):
        while self.action:
            if self.state==1:
                data_to_send = self.feeder.get_data()
                msg = {
                    "ack":self.receiver_ack,
                    "seq":self.sender_sequence,
                    "verify_sum":self.verify_sum(data_to_send),
                    "finish_file_transmission":self.feeder.finish,
                    "data":data_to_send
                }
                encoded_msg = self.encode_msg(msg)
                self.send(encoded_msg)
                if hasattr(self,'last_response') and self.feeder.finish and self.last_response['finish_file_transmission'] and not self.retransmit: 
                     self.action = False
            elif self.state == 2:
                self.recieve_response()
        self.saver.close()
        self.socket.close()


class feeder:
    def __init__(self,filename,size):
        self.file = open(filename,'rb')
        self.size = size
        self.data = None
        self.finish = False

    def get_data(self):
        return self.data
 
    def load_next_data(self):
        if not self.finish:
            self.data = self.file.read(self.size)
            if self.data==b'': 
                self.finish = True
                self.file.close()