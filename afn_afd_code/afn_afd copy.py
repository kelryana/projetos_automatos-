import tkinter as tk
from tkinter import ttk, messagebox, font
import math
import json

# --- Estrutura de Dados para Autômatos Predefinidos ---
PREDEFINED_AUTOMATA = {
    "Exemplo AFD (Aula 2): L = a*b+a+b*": {
        "tipo": "AFD",
        "Q": ["q0", "q1", "q2"],
        "Sigma": ["a", "b"],
        "delta": {
            "q0": {"a": "q0", "b": "q1"},
            "q1": {"a": "q2", "b": "q1"},
            "q2": {"a": "q2", "b": "q2"}
        },
        "q0": "q0",
        "F": ["q2"]
    },
    "Exemplo AFN (Aula 4): Conversão": {
        "tipo": "AFN",
        "Q": ["q0", "q1", "q2"],
        "Sigma": ["0", "1"],
        "delta": {
            "q0": {"0": ["q0"], "epsilon": ["q1"]},
            "q1": {"1": ["q2"]},
            "q2": {"0": ["q1"]}
        },
        "q0": "q0",
        "F": ["q2"]
    }
}

# --- Classes Base dos Autômatos ---

class Automaton:
    def __init__(self, Q, Sigma, delta, q0, F, tipo="Automaton"):
        self.Q = set(Q)
        self.Sigma = set(Sigma)
        self.delta = self._parse_delta(delta)
        self.q0 = q0
        self.F = set(F)
        self.tipo = tipo
        self.state_positions = {}

    def _parse_delta(self, delta_dict):
        """Converte o dicionário JSON-friendly para o formato interno (tuplas)."""
        parsed_delta = {}
        for state, transitions in delta_dict.items():
            for symbol, target in transitions.items():
                parsed_delta[(state, symbol)] = target
        return parsed_delta

    def get_quintupla_info(self):
        return (
            f"Tipo: {self.tipo}\n"
            f"Q (Estados): {self._format_set(self.Q)}\n"
            f"Σ (Alfabeto): {self._format_set(self.Sigma)}\n"
            f"q0 (Inicial): {self.q0}\n"
            f"F (Finais): {self._format_set(self.F)}\n"
        )

    def get_transition_table_str(self):
        header = ["Estado"] + sorted(list(self.Sigma))
        if self.tipo == "AFN":
            has_epsilon = False
            for (state, symbol) in self.delta:
                if symbol == "epsilon":
                    has_epsilon = True
                    break
            if has_epsilon:
                header.append("epsilon")
        
        table_str = "\t".join(header) + "\n"
        table_str += "-" * (len(table_str) * 2) + "\n"

        for state in sorted(list(self.Q)):
            row = [state]
            for symbol in header[1:]:
                transition = self.delta.get((state, symbol), "Ø")
                if isinstance(transition, set):
                    row.append(self._format_set(transition) or "Ø")
                else:
                    row.append(str(transition))
            table_str += "\t".join(row) + "\n"
        return table_str

    def _format_set(self, s):
        if not s:
            return "Ø"
        return "{" + ", ".join(sorted(list(s))) + "}"

    def validate(self, input_string):
        raise NotImplementedError

    def _calculate_positions(self, width, height):
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) / 2 - 50
        num_states = len(self.Q)
        for i, state in enumerate(sorted(list(self.Q))):
            angle = (2 * math.pi / num_states) * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.state_positions[state] = (x, y)

# --- Classe AFD ---

class AFD(Automaton):
    def __init__(self, Q, Sigma, delta, q0, F):
        super().__init__(Q, Sigma, delta, q0, F, tipo="AFD")

    def validate(self, input_string):
        current_state = self.q0
        path = [current_state]

        for symbol in input_string:
            if symbol not in self.Sigma:
                return False, path, f"Símbolo '{symbol}' não está no alfabeto Σ."
            
            current_state = self.delta.get((current_state, symbol), None)
            
            if current_state is None:
                path.append("REJEITA (Trap)")
                return False, path, f"Transição não definida de {path[-2]} com '{symbol}'."
                
            path.append(current_state)

        is_accepted = current_state in self.F
        return is_accepted, path, f"Processamento concluído. Estado final: {current_state}."

