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
