import socket as sock
import threading
import tkinter as tk
from tkinter import messagebox

# Configurações de conexão com o servidor
HOST = '192.168.1.2'  # Deve ser o mesmo IP do servidor
PORTA = 2222

# Criação do socket para o cliente
socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket_cliente.connect((HOST, PORTA))
print(5 * "*" + " Chat Iniciado " + 5 * "*")

# Variável para controlar execução
running_flag = threading.Event()
running_flag.set()

# Nome do cliente
nome = input("Informe seu nome para entrar no chat: ")
socket_cliente.sendall((nome + "\n").encode())

# Funções do cliente
def receber_mensagens():
    """Função para receber mensagens do servidor."""
    while running_flag.is_set():
        try:
            mensagem = socket_cliente.recv(1024).decode()
            if mensagem:
                messages.insert(tk.END, mensagem)
                messages.yview(tk.END)  # Scroll automático
            else:
                # Conexão encerrada
                messages.insert(tk.END, "Conexão encerrada pelo servidor.")
                running_flag.clear()
                break
        except Exception as e:
            messages.insert(tk.END, f"Erro ao receber mensagem: {e}")
            running_flag.clear()
            break

def enviar_mensagem(entry_widget):
    """Função para enviar mensagens para o servidor."""
    mensagem = entry_widget.get().strip()
    if mensagem:
        # Comando para sair
        if mensagem.lower() == "/sair":
            running_flag.clear()
            socket_cliente.sendall(mensagem.encode())
            socket_cliente.close()
            window.destroy()
            return
        try:
            socket_cliente.sendall(mensagem.encode())
            entry_widget.delete(0, tk.END)
        except Exception as e:
            messages.insert(tk.END, f"Erro ao enviar mensagem: {e}")
            running_flag.clear()

def on_closing():
    """Encerrar conexão ao fechar a janela."""
    if messagebox.askokcancel("Sair", "Você deseja sair do chat?"):
        running_flag.clear()
        try:
            socket_cliente.sendall("/sair".encode())
        except:
            pass
        socket_cliente.close()
        window.destroy()

# Interface gráfica
window = tk.Tk()
window.title("Chatroom Monstrão")

# Frame de mensagens
frame_message = tk.Frame(master=window)
scrollBar = tk.Scrollbar(master=frame_message)
messages = tk.Listbox(master=frame_message, yscrollcommand=scrollBar.set)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
frame_message.grid(row=0, column=0, columnspan=2, sticky="nsew")

# Frame de entrada
frame_entry = tk.Frame(master=window)
textInput = tk.Entry(master=frame_entry)
textInput.pack(fill=tk.BOTH, expand=True)
textInput.bind("<Return>", lambda x: enviar_mensagem(textInput))
frame_entry.grid(row=1, column=0, padx=10, sticky="ew")

# Botão de enviar
btnSend = tk.Button(
    master=window,
    text="Enviar",
    command=lambda: enviar_mensagem(textInput)
)
btnSend.grid(row=1, column=1, padx=10, sticky="ew")

# Configuração de layout
window.rowconfigure(0, minsize=500, weight=1)
window.rowconfigure(1, minsize=50, weight=0)
window.columnconfigure(0, minsize=500, weight=1)
window.columnconfigure(1, minsize=200, weight=0)

# Eventos de fechamento
window.protocol("WM_DELETE_WINDOW", on_closing)

# Inicia a thread de recebimento
thread_receber = threading.Thread(target=receber_mensagens, daemon=True)
thread_receber.start()

# Inicia o loop da interface gráfica
window.mainloop()
