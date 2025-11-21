import math
import tkinter as tk
from tkinter import ttk

# ---------------------------
#  Estilo Moderno
# ---------------------------
def configure_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Rounded.TEntry",
                    padding=10,
                    relief="flat",
                    bordercolor="#d1d5db",
                    focusthickness=3,
                    focuscolor="#3b82f6")

    style.configure("Rounded.TButton",
                    padding=10,
                    font=("Segoe UI", 10, "bold"),
                    relief="flat",
                    background="#3b82f6",
                    foreground="white")

    style.map("Rounded.TButton",
              background=[("active", "#2563eb")])

    style.configure("Card.TFrame",
                    background="white",
                    relief="flat",
                    padding=20)

    style.configure("Header.TLabel",
                    font=("Segoe UI", 28, "bold"),
                    background="#f1f5f9")

    style.configure("SubHeader.TLabel",
                    font=("Segoe UI", 12),
                    background="#f1f5f9",
                    foreground="#64748b")


# ---------------------------
# Layout Principal
# ---------------------------
root = tk.Tk()
root.title("Simulador de Autômato a Pilha")
root.state("zoomed")
root.configure(bg="#f1f5f9")

configure_style()

# ---------------------------
# Header
# ---------------------------
header = tk.Frame(root, bg="#f1f5f9")
header.pack(fill="x", padx=20, pady=10)

title = ttk.Label(header,
                  text="Simulador de Autômato a Pilha",
                  style="Header.TLabel")
title.pack(anchor="w")

subtitle = ttk.Label(header,
                     text="Sistema educacional para criação e simulação de APNs",
                     style="SubHeader.TLabel")
subtitle.pack(anchor="w")

# ---------------------------
# Área principal
# ---------------------------
main_frame = tk.Frame(root, bg="#f1f5f9")
main_frame.pack(fill="both", expand=True, padx=15)

# Canvas à esquerda ----------------------
canvas_frame = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
canvas_frame.pack(side="left", expand=True, fill="both", padx=(0,15))

canvas = tk.Canvas(canvas_frame, bg="white")
canvas.pack(fill="both", expand=True)

# ---------------------------
# Estruturas de dados (globais)
# ---------------------------
estados = {}          # {"q0": {"inicial": True, "final": False}}
transicoes = []       # lista de dicionários de transição
posicoes_estados = {} # {"q0": (x,y)}
objetos_canvas = {}   # {"q0": {"circulo": id, "texto": id, "extra": id}}

# -----------------------------------------
# SIMULAÇÃO DO AUTÔMATO A PILHA
# -----------------------------------------

def simular_automato(entrada):
    inicios = [e for e, info in estados.items() if info.get("inicial")]
    if not inicios:
        return "ERRO: nenhum estado inicial definido."
    inicial = inicios[0]

    fila = [(inicial, 0, "Z")] 
    visitados = set()

    while fila:
        estado, i, pilha = fila.pop(0)

        chave = (estado, i, pilha)
        if chave in visitados:
            continue
        visitados.add(chave)

        if i == len(entrada) and estados[estado].get("final") and (pilha == "Z" or pilha == ""):
            return "ACEITA"

        for t in transicoes:
            if t["origem"] != estado:
                continue

            ler = t["entrada"]
            desempilha = t["pilha"]
            empilha = t["empilha"]
            prox = t["destino"]

            if ler != "ε":
                if i >= len(entrada) or entrada[i] != ler:
                    continue
                prox_i = i + 1
            else:
                prox_i = i

            if desempilha != "ε":
                if not pilha or pilha[-1] != desempilha:
                    continue
                nova_pilha = pilha[:-1]
            else:
                nova_pilha = pilha

            if empilha != "ε":
                nova_pilha = nova_pilha + empilha

            fila.append((prox, prox_i, nova_pilha))

    return "REJEITA"



