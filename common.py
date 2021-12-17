import socket
from struct import unpack

# classe principal do socket udp
class socket_udp:
    seqNumber = 0
    connected = {}

    qtd_participants = 0

    # abrindo conexão via socket para o servidor
    def open_socket_server(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (ip, port)
        print('Servidor ligado!')
        self.sock.bind(self.server_address)

    # abrindo conexão via socket para o client
    def open_socket_client(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (ip, port)
        print('Cliente ligado!')
        self.connect('server', self.server_address)

     # fecha a conexão
    def close_connection(self):
        print('\nSocket fechado!')
        self.sock.close() 

    # enviar mensagem
    def send(self, msg, address = ''):
        if not address:
            address = self.server_address 

        return self.sock.sendto(msg, address)

    # receber mensagem
    def receive(self, size, address = ''):
        if not address:
            return self.sock.recvfrom(size)
        
        return self.sock.recvfrom(size)
    
    # criar pacotes com a mensagem e a sequencia
    def make_package(self, msg, seq):
        cksum = self.check(msg)

        return str({
            'cksum': cksum,
            'data': msg,
            'seq': seq
        }).encode()
    
    # criar e atualizar pacotes
    def send_message(self, msg, address = ''):
        self.sock.settimeout(5)
        if not address:
            address = self.server_address
        
        package = self.make_package(msg, self.get_seq_number(address))
        
        ack = False 

        while not ack:
            self.send(package, address)

            try:
                msg, recv_address = self.receive(4096)
            except socket.timeout:
                print('tempo máximo de espera atigindo')
            else:
                msgACK = eval(msg.decode())['data'].decode()
                if recv_address != address or msgACK != 'ACK':
                    continue
                
                ack = self.recv_package(msg, address)
        
        self.update_seq_number(address)
        self.sock.settimeout(None)
    
    # receber mensagens
    def receiver_message(self):
        while True:
            package, address = self.sock.recvfrom(4096)
            # criar nova conexão
            new_connection = self.check_connection(package, address)
            # receber frequencias dos números
            seq = self.get_seq_number(address)
            not_corrupt = self.recv_package(package, address, 'receiver')
            # quantidade máx de participantes 5
            if self.qtd_participants < 5:
                self.qtd_participants += 1
            # caso o pacote não esteja corrompido ele envia e atualiza
            if not_corrupt:
                package_ack = self.make_package(bytes('ACK', 'utf8'), seq)
                self.send(package_ack, address)
                self.update_seq_number(address)
                return package, address, new_connection
            # caso não, ele cria um novo pacote para enviar
            else:
                self.send(self.make_package(bytes('ACK', 'utf8'), 1 - seq), address)
    
    # mostra o user
    def get_user(self, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connected:
            return self.connected[address]['user']
        else:
            self.connect(address[1], address)
            return self.connected[address]['user']
    
    # mostra lista de conectados 
    def get_connecteds(self):
        msg_list = 'Lista de usuarios:'
        for address in self.connected:
            msg_list += '\n' + str(self.connected[address]['user'])

        return msg_list
    
    # faz uma conexão
    def connect(self, user, address):
        self.connected[address] = {
            'user': user,
            'seqNumber': 0
        }
        print('usuario', user, 'conectado')
    
    # checa as conexões
    def check_connection(self, package, address):
        if address in self.connected:
            return False
        
        if package:
            dicio = eval(package.decode())
            user = dicio['data'].decode()
            self.connect(user, address)
            return True
        else:
            return False
 
    # desconecta
    def disconnect(self, address):
        if address in self.connected:
            print(self.connected[address]['user'] + ' disconnected')
            del self.connected[address]
    
    # pega o número de frequancia
    def get_seq_number(self, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connected:
            return self.connected[address]['seqNumber']
        else:
            self.connect(address[1], address)
            return self.connected[address]['seqNumber']
    
    # atualiza número de frequencia
    def update_seq_number(self, address = ''):
        if not address:
            address = self.server_address
        
        self.connected[address]['seqNumber'] = 1 - self.connected[address]['seqNumber']
    
    # verifica se existe mensagens
    def has_message(self):
        return self.sock.recv is not None
    
    # checa as mensagens
    def check(self, msg):
        cksum = 0

        array = bytearray(msg)[::-1]
        lenght = len(array)

        for i in range(lenght):
            if i % 2:
                continue 
            
            cksum += (array[i] << 8)
            if i + 1 < lenght:
                cksum += array[i+1]

        while cksum >> 16:
            cksum = (cksum >> 16) + (cksum & 0xffff)
        
        cksum = cksum ^ 0xffff
        return cksum
    
    # envia para todos as mensagens que chegam no servidor
    def send_to_all(self, msg):
        for address in self.connected:
            self.send_message(msg, address)
    
    # recebe o pacote
    def recv_package(self, msg, address, type='sender'):    
        dicio = eval(msg.decode())
        cksum = self.check(dicio['data'])
        
        seq = self.get_seq_number(address)

        if cksum != dicio['cksum']:
            return False

        if seq != dicio['seq']:
            return False

        return True