import tkinter as tk
from tkinter import ttk, messagebox, font
import math

PREDEFINED_AUTOMATA = {
    "AFD: L = a*b+a+b* ": {
        "tipo": "AFD",
        "Q": {"q0", "q1", "q2"},
        "Sigma": {"a", "b"},
        "delta": {
            ("q0", "a"): "q0",
            ("q0", "b"): "q1",
            ("q1", "a"): "q2",
            ("q1", "b"): "q1",
            ("q2", "a"): "q2",
            ("q2", "b"): "q2",
        },
        "q0": "q0",
        "F": {"q2"},
    },
    "AFD: L = 0(0|1)*1": {
        "tipo": "AFD",
        "Q": {"q0", "q1", "q2", "q3"},
        "Sigma": {"0", "1"},
        "delta": {
            ("q0", "0"): "q1",
            ("q0", "1"): "q3",
            ("q1", "0"): "q1",
            ("q1", "1"): "q2",
            ("q2", "0"): "q1",
            ("q2", "1"): "q2",
            ("q3", "0"): "q3",
            ("q3", "1"): "q3",
        },
        "q0": "q0",
        "F": {"q2"},
    },
    "AFN (com ε): L = 0*1*2* ": {
        "tipo": "AFN",
        "Q": {"q1", "q2", "q3"},
        "Sigma": {"0", "1", "2"},
        "delta": {
            ("q1", "0"): {"q1"},
            ("q1", "epsilon"): {"q2"},
            ("q2", "1"): {"q2"},
            ("q2", "epsilon"): {"q3"},
            ("q3", "2"): {"q3"},
        },
        "q0": "q1",
        "F": {"q3"},
    },
    
    "AFN (com ε): Conversão )": {
        "tipo": "AFN",
        "Q": {"q0", "q1", "q2"},
        "Sigma": {"0", "1"},
        "delta": {
            ("q0", "0"): {"q0"},
            ("q0", "epsilon"): {"q1"},
            ("q1", "1"): {"q2"},
            ("q2", "0"): {"q1"},
        },
        "q0": "q0",
        "F": {"q2"},
    }
}

class Automaton:
   
    def __init__(self, Q, Sigma, delta, q0, F, tipo="Automaton"):
        self.Q = set(Q)
        self.Sigma = set(Sigma)
        self.delta = delta
        self.q0 = q0
        self.F = set(F)
        self.tipo = tipo
    
        self.state_positions = {}

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
            if any("epsilon" in k[0] or "epsilon" in k[1] for k in self.delta.keys()):
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

        raise NotImplementedError("O método 'validate' deve ser implementado por uma subclasse (AFD ou AFN).")

    def _calculate_positions(self, width, height):
       
        self.state_positions = {}
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) / 2 - 50  
        num_states = len(self.Q)
        
        for i, state in enumerate(sorted(list(self.Q))):
            angle = (2 * math.pi / num_states) * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.state_positions[state] = (x, y)

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

class AFN(Automaton):
   
    def __init__(self, Q, Sigma, delta, q0, F):
        super().__init__(Q, Sigma, delta, q0, F, tipo="AFN")
       
        self._normalize_delta()

    def _normalize_delta(self):
       
        normalized_delta = {}
        for (state, symbol), dest in self.delta.items():
            if isinstance(dest, set):
                normalized_delta[(state, symbol)] = dest
            else:
                
                normalized_delta[(state, symbol)] = {dest}
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
                return False, path, f"Nenhuma transição definida para '{symbol}' a partir de {path[-2]}."

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
                
                afd_delta[(current_afd_state_name, symbol)] = next_afd_state_name
                
                if next_afd_state_name not in processed:
                   
                    afd_Q.add(next_afd_state_name)
                    processed.add(next_afd_state_name)
                    queue.append(next_afn_states)
                    
        print(f"Conversão concluída. Q={afd_Q}")
        
        if not afd_Q:
            
             q0_afd = "q0_vazio"
             afd_Q = {q0_afd}
             return AFD(afd_Q, self.Sigma, {}, q0_afd, set())
             
        return AFD(afd_Q, self.Sigma, afd_delta, q0_afd, afd_F)

    def _set_to_state_name(self, states_set):
        
        if not states_set:
            return "Ø" 
        return "{" + ",".join(sorted(list(states_set))) + "}"

class AutomatonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Interativo de Autômatos (Python/Tkinter)")
        self.root.geometry("1200x800")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Inter", 10))
        self.style.configure("TButton", font=("Inter", 10, "bold"))
        self.style.configure("TCombobox", font=("Inter", 10))
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
       
        ttk.Label(self.control_frame, text="1. Seleção do Autômato", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        
        self.automaton_var = tk.StringVar()
        self.automaton_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.automaton_var,
            values=list(PREDEFINED_AUTOMATA.keys()),
            state="readonly",
            width=40
        )
        self.automaton_combo.pack(fill=tk.X, pady=5)
        self.automaton_combo.set("Selecione um autômato predefinido...")
        
        self.load_button = ttk.Button(
            self.control_frame,
            text="Carregar Autômato",
            command=self.load_automaton
        )
        self.load_button.pack(fill=tk.X, pady=10)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        self.conversion_frame = ttk.Frame(self.control_frame)
        self.conversion_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.conversion_frame, text="Conversão AFN -> AFD", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        self.convert_button = ttk.Button(
            self.conversion_frame,
            text="Converter AFN para AFD",
            command=self.run_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(fill=tk.X, pady=5)
        
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        ttk.Label(self.control_frame, text="2. Teste de Cadeia", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        
        ttk.Label(self.control_frame, text="Cadeia de Entrada:").pack(anchor=tk.W)
        self.string_entry = ttk.Entry(self.control_frame, font=("Inter", 12), width=30)
        self.string_entry.pack(fill=tk.X, pady=5)
        
        self.run_button = ttk.Button(
            self.control_frame,
            text="Executar Validação",
            command=self.run_validation,
            state=tk.DISABLED
        )
        self.run_button.pack(fill=tk.X, pady=10)

        ttk.Label(self.control_frame, text="Status da Validação:", style="Header.TLabel").pack(pady=10, anchor=tk.W)
        self.status_label = ttk.Label(
            self.control_frame, 
            text="Aguardando carregamento...", 
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
      
        ttk.Label(self.canvas_frame, text="Diagrama de Estados", style="Header.TLabel").pack(pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", relief=tk.GROOVE, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)
       
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def _create_info_widgets(self):
       
        ttk.Label(self.info_frame, text="Painel de Informações", style="Header.TLabel").pack(pady=5, anchor=tk.W)
        self.info_text = tk.Text(self.info_frame, height=10, width=40, font=("Courier", 10), wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, expand=False)
        self.info_text.insert(tk.END, "Carregue um autômato para ver os detalhes.")
        self.info_text.config(state=tk.DISABLED)
        
        ttk.Label(self.info_frame, text="Tabela de Transição (δ)", style="Header.TLabel").pack(pady=10, anchor=tk.W)
        self.table_text = tk.Text(self.info_frame, height=15, width=40, font=("Courier", 10), wrap=tk.NONE)
        self.table_text.pack(fill=tk.X, expand=False)
        self.table_text.insert(tk.END, "")
        self.table_text.config(state=tk.DISABLED)

    def load_automaton(self):
       
        key = self.automaton_var.get()
        if key not in PREDEFINED_AUTOMATA:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um autômato predefinido válido.")
            return

        automaton_data = PREDEFINED_AUTOMATA[key]
        
        self.original_automaton_data = automaton_data
        
        self._load_automaton_data(automaton_data, f"Autômato '{key}' carregado.")


    def _load_automaton_data(self, automaton_data, load_message):
       
        try:
           
            self.current_automaton = None 
            
            if automaton_data["tipo"] == "AFD":
                self.current_automaton = AFD(
                    automaton_data["Q"],
                    automaton_data["Sigma"],
                    automaton_data["delta"],
                    automaton_data["q0"],
                    automaton_data["F"]
                )
               
                self.convert_button.config(state=tk.DISABLED)
                
            elif automaton_data["tipo"] == "AFN":
                self.current_automaton = AFN(
                    automaton_data["Q"],
                    automaton_data["Sigma"],
                    automaton_data["delta"],
                    automaton_data["q0"],
                    automaton_data["F"]
                )
               
                self.convert_button.config(state=tk.NORMAL)
                
            else:
                raise ValueError("Tipo de autômato desconhecido.")
                
            self.run_button.config(state=tk.NORMAL)
            self.status_label.config(text=load_message)
            self.result_label.config(text="")
            self.string_entry.delete(0, tk.END)
            
            self._update_info_panel()
            self._draw_automaton()

        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar o autômato: {e}")
            self.current_automaton = None
            self.run_button.config(state=tk.DISABLED)
            self.convert_button.config(state=tk.DISABLED)

    def _update_info_panel(self):
        
        if not self.current_automaton:
            return

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
        
        if not self.current_automaton:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if not self.current_automaton.state_positions:
             self.current_automaton._calculate_positions(width, height)
        
        positions = self.current_automaton.state_positions
        radius = 30 
        
        self._draw_transitions(positions, radius)

        for state in self.current_automaton.Q:
            x, y = positions[state]
            
            if state in self.current_automaton.F:
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="black", width=2, fill="white", tags=(state, "state_circle"))
                self.canvas.create_oval(x - radius + 4, y - radius + 4, x + radius - 4, y + radius - 4, outline="black", width=2, fill="white", tags=(state, "state_circle"))
            else:
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="black", width=2, fill="white", tags=(state, "state_circle"))

            self.canvas.create_text(x, y, text=state, font=("Inter", 12, "bold"), tags=(state, "state_text"))
            
            if state == self.current_automaton.q0:
               
                start_x_arrow = x - radius - 40
                if start_x_arrow < 10:
                    start_x_arrow = 10
                
                self.canvas.create_line(start_x_arrow, y, x - radius - 5, y, arrow=tk.LAST, width=2, tags=(state, "start_arrow"))
                
            self.canvas_elements["states"][state] = self.canvas.find_withtag(state)

    def _draw_transitions(self, positions, radius):
        
        grouped_transitions = {}
        
        for (start_state, symbol), end_states in self.current_automaton.delta.items():
            if not isinstance(end_states, set):
                end_states = {end_states}
                
            for end_state in end_states:
                key = (start_state, end_state)
                if key not in grouped_transitions:
                    grouped_transitions[key] = []
                grouped_transitions[key].append(symbol)
        
        for (start_state, end_state), symbols in grouped_transitions.items():
            label = ", ".join(sorted(symbols))
            x1, y1 = positions[start_state]
            x2, y2 = positions[end_state]

            if start_state == end_state:
               
                self.canvas.create_arc(
                    x1 - radius, y1 - radius - (radius * 1.5), x1 + radius, y1 - (radius * 0.5),
                    start=270, extent=270, style=tk.ARC, width=2, outline="#555555", tags="transition_line"
                )
                self.canvas.create_text(x1, y1 - radius * 1.5, text=label, fill="#333333", tags="transition_text")
            else:
               
                angle = math.atan2(y2 - y1, x2 - x1)
                start_x = x1 + radius * math.cos(angle)
                start_y = y1 + radius * math.sin(angle)
                end_x = x2 - radius * math.cos(angle)
                end_y = y2 - radius * math.sin(angle)
                
                line_id = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    arrow=tk.LAST, width=2, fill="#555555", tags="transition_line"
                )
                
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                offset = 10
                angle_perp = angle + math.pi / 2
                label_x = mid_x + offset * math.cos(angle_perp)
                label_y = mid_y + offset * math.sin(angle_perp)

                self.canvas.create_text(label_x, label_y, text=label, fill="#333333", tags="transition_text")

    def run_conversion(self):
      
        if not self.current_automaton or self.current_automaton.tipo != "AFN":
            messagebox.showwarning("Ação Inválida", "Carregue um AFN primeiro para poder convertê-lo.")
            return
            
        try:
        
            afd_convertido = self.current_automaton.convert_to_afd()
            
            new_automaton_data = {
                "tipo": "AFD",
                "Q": afd_convertido.Q,
                "Sigma": afd_convertido.Sigma,
                "delta": afd_convertido.delta,
                "q0": afd_convertido.q0,
                "F": afd_convertido.F
            }
            
            self._load_automaton_data(new_automaton_data, "Conversão AFN -> AFD concluída. Exibindo AFD resultante.")
            
            self.convert_button.config(state=tk.DISABLED)
            
            messagebox.showinfo("Conversão Concluída", 
                                "O AFN foi convertido para um AFD.\n"
                                "O diagrama e a tabela de transição foram atualizados.\n"
                                "Pode agora testar cadeias no AFD resultante (Parte 1.3.b).")

        except Exception as e:
            messagebox.showerror("Erro na Conversão", f"Ocorreu um erro durante a conversão: {e}")

    def run_validation(self):

        if not self.current_automaton:
            return
            
        input_string = self.string_entry.get()
        
        self._reset_canvas_colors()
        self.animation_step = 0
        self.result_label.config(text="")
        
        is_accepted, path, message = self.current_automaton.validate(input_string)
        
        self.animation_path = path
        self.final_result = (is_accepted, message)
        
        self.status_label.config(text=f"Iniciando validação para: '{input_string}'")
        
        self._animate_step()

    def _animate_step(self):
        
        if self.animation_step >= len(self.animation_path):
            
            self._show_final_result()
            return
            
        
        self._reset_canvas_colors()
        
        current_step_data = self.animation_path[self.animation_step]
        
        symbol = ""
        input_str = self.string_entry.get()
        if self.animation_step > 0 and self.animation_step <= len(input_str):
            symbol = f" (lendo '{input_str[self.animation_step - 1]}')"
            
        if self.current_automaton.tipo == "AFD":
            if current_step_data in self.canvas_elements["states"]:
                self._highlight_state(current_step_data, "yellow")
                self.status_label.config(text=f"Passo {self.animation_step}{symbol}: Estado atual -> {current_step_data}")
        
        elif self.current_automaton.tipo == "AFN":
            if isinstance(current_step_data, set):
                states_str = self.current_automaton._format_set(current_step_data)
                self.status_label.config(text=f"Passo {self.animation_step}{symbol}: Estados ativos -> {states_str}")
                for state in current_step_data:
                    if state in self.canvas_elements["states"]:
                        self._highlight_state(state, "yellow")
            
        self.animation_step += 1
        
        self.root.after(800, self._animate_step) 

    def _show_final_result(self):
      
        is_accepted, message = self.final_result
        self.status_label.config(text=message)
        
        if is_accepted:
            self.result_label.config(text="ACEITO", foreground="green")
            
            final_states_in_path = self.animation_path[-1]
            if not isinstance(final_states_in_path, set):
                final_states_in_path = {final_states_in_path}
            
            for state in final_states_in_path:
                 if state in self.current_automaton.F:
                     self._highlight_state(state, "lightgreen")

        else:
            self.result_label.config(text="REJEITADO", foreground="red")
           
            final_states_in_path = self.animation_path[-1]
            if not isinstance(final_states_in_path, set):
                final_states_in_path = {final_states_in_path}
                
            for state in final_states_in_path:
                 if state in self.canvas_elements["states"]:
                    self._highlight_state(state, "salmon")

    def _reset_canvas_colors(self):
       
        for state_id in self.canvas.find_withtag("state_circle"):
            self.canvas.itemconfig(state_id, fill="white")
            
    def _highlight_state(self, state, color):
        
        state_ovals = self.canvas.find_withtag(state)
        for item_id in state_ovals:
            if "state_circle" in self.canvas.gettags(item_id):
                 self.canvas.itemconfig(item_id, fill=color)

if __name__ == "__main__":
    try:
        main_root = tk.Tk()
        app = AutomatonApp(main_root)
        main_root.mainloop()
    except ImportError:
        print("se aparecer isso, é pq a biblioteca tkinter nao ta instalada, instale ela e tente dnv")
    except Exception as e:
        print(f"ocorreu um erro{e}")