# ---------------------------
# Funções de desenho
# ---------------------------
def desenhar_estado(nome):
    """Desenha um estado no canvas se ainda não existir."""
    if nome in objetos_canvas:
        # Atualizar desenho de inicial/final se necessário
        atualizar_decoracoes_estado(nome)
        return

    total = len(objetos_canvas)
    # posição automática simples (linha)
    x = 150 + (total * 150)
    y = 150

    posicoes_estados[nome] = (x, y)

    # Desenhar círculo
    r = 35
    circ = canvas.create_oval(x - r, y - r, x + r, y + r, fill="#e2e8f0", outline="#475569", width=3)

    # Nome do estado
    txt = canvas.create_text(x, y, text=nome, font=("Segoe UI", 14, "bold"), fill="#1e293b")

    objetos_canvas[nome] = {"circulo": circ, "texto": txt, "r": r}

    atualizar_decoracoes_estado(nome)

def atualizar_decoracoes_estado(nome):
    """Desenha/atualiza seta de entrada para inicial e círculo duplo para final."""
    # Remover decorações antigas se houver
    extra_id = objetos_canvas[nome].get("extra")
    if extra_id:
        # extra pode ser uma lista de objetos
        if isinstance(extra_id, list):
            for oid in extra_id:
                try:
                    canvas.delete(oid)
                except:
                    pass
        else:
            try:
                canvas.delete(extra_id)
            except:
                pass
        objetos_canvas[nome]["extra"] = None

    x, y = posicoes_estados[nome]
    r = objetos_canvas[nome].get("r", 35)
    extras = []

    # seta de entrada (estado inicial)
    if estados.get(nome, {}).get("inicial"):
        # seta à esquerda do círculo
        line = canvas.create_line(x - r - 30, y, x - r - 5, y, arrow=tk.LAST, width=2)
        extras.append(line)

    # círculo duplo (estado final)
    if estados.get(nome, {}).get("final"):
        inner = canvas.create_oval(x - r + 6, y - r + 6, x + r - 6, y + r - 6, outline="#475569", width=2)
        extras.append(inner)

    if extras:
        objetos_canvas[nome]["extra"] = extras

def desenhar_transicao(origem, destino, simbolo_label=None):
    """
    Desenha uma linha com seta entre dois estados. Se origem==destino, desenha um laço.
    simbolo_label: texto a ser exibido perto da seta (pode ser None).
    """
    # Garantir que ambos os estados existam no canvas (desenhar se necessário)
    if origem not in posicoes_estados:
        desenhar_estado(origem)
    if destino not in posicoes_estados:
        desenhar_estado(destino)

    x1, y1 = posicoes_estados[origem]
    x2, y2 = posicoes_estados[destino]
    r1 = objetos_canvas[origem].get("r", 35)
    r2 = objetos_canvas[destino].get("r", 35)

    if origem == destino:
        # Desenhar loop (oval pequeno acima do estado)
        loop_r = 30
        loop = canvas.create_oval(x1 - loop_r, y1 - r1 - 2*loop_r, x1 + loop_r, y1 - r1, outline="#0f172a", width=2)
        # seta manual (pequena)
        arrow_x = x1 + loop_r
        arrow_y = y1 - r1 - loop_r/2
        arrow = canvas.create_line(arrow_x - 10, arrow_y + 6, arrow_x, arrow_y, arrow=tk.LAST, width=2)
        if simbolo_label:
            lbl = canvas.create_text(x1, y1 - r1 - loop_r - 10, text=simbolo_label, font=("Segoe UI", 10))
            return (loop, arrow, lbl)
        return (loop, arrow)

    # Calcular bordas para que a linha não entre no círculo
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        dist = 0.0001
    # offset dos centros para as bordas dos círculos
    offset_x1 = x1 + dx * (r1 / dist)
    offset_y1 = y1 + dy * (r1 / dist)
    offset_x2 = x2 - dx * (r2 / dist)
    offset_y2 = y2 - dy * (r2 / dist)

    line = canvas.create_line(offset_x1, offset_y1, offset_x2, offset_y2, arrow=tk.LAST, width=2, smooth=True)

    if simbolo_label:
        xm = (offset_x1 + offset_x2) / 2
        ym = (offset_y1 + offset_y2) / 2
        lbl = canvas.create_text(xm, ym - 10, text=simbolo_label, font=("Segoe UI", 10))
        return (line, lbl)
    return (line,)