# --- Classe AFN ---

class AFN(Automaton):
    def __init__(self, Q, Sigma, delta, q0, F):
        super().__init__(Q, Sigma, delta, q0, F, tipo="AFN")
        self._normalize_delta()

    def _normalize_delta(self):
        normalized_delta = {}
        for (state, symbol), dest in self.delta.items():
            if isinstance(dest, list):
                normalized_delta[(state, symbol)] = set(dest)
            elif isinstance(dest, str):
                normalized_delta[(state, symbol)] = {dest}
            elif isinstance(dest, set):
                normalized_delta[(state, symbol)] = dest
        self.delta = normalized_delta

    def epsilon_closure(self, states):
        if isinstance(states, str):
            states = {states}
        
        closure = set(states)
        stack = list(states)
        
        while stack:
            current = stack.pop()
            epsilon_moves = self.delta.get((current, "epsilon"), set())
            for state in epsilon_moves:
                if state not in closure:
                    closure.add(state)
                    stack.append(state)
        return closure

    def move(self, states, symbol):
        next_states = set()
        for state in states:
            moves = self.delta.get((state, symbol), set())
            next_states.update(moves)
        return next_states

    def validate(self, input_string):
        current_states = self.epsilon_closure({self.q0})
        path = [current_states]

        for symbol in input_string:
            if symbol not in self.Sigma:
                return False, path, f"Símbolo '{symbol}' não está no alfabeto Σ."
            
            moved_states = self.move(current_states, symbol)
            current_states = self.epsilon_closure(moved_states)
            
            path.append(current_states)
            
            if not current_states:
                path.append("REJEITA (Trap)")
                return False, path, f"Nenhuma transição definida para '{symbol}'."

        is_accepted = not self.F.isdisjoint(current_states)
        return is_accepted, path, f"Processamento concluído. Estados finais: {self._format_set(current_states)}."

    def convert_to_afd(self):
        print("Iniciando conversão AFN -> AFD...")
        afd_Q = set()
        afd_delta = {}
        afd_F = set()
        
        q0_afn = self.q0
        q0_afd_states = self.epsilon_closure({q0_afn})
        q0_afd = self._set_to_state_name(q0_afd_states)
        afd_Q.add(q0_afd)
        
        queue = [q0_afd_states]
        processed = {q0_afd}

        while queue:
            current_afn_states = queue.pop(0)
            current_afd_state_name = self._set_to_state_name(current_afn_states)

            if not self.F.isdisjoint(current_afn_states):
                afd_F.add(current_afd_state_name)

            for symbol in self.Sigma:
                moved_states = self.move(current_afn_states, symbol)
                next_afn_states = self.epsilon_closure(moved_states)
                
                if not next_afn_states:
                    continue 

                next_afd_state_name = self._set_to_state_name(next_afn_states)
                
                if current_afd_state_name not in afd_delta:
                    afd_delta[current_afd_state_name] = {}
                afd_delta[current_afd_state_name][symbol] = next_afd_state_name
                
                if next_afd_state_name not in processed:
                    afd_Q.add(next_afd_state_name)
                    processed.add(next_afd_state_name)
                    queue.append(next_afn_states)
                    
        if not afd_Q:
             q0_afd = "q0_vazio"
             afd_Q = {q0_afd}
             return AFD(list(afd_Q), list(self.Sigma), {}, q0_afd, list(afd_F))
             
        return AFD(list(afd_Q), list(self.Sigma), afd_delta, q0_afd, list(afd_F))

    def _set_to_state_name(self, states_set):
        if not states_set:
            return "Ø"
        return "{" + ",".join(sorted(list(states_set))) + "}"

