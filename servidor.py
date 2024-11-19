import socket as sock
import threading

# Configurações do servidor
HOST = '192.168.1.2'  # Mantenha 127.0.0.1 se o teste é local
PORTA = 2222

# Lista de clientes conectados e nomes
clientes = {}
lock = threading.Lock()

# Função para enviar mensagens a todos os clientes (broadcast)
def broadcast(mensagem, remetente=None):
    print(f"[Broadcast] Enviando mensagem: {mensagem}")
    with lock:
        for cliente, nome in clientes.items():
            try:
                cliente.sendall(mensagem.encode())  
            except Exception as e:
                print(f"Erro ao enviar mensagem para {nome}: {e}")
                cliente.close()
                remove_cliente(cliente)

# Função para enviar mensagem privada
def enviar_privado(mensagem, destinatario):
    with lock:
        for cliente, nome in clientes.items():
            if nome == destinatario:
                try:
                    cliente.sendall(mensagem.encode())
                    return True
                except Exception as e:
                    print(f"Erro ao enviar mensagem privada para {nome}: {e}")
                    cliente.close()
                    remove_cliente(cliente)
                return False
    return False

# Função para remover cliente da lista
def remove_cliente(cliente):
    with lock:
        if cliente in clientes:
            nome = clientes[cliente]
            del clientes[cliente]
            print(f"{nome} foi removido da lista de clientes.")

# Função para gerenciar mensagens dos clientes  
def recebe_dados(cliente_socket, endereco):
    try:
        # Recebe o nome do cliente
        nome = cliente_socket.recv(1024).decode().strip()
        with lock:
            clientes[cliente_socket] = nome
        print(f"{nome} ({endereco}) entrou no chat.")
        broadcast(f"{nome} entrou no chat.")

        while True:
            mensagem = cliente_socket.recv(1024).decode()
            if not mensagem:
                break

            # Verifica se é uma mensagem privada
            if mensagem.startswith("/privado"):
                partes = mensagem.split(" ", 2)
                if len(partes) >= 3:
                    destinatario = partes[1]
                    mensagem_privada = partes[2]
                    if enviar_privado(f"[Privado de {nome}]: {mensagem_privada}", destinatario):
                        cliente_socket.sendall(f"[Para {destinatario}]: {mensagem_privada}".encode())
                    else:
                        cliente_socket.sendall(f"Usuário '{destinatario}' não encontrado.".encode())
                else:
                    cliente_socket.sendall("Formato inválido. Use: /privado <nome> <mensagem>".encode())
            else:
                broadcast(f"{nome}: {mensagem}")

    except Exception as e:
        print(f"Erro ao processar dados de {endereco}: {e}")
    
    finally:
        cliente_socket.close()
        remove_cliente(cliente_socket)
        broadcast(f"{nome} saiu do chat.")
        print(f"{nome} ({endereco}) desconectou.")

# Inicialização do servidor
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
sock_server.bind((HOST, PORTA))
sock_server.listen()
print(f"Servidor ativo e aguardando conexões em {HOST}:{PORTA}")

# Aceitar conexões de clientes
while True:
    try:
        cliente_socket, endereco = sock_server.accept()
        print(f"Nova conexão de {endereco}")
        thread_cliente = threading.Thread(target=recebe_dados, args=(cliente_socket, endereco))
        thread_cliente.start()
    except Exception as e:
        print(f"Erro ao aceitar nova conexão: {e}")
