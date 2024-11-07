import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

# Conexão e criação do banco de dados
conn = sqlite3.connect('meu_banco.db')
cursor = conn.cursor()

# Adiciona colunas se não existirem na tabela 'carros'
cursor.execute('''CREATE TABLE IF NOT EXISTS carros (
                   placa TEXT PRIMARY KEY,
                   hora_entrada TEXT
                 )''')
try:
    cursor.execute("ALTER TABLE carros ADD COLUMN hora_saida TEXT")
except sqlite3.OperationalError:
    pass  # Coluna já existe

try:
    cursor.execute("ALTER TABLE carros ADD COLUMN valor_pago REAL")
except sqlite3.OperationalError:
    pass  # Coluna já existe

conn.commit()

# Função para adicionar veículo
def adicionar_carro():
    placa = entry_placa.get()
    hora_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Obtém a hora atual
    
    try:
        cursor.execute("INSERT INTO carros (placa, hora_entrada) VALUES (?, ?)", (placa, hora_atual))
        conn.commit()
        label_status.config(text="Carro adicionado com sucesso!", fg="green")
        exibir_carros()
    except sqlite3.IntegrityError:
        label_status.config(text="Erro: Carro já está registrado.", fg="red")

# Função para exibir os carros estacionados
def exibir_carros():
    listbox_carros.delete(0, tk.END)
    cursor.execute("SELECT placa, hora_entrada FROM carros WHERE hora_saida IS NULL")
    carros = cursor.fetchall()
    for carro in carros:
        listbox_carros.insert(tk.END, f"Placa: {carro[0]} | Entrada: {carro[1]}")

# Função para fechar o estacionamento de um veículo
def fechar_estacionamento():
    placa = entry_placa_saida.get()
    cursor.execute("SELECT hora_entrada FROM carros WHERE placa = ? AND hora_saida IS NULL", (placa,))
    resultado = cursor.fetchone()
    
    if resultado:
        hora_entrada = datetime.strptime(resultado[0], '%Y-%m-%d %H:%M:%S')
        hora_saida = datetime.now()
        tempo_estacionado = (hora_saida - hora_entrada).total_seconds() / 3600  # Tempo em horas
        valor_por_hora = 5.0  # Valor fixo por hora
        valor_total = round(tempo_estacionado * valor_por_hora, 2)
        
        # Atualiza o banco de dados com a hora de saída e o valor pago
        cursor.execute("UPDATE carros SET hora_saida = ?, valor_pago = ? WHERE placa = ?", 
                       (hora_saida.strftime('%Y-%m-%d %H:%M:%S'), valor_total, placa))
        conn.commit()
        
        label_saida_status.config(text=f"Fechamento concluído! Total a pagar: R$ {valor_total}", fg="green")
        exibir_carros()  # Atualiza a lista de carros estacionados
    else:
        label_saida_status.config(text="Erro: Carro não encontrado ou já retirado.", fg="red")


# Função para calcular o faturamento do dia
def calcular_faturamento():
    data_atual = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT SUM(valor_pago) FROM carros WHERE DATE(hora_saida) = ?", (data_atual,))
    resultado = cursor.fetchone()
    faturamento = resultado[0] if resultado[0] is not None else 0
    label_faturamento.config(text=f"Faturamento do dia: R$ {faturamento:.2f}")


# Interface gráfica
root = tk.Tk()
root.title("Sistema de Estacionamento")
root.configure(background='blue')
root.geometry("900x600")  # Define o tamanho da janela

# Notebook para as abas
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

# Aba de Adicionar Carro
aba_adicionar = tk.Frame(notebook)
notebook.add(aba_adicionar, text="Adicionar Carro")

label_placa = tk.Label(aba_adicionar, text="Placa:", font=("Arial", 12))
label_placa.grid(row=0, column=0, padx=10, pady=5)

entry_placa = tk.Entry(aba_adicionar, font=("Arial", 12))
entry_placa.grid(row=0, column=1, padx=10, pady=5)

botao_adicionar = tk.Button(aba_adicionar, text="Adicionar", command=adicionar_carro, font=("Arial", 12))
botao_adicionar.grid(row=1, column=0, columnspan=2, pady=15)

label_status = tk.Label(aba_adicionar, text="", font=("Arial", 10))
label_status.grid(row=2, column=0, columnspan=2)

listbox_carros = tk.Listbox(aba_adicionar, width=50, height=10, font=("Arial", 10))
listbox_carros.grid(row=3, column=0, columnspan=2, padx=10, pady=15)

# Carrega a lista de carros ao iniciar o programa
exibir_carros()

# Aba de Fechar Estacionamento
aba_fechar = tk.Frame(notebook)
notebook.add(aba_fechar, text="Fechar Estacionamento")

label_placa_saida = tk.Label(aba_fechar, text="Placa do veículo para fechar:", font=("Arial", 12))
label_placa_saida.grid(row=0, column=0, padx=10, pady=5)

entry_placa_saida = tk.Entry(aba_fechar, font=("Arial", 12))
entry_placa_saida.grid(row=0, column=1, padx=10, pady=5)

botao_fechar = tk.Button(aba_fechar, text="Fechar", command=fechar_estacionamento, font=("Arial", 12))
botao_fechar.grid(row=1, column=0, columnspan=2, pady=15)

label_saida_status = tk.Label(aba_fechar, text="", font=("Arial", 10))
label_saida_status.grid(row=2, column=0, columnspan=2)

# Aba de Faturamento do Dia
aba_faturamento = tk.Frame(notebook)
notebook.add(aba_faturamento, text="Faturamento do Dia")

botao_calcular = tk.Button(aba_faturamento, text="Calcular Faturamento", command=calcular_faturamento, font=("Arial", 12))
botao_calcular.grid(row=0, column=0, padx=10, pady=10)

label_faturamento = tk.Label(aba_faturamento, text="Faturamento do dia: R$ 0.00", font=("Arial", 12))
label_faturamento.grid(row=1, column=0, padx=10, pady=10)

# Ajuste para expandir
root.grid_rowconfigure(900, weight=900)
root.grid_columnconfigure(200, weight=50)

# Outros elementos da interface
root.mainloop()

# Fechamento da conexão com o banco de dados ao encerrar o programa
conn.close()
