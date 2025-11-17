#!/usr/bin/env python3
"""
Script para adicionar funcionalidades avançadas à GUI
- Detecção de padrões suspeitos
- Associações pessoa-empresa
- Conflitos de interesse
- Menu de configurações
"""

import re
from pathlib import Path


def add_imports():
    """Adiciona imports necessários"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    # Verificar se já tem
    if "from suspicious_patterns import" in content:
        print("✓ Imports já existem")
        return

    # Adicionar após imports internos
    new_imports = """from sync import SyncManager
from suspicious_patterns import SuspiciousPatternDetector, LimitesLegais, analisar_todos_contratos
from associations import AssociationsManager"""

    content = content.replace(
        "from sync import SyncManager",
        new_imports
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Imports adicionados")


def add_initialization():
    """Adiciona inicialização dos novos gestores"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    if "self.suspicious_detector" in content:
        print("✓ Inicialização já existe")
        return

    new_init = """self.sync_manager = SyncManager(self.db, self.scraper)
        self.suspicious_detector = SuspiciousPatternDetector()
        self.associations_manager = AssociationsManager(self.db)"""

    content = content.replace(
        "self.sync_manager = SyncManager(self.db, self.scraper)",
        new_init
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Inicialização adicionada")


def add_menu_items():
    """Adiciona items ao menu"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    if "Análise Avançada" in content:
        print("✓ Menu items já existem")
        return

    # Adicionar menu de análise
    menu_code = '''
        # Menu Análise Avançada
        analise_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Análise Avançada", menu=analise_menu)
        analise_menu.add_command(label="Analisar Padrões Suspeitos", command=self.analisar_padroes_suspeitos)
        analise_menu.add_command(label="Detectar Conflitos de Interesse", command=self.detectar_conflitos_interesse)
        analise_menu.add_command(label="Configurar Detecção", command=self.configurar_deteccao)
        analise_menu.add_separator()
        analise_menu.add_command(label="Relatório Completo", command=self.gerar_relatorio_completo)
'''

    # Inserir antes do menu Ajuda
    content = content.replace(
        "# Menu Ajuda",
        menu_code + "\n        # Menu Ajuda"
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Menu items adicionados")


def add_tabs():
    """Adiciona novas abas"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    if "create_suspicious_tab" in content:
        print("✓ Abas já existem")
        return

    # Adicionar chamadas para criar abas
    new_tabs = """self.create_sync_tab()
        self.create_suspicious_tab()
        self.create_associations_tab()"""

    content = content.replace(
        "self.create_sync_tab()",
        new_tabs
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Chamadas de abas adicionadas")


def add_tab_methods():
    """Adiciona métodos para criar as novas abas"""
    gui_path = Path("src/gui.py")
    content = gui_path.read_text(encoding='utf-8')

    if "def create_suspicious_tab" in content:
        print("✓ Métodos de abas já existem")
        return

    tabs_code = '''
    def create_suspicious_tab(self):
        """Cria aba de análise de padrões suspeitos"""
        susp_frame = ttk.Frame(self.notebook)
        self.notebook.add(susp_frame, text="Padrões Suspeitos 🔍")

        # Título
        titulo = ttk.Label(
            susp_frame,
            text="Análise de Padrões Suspeitos",
            font=('Arial', 14, 'bold')
        )
        titulo.pack(pady=10)

        # Botões de análise
        btn_frame = ttk.Frame(susp_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(
            btn_frame,
            text="Analisar Todos os Contratos",
            command=self.analisar_todos_contratos_suspeitos
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Configurar Detecção",
            command=self.configurar_deteccao
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Exportar Relatório",
            command=self.exportar_relatorio_suspeitos
        ).pack(side=tk.LEFT, padx=5)

        # Frame de resultados
        resultados_frame = ttk.LabelFrame(susp_frame, text="Padrões Detectados", padding=10)
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview
        columns = ('Tipo', 'Gravidade', 'Descrição', 'Valor')
        self.suspicious_tree = ttk.Treeview(
            resultados_frame,
            columns=columns,
            show='headings',
            height=15
        )

        for col in columns:
            self.suspicious_tree.heading(col, text=col)

        self.suspicious_tree.column('Tipo', width=150)
        self.suspicious_tree.column('Gravidade', width=100)
        self.suspicious_tree.column('Descrição', width=400)
        self.suspicious_tree.column('Valor', width=120)

        self.suspicious_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL,
                                 command=self.suspicious_tree.yview)
        self.suspicious_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cores por gravidade
        self.suspicious_tree.tag_configure('critica', background='#ffcccc')
        self.suspicious_tree.tag_configure('alta', background='#ffe6cc')
        self.suspicious_tree.tag_configure('media', background='#fff9cc')
        self.suspicious_tree.tag_configure('baixa', background='#ffffff')

    def create_associations_tab(self):
        """Cria aba de associações pessoa-empresa"""
        assoc_frame = ttk.Frame(self.notebook)
        self.notebook.add(assoc_frame, text="Associações 👥")

        # Título
        titulo = ttk.Label(
            assoc_frame,
            text="Associações Pessoa-Empresa",
            font=('Arial', 14, 'bold')
        )
        titulo.pack(pady=10)

        # Frame de pesquisa
        search_frame = ttk.LabelFrame(assoc_frame, text="Pesquisar", padding=10)
        search_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(search_frame, text="Nome (pessoa ou empresa):").pack(side=tk.LEFT, padx=5)
        self.assoc_search_entry = ttk.Entry(search_frame, width=40)
        self.assoc_search_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="Pesquisar Contratos",
            command=self.pesquisar_por_associacao
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            search_frame,
            text="Adicionar Associação",
            command=self.adicionar_associacao_dialog
        ).pack(side=tk.LEFT, padx=5)

        # Frame de resultados
        results_frame = ttk.LabelFrame(assoc_frame, text="Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Texto de resultados
        self.assoc_results_text = scrolledtext.ScrolledText(
            results_frame,
            height=20,
            wrap=tk.WORD
        )
        self.assoc_results_text.pack(fill=tk.BOTH, expand=True)

    # ==================== MÉTODOS DE ANÁLISE ====================

    def analisar_todos_contratos_suspeitos(self):
        """Analisa todos os contratos para padrões suspeitos"""
        self.update_status("A analisar padrões suspeitos...")

        try:
            # Obter todos os contratos
            contratos = self.db.pesquisar_contratos({})

            if not contratos:
                messagebox.showinfo("Info", "Nenhum contrato na base de dados")
                return

            # Analisar
            padroes = self.suspicious_detector.analisar_contratos(contratos)

            # Limpar resultados anteriores
            self.suspicious_tree.delete(*self.suspicious_tree.get_children())

            # Inserir novos resultados
            for padrao in padroes:
                gravidade = padrao.get('gravidade', 'baixa')
                valor = padrao.get('valor', '')
                valor_str = f"€{valor:,.2f}" if valor else ""

                self.suspicious_tree.insert('', 'end', values=(
                    padrao['tipo'],
                    gravidade.upper(),
                    padrao['descricao'],
                    valor_str
                ), tags=(gravidade,))

            messagebox.showinfo(
                "Análise Completa",
                f"Detectados {len(padroes)} padrões suspeitos\\n\\n"
                f"🔴 Alta: {sum(1 for p in padroes if p.get('gravidade') == 'alta')}\\n"
                f"🟡 Média: {sum(1 for p in padroes if p.get('gravidade') == 'media')}\\n"
                f"⚪ Baixa: {sum(1 for p in padroes if p.get('gravidade') == 'baixa')}"
            )

            self.update_status("Análise concluída")

        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

    def configurar_deteccao(self):
        """Abre diálogo de configuração de detecção"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Detecção de Padrões Suspeitos")
        config_window.geometry("600x500")

        # Título
        ttk.Label(
            config_window,
            text="Configurações de Detecção",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)

        # Frame de configurações
        config_frame = ttk.LabelFrame(config_window, text="Parâmetros", padding=20)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        config = self.suspicious_detector.config

        # Variáveis
        vars_dict = {}

        # Valores suspeitos
        vars_dict['detectar_valores_suspeitos'] = tk.BooleanVar(
            value=config['detectar_valores_suspeitos']
        )
        ttk.Checkbutton(
            config_frame,
            text="Detectar valores suspeitos (próximos dos limites legais)",
            variable=vars_dict['detectar_valores_suspeitos']
        ).pack(anchor=tk.W, pady=5)

        # Fracionamento
        vars_dict['detectar_fracionamento'] = tk.BooleanVar(
            value=config['detectar_fracionamento']
        )
        ttk.Checkbutton(
            config_frame,
            text="Detectar fracionamento ilegal de contratos",
            variable=vars_dict['detectar_fracionamento']
        ).pack(anchor=tk.W, pady=5)

        # Contratos repetidos
        vars_dict['detectar_contratos_repetidos'] = tk.BooleanVar(
            value=config['detectar_contratos_repetidos']
        )
        ttk.Checkbutton(
            config_frame,
            text="Detectar contratos excessivamente repetidos",
            variable=vars_dict['detectar_contratos_repetidos']
        ).pack(anchor=tk.W, pady=5)

        # Procedimentos inadequados
        vars_dict['detectar_procedimento_inadequado'] = tk.BooleanVar(
            value=config['detectar_procedimento_inadequado']
        )
        ttk.Checkbutton(
            config_frame,
            text="Detectar procedimentos inadequados para o valor",
            variable=vars_dict['detectar_procedimento_inadequado']
        ).pack(anchor=tk.W, pady=5)

        # Valores redondos suspeitos
        vars_dict['detectar_valores_redondos'] = tk.BooleanVar(
            value=config['detectar_valores_redondos']
        )
        ttk.Checkbutton(
            config_frame,
            text="Detectar valores 'calculados' (ex: €74.999)",
            variable=vars_dict['detectar_valores_redondos']
        ).pack(anchor=tk.W, pady=5)

        # Limites legais
        ttk.Label(
            config_frame,
            text="\\n📋 Limites Legais em Portugal:",
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W, pady=10)

        limits_text = f"""
• Ajuste Direto (Bens/Serviços): até €{LimitesLegais.AJUSTE_DIRETO_BENS_SERVICOS:,.0f}
• Ajuste Direto (Obras): até €{LimitesLegais.AJUSTE_DIRETO_OBRAS:,.0f}
• Consulta Prévia (Bens/Serviços): €{LimitesLegais.AJUSTE_DIRETO_BENS_SERVICOS:,.0f} - €{LimitesLegais.CONSULTA_PREVIA_BENS_SERVICOS:,.0f}
• Concurso Público: acima de €{LimitesLegais.CONCURSO_PUBLICO_BENS_SERVICOS:,.0f}
        """

        ttk.Label(config_frame, text=limits_text).pack(anchor=tk.W, padx=20)

        # Botões
        btn_frame = ttk.Frame(config_window)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        def guardar_config():
            for key, var in vars_dict.items():
                self.suspicious_detector.config[key] = var.get()
            messagebox.showinfo("Sucesso", "Configuração guardada!")
            config_window.destroy()

        ttk.Button(btn_frame, text="Guardar", command=guardar_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=config_window.destroy).pack(side=tk.LEFT, padx=5)

    def exportar_relatorio_suspeitos(self):
        """Exporta relatório de padrões suspeitos"""
        if not self.suspicious_tree.get_children():
            messagebox.showwarning("Aviso", "Nenhum padrão detectado para exportar")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            # Gerar relatório
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE PADRÕES SUSPEITOS\\n")
                f.write("=" * 70 + "\\n\\n")

                for item in self.suspicious_tree.get_children():
                    valores = self.suspicious_tree.item(item)['values']
                    f.write(f"Tipo: {valores[0]}\\n")
                    f.write(f"Gravidade: {valores[1]}\\n")
                    f.write(f"Descrição: {valores[2]}\\n")
                    if valores[3]:
                        f.write(f"Valor: {valores[3]}\\n")
                    f.write("\\n" + "-" * 70 + "\\n\\n")

            messagebox.showinfo("Sucesso", f"Relatório exportado: {filepath}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def pesquisar_por_associacao(self):
        """Pesquisa contratos por pessoa/empresa usando associações"""
        nome = self.assoc_search_entry.get().strip()

        if not nome:
            messagebox.showwarning("Aviso", "Digite um nome para pesquisar")
            return

        try:
            # Pesquisar por pessoa
            resultado = self.associations_manager.pesquisar_contratos_por_pessoa(nome)

            # Limpar resultados anteriores
            self.assoc_results_text.delete(1.0, tk.END)

            # Mostrar resultados
            texto = f"""
╔════════════════════════════════════════════════════════════════╗
║     PESQUISA POR ASSOCIAÇÕES: {nome.upper():<40}║
╚════════════════════════════════════════════════════════════════╝

Total de Contratos Encontrados: {resultado['total_contratos']}
Valor Total: €{resultado['valor_total']:,.2f}

EMPRESAS ASSOCIADAS ({len(resultado['empresas_associadas'])}):
"""
            for empresa in resultado['empresas_associadas']:
                texto += f"  • {empresa}\\n"

            texto += f"\\nCONTRATOS DIRETOS ({len(resultado['contratos_diretos'])}):  \\n"
            for c in resultado['contratos_diretos'][:10]:
                texto += f"  • {c.get('adjudicante', 'N/D')} → {c.get('adjudicataria', 'N/D')} (€{c.get('valor', 0):,.2f})\\n"

            texto += f"\\nCONTRATOS DE EMPRESAS ASSOCIADAS ({len(resultado['contratos_empresas'])}):\\n"
            for c in resultado['contratos_empresas'][:10]:
                texto += f"  • {c.get('_empresa_associada', 'N/D')} ({c.get('_tipo_associacao', '')}): €{c.get('valor', 0):,.2f}\\n"

            self.assoc_results_text.insert(tk.END, texto)

        except Exception as e:
            logger.error(f"Erro na pesquisa: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

    def adicionar_associacao_dialog(self):
        """Diálogo para adicionar associação pessoa-empresa"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Associação")
        dialog.geometry("500x400")

        ttk.Label(dialog, text="Nome da Pessoa:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        nome_entry = ttk.Entry(dialog, width=40)
        nome_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Cargo Político:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        cargo_entry = ttk.Entry(dialog, width=40)
        cargo_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Empresa:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        empresa_entry = ttk.Entry(dialog, width=40)
        empresa_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Tipo Relação:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        tipo_combo = ttk.Combobox(dialog, width=37)
        tipo_combo['values'] = ['dono', 'socio', 'gerente', 'administrador', 'familiar', 'outro']
        tipo_combo.set('socio')
        tipo_combo.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Fonte:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        fonte_entry = ttk.Entry(dialog, width=40)
        fonte_entry.grid(row=4, column=1, padx=5, pady=5)

        def guardar():
            try:
                # Adicionar pessoa
                pessoa_id = self.associations_manager.adicionar_pessoa(
                    nome=nome_entry.get(),
                    cargo_politico=cargo_entry.get()
                )

                # Adicionar associação
                self.associations_manager.associar_pessoa_empresa(
                    pessoa_id=pessoa_id,
                    empresa_nome=empresa_entry.get(),
                    tipo_relacao=tipo_combo.get(),
                    fonte=fonte_entry.get()
                )

                messagebox.showinfo("Sucesso", "Associação adicionada!")
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

        ttk.Button(dialog, text="Guardar", command=guardar).grid(row=5, column=0, columnspan=2, pady=20)

    def detectar_conflitos_interesse(self):
        """Detecta conflitos de interesse"""
        self.update_status("A detectar conflitos de interesse...")

        try:
            conflitos = self.associations_manager.detectar_conflitos_interesse()

            if not conflitos:
                messagebox.showinfo("Info", "Nenhum conflito de interesse detectado")
                return

            # Mostrar em janela
            window = tk.Toplevel(self.root)
            window.title(f"Conflitos de Interesse Detectados ({len(conflitos)})")
            window.geometry("800x600")

            text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            texto = f"""
╔════════════════════════════════════════════════════════════════╗
║     CONFLITOS DE INTERESSE DETECTADOS                          ║
╚════════════════════════════════════════════════════════════════╝

Total: {len(conflitos)}

"""
            for i, c in enumerate(conflitos, 1):
                gravidade_emoji = {
                    'critica': '🔴',
                    'alta': '🟠',
                    'media': '🟡',
                    'baixa': '⚪'
                }.get(c['gravidade'], '⚪')

                texto += f"{i}. {gravidade_emoji} {c['gravidade'].upper()}\\n"
                texto += f"   Pessoa: {c['pessoa_nome']} ({c['cargo']})\\n"
                texto += f"   Empresa: {c['empresa']}\\n"
                texto += f"   Contrato: {c['adjudicante']} (€{c['valor']:,.2f})\\n"
                texto += f"   {c['descricao']}\\n\\n"

            text_widget.insert(tk.END, texto)
            text_widget.config(state=tk.DISABLED)

            self.update_status("Conflitos detectados")

        except Exception as e:
            logger.error(f"Erro: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

    def gerar_relatorio_completo(self):
        """Gera relatório completo de análise"""
        messagebox.showinfo(
            "Relatório Completo",
            "Funcionalidade em desenvolvimento!\\n\\n"
            "Irá incluir:\\n"
            "• Padrões suspeitos\\n"
            "• Conflitos de interesse\\n"
            "• Estatísticas avançadas\\n"
            "• Exportação em PDF"
        )
'''

    # Inserir antes de create_status_bar
    content = content.replace(
        "    def create_status_bar(self):",
        tabs_code + "\n    def create_status_bar(self):"
    )

    gui_path.write_text(content, encoding='utf-8')
    print("✓ Métodos de abas adicionados")


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║     ADICIONAR FUNCIONALIDADES AVANÇADAS                        ║
╚════════════════════════════════════════════════════════════════╝
    """)

    try:
        add_imports()
        add_initialization()
        add_menu_items()
        add_tabs()
        add_tab_methods()

        print("\n✅ TODAS AS FUNCIONALIDADES ADICIONADAS!")

        print("""
╔════════════════════════════════════════════════════════════════╗
║     NOVAS FUNCIONALIDADES                                      ║
╚════════════════════════════════════════════════════════════════╝

1. 🔍 ABA "PADRÕES SUSPEITOS":
   • Detecta valores suspeitos (ex: €74.999)
   • Detecta fracionamento ilegal
   • Detecta procedimentos inadequados
   • Detecta contratos repetidos excessivamente
   • Configurável por tipo de padrão

2. 👥 ABA "ASSOCIAÇÕES":
   • Associar pessoas a empresas
   • Pesquisar "Luís Montenegro" → ver contratos da Spinumviva
   • Detetar conflitos de interesse
   • Políticos com empresas em contratos públicos

3. 📊 MENU "ANÁLISE AVANÇADA":
   • Analisar Padrões Suspeitos
   • Detectar Conflitos de Interesse
   • Configurar Detecção
   • Relatório Completo

VALORES SUSPEITOS DETECTADOS:
• €74.900 - €75.000 (limite ajuste direto bens/serviços)
• €149.900 - €150.000 (limite ajuste direto obras)
• €213.900 - €214.000 (limite consulta prévia)
• Valores "calculados" (€74.999, €74.990, etc)

EXEMPLO DE USO:
1. Adicionar pessoa "Luís Montenegro" com cargo "Primeiro-Ministro"
2. Associar a empresa "Spinumviva" como "socio" ou "dono"
3. Pesquisar "Luís Montenegro"
4. Ver TODOS os contratos (diretos + empresas associadas)
5. Detetar conflitos de interesse automáticos
        """)

    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
