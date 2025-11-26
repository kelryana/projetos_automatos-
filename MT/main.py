from interface import InterfaceGrafica

if __name__ == "__main__":
    app = InterfaceGrafica()
    app.mainloop()

'''
        # Alfabetos
        alpha_frame = ttk.LabelFrame(scrollable_frame, text="Alfabetos")
        alpha_frame.pack(fill=tk.X, padx=4, pady=4)
        ttk.Label(alpha_frame, text="Σ (alfabeto de entrada)").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.ent_sigma = ttk.Entry(alpha_frame, width=24)
        self.ent_sigma.grid(row=0, column=0, padx=4, pady=4)
        ttk.Label(alpha_frame, text="Σ (alfabeto da fita)").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.ent_gamma = ttk.Entry(alpha_frame, width=24)
        self.ent_gamma.insert(0, "0,1,λ")
        self.ent_gamma.grid(row=1, column=0, padx=4, pady=4)
        ttk.Label(alpha_frame, text="Simbolo branco").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.ent_blank = ttk.Entry(alpha_frame, width=10)
        self.ent_blank.insert(0, "λ")
        self.ent_blank.grid(row=2, column=0, padx=4, pady=4)
        ttk.Button(alpha_frame, text="Aplicar", command=self._apply_alphabets).grid(row=3, column=0, padx=4, pady=4)

                # Criar transição corretamente
        t = Transicao(from_state, symbol, to_state, write, move)

        # Atualizar grafo e log
        self._refresh_graph()
        self._log(f"Transição adicionada: ({t.from_state}, {t.read}) → "
                f"({t.to_state}, {t.write}, {t.move})")
        '''