# ---------------------------
# Painel lateral
# ---------------------------
panel = ttk.Frame(main_frame, style="Card.TFrame")
panel.pack(side="right", fill="y", padx=5)

panel_title = tk.Label(panel,
                       text="⚙️  Painel de Controle",
                       font=("Segoe UI", 16, "bold"),
                       bg="white")
panel_title.pack(anchor="w")

# Abas -----------------------------------
tabs = ttk.Notebook(panel)
tab_estados = ttk.Frame(tabs)
tab_trans = ttk.Frame(tabs)
tab_config = ttk.Frame(tabs)

tabs.add(tab_estados, text="Estados")
tabs.add(tab_trans, text="Transições")
tabs.pack(fill="both", expand=True, pady=10)

# ---------------------------
# Conteúdo da aba ESTADOS
# ---------------------------
for widget in tab_estados.winfo_children():
    widget.destroy()

# Título interno
title_est = tk.Label(tab_estados,
                     text="Adicionar Estado",
                     font=("Segoe UI", 10, "bold"),
                     bg="white")
title_est.pack(anchor="w", pady=(10,0))

# Frame do input e botão "+"
input_frame = tk.Frame(tab_estados, bg="white")
input_frame.pack(fill="x", pady=(5,10))

entry_estado = ttk.Entry(input_frame, style="Rounded.TEntry")
entry_estado.pack(side="left", fill="x", expand=True, padx=(0,10))

# Checkboxes para marcar estado inicial e final
var_inicial = tk.BooleanVar()
var_final = tk.BooleanVar()

chk_inicial = tk.Checkbutton(
    tab_estados,
    text="Estado Inicial",
    bg="white",
    variable=var_inicial
)
chk_inicial.pack(anchor="w")

chk_final = tk.Checkbutton(
    tab_estados,
    text="Estado Final",
    bg="white",
    variable=var_final
)
chk_final.pack(anchor="w")

def update_comboboxes():
    """Atualiza as opções dos comboboxes de origem/destino com os estados atuais."""
    vals = list(estados.keys())
    cb_origem['values'] = vals
    cb_destino['values'] = vals

def adicionar_estado():
    nome = entry_estado.get().strip()
    if nome == "":
        return

    # Evitar duplicata:
    if nome in estados:
        # Atualiza flags e decorações
        estados[nome]["inicial"] = var_inicial.get()
        estados[nome]["final"] = var_final.get()
        atualizar_decoracoes_estado(nome)
    else:
        estados[nome] = {
            "inicial": var_inicial.get(),
            "final": var_final.get()
        }
        # inserir visual e na listbox
        label = nome
        tags = []
        if estados[nome]["inicial"]:
            tags.append("I")
        if estados[nome]["final"]:
            tags.append("F")
        if tags:
            label += " (" + ", ".join(tags) + ")"
        estados_listbox.insert(tk.END, label)
        desenhar_estado(nome)

    # Atualiza comboboxes de transição
    update_comboboxes()

    # Limpar campos
    entry_estado.delete(0, tk.END)
    var_inicial.set(False)
    var_final.set(False)

btn_add_estado = tk.Button(input_frame,
                           text="+",
                           font=("Segoe UI", 14, "bold"),
                           width=3,
                           bg="#3b82f6",
                           fg="white",
                           relief="flat",
                           activebackground="#2563eb",
                           activeforeground="white",
                           bd=0)
btn_add_estado.pack(side="right")

btn_add_estado.configure(command=adicionar_estado)

# Área com Scroll para listar estados
list_frame = tk.Frame(tab_estados, bg="white")
list_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

estados_listbox = tk.Listbox(
    list_frame,
    bg="white",
    fg="#1e293b",
    font=("Segoe UI", 11),
    highlightthickness=0,
    activestyle="none",
    bd=0,
    yscrollcommand=scrollbar.set
)
estados_listbox.pack(fill="both", expand=True)