# --- Janela de Criação Manual ---

class CreateAutomatonWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Criar Novo Autômato")
        self.geometry("500x600")
        self.callback = callback
        
        ttk.Label(self, text="Definição do Autômato (JSON)", font=("Inter", 12, "bold")).pack(pady=10)
        
        self.text_area = tk.Text(self, height=20, width=50, font=("Courier", 10))
        self.text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        default_json = """{
    "tipo": "AFD",
    "Q": ["q0", "q1"],
    "Sigma": ["a", "b"],
    "delta": {
        "q0": {"a": "q1", "b": "q0"},
        "q1": {"a": "q0", "b": "q1"}
    },
    "q0": "q0",
    "F": ["q1"]
}"""
        self.text_area.insert(tk.END, default_json)
        
        ttk.Label(self, text="Dica: Para AFN, use listas nos destinos: \"q0\": {\"a\": [\"q1\", \"q2\"]}").pack(pady=5)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10, fill=tk.X)
        
        ttk.Button(btn_frame, text="Carregar Autômato", command=self.load_json).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=10)

    def load_json(self):
        try:
            content = self.text_area.get("1.0", tk.END)
            data = json.loads(content)
            
            required_keys = ["tipo", "Q", "Sigma", "delta", "q0", "F"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Faltando chave obrigatória: {key}")
            
            self.callback(data)
            self.destroy()
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro JSON", f"Erro ao ler JSON: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na estrutura: {e}")

# --- Classe Principal da Aplicação (GUI) ---

class AutomatonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Interativo de Autômatos (Python/Tkinter)")
        self.root.geometry("1200x800")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Inter", 10))
        self.style.configure("TButton", font=("Inter", 10, "bold"))
        self.style.configure("Header.TLabel", font=("Inter", 12, "bold"))
        
        self.current_automaton = None
        self.animation_step = 0
        self.animation_path = []
        self.canvas_elements = {"states": {}, "transitions": {}}

        self.control_frame = ttk.Frame(root, padding=10, width=250)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        
        self.canvas_frame = ttk.Frame(root, padding=10, relief=tk.SUNKEN)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.info_frame = ttk.Frame(root, padding=10, width=350)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        self.info_frame.pack_propagate(False)

        self._create_control_widgets()
        self._create_canvas_widgets()
        self._create_info_widgets()

    def _create_control_widgets(self):
        ttk.Label(self.control_frame, text="1. Autômato", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        
        self.create_btn = ttk.Button(
            self.control_frame, 
            text="+ Criar/Editar Autômato", 
            command=self.open_create_window
        )
        self.create_btn.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.control_frame, text="Ou selecione exemplo:", font=("Inter", 9)).pack(pady=(10,0), anchor=tk.W)
        
        self.automaton_var = tk.StringVar()
        self.automaton_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.automaton_var,
            values=list(PREDEFINED_AUTOMATA.keys()),
            state="readonly",
            width=30
        )
        self.automaton_combo.pack(fill=tk.X, pady=5)
        self.automaton_combo.bind("<<ComboboxSelected>>", self.load_predefined_automaton)
        
        self.convert_button = ttk.Button(
            self.control_frame,
            text="Converter AFN -> AFD",
            command=self.run_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(fill=tk.X, pady=10)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(self.control_frame, text="2. Validação", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        
        ttk.Label(self.control_frame, text="Cadeia de Entrada:").pack(anchor=tk.W)
        self.string_entry = ttk.Entry(self.control_frame, font=("Inter", 12))
        self.string_entry.pack(fill=tk.X, pady=5)
        
        self.run_button = ttk.Button(
            self.control_frame,
            text="Validar Cadeia",
            command=self.run_validation,
            state=tk.DISABLED
        )
        self.run_button.pack(fill=tk.X, pady=10)

        self.status_label = ttk.Label(
            self.control_frame, 
            text="Aguardando autômato...", 
            font=("Inter", 10, "italic"),
            wraplength=230
        )
        self.status_label.pack(fill=tk.X, pady=5)
        
        self.result_label = ttk.Label(
            self.control_frame, 
            text="", 
            font=("Inter", 16, "bold")
        )
        self.result_label.pack(fill=tk.X, pady=20)

    def _create_canvas_widgets(self):
        ttk.Label(self.canvas_frame, text="Visualização", style="Header.TLabel").pack(pady=5)
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", relief=tk.GROOVE, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def _create_info_widgets(self):
        ttk.Label(self.info_frame, text="Definição Formal", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        self.info_text = tk.Text(self.info_frame, height=8, width=40, font=("Courier", 10), wrap=tk.WORD)
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        ttk.Label(self.info_frame, text="Tabela de Transição", style="Header.TLabel").pack(pady=10, anchor=tk.W)
        self.table_text = tk.Text(self.info_frame, height=20, width=40, font=("Courier", 10), wrap=tk.NONE)
        self.table_text.pack(fill=tk.BOTH, expand=True)
        
        h_scroll = ttk.Scrollbar(self.info_frame, orient="horizontal", command=self.table_text.xview)
        h_scroll.pack(fill=tk.X)
        self.table_text.configure(xscrollcommand=h_scroll.set)
        self.table_text.config(state=tk.DISABLED)

    def open_create_window(self):
        CreateAutomatonWindow(self.root, self._load_automaton_data_json)

    def load_predefined_automaton(self, event=None):
        key = self.automaton_var.get()
        if key in PREDEFINED_AUTOMATA:
            self._load_automaton_data_json(PREDEFINED_AUTOMATA[key])

    def _load_automaton_data_json(self, data):
        try:
            self.current_automaton = None
            self.convert_button.config(state=tk.DISABLED)
            
            if data["tipo"] == "AFD":
                self.current_automaton = AFD(
                    data["Q"], data["Sigma"], data["delta"], data["q0"], data["F"]
                )
            elif data["tipo"] == "AFN":
                self.current_automaton = AFN(
                    data["Q"], data["Sigma"], data["delta"], data["q0"], data["F"]
                )
                self.convert_button.config(state=tk.NORMAL)
            else:
                raise ValueError("Tipo desconhecido")

            self.run_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"Autômato {data['tipo']} carregado.")
            self.result_label.config(text="")
            self.string_entry.delete(0, tk.END)
            
            self._update_info_panel()
            self._draw_automaton()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar: {e}")

    def _update_info_panel(self):
        if not self.current_automaton: return
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, self.current_automaton.get_quintupla_info())
        self.info_text.config(state=tk.DISABLED)
        
        self.table_text.config(state=tk.NORMAL)
        self.table_text.delete(1.0, tk.END)
        self.table_text.insert(tk.END, self.current_automaton.get_transition_table_str())
        self.table_text.config(state=tk.DISABLED)

    def on_canvas_resize(self, event):
        if self.current_automaton:
            self.current_automaton.state_positions = {}
            self._draw_automaton()

    def _draw_automaton(self):
        self.canvas.delete("all")
        self.canvas_elements = {"states": {}, "transitions": {}}
        
        if not self.current_automaton: return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if not self.current_automaton.state_positions:
             self.current_automaton._calculate_positions(width, height)
        
        positions = self.current_automaton.state_positions
        radius = 25
        
        grouped = {}
        for (src, sym), targets in self.current_automaton.delta.items():
            if not isinstance(targets, set): targets = {targets}
            for tgt in targets:
                key = (src, tgt)
                if key not in grouped: grouped[key] = []
                grouped[key].append(sym)
        
        for (src, tgt), syms in grouped.items():
            label = ",".join(sorted(syms))
            x1, y1 = positions[src]
            x2, y2 = positions[tgt]
            
            if src == tgt:
                self.canvas.create_arc(x1-20, y1-50, x1+20, y1-10, start=0, extent=180, style=tk.ARC, width=2)
                self.canvas.create_text(x1, y1-60, text=label)
            else:
                angle = math.atan2(y2-y1, x2-x1)
                sx = x1 + radius * math.cos(angle)
                sy = y1 + radius * math.sin(angle)
                ex = x2 - radius * math.cos(angle)
                ey = y2 - radius * math.sin(angle)
                
                self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, smooth=True, width=2)
                mx, my = (sx+ex)/2, (sy+ey)/2
                self.canvas.create_text(mx, my-10, text=label)

        for state, (x, y) in positions.items():
            color = "white"
            width_outline = 2
            
            if state in self.current_automaton.F:
                self.canvas.create_oval(x-radius+4, y-radius+4, x+radius-4, y+radius-4)
            
            item = self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, width=width_outline, tags=state)
            self.canvas.create_text(x, y, text=state, font=("Inter", 10, "bold"))
            self.canvas_elements["states"][state] = item
            
            if state == self.current_automaton.q0:
                self.canvas.create_line(x-radius-30, y, x-radius, y, arrow=tk.LAST, width=2)

    def run_conversion(self):
        if not self.current_automaton or self.current_automaton.tipo != "AFN": return
        try:
            afd = self.current_automaton.convert_to_afd()
            delta_dict = {}
            for (src, sym), tgt in afd.delta.items():
                if src not in delta_dict: delta_dict[src] = {}
                delta_dict[src][sym] = tgt
            
            data = {
                "tipo": "AFD",
                "Q": list(afd.Q),
                "Sigma": list(afd.Sigma),
                "delta": delta_dict,
                "q0": afd.q0,
                "F": list(afd.F)
            }
            self._load_automaton_data_json(data)
            messagebox.showinfo("Sucesso", "AFN convertido para AFD com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conversão: {e}")

    def run_validation(self):
        if not self.current_automaton: return
        inp = self.string_entry.get()
        
        for item in self.canvas_elements["states"].values():
            self.canvas.itemconfig(item, fill="white")
            
        try:
            accepted, path, msg = self.current_automaton.validate(inp)
            self.animation_path = path
            self.animation_step = 0
            self.final_res = (accepted, msg)
            self.status_label.config(text=f"Validando: {inp}")
            self._animate()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _animate(self):
        if self.animation_step >= len(self.animation_path):
            acc, msg = self.final_res
            color = "lightgreen" if acc else "salmon"
            res_text = "ACEITO" if acc else "REJEITADO"
            self.result_label.config(text=res_text, foreground="green" if acc else "red")
            self.status_label.config(text=msg)
            
            last = self.animation_path[-1]
            if isinstance(last, set):
                for s in last:
                    if s in self.canvas_elements["states"]:
                        self.canvas.itemconfig(self.canvas_elements["states"][s], fill=color)
            elif last in self.canvas_elements["states"]:
                self.canvas.itemconfig(self.canvas_elements["states"][last], fill=color)
            return

        for item in self.canvas_elements["states"].values():
            self.canvas.itemconfig(item, fill="white")
            
        current = self.animation_path[self.animation_step]
        
        if isinstance(current, set): # AFN
            states_str = "{" + ",".join(current) + "}"
            self.status_label.config(text=f"Passo {self.animation_step}: {states_str}")
            for s in current:
                if s in self.canvas_elements["states"]:
                    self.canvas.itemconfig(self.canvas_elements["states"][s], fill="yellow")
        else: # AFD
            if current in self.canvas_elements["states"]:
                self.canvas.itemconfig(self.canvas_elements["states"][current], fill="yellow")
                self.status_label.config(text=f"Passo {self.animation_step}: {current}")
        
        self.animation_step += 1
        self.root.after(800, self._animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomatonApp(root)
    root.mainloop()