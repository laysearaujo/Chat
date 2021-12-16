from common import *
from datetime import datetime

def hour():
    date = datetime.now().timetuple()
    year, month, day, hour, mim, sec, a, b, c = date
    return edit_time(hour) + ':' + edit_time(min) + ':' + edit_time(sec)

def edit_time(t):
    if t < 10:
        return '0' + str(t)
    
    return str(t)

# criando conexão udp
server = socket_udp()
server.open_socket_server('123.1.0.3', 5000)

try: 
    while True:
        # receber mensagem enviada do client
        message, client_address, new_connection = server.receiver_message()
        
        # decodificando a mensagem
        dic = eval(message.decode())
        # usuário conectado no servidor
        user = str(server.get_user(client_address))

        # pegando hora e data pelo server
        time = hour()

        message =  str(time) + ' ' + user + ': ' + dic['data'].decode()
        
        message_bye = ''
        message_list = ''

        # se a conexão for nova printa isso na dela
        if new_connection:
            message = user + ' entrou na sala.'

        # se a mensagem for bye printa que saiu da sala e desconecta o client do server
        if dic['data'].decode() == 'bye':
            message_bye = user + ' saiu da sala.'
            server.disconnect(client_address)
        
        # se a mensagem for list listar pessoas da sala
        if dic['data'].decode() == 'list':
            message_list = server.get_connecteds()
        
        # retorna as mensagens enviadas para o server para todos os clients
        server.send_to_all(message.encode())

        # 
        if message_bye:
            # retorna as mensagens enviadas para o server para todos os clients
            server.send_to_all(message_bye.encode())

        if message_list:
            # printa na tela todas as pessoas da sala
            server.send_message(message_list.encode(), client_address)
    
# caso force a saida do terminal consegue fechar o server
except KeyboardInterrupt:
    server.close_connection()