scrollbar.config(command=estados_listbox.yview)

# ---------------------------
# Conteúdo da aba Transições
# ---------------------------
def add_section(parent, text):
    label = tk.Label(parent, text=text,
                     font=("Segoe UI", 10, "bold"),
                     bg="white")
    label.pack(anchor="w", pady=(10,0))

add_section(tab_trans, "Estado Origem")
cb_origem = ttk.Combobox(tab_trans, values=[])
cb_origem.pack(fill="x", pady=5)

add_section(tab_trans, "Estado Destino")
cb_destino = ttk.Combobox(tab_trans, values=[])
cb_destino.pack(fill="x", pady=5)

add_section(tab_trans, "Símbolo de Entrada")
cb_entrada = ttk.Combobox(tab_trans, values=["a","b","ε"])
cb_entrada.pack(fill="x", pady=5)

add_section(tab_trans, "Topo da Pilha")
cb_pilha = ttk.Combobox(tab_trans, values=["X","Z","ε"])
cb_pilha.pack(fill="x", pady=5)

add_section(tab_trans, "Empilhar (resultado)")
entry_empilha = ttk.Entry(tab_trans)
entry_empilha.pack(fill="x", pady=5)

def salvar_transicao():
    origem = cb_origem.get().strip()
    destino = cb_destino.get().strip()
    entrada = cb_entrada.get().strip()
    pilha = cb_pilha.get().strip()
    empilha = entry_empilha.get().strip()

    if origem == "" or destino == "" or entrada == "" or pilha == "":
        print("Preencha todos os campos da transição!")
        return

    transicao = {
        "origem": origem,
        "destino": destino,
        "entrada": entrada,
        "pilha": pilha,
        "empilha": empilha if empilha != "" else "ε"
    }

    transicoes.append(transicao)

    # Desenha transição (cria estados no canvas caso ainda não existam)
    simbolo_label = f"{entrada}, {pilha}→{transicao['empilha']}"
    desenhar_transicao(origem, destino, simbolo_label)

    print("Transição adicionada:", transicao)

    # Limpa campos
    cb_origem.set("")
    cb_destino.set("")
    cb_entrada.set("")
    cb_pilha.set("")
    entry_empilha.delete(0, tk.END)

# Botão de adicionar ---------------------
btn_add = ttk.Button(tab_trans,
                     text="Adicionar Transição",
                     style="Rounded.TButton")
btn_add.pack(fill="x", pady=20)

btn_add.configure(command=salvar_transicao)

# ---------------------------
# SIMULAÇÃO
# ---------------------------
sim_frame = ttk.Frame(panel, style="Card.TFrame")
sim_frame.pack(fill="x", pady=20)

sim_label = tk.Label(sim_frame,
                     text="▶ Simulação",
                     font=("Segoe UI", 14, "bold"),
                     bg="white")
sim_label.pack(anchor="w")

entry_sim = ttk.Entry(sim_frame, style="Rounded.TEntry")
entry_sim.pack(fill="x", pady=10)

from tkinter import messagebox

def iniciar_simulacao():
    cadeia = entry_sim.get().strip()

    if cadeia == "":
        messagebox.showwarning("Aviso", "Digite uma cadeia para simular.")
        return

    resultado = simular_automato(cadeia)

    if resultado == "ACEITA":
        messagebox.showinfo("Resultado", f"A cadeia '{cadeia}' foi ACEITA.")
    elif resultado.startswith("ERRO"):
        messagebox.showerror("Erro", resultado)
    else:
        messagebox.showwarning("Resultado", f"A cadeia '{cadeia}' foi rejeitada.")


run_button = ttk.Button(sim_frame,
                        text="Iniciar",
                        style="Rounded.TButton",
                        command=iniciar_simulacao)
run_button.pack(fill="x")

# Inicializa comboboxes vazios corretamente
update_comboboxes()

root.mainloop()
