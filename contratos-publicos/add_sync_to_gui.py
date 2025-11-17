#!/usr/bin/env python3
"""
Script para adicionar funcionalidades de sincronização à GUI
Execute este script para atualizar automaticamente a gui.py
"""

import re
from pathlib import Path

def add_sync_import():
    """Adiciona import do módulo sync"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    # Verificar se já tem o import
    if "from sync import SyncManager" in content:
        print("✓ Import de sync já existe")
        return

    # Adicionar após os outros imports internos
    content = content.replace(
        "from alerts import AlertsManager",
        "from alerts import AlertsManager\nfrom sync import SyncManager"
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Import de sync adicionado")


def add_sync_initialization():
    """Adiciona inicialização do SyncManager"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    # Verificar se já tem
    if "self.sync_manager = SyncManager" in content:
        print("✓ Inicialização de sync já existe")
        return

    # Adicionar após self.alerts_manager
    content = content.replace(
        "self.alerts_manager = AlertsManager(self.db)",
        "self.alerts_manager = AlertsManager(self.db)\n        self.sync_manager = SyncManager(self.db, self.scraper)"
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Inicialização de sync adicionada")


def add_sync_tab():
    """Adiciona aba de sincronização"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    # Verificar se já tem
    if "create_sync_tab" in content:
        print("✓ Aba de sincronização já existe")
        return

    # Adicionar chamada de criação da aba
    content = content.replace(
        "self.create_import_tab()",
        "self.create_import_tab()\n        self.create_sync_tab()"
    )

    # Adicionar método create_sync_tab antes de create_status_bar
    sync_tab_code = '''
    def create_sync_tab(self):
        """Cria a aba de sincronização"""
        sync_frame = ttk.Frame(self.notebook)
        self.notebook.add(sync_frame, text="Sincronização")

        # Título
        titulo = ttk.Label(
            sync_frame,
            text="Sincronização Automática de Dados",
            font=('Arial', 14, 'bold')
        )
        titulo.pack(pady=20)

        # Frame de status
        status_frame = ttk.LabelFrame(sync_frame, text="Estado da Sincronização", padding=20)
        status_frame.pack(fill=tk.X, padx=40, pady=10)

        self.sync_status_labels = {}

        info_items = [
            ('auto_sync', 'Sincronização Automática:', 0),
            ('ultima_sync', 'Última Sincronização:', 1),
            ('proxima_sync', 'Próxima Sincronização:', 2),
            ('total_contratos', 'Total de Contratos:', 3),
            ('contratos_24h', 'Novos (24h):', 4),
        ]

        for key, label, row in info_items:
            ttk.Label(status_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=5
            )
            value_label = ttk.Label(status_frame, text="...", font=('Arial', 10))
            value_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.sync_status_labels[key] = value_label

        # Frame de configuração
        config_frame = ttk.LabelFrame(sync_frame, text="Configuração", padding=20)
        config_frame.pack(fill=tk.X, padx=40, pady=10)

        # Auto sync checkbox
        self.auto_sync_var = tk.BooleanVar()
        ttk.Checkbutton(
            config_frame,
            text="Ativar sincronização automática",
            variable=self.auto_sync_var,
            command=self.toggle_auto_sync
        ).pack(anchor=tk.W, pady=5)

        # Intervalo
        interval_frame = ttk.Frame(config_frame)
        interval_frame.pack(anchor=tk.W, pady=10)

        ttk.Label(interval_frame, text="Intervalo:").pack(side=tk.LEFT, padx=5)
        self.sync_interval_var = tk.IntVar(value=24)
        ttk.Spinbox(
            interval_frame,
            from_=1,
            to=168,
            textvariable=self.sync_interval_var,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(interval_frame, text="horas").pack(side=tk.LEFT, padx=5)

        ttk.Button(
            config_frame,
            text="Guardar Configuração",
            command=self.save_sync_config
        ).pack(anchor=tk.W, pady=10)

        # Frame de ações
        action_frame = ttk.LabelFrame(sync_frame, text="Ações", padding=20)
        action_frame.pack(fill=tk.X, padx=40, pady=10)

        ttk.Button(
            action_frame,
            text="Sincronizar Agora",
            command=self.sync_now
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            action_frame,
            text="Otimizar Base de Dados",
            command=self.optimize_database
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            action_frame,
            text="Ver Estimativas de Tamanho",
            command=self.show_size_estimates
        ).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(
            action_frame,
            text="Atualizar Estado",
            command=self.update_sync_status
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Carregar estado inicial
        self.update_sync_status()

    def update_sync_status(self):
        """Atualiza informações de estado da sincronização"""
        try:
            status = self.sync_manager.get_sync_status()

            self.sync_status_labels['auto_sync'].config(
                text="Ativo" if status['auto_sync_ativo'] else "Inativo"
            )

            ultima = status['ultima_sincronizacao']
            self.sync_status_labels['ultima_sync'].config(
                text=ultima[:19] if ultima else "Nunca"
            )

            proxima = status['proxima_sincronizacao']
            self.sync_status_labels['proxima_sync'].config(
                text=proxima[:19] if proxima else "N/A"
            )

            self.sync_status_labels['total_contratos'].config(
                text=f"{status['total_contratos_bd']:,}"
            )

            self.sync_status_labels['contratos_24h'].config(
                text=f"{status['contratos_ultimas_24h']:,}"
            )

            # Atualizar variáveis
            config = self.sync_manager.config
            self.auto_sync_var.set(config.get('auto_sync', False))
            self.sync_interval_var.set(config.get('sync_interval_hours', 24))

        except Exception as e:
            logger.error(f"Erro ao atualizar status de sync: {e}")

    def toggle_auto_sync(self):
        """Ativa/desativa sincronização automática"""
        auto_sync = self.auto_sync_var.get()
        self.sync_manager.configure_sync(
            auto_sync=auto_sync,
            interval_hours=self.sync_interval_var.get()
        )
        self.update_sync_status()
        messagebox.showinfo(
            "Sincronização",
            f"Sincronização automática {'ativada' if auto_sync else 'desativada'}"
        )

    def save_sync_config(self):
        """Guarda configuração de sincronização"""
        try:
            self.sync_manager.configure_sync(
                auto_sync=self.auto_sync_var.get(),
                interval_hours=self.sync_interval_var.get(),
                incremental=True
            )
            messagebox.showinfo("Sucesso", "Configuração guardada!")
            self.update_sync_status()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar configuração: {e}")

    def sync_now(self):
        """Executa sincronização agora"""
        resposta = messagebox.askyesno(
            "Sincronizar",
            "Executar sincronização agora?\\n\\n"
            "Isto pode demorar alguns minutos se houver muitos dados novos."
        )

        if not resposta:
            return

        try:
            self.update_status("A sincronizar...")

            # Executar em thread para não bloquear UI
            import threading

            def sync_thread():
                stats = self.sync_manager.sync_now()

                # Atualizar UI na thread principal
                self.root.after(0, lambda: self._sync_completed(stats))

            thread = threading.Thread(target=sync_thread, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")
            messagebox.showerror("Erro", f"Erro na sincronização: {e}")

    def _sync_completed(self, stats):
        """Callback quando sincronização completa"""
        if stats.get('sucesso'):
            messagebox.showinfo(
                "Sincronização Completa",
                f"Contratos novos: {stats.get('contratos_novos', 0)}\\n"
                f"Alertas gerados: {stats.get('alertas_gerados', 0)}"
            )
            self.update_sync_status()
            self.atualizar_dashboard()
        else:
            erros = "\\n".join(stats.get('erros', []))
            messagebox.showerror("Erro", f"Sincronização falhou:\\n{erros}")

        self.update_status("Pronto")

    def optimize_database(self):
        """Otimiza a base de dados"""
        resposta = messagebox.askyesno(
            "Otimizar",
            "Otimizar base de dados?\\n\\n"
            "Isto irá:\\n"
            "• Compactar dados (VACUUM)\\n"
            "• Atualizar estatísticas\\n"
            "• Reindexar tabelas\\n\\n"
            "Pode demorar alguns minutos com bases de dados grandes."
        )

        if not resposta:
            return

        try:
            self.update_status("A otimizar base de dados...")

            import threading

            def optimize_thread():
                stats = self.sync_manager.optimize_database()
                self.root.after(0, lambda: self._optimize_completed(stats))

            thread = threading.Thread(target=optimize_thread, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"Erro na otimização: {e}")
            messagebox.showerror("Erro", f"Erro na otimização: {e}")

    def _optimize_completed(self, stats):
        """Callback quando otimização completa"""
        reducao = self.sync_manager._format_bytes(stats['reducao_bytes'])
        percentagem = stats['reducao_percentagem']

        messagebox.showinfo(
            "Otimização Completa",
            f"Base de dados otimizada!\\n\\n"
            f"Espaço recuperado: {reducao}\\n"
            f"Redução: {percentagem:.1f}%"
        )

        self.update_status("Pronto")

    def show_size_estimates(self):
        """Mostra estimativas de tamanho"""
        try:
            stats = self.db.obter_estatisticas()
            total_contratos = stats['total_contratos']

            # Estimativas para diferentes cenários
            estimativas = self.sync_manager.estimate_database_size(total_contratos)

            texto = f"""
╔════════════════════════════════════════════════════════════════╗
║     ESTIMATIVAS DE TAMANHO DA BASE DE DADOS                    ║
╚════════════════════════════════════════════════════════════════╝

ATUAL ({total_contratos:,} contratos):
  • Sem otimizar: {estimativas['tamanho_sem_otimizar_formatado']}
  • Otimizado: {estimativas['tamanho_otimizado_formatado']}
  • Bytes por contrato: ~{estimativas['bytes_por_contrato']} bytes

PROJEÇÕES:
  • 10 mil contratos: {estimativas['estimativas_cenarios']['10_mil_contratos']}
  • 100 mil contratos: {estimativas['estimativas_cenarios']['100_mil_contratos']}
  • 500 mil contratos: {estimativas['estimativas_cenarios']['500_mil_contratos']}
  • 1 milhão contratos: {estimativas['estimativas_cenarios']['1_milhao_contratos']}

💡 DICAS:
  • Execute "Otimizar BD" regularmente (reduz ~30%)
  • Exporte e remova contratos muito antigos
  • Mantenha apenas dados relevantes

═══════════════════════════════════════════════════════════════════
            """

            # Mostrar em janela
            window = tk.Toplevel(self.root)
            window.title("Estimativas de Tamanho")
            window.geometry("700x500")

            text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=('Courier', 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, texto)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(window, text="Fechar", command=window.destroy).pack(pady=10)

        except Exception as e:
            logger.error(f"Erro ao calcular estimativas: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

'''

    # Inserir antes de create_status_bar
    content = content.replace(
        "    def create_status_bar(self):",
        sync_tab_code + "\n    def create_status_bar(self):"
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Aba de sincronização adicionada")


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     ADICIONAR FUNCIONALIDADES DE SINCRONIZAÇÃO                 ║
╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        add_sync_import()
        add_sync_initialization()
        add_sync_tab()

        print("\n✓ Todas as modificações aplicadas com sucesso!")
        print("\nA GUI agora inclui:")
        print("  • Aba de Sincronização")
        print("  • Sincronização automática configurável")
        print("  • Otimização de base de dados")
        print("  • Estimativas de tamanho")

    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
