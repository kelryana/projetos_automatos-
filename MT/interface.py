import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import time
import threading
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from maquina_turing import MaquinaTuring, Transicao
from simulador import SimuladorTM
from exemplos import exemplo_incrementador_binario
from tema import TemaManager


class InterfaceGrafica(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Máquina de Turing Visual")
        self.geometry("1000x700")
        self.minsize(900, 600)


        # Estado principal
        self.mt = MaquinaTuring()
        self.sim = SimuladorTM(self.mt)
        self.auto_running = False

        # Tema
        self.tema = TemaManager(self)

        # Layout principal: esquerda (grafo), direita (controles roláveis)
        self._build_layout()
        self._refresh_graph()
        self._refresh_tape()

    def _build_layout(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(0, weight=3)  # ocupa 3 partes
        main_frame.columnconfigure(1, weight=1)  # ocupa 1 parte
        main_frame.rowconfigure(0, weight=1)

        # Área esquerda: grafo (2/3)
        graph_frame = ttk.Frame(main_frame)
        graph_frame.grid(row=0, column=0, sticky="nsew")
    
        self.fig = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Área direita: controles (1/3) com scrollbar
        right_frame = ttk.Frame(main_frame, width=420)
        right_frame.grid(row=0, column=1, sticky="nsew")   # <<< AQUI
        right_frame.pack_propagate(False)

        right_canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=right_canvas.yview)

        scrollable_frame = ttk.Frame(right_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        )

        window_id = right_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        right_canvas.bind(
            "<Configure>",
            lambda e: (
                right_canvas.itemconfig(window_id, width=e.width),
                right_canvas.configure(scrollregion=right_canvas.bbox("all"))
            )
        )

        right_canvas.configure(yscrollcommand=scrollbar.set)

        right_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # -------------------------
        # Estados
        st_frame = ttk.LabelFrame(scrollable_frame, text="Estados")
        st_frame.pack(fill=tk.X, padx=4, pady=4)
        st_frame.columnconfigure(0, weight=1)

        ttk.Label(st_frame, text="Nome do Estado").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_state = ttk.Entry(st_frame, width=20)
        self.ent_state.insert(0, "q0, q1, ...")
        self.ent_state.grid(row=1, column=0, columnspan=3, padx=4, pady=2)

        self.var_initial = tk.BooleanVar()
        self.var_accept = tk.BooleanVar()
        self.var_reject = tk.BooleanVar()

        ttk.Checkbutton(st_frame, text="Inicial", variable=self.var_initial).grid(row=2, column=0, padx=4, pady=2)
        ttk.Checkbutton(st_frame, text="Aceitação", variable=self.var_accept).grid(row=2, column=1, padx=4, pady=2)
        ttk.Checkbutton(st_frame, text="Rejeição", variable=self.var_reject).grid(row=2, column=2, padx=4, pady=2)

        ttk.Button(st_frame, text="Adicionar Estado", style="Rounded.TButton", command=self._add_state).grid(row=3, column=0, columnspan=3, padx=4, pady=6, sticky="ew")
        

        # Transições
        tr_frame = ttk.LabelFrame(scrollable_frame, text="Transições")
        tr_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(tr_frame, text="Estado Origem").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.cmb_from = ttk.Combobox(tr_frame, values=list(self.mt.Q))
        self.cmb_from.grid(row=1, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(tr_frame, text="Símbolo lido").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.ent_symbol = ttk.Entry(tr_frame)
        self.ent_symbol.insert(0, "a, b, ε, ...")
        self.ent_symbol.grid(row=3, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(tr_frame, text="Estado Destino").grid(row=4, column=0, sticky="w", padx=4, pady=2)
        self.cmb_to = ttk.Combobox(tr_frame, values=list(self.mt.Q))
        self.cmb_to.grid(row=5, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(tr_frame, text="Símbolo gerado").grid(row=6, column=0, sticky="w", padx=4, pady=2)
        self.ent_write = ttk.Entry(tr_frame)
        self.ent_write.insert(0, "a, b, ε, ...")
        self.ent_write.grid(row=7, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(tr_frame, text="Direção").grid(row=8, column=0, sticky="w", padx=4, pady=2)
        self.cmb_move = ttk.Combobox(tr_frame, values=["R", "L", "S"])
        self.cmb_move.set("R")
        self.cmb_move.grid(row=9, column=0, padx=4, pady=2, sticky="ew")

        ttk.Button(tr_frame, text="Adicionar Transição", style="Rounded.TButton", command=self._add_transition).grid(row=10, column=0, padx=4, pady=6, sticky="ew")
        tr_frame.columnconfigure(0, weight=1)

        # Alfabetos
        alf_frame = ttk.LabelFrame(scrollable_frame, text="Alfabetos")
        alf_frame.pack(fill=tk.X, padx=4, pady=4)
        alf_frame.columnconfigure(0, weight=1)

        ttk.Label(alf_frame, text="Σ (alfabeto de entrada)").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_sigma = ttk.Entry(alf_frame)
        self.ent_sigma.insert(0, "Ex: a, b")
        self.ent_sigma.grid(row=1, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(alf_frame, text="Γ (alfabeto da fita)").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.ent_gamma = ttk.Entry(alf_frame)
        self.ent_gamma.insert(0, "Ex: a, b, X, Y")
        self.ent_gamma.grid(row=3, column=0, padx=4, pady=2, sticky="ew")

        ttk.Label(alf_frame, text="Símbolo branco (blank)").grid(row=4, column=0, sticky="w", padx=4, pady=2)
        self.ent_blank = ttk.Entry(alf_frame)
        self.ent_blank.insert(0, "Ex: □ ou λ")
        self.ent_blank.grid(row=5, column=0, padx=4, pady=2, sticky="ew")

        ttk.Button(alf_frame, text="Aplicar Alfabetos", command=self._apply_alphabets).grid(row=6, column=0, padx=4, pady=6, sticky="ew")

        # Simulação
        sim_frame = ttk.LabelFrame(scrollable_frame, text="Simulação")
        sim_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(sim_frame, text="Entrada da fita").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_input = ttk.Entry(sim_frame, width=30)
        self.ent_input.insert(0, "Ex: aabb")   # placeholder
        self.ent_input.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        ttk.Label(sim_frame, text="Limite de passos").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.ent_limit = ttk.Entry(sim_frame, width=10)
        self.ent_limit.insert(0, "500")   # valor padrão
        self.ent_limit.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        ttk.Label(sim_frame, text="Velocidade (ms)").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.ent_speed = ttk.Entry(sim_frame, width=10)
        self.ent_speed.insert(0, "100")   # valor padrão
        self.ent_speed.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        # Botões de controle
        ttk.Button(sim_frame, text="Reset", command=self._reset_sim).grid(row=3, column=0, padx=4, pady=4)
        ttk.Button(sim_frame, text="Passo", command=self._step_sim).grid(row=3, column=1, padx=4, pady=4)
        ttk.Button(sim_frame, text="Rodar", command=self._run_sim).grid(row=3, column=2, padx=4, pady=4)
        ttk.Button(sim_frame, text="Parar", command=self._stop_sim).grid(row=3, column=3, padx=4, pady=4)

        # Arquivos
        file_frame = ttk.LabelFrame(scrollable_frame, text="Arquivos")
        file_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Button(file_frame, text="Salvar", style="Rounded.TButton", command=self._save_json).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(file_frame, text="Carregar", style="Rounded.TButton", command=self._load_json).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(file_frame, text="Exportar Grafo", style="Rounded.TButton", command=self._export_graph_png).grid(row=0, column=2, padx=4, pady=4, sticky="ew")

        # Extras
        extra_frame = ttk.LabelFrame(scrollable_frame, text="Extras")
        extra_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Button(extra_frame, text="Gerar Exemplo", style="Rounded.TButton", command=self._load_example).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ttk.Button(extra_frame, text="Limpar Tudo", style="Rounded.TButton", command=self._clear_all).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(extra_frame, text="Tema Claro/Escuro", style="Rounded.TButton", command=self.tema.toggle).grid(row=0, column=2, padx=4, pady=4, sticky="ew")

        # Fita + Console
        tape_frame = ttk.LabelFrame(scrollable_frame, text="Fita")
        tape_frame.pack(fill=tk.X, padx=8, pady=4)
        self.tape_canvas = tk.Canvas(tape_frame, height=120, bg="#ffffff")
        self.tape_canvas.pack(fill=tk.X, padx=4, pady=4)

        console_frame = ttk.LabelFrame(scrollable_frame, text="Console")
        console_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.txt_console = tk.Text(console_frame, height=15, bg="#111827", fg="#e5e7eb")
        self.txt_console.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    # -------------------------
    # Funções de controle
    # -------------------------
    def _add_state(self):
        s = self.ent_state.get().strip()
        if not s:
            messagebox.showerror("Erro", "Nome do estado não pode ser vazio.")
            return
        self.mt.add_state(s)
        if self.var_initial.get():
            self.mt.set_initial(s)
        if self.var_accept.get():
            self.mt.add_accept(s)
        if self.var_reject.get():
            self.mt.add_reject(s)
        
        # Atualizar comboboxes
        self.cmb_from["values"] = list(self.mt.Q)
        self.cmb_to["values"] = list(self.mt.Q)
        self._refresh_graph()

    def _set_initial(self):
        s = self.ent_state.get().strip()
        if s:
            self.mt.set_initial(s)
            self._refresh_graph()

    def _add_accept(self):
        s = self.ent_state.get().strip()
        if s:
            self.mt.add_accept(s)
            self._refresh_graph()

    def _add_reject(self):
        s = self.ent_state.get().strip()
        if s:
            self.mt.add_reject(s)
            self._refresh_graph()

    def _add_transition(self):
        from_state = self.cmb_from.get().strip()
        symbol = self.ent_symbol.get().strip() or self.mt.blank
        to_state = self.cmb_to.get().strip()
        write = self.ent_write.get().strip() or self.mt.blank
        move = self.cmb_move.get().strip()

        # Verificações
        if not from_state or not to_state or not move:
            messagebox.showerror("Erro", "Origem, destino e movimento são obrigatórios.")
            return

        if from_state not in self.mt.Q or to_state not in self.mt.Q:
            messagebox.showerror("Erro", "Estados origem/destino devem existir.")
            return

        if symbol not in self.mt.gamma:
            messagebox.showerror("Erro", f"Símbolo '{symbol}' não está no alfabeto da fita.")
            return



        # Validação
        if from_state not in self.mt.Q or to_state not in self.mt.Q:
            messagebox.showerror("Erro", "Estados origem/destino devem existir.")
            return
        if symbol not in self.mt.gamma:
            messagebox.showerror("Erro", f"Símbolo '{symbol}' não está no alfabeto da fita.")
            return

        t = Transicao(from_state, symbol, to_state, write, move)
        self.mt.add_transition(t)
        self._refresh_graph()
        self._log(f"Transição adicionada: ({t.from_state}, {t.read}) → ({t.to_state}, {t.write}, {t.move})")
    
    def _apply_alphabets(self):
        try:
            sigma = [s.strip() for s in self.ent_sigma.get().split(",") if s.strip()]
            gamma = [s.strip() for s in self.ent_gamma.get().split(",") if s.strip()]
            blank = self.ent_blank.get().strip() or "λ"
            self.mt.set_alphabets(sigma, gamma, blank)
            self._log("Alfabetos aplicados.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # -------------------------
    # Simulação
    # -------------------------
    def _reset_sim(self):
        try:
            entrada = self.ent_input.get()
            limit = int(self.ent_limit.get())
            self.sim.timeout_steps = limit
            self.sim.reset(entrada)
            self._refresh_tape()
            self._highlight_current_state()
            self._log(f"Reset: estado={self.sim.current_state}, head={self.sim.fita.head}, limite={limit}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _step_sim(self):
        try:
            tr = self.sim.step()
            self._refresh_tape()
            self._highlight_current_state()
            if tr is None:
                self._log(self._final_result())
            else:
                self._log(f"Passo {self.sim.step_count}: ({tr.from_state}, lido='{tr.read}') → escreve '{tr.write}', move {tr.move}, novo estado {tr.to_state}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _run_sim(self):
        if self.auto_running:
            return
        try:
            if self.sim.current_state is None:
                self._reset_sim()
            delay_ms = int(self.ent_speed.get())
            self.auto_running = True
            def worker():
                while self.auto_running and not self.sim.is_accept() and not self.sim.is_reject():
                    if self.sim.step_count >= self.sim.timeout_steps:
                        break
                    tr = self.sim.step()
                    self._refresh_tape()
                    self._highlight_current_state()
                    if tr is None:
                        break
                    self._log(f"Passo {self.sim.step_count}: ({tr.from_state}, lido='{tr.read}') → escreve '{tr.write}', move {tr.move}, novo estado {tr.to_state}")
                    time.sleep(max(0.0, delay_ms / 1000.0))
                self.auto_running = False
                self._log(self._final_result())
            threading.Thread(target=worker, daemon=True).start()
        except Exception as e:
            self.auto_running = False
            messagebox.showerror("Erro", str(e))

    def _stop_sim(self):
        self.auto_running = False
        self.sim.running = False
        self._log("Execução parada.")

    def _final_result(self) -> str:
        if self.sim.step_count >= self.sim.timeout_steps and not self.sim.is_accept() and not self.sim.is_reject():
            return f"Não parou (limite atingido: {self.sim.timeout_steps} passos)."
        if self.sim.is_accept():
            return f"Cadeia aceita em {self.sim.step_count} passos."
        if self.sim.is_reject():
            return f"Cadeia rejeitada em {self.sim.step_count} passos."
        return f"Cadeia rejeitada (transição inexistente)."

    # -------------------------
    # Visualização
    # -------------------------
    def _refresh_graph(self):
        self.ax.clear()

        # MULTI-GRAFO → permite múltiplas arestas entre os mesmos nós
        G = nx.MultiDiGraph()

        # Adiciona estados
        for q in self.mt.Q:
            G.add_node(q)

        # Agrupar transições por par (from → to)
        edge_map = {}

        for tr in self.mt.transitions:
            key = (tr.from_state, tr.to_state)
            text = f"{tr.read}/{tr.write},{tr.move}"

            if key not in edge_map:
                edge_map[key] = [text]
            else:
                edge_map[key].append(text)

        # Criar arestas com labels combinados
        for (u, v), labels in edge_map.items():
            G.add_edge(u, v, label="\n".join(labels))



        # Layout
        pos = nx.spring_layout(G, seed=42, k=0.8)

        # Cores e tamanhos dos estados
        node_colors = []
        node_sizes = []
        for n in G.nodes():
            if n in self.mt.q_accept:
                node_colors.append("#10b981")
                node_sizes.append(1600)
            elif n in self.mt.q_reject:
                node_colors.append("#ef4444")
                node_sizes.append(1400)
            elif n == self.mt.q0:
                node_colors.append("#3b82f6")
                node_sizes.append(1400)
            else:
                node_colors.append("#9ca3af")
                node_sizes.append(1200)

        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=node_sizes,
            ax=self.ax, linewidths=1.5, edgecolors="#111827"
        )
        nx.draw_networkx_labels(G, pos, font_color="#111827", ax=self.ax)

        # Arestas → MULTIPLE EDGES FUNCIONAM AQUI
        nx.draw_networkx_edges(
            G, pos, arrowstyle="-|>", arrowsize=16,
            width=1.5, edge_color="#111827", ax=self.ax,
            connectionstyle="arc3,rad=0.2"   # curva para separar arestas múltiplas
        )

        # Labels das arestas
        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels, font_size=9, ax=self.ax,
            bbox=dict(boxstyle="round", fc="#f9fafb", ec="#d1d5db")
        )

        # Indicador do estado inicial
        if self.mt.q0 in G.nodes():
            x, y = pos[self.mt.q0]
            self.ax.annotate(
                "", xy=(x, y + 0.12), xytext=(x, y + 0.35),
                arrowprops=dict(arrowstyle="->", color="#3b82f6", lw=2)
            )

        self.ax.set_axis_off()
        self.fig.tight_layout()
        self.canvas.draw()

        
    def _highlight_current_state(self):
        if self.sim.current_state:
            self.ax.set_title(f"Estado atual: {self.sim.current_state}")
        else:
            self.ax.set_title("Grafo de estados")
        self.canvas.draw()

    def _refresh_tape(self):
        self.tape_canvas.delete("all")
        cells = self.sim.fita.window(radius=10)
        x = 10
        y = 30
        for pos, sym in cells:
            sym = "□" if sym == self.mt.blank else sym
            color = "#e5e7eb"
            outline = "#9ca3af"
            if pos == self.sim.fita.head:
                color = "#bfdbfe"
                outline = "#2563eb"
            self.tape_canvas.create_rectangle(x, y, x+40, y+40, fill=color, outline=outline)
            self.tape_canvas.create_text(x+20, y+20, text=sym)
            self.tape_canvas.create_text(x+20, y+55, text=str(pos), font=("Consolas", 8))
            x += 45

    def _log(self, text: str):
        self.txt_console.insert(tk.END, text + "\n")
        self.txt_console.see(tk.END)

    # -------------------------
    # Arquivos e Extras
    # -------------------------
    def _save_json(self):
        try:
            d = self.mt.to_json()
            fname = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if fname:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False, indent=2)
                self._log(f"Máquina salva em {fname}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _load_json(self):
        try:
            fname = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
            if fname:
                with open(fname, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.mt = MaquinaTuring.from_json(d)
                self.sim = SimuladorTM(self.mt)
                self._refresh_graph()
                self._refresh_tape()
                self._log(f"Máquina carregada de {fname}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _export_graph_png(self):
        try:
            fname = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if fname:
                self.fig.savefig(fname, dpi=200)
                self._log(f"Grafo exportado em {fname}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _load_example(self):
        self.mt = exemplo_incrementador_binario()
        self.sim = SimuladorTM(self.mt)
        self._refresh_graph()
        self._refresh_tape()
        self._log("Exemplo carregado: Incrementador binário.")

    def _clear_all(self):
        self.mt = MaquinaTuring()
        self.sim = SimuladorTM(self.mt)
        self.txt_console.delete("1.0", tk.END)
        self._refresh_graph()
        self._refresh_tape()
        self._log("Máquina limpa.")
