from common import *
import signal

# função de indica inatividade
def max_time(signum, frame):
    raise Exception('Voce saiu por inatividade')

# função que indica quando um novo usuário entra com o comando 'hi, meu nome eh '
def new_user():
    while True:
        message = input('escreve aqui: ')
        
        # caso a mensagem seja menor que 17 caracteres então sabemos que ela não é o comando de entrar, podendo assim ser outra mensagem. Nos dois casos continuamos de onde a função foi chamada
        if len(message) < 17:
            continue 
    
        # Pega as primeiras palavras para saber se é o comando de entrar
        cmd = message[:16]
        if cmd == 'hi, meu nome eh ':
            return message[16:]


# função de receber a mensagem de volta do servidor
def read_message():
    try: 
        # recebendo a mensagem
        signal.alarm(2)
        message, a, b = client.receiver_message()
        
        # decodificando a mensagem e a retornando
        signal.alarm(0)
        dic = eval(message.decode()) 
        return dic['data'].decode()

    # caso aconteça algum erro retorna vazio
    except Exception:
        return ''

# função usada na hora de sair do chat
def bye(user):
    print(user + ': bye')
    print('\nVoce saiu do chat :(')
    client.close_connection()

# criando o alarme
signal.signal(signal.SIGALRM, max_time)

# criando conexão udp
client = socket_udp()
client.open_socket_client('123.1.0.3', 5000)

try:
    # criando novo usuário
    user = new_user()
    # enviando a mensagem
    client.send_message(user.encode())

    # sempre fazer essa verificação
    while True:
        # verifica se tem mensagem
        if client.has_message():
            # caso tenha mensagem, ela é lida e printada na tela
            message_received = read_message()
            if message_received:
                print(message_received)

        try: 
            signal.alarm(3)
            # pega o input do teclado
            message_send = input()
            signal.alarm(0)

            # caso tenha mensagem, ela é lida e printada na tela, se não tiver para esse while
            while client.has_message():
                message_received = read_message()
                if message_received:
                    print(message_received)
                else:
                    break
            
            # envia a mensagem do input
            client.send_message(message_send.encode())

            # se a mensagem for 'bye' para esse try
            if message_send == 'bye':
                break
        
        # para continuar dentro do while
        except Exception:
            continue
    
    bye(user)

# caso force a saida do terminal consegue sair do chat
except KeyboardInterrupt:
    while client.has_message():
        message_received = read_message()
        if message_received == '':
            break
    
    client.send_message('bye'.encode())
    bye(user)