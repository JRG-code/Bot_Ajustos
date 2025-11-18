"""
Interface Gráfica da Aplicação de Monitorização de Contratos Públicos
Usa tkinter para criar uma GUI desktop completa
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import threading

# Módulos internos
from database import DatabaseManager
from scraper import ContratosPublicosScraper
from entities import EntitiesManager
from alerts import AlertsManager
from sync import SyncManager
from suspicious_patterns import SuspiciousPatternDetector, LimitesLegais, analisar_todos_contratos
from associations import AssociationsManager
from autocomplete import AutocompleteEntry, SuggestionsManager
from updater import check_for_updates, get_current_version, get_update_info_json

logger = logging.getLogger(__name__)


class ContratosPublicosGUI:
    """Classe principal da interface gráfica"""

    def __init__(self, root: tk.Tk):
        """
        Inicializa a interface gráfica

        Args:
            root: Janela principal do tkinter
        """
        self.root = root
        self.root.title("Monitor de Contratos Públicos - BASE.gov.pt")
        self.root.geometry("1200x800")

        # Inicializar componentes
        self.db = DatabaseManager("data/contratos.db")
        self.scraper = ContratosPublicosScraper()
        self.entities_manager = EntitiesManager(self.db)
        self.alerts_manager = AlertsManager(self.db)
        self.sync_manager = SyncManager(self.db, self.scraper)
        self.suspicious_detector = SuspiciousPatternDetector()
        self.associations_manager = AssociationsManager(self.db)
        self.suggestions_manager = SuggestionsManager(self.db)

        # Configurar estilo
        self.setup_styles()

        # Criar interface
        self.create_widgets()

        # Configurar evento de fecho
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Atualizar dados iniciais (após criar todos os widgets)
        self.atualizar_dashboard()

    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')

        # Cores
        self.cores = {
            'primaria': '#2c3e50',
            'secundaria': '#3498db',
            'sucesso': '#27ae60',
            'alerta': '#e74c3c',
            'aviso': '#f39c12',
            'fundo': '#ecf0f1',
            'texto': '#2c3e50'
        }

    def create_widgets(self):
        """Cria todos os widgets da interface"""

        # Barra de menu
        self.create_menu_bar()

        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame de filtro rápido (topo)
        self.create_quick_filter_bar(main_frame)

        # Criar notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Criar abas
        self.create_dashboard_tab()
        self.create_search_tab()
        self.create_figures_tab()
        self.create_alerts_tab()
        self.create_import_tab()
        self.create_sync_tab()
        self.create_suspicious_tab()
        self.create_associations_tab()
        self.create_connections_tab()

        # Barra de status
        self.create_status_bar()

    def create_quick_filter_bar(self, parent):
        """Cria barra de filtro rápido no topo"""
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # Label à esquerda
        ttk.Label(
            filter_frame,
            text="Filtro Rápido:",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Combobox com autocomplete no centro-direita
        ttk.Label(filter_frame, text="Figura de Interesse:").pack(side=tk.LEFT, padx=(0, 5))

        self.quick_filter_var = tk.StringVar()
        self.quick_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.quick_filter_var,
            width=40,
            state='normal'
        )
        self.quick_filter_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Bind para autocomplete
        self.quick_filter_combo.bind('<KeyRelease>', self.on_quick_filter_keyrelease)
        self.quick_filter_combo.bind('<<ComboboxSelected>>', self.on_quick_filter_select)

        # Botão de pesquisa
        ttk.Button(
            filter_frame,
            text="Ver Contratos",
            command=self.aplicar_filtro_rapido,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Botão de limpar
        ttk.Button(
            filter_frame,
            text="Limpar",
            command=self.limpar_filtro_rapido,
            width=10
        ).pack(side=tk.LEFT)

        # Carregar figuras iniciais
        self.atualizar_quick_filter_figuras()

    def atualizar_quick_filter_figuras(self):
        """Atualiza a lista de figuras no filtro rápido"""
        try:
            figuras = self.db.listar_figuras_interesse(apenas_ativas=True)
            # Criar lista de nomes formatados
            self.figuras_dict = {}
            figuras_nomes = []

            for figura in figuras:
                nome = figura.get('nome', '')
                tipo = figura.get('tipo', '')
                nif = figura.get('nif', '')

                # Formato: "Nome (Tipo) [NIF]" ou "Nome (Tipo)" se não tiver NIF
                if nif:
                    nome_formatado = f"{nome} ({tipo}) [{nif}]"
                else:
                    nome_formatado = f"{nome} ({tipo})"

                figuras_nomes.append(nome_formatado)
                self.figuras_dict[nome_formatado] = figura

            self.quick_filter_combo['values'] = figuras_nomes

        except Exception as e:
            logger.error(f"Erro ao atualizar figuras do filtro rápido: {e}")

    def on_quick_filter_keyrelease(self, event):
        """Implementa autocomplete no filtro rápido"""
        if event.keysym in ('BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right'):
            return

        value = self.quick_filter_var.get().lower()

        if value == '':
            self.quick_filter_combo['values'] = [k for k in self.figuras_dict.keys()]
        else:
            # Filtrar figuras que contêm o texto digitado
            filtered = [k for k in self.figuras_dict.keys() if value in k.lower()]
            self.quick_filter_combo['values'] = filtered

    def on_quick_filter_select(self, event):
        """Quando uma figura é selecionada no filtro rápido"""
        # Pode aplicar automaticamente ou esperar o clique no botão
        pass

    def aplicar_filtro_rapido(self):
        """Aplica o filtro rápido e mostra contratos da figura selecionada"""
        selecionado = self.quick_filter_var.get()

        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma figura de interesse primeiro")
            return

        if selecionado not in self.figuras_dict:
            messagebox.showwarning("Aviso", "Figura não encontrada. Use uma das opções da lista.")
            return

        figura = self.figuras_dict[selecionado]
        figura_id = figura.get('id')

        # Mudar para a aba de pesquisa
        self.notebook.select(1)  # Índice da aba "Pesquisar Contratos"

        # Preencher filtro com a figura
        self.filtro_adjudicante.delete(0, tk.END)
        self.filtro_adjudicataria.delete(0, tk.END)

        nome_figura = figura.get('nome', '')
        # Preencher nos dois campos para pegar contratos onde a figura aparece
        self.filtro_adjudicante.insert(0, nome_figura)

        # Executar pesquisa
        self.pesquisar_contratos()

        self.update_status(f"Mostrando contratos de: {nome_figura}")

    def limpar_filtro_rapido(self):
        """Limpa o filtro rápido"""
        self.quick_filter_var.set('')
        self.atualizar_quick_filter_figuras()

    def create_menu_bar(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Ficheiro
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ficheiro", menu=file_menu)
        file_menu.add_command(label="Exportar Resultados...", command=self.exportar_resultados)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing)

        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Atualizar Dados", command=self.atualizar_dados)
        tools_menu.add_command(label="Limpar Cache", command=self.limpar_cache)

        
        # Menu Análise Avançada
        analise_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Análise Avançada", menu=analise_menu)
        analise_menu.add_command(label="Analisar Padrões Suspeitos", command=self.analisar_todos_contratos_suspeitos)
        analise_menu.add_command(label="Detectar Conflitos de Interesse", command=self.detectar_conflitos_interesse)
        analise_menu.add_command(label="Configurar Detecção", command=self.configurar_deteccao)
        analise_menu.add_separator()
        analise_menu.add_command(label="Relatório Completo", command=self.gerar_relatorio_completo)

        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Verificar Atualizações", command=self.verificar_atualizacoes)
        help_menu.add_separator()
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)

    def create_dashboard_tab(self):
        """Cria a aba de dashboard"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Dashboard")

        # Título
        titulo = ttk.Label(
            dashboard_frame,
            text="Dashboard - Visão Geral",
            font=('Arial', 16, 'bold')
        )
        titulo.pack(pady=10)

        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Estatísticas Gerais", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        # Grid de estatísticas
        self.stats_labels = {}

        stats_info = [
            ('total_contratos', 'Total de Contratos:', 0),
            ('total_figuras', 'Figuras de Interesse:', 1),
            ('alertas_nao_lidos', 'Alertas Não Lidos:', 2),
            ('valor_total', 'Valor Total:', 3)
        ]

        for key, label, row in stats_info:
            ttk.Label(stats_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=5
            )
            value_label = ttk.Label(stats_frame, text="0", font=('Arial', 10))
            value_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
            self.stats_labels[key] = value_label

        # Frame de alertas recentes
        alertas_frame = ttk.LabelFrame(dashboard_frame, text="Alertas Recentes", padding=10)
        alertas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview de alertas
        columns = ('Figura', 'Tipo', 'Data', 'Status')
        self.dashboard_alertas_tree = ttk.Treeview(
            alertas_frame,
            columns=columns,
            show='headings',
            height=10
        )

        for col in columns:
            self.dashboard_alertas_tree.heading(col, text=col)
            self.dashboard_alertas_tree.column(col, width=150)

        self.dashboard_alertas_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(alertas_frame, orient=tk.VERTICAL,
                                 command=self.dashboard_alertas_tree.yview)
        self.dashboard_alertas_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botão de atualizar
        ttk.Button(
            dashboard_frame,
            text="Atualizar Dashboard",
            command=self.atualizar_dashboard
        ).pack(pady=10)

    def create_search_tab(self):
        """Cria a aba de pesquisa de contratos"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Pesquisar Contratos")

        # Frame de filtros
        filtros_frame = ttk.LabelFrame(search_frame, text="Filtros de Pesquisa", padding=10)
        filtros_frame.pack(fill=tk.X, padx=20, pady=10)

        # Distrito
        ttk.Label(filtros_frame, text="Distrito:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_distrito = ttk.Combobox(filtros_frame, width=20)
        self.filtro_distrito['values'] = ['', 'Lisboa', 'Porto', 'Aveiro', 'Braga', 'Coimbra',
                                          'Faro', 'Setúbal', 'Viseu', 'Santarém', 'Évora']
        self.filtro_distrito.grid(row=0, column=1, padx=5, pady=5)

        # Concelho
        ttk.Label(filtros_frame, text="Concelho:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.filtro_concelho = ttk.Entry(filtros_frame, width=20)
        self.filtro_concelho.grid(row=0, column=3, padx=5, pady=5)

        # Ano início
        ttk.Label(filtros_frame, text="Ano (de):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_ano_inicio = ttk.Spinbox(filtros_frame, from_=2012, to=2025, width=18)
        self.filtro_ano_inicio.set(2020)
        self.filtro_ano_inicio.grid(row=1, column=1, padx=5, pady=5)

        # Ano fim
        ttk.Label(filtros_frame, text="Ano (até):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.filtro_ano_fim = ttk.Spinbox(filtros_frame, from_=2012, to=2025, width=18)
        self.filtro_ano_fim.set(2025)
        self.filtro_ano_fim.grid(row=1, column=3, padx=5, pady=5)

        # Adjudicante
        ttk.Label(filtros_frame, text="Adjudicante:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_adjudicante = ttk.Entry(filtros_frame, width=20)
        self.filtro_adjudicante.grid(row=2, column=1, padx=5, pady=5)

        # Adjudicatária
        ttk.Label(filtros_frame, text="Adjudicatária:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.filtro_adjudicataria = ttk.Entry(filtros_frame, width=20)
        self.filtro_adjudicataria.grid(row=2, column=3, padx=5, pady=5)

        # Valor mínimo
        ttk.Label(filtros_frame, text="Valor Mín. (€):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_valor_min = ttk.Entry(filtros_frame, width=20)
        self.filtro_valor_min.grid(row=3, column=1, padx=5, pady=5)

        # Valor máximo
        ttk.Label(filtros_frame, text="Valor Máx. (€):").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        self.filtro_valor_max = ttk.Entry(filtros_frame, width=20)
        self.filtro_valor_max.grid(row=3, column=3, padx=5, pady=5)

        # Tipo de Procedimento
        ttk.Label(filtros_frame, text="Tipo de Procedimento:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.filtro_tipo_procedimento = ttk.Combobox(filtros_frame, width=20)
        self.filtro_tipo_procedimento['values'] = ['', 'Ajuste direto', 'Concurso público', 'Concurso limitado por prévia qualificação',
                                                     'Consulta prévia', 'Procedimento de negociação', 'Diálogo concorrencial']
        self.filtro_tipo_procedimento.grid(row=4, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)

        # Botões
        buttons_frame = ttk.Frame(filtros_frame)
        buttons_frame.grid(row=5, column=0, columnspan=4, pady=10)

        ttk.Button(buttons_frame, text="Pesquisar", command=self.pesquisar_contratos).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpar Filtros", command=self.limpar_filtros).pack(side=tk.LEFT, padx=5)

        # Frame de resultados
        resultados_frame = ttk.LabelFrame(search_frame, text="Resultados", padding=10)
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview de resultados
        columns = ('ID', 'Adjudicante', 'Adjudicatária', 'Valor', 'Data', 'Tipo de Procedimento')
        self.resultados_tree = ttk.Treeview(
            resultados_frame,
            columns=columns,
            show='headings',
            height=15
        )

        for col in columns:
            self.resultados_tree.heading(col, text=col)

        self.resultados_tree.column('ID', width=100)
        self.resultados_tree.column('Adjudicante', width=200)
        self.resultados_tree.column('Adjudicatária', width=200)
        self.resultados_tree.column('Valor', width=100)
        self.resultados_tree.column('Data', width=100)
        self.resultados_tree.column('Tipo de Procedimento', width=180)

        self.resultados_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(resultados_frame, orient=tk.VERTICAL,
                                 command=self.resultados_tree.yview)
        self.resultados_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind duplo clique para ver detalhes
        self.resultados_tree.bind('<Double-1>', self.mostrar_detalhes_contrato)

    def create_figures_tab(self):
        """Cria a aba de figuras de interesse"""
        figures_frame = ttk.Frame(self.notebook)
        self.notebook.add(figures_frame, text="Figuras de Interesse")

        # Frame de adicionar figura
        add_frame = ttk.LabelFrame(figures_frame, text="Adicionar Figura de Interesse", padding=10)
        add_frame.pack(fill=tk.X, padx=20, pady=10)

        # Linha 0: Nome e NIF
        ttk.Label(add_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.figura_nome = ttk.Entry(add_frame, width=30)
        self.figura_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="NIF (opcional):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.figura_nif = ttk.Entry(add_frame, width=20)
        self.figura_nif.grid(row=0, column=3, padx=5, pady=5)

        # Linha 1: Tipo
        ttk.Label(add_frame, text="Tipo:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.figura_tipo = ttk.Combobox(add_frame, width=27, state='readonly')
        self.figura_tipo['values'] = ['pessoa', 'empresa', 'entidade_publica']
        self.figura_tipo.set('pessoa')
        self.figura_tipo.grid(row=1, column=1, padx=5, pady=5)
        self.figura_tipo.bind('<<ComboboxSelected>>', self._on_tipo_figura_changed)

        # Linha 2: Cargo Governamental (só para pessoas)
        self.label_cargo = ttk.Label(add_frame, text="Cargo Governamental:")
        self.label_cargo.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.figura_cargo = AutocompleteEntry(
            add_frame,
            suggestions_callback=self.suggestions_manager.get_cargos,
            width=27
        )
        self.figura_cargo.grid(row=2, column=1, padx=5, pady=5)

        # Linha 2: Partido (só para pessoas com cargo)
        self.label_partido = ttk.Label(add_frame, text="Partido:")
        self.label_partido.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.figura_partido = AutocompleteEntry(
            add_frame,
            suggestions_callback=self.suggestions_manager.get_partidos,
            width=18
        )
        self.figura_partido.grid(row=2, column=3, padx=5, pady=5)

        # Linha 3: Notas
        ttk.Label(add_frame, text="Notas:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.figura_notas = ttk.Entry(add_frame, width=30)
        self.figura_notas.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        # Linha 4: Botão adicionar
        ttk.Button(add_frame, text="Adicionar Figura", command=self.adicionar_figura).grid(
            row=4, column=0, columnspan=4, pady=10
        )

        # Configurar grid para expandir
        add_frame.columnconfigure(1, weight=1)
        add_frame.columnconfigure(3, weight=1)

        # Frame de lista de figuras
        lista_frame = ttk.LabelFrame(figures_frame, text="Figuras Cadastradas", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview de figuras
        columns = ('ID', 'Nome', 'NIF', 'Tipo', 'Contratos', 'Status')
        self.figuras_tree = ttk.Treeview(
            lista_frame,
            columns=columns,
            show='headings',
            height=10
        )

        for col in columns:
            self.figuras_tree.heading(col, text=col)

        self.figuras_tree.column('ID', width=50)
        self.figuras_tree.column('Nome', width=250)
        self.figuras_tree.column('NIF', width=100)
        self.figuras_tree.column('Tipo', width=120)
        self.figuras_tree.column('Contratos', width=80)
        self.figuras_tree.column('Status', width=80)

        self.figuras_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL,
                                 command=self.figuras_tree.yview)
        self.figuras_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões de ação
        action_frame = ttk.Frame(figures_frame)
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(action_frame, text="Analisar Figura", command=self.analisar_figura_selecionada).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Ver Contratos", command=self.ver_contratos_figura).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Criar Associação", command=self.criar_associacao_figura).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Remover Figura", command=self.remover_figura_selecionada).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(action_frame, text="Atualizar Lista", command=self.atualizar_lista_figuras).pack(
            side=tk.LEFT, padx=5
        )

        # Carregar figuras iniciais
        self.atualizar_lista_figuras()

    def create_alerts_tab(self):
        """Cria a aba de alertas"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alertas")

        # Frame de filtros
        filtros_frame = ttk.Frame(alerts_frame)
        filtros_frame.pack(fill=tk.X, padx=20, pady=10)

        self.alertas_apenas_nao_lidos = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            filtros_frame,
            text="Apenas não lidos",
            variable=self.alertas_apenas_nao_lidos,
            command=self.atualizar_lista_alertas
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(filtros_frame, text="Marcar Todos como Lidos",
                  command=self.marcar_todos_alertas_lidos).pack(side=tk.RIGHT, padx=5)
        ttk.Button(filtros_frame, text="Atualizar",
                  command=self.atualizar_lista_alertas).pack(side=tk.RIGHT, padx=5)

        # Frame de lista de alertas
        lista_frame = ttk.LabelFrame(alerts_frame, text="Lista de Alertas", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview de alertas
        columns = ('ID', 'Figura', 'Tipo', 'Contrato', 'Data', 'Status')
        self.alertas_tree = ttk.Treeview(
            lista_frame,
            columns=columns,
            show='headings',
            height=10
        )

        for col in columns:
            self.alertas_tree.heading(col, text=col)

        self.alertas_tree.column('ID', width=50)
        self.alertas_tree.column('Figura', width=200)
        self.alertas_tree.column('Tipo', width=100)
        self.alertas_tree.column('Contrato', width=150)
        self.alertas_tree.column('Data', width=150)
        self.alertas_tree.column('Status', width=80)

        self.alertas_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL,
                                 command=self.alertas_tree.yview)
        self.alertas_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame de detalhes do alerta
        detalhes_frame = ttk.LabelFrame(alerts_frame, text="Detalhes do Alerta", padding=10)
        detalhes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.alerta_detalhes_text = scrolledtext.ScrolledText(
            detalhes_frame,
            height=8,
            wrap=tk.WORD
        )
        self.alerta_detalhes_text.pack(fill=tk.BOTH, expand=True)

        # Bind para mostrar detalhes
        self.alertas_tree.bind('<<TreeviewSelect>>', self.mostrar_detalhes_alerta)

        # Carregar alertas iniciais
        self.atualizar_lista_alertas()

    def create_import_tab(self):
        """Cria a aba de importação de dados"""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="Importar Dados")

        # Título
        titulo = ttk.Label(
            import_frame,
            text="Importação de Dados de Contratos",
            font=('Arial', 14, 'bold')
        )
        titulo.pack(pady=20)

        # Frame de opções
        opcoes_frame = ttk.LabelFrame(import_frame, text="Fonte de Dados", padding=20)
        opcoes_frame.pack(fill=tk.X, padx=40, pady=10)

        self.import_source = tk.StringVar(value='csv')

        ttk.Radiobutton(
            opcoes_frame,
            text="Ficheiro CSV Local",
            variable=self.import_source,
            value='csv'
        ).pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(
            opcoes_frame,
            text="Portal BASE (download automático - BASE.gov.pt)",
            variable=self.import_source,
            value='dados_abertos'
        ).pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(
            opcoes_frame,
            text="API Portal BASE (requer configuração)",
            variable=self.import_source,
            value='api'
        ).pack(anchor=tk.W, pady=5)

        # Frame de configuração
        config_frame = ttk.LabelFrame(import_frame, text="Configurações", padding=20)
        config_frame.pack(fill=tk.X, padx=40, pady=10)

        ttk.Label(config_frame, text="Limite de registos (0 = todos):").pack(anchor=tk.W, pady=5)
        self.import_limit = ttk.Entry(config_frame, width=20)
        self.import_limit.insert(0, "1000")
        self.import_limit.pack(anchor=tk.W, pady=5)

        ttk.Label(config_frame, text="Limite de tamanho do ficheiro (MB, 0 = sem limite):").pack(anchor=tk.W, pady=5)
        self.import_size_limit = ttk.Entry(config_frame, width=20)
        self.import_size_limit.insert(0, "500")
        self.import_size_limit.pack(anchor=tk.W, pady=5)

        # Frame horizontal para botão e barra de progresso lado a lado
        action_progress_frame = ttk.Frame(import_frame)
        action_progress_frame.pack(fill=tk.X, padx=40, pady=20)

        # Botão de importar (esquerda)
        ttk.Button(
            action_progress_frame,
            text="Iniciar Importação",
            command=self.iniciar_importacao
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Spinner/rodinha de loading (entre botão e barra de progresso)
        self.import_spinner = ttk.Progressbar(
            action_progress_frame,
            mode='indeterminate',
            length=30
        )
        self.import_spinner.pack(side=tk.LEFT, padx=(0, 20))
        self.import_spinner.pack_forget()  # Esconder inicialmente

        # Frame de progresso (direita, expande)
        progress_container = ttk.Frame(action_progress_frame)
        progress_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Barra de progresso
        self.import_progressbar = ttk.Progressbar(
            progress_container,
            mode='determinate',
            maximum=100
        )
        self.import_progressbar.pack(fill=tk.X, pady=(0, 5))

        # Label de status
        self.import_progress_label = ttk.Label(
            progress_container,
            text="Aguardando início da importação...",
            font=('Arial', 9)
        )
        self.import_progress_label.pack(anchor=tk.W)

        # Área de log com tamanho mínimo e scrollbar
        log_frame = ttk.LabelFrame(import_frame, text="Log de Importação", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 10))

        # ScrolledText já inclui scrollbar vertical automática
        self.import_log = scrolledtext.ScrolledText(
            log_frame,
            height=15,  # Altura mínima de 15 linhas
            width=80,   # Largura mínima
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.import_log.pack(fill=tk.BOTH, expand=True)


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
            "Executar sincronização agora?\n\n"
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
                f"Contratos novos: {stats.get('contratos_novos', 0)}\n"
                f"Alertas gerados: {stats.get('alertas_gerados', 0)}"
            )
            self.update_sync_status()
            self.atualizar_dashboard()
        else:
            erros = "\n".join(stats.get('erros', []))
            messagebox.showerror("Erro", f"Sincronização falhou:\n{erros}")

        self.update_status("Pronto")

    def optimize_database(self):
        """Otimiza a base de dados"""
        resposta = messagebox.askyesno(
            "Otimizar",
            "Otimizar base de dados?\n\n"
            "Isto irá:\n"
            "• Compactar dados (VACUUM)\n"
            "• Atualizar estatísticas\n"
            "• Reindexar tabelas\n\n"
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
            f"Base de dados otimizada!\n\n"
            f"Espaço recuperado: {reducao}\n"
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

        # Frame de ações
        action_frame = ttk.Frame(assoc_frame)
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(
            action_frame,
            text="➕ Adicionar Associação",
            command=self.adicionar_associacao_dialog
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="🔄 Atualizar Lista",
            command=self.atualizar_lista_associacoes
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="🔍 Pesquisar Contratos",
            command=self.pesquisar_por_associacao
        ).pack(side=tk.LEFT, padx=5)

        # Frame de lista de associações
        lista_frame = ttk.LabelFrame(assoc_frame, text="Associações Cadastradas", padding=10)
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview de associações
        columns = ('ID', 'Pessoa', 'Empresa', 'Relação', 'Participação %', 'Status', 'Notas')
        self.associacoes_tree = ttk.Treeview(
            lista_frame,
            columns=columns,
            show='headings',
            height=15
        )

        for col in columns:
            self.associacoes_tree.heading(col, text=col)

        self.associacoes_tree.column('ID', width=40)
        self.associacoes_tree.column('Pessoa', width=200)
        self.associacoes_tree.column('Empresa', width=200)
        self.associacoes_tree.column('Relação', width=100)
        self.associacoes_tree.column('Participação %', width=100)
        self.associacoes_tree.column('Status', width=70)
        self.associacoes_tree.column('Notas', width=200)

        self.associacoes_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient=tk.VERTICAL,
                                 command=self.associacoes_tree.yview)
        self.associacoes_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind duplo clique para ver detalhes
        self.associacoes_tree.bind('<Double-1>', self.mostrar_detalhes_associacao)

        # Carregar associações iniciais
        self.atualizar_lista_associacoes()

    def create_connections_tab(self):
        """Cria aba de visualização de ligações (grafo de rede)"""
        conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(conn_frame, text="Ver Ligações 🔗")

        # Título
        titulo = ttk.Label(
            conn_frame,
            text="Visualização de Ligações",
            font=('Arial', 14, 'bold')
        )
        titulo.pack(pady=10)

        # Frame de controlos
        controls_frame = ttk.Frame(conn_frame)
        controls_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(
            controls_frame,
            text="🔄 Atualizar Grafo",
            command=self.atualizar_grafo_ligacoes
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="🔍 Zoom In",
            command=self.zoom_in_grafo
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="🔍 Zoom Out",
            command=self.zoom_out_grafo
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            controls_frame,
            text="↺ Reset Zoom",
            command=self.reset_zoom_grafo
        ).pack(side=tk.LEFT, padx=5)

        # Legenda
        legend_frame = ttk.LabelFrame(conn_frame, text="Legenda", padding=5)
        legend_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(legend_frame, text="━", foreground="red", font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Contratos (Empresa ↔ Câmara Municipal)").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="  |  ").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="━", foreground="black", font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Associações (Pessoa ↔ Empresa)").pack(side=tk.LEFT, padx=5)

        # Frame do canvas com scrollbars
        canvas_frame = ttk.Frame(conn_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Canvas para desenhar o grafo
        self.connections_canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            width=800,
            height=600
        )

        # Scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.connections_canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.connections_canvas.yview)

        self.connections_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # Grid layout
        self.connections_canvas.grid(row=0, column=0, sticky='nsew')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')

        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Variáveis para zoom
        self.grafo_zoom = 1.0

        # Carregar grafo inicial
        self.atualizar_grafo_ligacoes()

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
                f"Detectados {len(padroes)} padrões suspeitos\n\n"
                f"🔴 Alta: {sum(1 for p in padroes if p.get('gravidade') == 'alta')}\n"
                f"🟡 Média: {sum(1 for p in padroes if p.get('gravidade') == 'media')}\n"
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
            text="\n📋 Limites Legais em Portugal:",
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
                f.write("RELATÓRIO DE PADRÕES SUSPEITOS\n")
                f.write("=" * 70 + "\n\n")

                for item in self.suspicious_tree.get_children():
                    valores = self.suspicious_tree.item(item)['values']
                    f.write(f"Tipo: {valores[0]}\n")
                    f.write(f"Gravidade: {valores[1]}\n")
                    f.write(f"Descrição: {valores[2]}\n")
                    if valores[3]:
                        f.write(f"Valor: {valores[3]}\n")
                    f.write("\n" + "-" * 70 + "\n\n")

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
                texto += f"  • {empresa}\n"

            texto += f"\nCONTRATOS DIRETOS ({len(resultado['contratos_diretos'])}):  \n"
            for c in resultado['contratos_diretos'][:10]:
                texto += f"  • {c.get('adjudicante', 'N/D')} → {c.get('adjudicataria', 'N/D')} (€{c.get('valor', 0):,.2f})\n"

            texto += f"\nCONTRATOS DE EMPRESAS ASSOCIADAS ({len(resultado['contratos_empresas'])}):\n"
            for c in resultado['contratos_empresas'][:10]:
                texto += f"  • {c.get('_empresa_associada', 'N/D')} ({c.get('_tipo_associacao', '')}): €{c.get('valor', 0):,.2f}\n"

            self.assoc_results_text.insert(tk.END, texto)

        except Exception as e:
            logger.error(f"Erro na pesquisa: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

    def atualizar_lista_associacoes(self):
        """Atualiza a lista de associações"""
        try:
            self.associacoes_tree.delete(*self.associacoes_tree.get_children())

            # Obter todas as associações
            associacoes = self.associations_manager.listar_associacoes()

            for assoc in associacoes:
                # Obter nome da pessoa
                pessoa_id = assoc.get('pessoa_id')
                pessoa = self.associations_manager.obter_pessoa(pessoa_id)
                pessoa_nome = pessoa.get('nome', 'N/D') if pessoa else 'N/D'

                # Formatação
                empresa = assoc.get('empresa_nome', 'N/D')
                relacao = assoc.get('tipo_relacao', 'N/D')
                participacao = assoc.get('percentagem_participacao')
                participacao_str = f"{participacao}%" if participacao else "N/D"
                status = "Ativo" if assoc.get('ativo') else "Inativo"
                notas = assoc.get('notas', '')[:50] + '...' if len(assoc.get('notas', '')) > 50 else assoc.get('notas', '')

                self.associacoes_tree.insert('', 'end', values=(
                    assoc.get('id'),
                    pessoa_nome,
                    empresa,
                    relacao,
                    participacao_str,
                    status,
                    notas
                ))

            self.update_status(f"{len(associacoes)} associações cadastradas")

        except Exception as e:
            logger.error(f"Erro ao atualizar associações: {e}")

    def mostrar_detalhes_associacao(self, event):
        """Mostra detalhes de uma associação selecionada"""
        selection = self.associacoes_tree.selection()
        if not selection:
            return

        item = self.associacoes_tree.item(selection[0])
        assoc_id = item['values'][0]

        try:
            # Obter dados da associação
            assoc = self.associations_manager.obter_associacao(assoc_id)
            if not assoc:
                return

            # Obter pessoa
            pessoa = self.associations_manager.obter_pessoa(assoc.get('pessoa_id'))

            # Criar janela de detalhes
            detalhes_window = tk.Toplevel(self.root)
            detalhes_window.title(f"Detalhes da Associação #{assoc_id}")
            detalhes_window.geometry("600x500")

            texto = f"""
═══════════════════════════════════════════════════
DETALHES DA ASSOCIAÇÃO
═══════════════════════════════════════════════════

ID: {assoc.get('id')}

PESSOA:
  Nome: {pessoa.get('nome', 'N/D') if pessoa else 'N/D'}
  Cargo Político: {pessoa.get('cargo_politico', 'N/D') if pessoa else 'N/D'}
  Partido: {pessoa.get('partido', 'N/D') if pessoa else 'N/D'}

EMPRESA:
  Nome: {assoc.get('empresa_nome', 'N/D')}
  NIF: {assoc.get('empresa_nif', 'N/D')}

RELAÇÃO:
  Tipo: {assoc.get('tipo_relacao', 'N/D')}
  Participação: {assoc.get('percentagem_participacao', 'N/D')}%
  Data Início: {assoc.get('data_inicio', 'N/D')}
  Data Fim: {assoc.get('data_fim', 'N/D')}

STATUS: {"Ativo" if assoc.get('ativo') else "Inativo"}

FONTE: {assoc.get('fonte', 'N/D')}

NOTAS:
{assoc.get('notas', 'Sem notas')}

Data de Adição: {assoc.get('data_adicao', 'N/D')}
═══════════════════════════════════════════════════
            """

            text_widget = scrolledtext.ScrolledText(detalhes_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, texto)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(detalhes_window, text="Fechar",
                      command=detalhes_window.destroy).pack(pady=10)

        except Exception as e:
            logger.error(f"Erro ao mostrar detalhes: {e}")
            messagebox.showerror("Erro", f"Erro: {e}")

    def criar_associacao_figura(self):
        """Cria associação a partir da figura selecionada"""
        selection = self.figuras_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma figura primeiro!")
            return

        item = self.figuras_tree.item(selection[0])
        figura_nome = item['values'][1]
        figura_tipo = item['values'][3]

        # Abrir diálogo pré-preenchido
        dialog = tk.Toplevel(self.root)
        dialog.title("Criar Associação")
        dialog.geometry("500x450")

        ttk.Label(dialog, text=f"Criar associação para: {figura_nome} ({figura_tipo})",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        if figura_tipo == 'pessoa':
            # Pessoa -> Empresa
            ttk.Label(dialog, text="Nome da Pessoa:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            nome_entry = ttk.Entry(dialog, width=40)
            nome_entry.insert(0, figura_nome)
            nome_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Cargo Político:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            cargo_entry = ttk.Entry(dialog, width=40)
            cargo_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Empresa:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            empresa_entry = ttk.Entry(dialog, width=40)
            empresa_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Tipo Relação:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
            tipo_combo = ttk.Combobox(dialog, width=37)
            tipo_combo['values'] = ['dono', 'socio', 'gerente', 'administrador', 'familiar', 'conselheiro', 'outro']
            tipo_combo.set('socio')
            tipo_combo.grid(row=4, column=1, padx=5, pady=5)

        else:
            # Empresa -> Pessoa
            ttk.Label(dialog, text="Nome da Pessoa:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            nome_entry = ttk.Entry(dialog, width=40)
            nome_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Cargo Político:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            cargo_entry = ttk.Entry(dialog, width=40)
            cargo_entry.grid(row=2, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Empresa:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            empresa_entry = ttk.Entry(dialog, width=40)
            empresa_entry.insert(0, figura_nome)
            empresa_entry.grid(row=3, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Tipo Relação:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
            tipo_combo = ttk.Combobox(dialog, width=37)
            tipo_combo['values'] = ['dono', 'socio', 'gerente', 'administrador', 'familiar', 'conselheiro', 'outro']
            tipo_combo.set('socio')
            tipo_combo.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Fonte:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        fonte_entry = ttk.Entry(dialog, width=40)
        fonte_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Notas:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        notas_entry = ttk.Entry(dialog, width=40)
        notas_entry.grid(row=6, column=1, padx=5, pady=5)

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
                    fonte=fonte_entry.get(),
                    notas=notas_entry.get()
                )

                messagebox.showinfo("Sucesso", "Associação criada!")
                self.atualizar_lista_associacoes()
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

        ttk.Button(dialog, text="Guardar", command=guardar).grid(row=7, column=0, columnspan=2, pady=20)

    def adicionar_associacao_dialog(self):
        """Diálogo para adicionar associação pessoa-empresa"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Associação Pessoa-Empresa")
        dialog.geometry("550x500")

        # Título
        ttk.Label(
            dialog,
            text="Nova Associação",
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Nome da Pessoa (com autocomplete)
        ttk.Label(dialog, text="Nome da Pessoa:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        nome_entry = AutocompleteEntry(
            dialog,
            suggestions_callback=self.suggestions_manager.get_pessoas,
            width=37
        )
        nome_entry.grid(row=1, column=1, padx=5, pady=5)

        # Cargo Governamental (com autocomplete)
        ttk.Label(dialog, text="Cargo Governamental:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        cargo_entry = AutocompleteEntry(
            dialog,
            suggestions_callback=self.suggestions_manager.get_cargos,
            width=37
        )
        cargo_entry.grid(row=2, column=1, padx=5, pady=5)

        # Partido (com autocomplete)
        ttk.Label(dialog, text="Partido:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        partido_entry = AutocompleteEntry(
            dialog,
            suggestions_callback=self.suggestions_manager.get_partidos,
            width=37
        )
        partido_entry.grid(row=3, column=1, padx=5, pady=5)

        # Separador
        ttk.Separator(dialog, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)

        # Empresa (com autocomplete)
        ttk.Label(dialog, text="Empresa:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        empresa_entry = AutocompleteEntry(
            dialog,
            suggestions_callback=self.suggestions_manager.get_empresas,
            width=37
        )
        empresa_entry.grid(row=5, column=1, padx=5, pady=5)

        # Tipo de Relação
        ttk.Label(dialog, text="Tipo de Relação:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        tipo_combo = ttk.Combobox(dialog, width=35, state='readonly')
        tipo_combo['values'] = ['dono', 'socio', 'gerente', 'administrador', 'familiar', 'outro']
        tipo_combo.set('socio')
        tipo_combo.grid(row=6, column=1, padx=5, pady=5)

        # Fonte
        ttk.Label(dialog, text="Fonte (opcional):").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
        fonte_entry = ttk.Entry(dialog, width=40)
        fonte_entry.grid(row=7, column=1, padx=5, pady=5)

        # Informação
        info_text = """
ℹ️ Esta associação irá:
• Adicionar a pessoa como Figura de Interesse (se não existir)
• Adicionar a empresa como Figura de Interesse (se não existir)
• Criar ligação entre pessoa e empresa
• Permitir pesquisa expandida (pessoa → todos contratos da empresa)
        """
        info_label = ttk.Label(dialog, text=info_text, foreground='blue')
        info_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(dialog, text="Notas:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        notas_entry = ttk.Entry(dialog, width=40)
        notas_entry.grid(row=5, column=1, padx=5, pady=5)

        def guardar():
            nome_pessoa = nome_entry.get().strip()
            cargo = cargo_entry.get().strip() or None
            partido = partido_entry.get().strip() or None
            empresa = empresa_entry.get().strip()
            tipo_relacao = tipo_combo.get()
            fonte = fonte_entry.get().strip() or None

            if not nome_pessoa:
                messagebox.showwarning("Aviso", "Nome da pessoa é obrigatório!")
                return

            if not empresa:
                messagebox.showwarning("Aviso", "Nome da empresa é obrigatório!")
                return

            try:
                # 1. Adicionar pessoa como figura de interesse (se não existir)
                pessoa_id = self.entities_manager.adicionar_figura(
                    nome=nome_pessoa,
                    tipo='pessoa',
                    notas=f"Associado a {empresa}",
                    cargo_governamental=cargo,
                    partido=partido
                )

                # 2. Adicionar empresa como figura de interesse (se não existir)
                empresa_id = self.entities_manager.adicionar_figura(
                    nome=empresa,
                    tipo='empresa',
                    notas=f"Associado a {nome_pessoa}"
                )

                # 3. Adicionar pessoa ao sistema de associações
                assoc_pessoa_id = self.associations_manager.adicionar_pessoa(
                    nome=nome_pessoa,
                    cargo_politico=cargo
                )

                # 4. Criar associação pessoa-empresa
                self.associations_manager.associar_pessoa_empresa(
                    pessoa_id=assoc_pessoa_id,
                    empresa_nome=empresa,
                    tipo_relacao=tipo_relacao,
                    fonte=fonte,
                    notas=notas_entry.get()  # Campo notas adicionado
                )

                messagebox.showinfo(
                    "Sucesso",
                    f"✓ Associação criada!\n\n"
                    f"Pessoa: {nome_pessoa} (ID: {pessoa_id})\n"
                    f"Empresa: {empresa} (ID: {empresa_id})\n\n"
                    f"Ambos foram adicionados como Figuras de Interesse."
                )

                # Atualizar listas e cache
                self.atualizar_lista_figuras()
                self.atualizar_lista_associacoes()  # Atualizar lista de associações também
                self.suggestions_manager.limpar_cache()

                dialog.destroy()

            except Exception as e:
                logger.error(f"Erro ao adicionar associação: {e}")
                messagebox.showerror("Erro", f"Erro: {e}")

        # Botões
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=9, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Guardar Associação", command=guardar).pack(side=tk.LEFT, padx=5)

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

                texto += f"{i}. {gravidade_emoji} {c['gravidade'].upper()}\n"
                texto += f"   Pessoa: {c['pessoa_nome']} ({c['cargo']})\n"
                texto += f"   Empresa: {c['empresa']}\n"
                texto += f"   Contrato: {c['adjudicante']} (€{c['valor']:,.2f})\n"
                texto += f"   {c['descricao']}\n\n"

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
            "Funcionalidade em desenvolvimento!\n\n"
            "Irá incluir:\n"
            "• Padrões suspeitos\n"
            "• Conflitos de interesse\n"
            "• Estatísticas avançadas\n"
            "• Exportação em PDF"
        )

    def create_status_bar(self):
        """Cria a barra de status na parte inferior"""
        self.status_bar = ttk.Label(
            self.root,
            text="Pronto",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ==================== MÉTODOS DO DASHBOARD ====================

    def atualizar_dashboard(self):
        """Atualiza as informações do dashboard"""
        try:
            stats = self.db.obter_estatisticas()

            self.stats_labels['total_contratos'].config(text=f"{stats['total_contratos']:,}")
            self.stats_labels['total_figuras'].config(text=f"{stats['total_figuras']:,}")
            self.stats_labels['alertas_nao_lidos'].config(text=f"{stats['alertas_nao_lidos']:,}")
            self.stats_labels['valor_total'].config(
                text=f"€{stats['valor_total_contratos']:,.2f}"
            )

            # Atualizar alertas recentes
            self.dashboard_alertas_tree.delete(*self.dashboard_alertas_tree.get_children())

            alertas = self.alerts_manager.listar_alertas(apenas_nao_lidos=False)[:10]

            for alerta in alertas:
                status = "Lido" if alerta.get('lido') else "Não lido"
                self.dashboard_alertas_tree.insert('', 'end', values=(
                    alerta.get('figura_nome', 'N/D'),
                    alerta.get('tipo_alerta', 'N/D'),
                    alerta.get('data_alerta', 'N/D')[:19],
                    status
                ))

            self.update_status("Dashboard atualizado")

        except Exception as e:
            logger.error(f"Erro ao atualizar dashboard: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar dashboard: {e}")

    # ==================== MÉTODOS DE PESQUISA ====================

    def pesquisar_contratos(self):
        """Executa a pesquisa de contratos com os filtros especificados"""
        try:
            filtros = {}

            if self.filtro_distrito.get():
                filtros['distrito'] = self.filtro_distrito.get()

            if self.filtro_concelho.get():
                filtros['concelho'] = self.filtro_concelho.get()

            if self.filtro_ano_inicio.get():
                filtros['ano_inicio'] = int(self.filtro_ano_inicio.get())

            if self.filtro_ano_fim.get():
                filtros['ano_fim'] = int(self.filtro_ano_fim.get())

            if self.filtro_adjudicante.get():
                filtros['adjudicante'] = self.filtro_adjudicante.get()

            if self.filtro_adjudicataria.get():
                filtros['adjudicataria'] = self.filtro_adjudicataria.get()

            if self.filtro_valor_min.get():
                filtros['valor_min'] = float(self.filtro_valor_min.get())

            if self.filtro_valor_max.get():
                filtros['valor_max'] = float(self.filtro_valor_max.get())

            if self.filtro_tipo_procedimento.get():
                filtros['tipo_procedimento'] = self.filtro_tipo_procedimento.get()

            # Executar pesquisa
            resultados = self.db.pesquisar_contratos(filtros)

            # Limpar resultados anteriores
            self.resultados_tree.delete(*self.resultados_tree.get_children())

            # Inserir novos resultados
            for contrato in resultados:
                valor = f"€{contrato.get('valor', 0):,.2f}" if contrato.get('valor') else "N/D"

                self.resultados_tree.insert('', 'end', values=(
                    contrato.get('id_contrato', 'N/D'),
                    contrato.get('adjudicante', 'N/D'),
                    contrato.get('adjudicataria', 'N/D'),
                    valor,
                    contrato.get('data_contrato', 'N/D'),
                    contrato.get('tipo_procedimento', 'N/D')
                ))

            self.update_status(f"Encontrados {len(resultados)} contratos")

        except Exception as e:
            logger.error(f"Erro na pesquisa: {e}")
            messagebox.showerror("Erro", f"Erro ao pesquisar: {e}")

    def limpar_filtros(self):
        """Limpa todos os filtros de pesquisa"""
        self.filtro_distrito.set('')
        self.filtro_concelho.delete(0, tk.END)
        self.filtro_ano_inicio.set(2020)
        self.filtro_ano_fim.set(2025)
        self.filtro_adjudicante.delete(0, tk.END)
        self.filtro_adjudicataria.delete(0, tk.END)
        self.filtro_valor_min.delete(0, tk.END)
        self.filtro_valor_max.delete(0, tk.END)
        self.filtro_tipo_procedimento.set('')

        self.resultados_tree.delete(*self.resultados_tree.get_children())
        self.update_status("Filtros limpos")

    def mostrar_detalhes_contrato(self, event):
        """Mostra detalhes de um contrato selecionado"""
        selection = self.resultados_tree.selection()
        if not selection:
            return

        item = self.resultados_tree.item(selection[0])
        id_contrato = item['values'][0]

        contrato = self.db.obter_contrato_por_id(id_contrato)

        if contrato:
            # Criar janela de detalhes
            detalhes_window = tk.Toplevel(self.root)
            detalhes_window.title(f"Detalhes do Contrato - {id_contrato}")
            detalhes_window.geometry("600x500")

            # Criar texto formatado
            texto = f"""
═══════════════════════════════════════════════════
DETALHES DO CONTRATO
═══════════════════════════════════════════════════

ID: {contrato.get('id_contrato', 'N/D')}

Adjudicante: {contrato.get('adjudicante', 'N/D')}
NIF Adjudicante: {contrato.get('adjudicante_nif', 'N/D')}

Adjudicatária: {contrato.get('adjudicataria', 'N/D')}
NIF Adjudicatária: {contrato.get('adjudicataria_nif', 'N/D')}

Valor: €{contrato.get('valor', 0):,.2f}
Data do Contrato: {contrato.get('data_contrato', 'N/D')}
Data de Publicação: {contrato.get('data_publicacao', 'N/D')}

Tipo de Contrato: {contrato.get('tipo_contrato', 'N/D')}
Tipo de Procedimento: {contrato.get('tipo_procedimento', 'N/D')}

Localização:
  Distrito: {contrato.get('distrito', 'N/D')}
  Concelho: {contrato.get('concelho', 'N/D')}

CPV: {contrato.get('cpv', 'N/D')}
Prazo de Execução: {contrato.get('prazo_execucao', 'N/D')} dias

Descrição/Objeto:
{contrato.get('descricao') or contrato.get('objeto_contrato', 'N/D')}

Link BASE: {contrato.get('link_base', 'N/D')}

═══════════════════════════════════════════════════
            """

            text_widget = scrolledtext.ScrolledText(detalhes_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, texto)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(detalhes_window, text="Fechar",
                      command=detalhes_window.destroy).pack(pady=10)

    # ==================== MÉTODOS DE FIGURAS ====================

    def _on_tipo_figura_changed(self, event=None):
        """Mostra/esconde campos baseado no tipo selecionado"""
        tipo = self.figura_tipo.get()

        if tipo == 'pessoa':
            # Mostrar campos de cargo e partido
            self.label_cargo.grid()
            self.figura_cargo.grid()
            self.label_partido.grid()
            self.figura_partido.grid()
        else:
            # Esconder campos de cargo e partido para empresas/entidades
            self.label_cargo.grid_remove()
            self.figura_cargo.grid_remove()
            self.label_partido.grid_remove()
            self.figura_partido.grid_remove()
            # Limpar valores
            self.figura_cargo.delete(0, tk.END)
            self.figura_partido.delete(0, tk.END)

    def adicionar_figura(self):
        """Adiciona uma nova figura de interesse"""
        nome = self.figura_nome.get().strip()
        nif = self.figura_nif.get().strip() or None
        tipo = self.figura_tipo.get()
        notas = self.figura_notas.get().strip()

        # Campos adicionais para pessoas
        cargo = None
        partido = None
        if tipo == 'pessoa':
            cargo = self.figura_cargo.get().strip() or None
            partido = self.figura_partido.get().strip() or None

        if not nome:
            messagebox.showwarning("Aviso", "O nome é obrigatório!")
            return

        try:
            figura_id = self.entities_manager.adicionar_figura(
                nome, nif, tipo, notas, cargo, partido
            )
            messagebox.showinfo("Sucesso", f"Figura '{nome}' adicionada com ID {figura_id}")

            # Limpar campos
            self.figura_nome.delete(0, tk.END)
            self.figura_nif.delete(0, tk.END)
            self.figura_tipo.set('pessoa')
            self.figura_notas.delete(0, tk.END)
            self.figura_cargo.delete(0, tk.END)
            self.figura_partido.delete(0, tk.END)
            self._on_tipo_figura_changed()  # Resetar visibilidade

            # Atualizar lista
            self.atualizar_lista_figuras()
            # Limpar cache de sugestões para incluir novos valores
            self.suggestions_manager.limpar_cache()

        except Exception as e:
            logger.error(f"Erro ao adicionar figura: {e}")
            messagebox.showerror("Erro", f"Erro ao adicionar figura: {e}")

    def atualizar_lista_figuras(self):
        """Atualiza a lista de figuras de interesse"""
        try:
            self.figuras_tree.delete(*self.figuras_tree.get_children())

            figuras = self.entities_manager.listar_figuras(apenas_ativas=True)

            for figura in figuras:
                # Contar contratos
                contratos = self.db.pesquisar_contratos_por_figura(figura['id'])
                n_contratos = len(contratos)

                status = "Ativo" if figura.get('ativo') else "Inativo"

                self.figuras_tree.insert('', 'end', values=(
                    figura['id'],
                    figura['nome'],
                    figura.get('nif', 'N/D'),
                    figura.get('tipo', 'N/D'),
                    n_contratos,
                    status
                ))

            # Atualizar também o filtro rápido
            self.atualizar_quick_filter_figuras()

            self.update_status(f"{len(figuras)} figuras de interesse")

        except Exception as e:
            logger.error(f"Erro ao atualizar lista de figuras: {e}")

    def analisar_figura_selecionada(self):
        """Analisa a figura de interesse selecionada"""
        selection = self.figuras_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma figura primeiro!")
            return

        item = self.figuras_tree.item(selection[0])
        figura_id = item['values'][0]

        try:
            analise = self.entities_manager.analisar_contratos_figura(figura_id)

            # Criar janela de análise
            analise_window = tk.Toplevel(self.root)
            analise_window.title(f"Análise - {analise['figura']['nome']}")
            analise_window.geometry("700x600")

            # Criar texto formatado
            texto = f"""
═══════════════════════════════════════════════════
ANÁLISE DA FIGURA DE INTERESSE
═══════════════════════════════════════════════════

Nome: {analise['figura']['nome']}
NIF: {analise['figura'].get('nif', 'N/D')}
Tipo: {analise['figura'].get('tipo', 'N/D')}

ESTATÍSTICAS:
Total de Contratos: {analise['total_contratos']}
Valor Total: €{analise['valor_total']:,.2f}

Como Adjudicante: {analise['como_adjudicante']} contratos
Como Adjudicatária: {analise['como_adjudicataria']} contratos

TOP 5 PARCEIROS:
"""
            for parceiro, count in analise['top_parceiros']:
                texto += f"  • {parceiro}: {count} contratos\n"

            texto += "\nDISTRIBUIÇÃO POR ANO:\n"
            for ano, count in sorted(analise['distribuicao_anos'].items(), reverse=True):
                texto += f"  {ano}: {count} contratos\n"

            texto += "\nTIPOS DE CONTRATO:\n"
            for tipo, count in sorted(analise['tipos_contrato'].items(),
                                    key=lambda x: x[1], reverse=True):
                texto += f"  • {tipo}: {count}\n"

            texto += "\n═══════════════════════════════════════════════════\n"

            text_widget = scrolledtext.ScrolledText(analise_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, texto)
            text_widget.config(state=tk.DISABLED)

            ttk.Button(analise_window, text="Fechar",
                      command=analise_window.destroy).pack(pady=10)

        except Exception as e:
            logger.error(f"Erro ao analisar figura: {e}")
            messagebox.showerror("Erro", f"Erro ao analisar figura: {e}")

    def ver_contratos_figura(self):
        """Mostra contratos de uma figura selecionada"""
        selection = self.figuras_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma figura primeiro!")
            return

        item = self.figuras_tree.item(selection[0])
        figura_id = item['values'][0]
        figura_nome = item['values'][1]

        # Mudar para aba de pesquisa e preencher filtro
        self.notebook.select(1)  # Aba de pesquisa
        self.limpar_filtros()
        self.filtro_adjudicante.insert(0, figura_nome)
        self.filtro_adjudicataria.insert(0, figura_nome)
        self.pesquisar_contratos()

    def remover_figura_selecionada(self):
        """Remove (desativa) uma figura selecionada"""
        selection = self.figuras_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma figura primeiro!")
            return

        item = self.figuras_tree.item(selection[0])
        figura_id = item['values'][0]
        figura_nome = item['values'][1]

        resposta = messagebox.askyesno(
            "Confirmar",
            f"Deseja remover a figura '{figura_nome}'?\n\n"
            "Nota: A figura será desativada mas os dados históricos serão mantidos."
        )

        if resposta:
            try:
                self.entities_manager.remover_figura(figura_id)
                messagebox.showinfo("Sucesso", f"Figura '{figura_nome}' removida")
                self.atualizar_lista_figuras()
            except Exception as e:
                logger.error(f"Erro ao remover figura: {e}")
                messagebox.showerror("Erro", f"Erro ao remover figura: {e}")

    # ==================== MÉTODOS DE ALERTAS ====================

    def atualizar_lista_alertas(self):
        """Atualiza a lista de alertas"""
        try:
            self.alertas_tree.delete(*self.alertas_tree.get_children())

            apenas_nao_lidos = self.alertas_apenas_nao_lidos.get()
            alertas = self.alerts_manager.listar_alertas(apenas_nao_lidos=apenas_nao_lidos)

            for alerta in alertas:
                status = "Lido" if alerta.get('lido') else "Não lido"

                self.alertas_tree.insert('', 'end', values=(
                    alerta['id'],
                    alerta.get('figura_nome', 'N/D'),
                    alerta.get('tipo_alerta', 'N/D'),
                    alerta.get('id_contrato', 'N/D'),
                    alerta.get('data_alerta', 'N/D')[:19],
                    status
                ), tags=('nao_lido' if not alerta.get('lido') else 'lido',))

            # Configurar tags de cores
            self.alertas_tree.tag_configure('nao_lido', background='#ffebee')
            self.alertas_tree.tag_configure('lido', background='white')

            self.update_status(f"{len(alertas)} alertas")

        except Exception as e:
            logger.error(f"Erro ao atualizar alertas: {e}")

    def mostrar_detalhes_alerta(self, event):
        """Mostra detalhes do alerta selecionado"""
        selection = self.alertas_tree.selection()
        if not selection:
            return

        item = self.alertas_tree.item(selection[0])
        alerta_id = item['values'][0]

        # Buscar alerta completo
        todos_alertas = self.alerts_manager.listar_alertas(apenas_nao_lidos=False)
        alerta = next((a for a in todos_alertas if a['id'] == alerta_id), None)

        if alerta:
            self.alerta_detalhes_text.config(state=tk.NORMAL)
            self.alerta_detalhes_text.delete(1.0, tk.END)
            self.alerta_detalhes_text.insert(tk.END, alerta.get('mensagem', 'Sem detalhes'))
            self.alerta_detalhes_text.config(state=tk.DISABLED)

            # Marcar como lido
            if not alerta.get('lido'):
                self.alerts_manager.marcar_lido(alerta_id)
                self.atualizar_lista_alertas()
                self.atualizar_dashboard()

    def marcar_todos_alertas_lidos(self):
        """Marca todos os alertas como lidos"""
        resposta = messagebox.askyesno(
            "Confirmar",
            "Marcar todos os alertas como lidos?"
        )

        if resposta:
            try:
                count = self.alerts_manager.marcar_todos_lidos()
                messagebox.showinfo("Sucesso", f"{count} alertas marcados como lidos")
                self.atualizar_lista_alertas()
                self.atualizar_dashboard()
            except Exception as e:
                logger.error(f"Erro ao marcar alertas: {e}")
                messagebox.showerror("Erro", f"Erro: {e}")

    # ==================== MÉTODOS DE IMPORTAÇÃO ====================

    def iniciar_importacao(self):
        """Inicia o processo de importação de dados"""
        fonte = self.import_source.get()
        limite_str = self.import_limit.get()
        limite_tamanho_str = self.import_size_limit.get()

        try:
            limite = int(limite_str) if limite_str and int(limite_str) > 0 else None
        except:
            messagebox.showerror("Erro", "Limite de registos inválido")
            return

        try:
            limite_tamanho_mb = int(limite_tamanho_str) if limite_tamanho_str and int(limite_tamanho_str) > 0 else None
        except:
            messagebox.showerror("Erro", "Limite de tamanho inválido")
            return

        # Se for Portal BASE, perguntar o ano ANTES de iniciar a thread
        ano = None
        if fonte == 'dados_abertos':
            from tkinter import simpledialog
            resposta = messagebox.askyesno(
                "Filtrar por Ano",
                "Deseja importar apenas um ano específico?\n\n"
                "• SIM: Escolher um ano (mais rápido, ficheiro menor)\n"
                "• NÃO: Importar TODOS os anos disponíveis\n"
                "  (AVISO: Pode ser MUITO grande - centenas de MB e demorar minutos!)"
            )

            if resposta:  # User wants to select a year
                ano = simpledialog.askinteger(
                    "Ano dos Contratos",
                    "Digite o ano (2012-2025):",
                    minvalue=2012,
                    maxvalue=2025,
                    parent=self.root
                )
                if ano is None:  # User cancelled
                    return

        self.import_log.delete(1.0, tk.END)
        self.log_import("Iniciando importação...")
        self.log_import(f"Fonte: {fonte}")
        self.log_import(f"Limite de registos: {limite or 'Sem limite'}")
        self.log_import(f"Limite de tamanho: {limite_tamanho_mb or 'Sem limite'} MB\n")

        # Mostrar spinner/rodinha de loading
        self.import_spinner.pack(side=tk.LEFT, padx=(0, 20))
        self.import_spinner.start(10)  # Velocidade da animação

        # Executar em thread separada para não bloquear a UI
        thread = threading.Thread(
            target=self._executar_importacao,
            args=(fonte, limite, limite_tamanho_mb, ano),
            daemon=True
        )
        thread.start()

    def _executar_importacao(self, fonte: str, limite: Optional[int], limite_tamanho_mb: Optional[int] = None, ano: Optional[int] = None):
        """Executa a importação em background"""
        try:
            # Reset progress bar
            self.update_import_progress(0, "Iniciando importação...")

            if fonte == 'csv':
                self.log_import("Selecionando ficheiro CSV...")
                csv_path = filedialog.askopenfilename(
                    title="Selecionar ficheiro CSV",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )

                if not csv_path:
                    self.log_import("Importação cancelada")
                    self.update_import_progress(0, "Importação cancelada")
                    return

                from pathlib import Path
                csv_path = Path(csv_path)

                # Verificar tamanho do ficheiro
                if limite_tamanho_mb:
                    tamanho_mb = csv_path.stat().st_size / (1024 * 1024)
                    self.log_import(f"Tamanho do ficheiro: {tamanho_mb:.2f} MB")

                    if tamanho_mb > limite_tamanho_mb:
                        self.log_import(f"AVISO: Ficheiro excede o limite de {limite_tamanho_mb} MB")
                        self.log_import(f"A importação será limitada aos primeiros {limite_tamanho_mb} MB de dados\n")
                    else:
                        self.log_import(f"Tamanho dentro do limite ({limite_tamanho_mb} MB)\n")

                self.log_import(f"A processar: {csv_path.name}\n")
                self.update_import_progress(5, f"A processar: {csv_path.name}")

                # Parse CSV com callback de progresso
                contratos = self.scraper.parse_csv_contratos(
                    csv_path,
                    limit=limite,
                    size_limit_mb=limite_tamanho_mb,
                    progress_callback=self.update_import_progress
                )
                self.log_import(f"Parseados {len(contratos)} contratos\n")

                # Processar contratos com callback de progresso
                stats = self.scraper.processar_lote_contratos(
                    contratos,
                    self.db,
                    progress_callback=self.update_import_progress
                )

                self.log_import("\n=== RESULTADO ===")
                self.log_import(f"Total processados: {stats['total']}")
                self.log_import(f"Inseridos: {stats['inseridos']}")
                self.log_import(f"Duplicados: {stats['duplicados']}")
                self.log_import(f"Inválidos: {stats['invalidos']}")

                # Verificar alertas
                self.log_import("\nA verificar figuras de interesse...")
                self.update_import_progress(100, "A verificar alertas...")
                alertas = self.alerts_manager.verificar_novos_contratos(contratos)
                self.log_import(f"Gerados {len(alertas)} alertas\n")

                messagebox.showinfo("Sucesso", "Importação concluída!")

                # Atualizar dashboard
                self.root.after(0, self.atualizar_dashboard)

            elif fonte == 'dados_abertos':
                self.log_import("=== IMPORTAÇÃO DO PORTAL BASE ===\n")
                self.log_import("A descarregar contratos do Portal BASE (BASE.gov.pt)...")
                self.log_import("AVISO: Downloads grandes podem demorar vários minutos!\n")
                self.update_import_progress(0, "A descarregar do Portal BASE...")

                ano_str = str(ano) if ano else "TODOS"
                self.log_import(f"Ano selecionado: {ano_str}\n")

                # Download do CSV
                from pathlib import Path
                csv_path = self.scraper.download_contratos_base_gov(ano=ano)

                if not csv_path or not Path(csv_path).exists():
                    self.log_import("\nERRO: Não foi possível descarregar os dados")
                    self.log_import("Possíveis causas:")
                    self.log_import("  • Sem conexão à internet")
                    self.log_import("  • Portal BASE indisponível")
                    self.log_import("  • Timeout (ficheiro muito grande)")
                    self.log_import("\nSolução: Tente:")
                    self.log_import("  1. Verificar a conexão")
                    self.log_import("  2. Escolher um ano específico (ficheiro menor)")
                    self.log_import("  3. Importar ficheiro CSV manualmente")
                    self.update_import_progress(0, "Erro ao descarregar dados")
                    return

                self.log_import(f"\nFicheiro descarregado: {csv_path}")
                self.log_import("A processar contratos...\n")
                self.update_import_progress(5, "Ficheiro descarregado, a processar...")

                # Parse do CSV com callback de progresso
                contratos = self.scraper.parse_csv_contratos(
                    Path(csv_path),
                    limit=limite,
                    progress_callback=self.update_import_progress
                )
                self.log_import(f"Parseados {len(contratos)} contratos\n")

                if not contratos:
                    self.log_import("\nERRO: Nenhum contrato encontrado no ficheiro")
                    self.log_import("O ficheiro pode estar vazio ou em formato incorreto")
                    self.update_import_progress(0, "Erro: nenhum contrato encontrado")
                    return

                # Processar e inserir na BD com callback de progresso
                self.log_import("A inserir contratos na base de dados...")
                stats = self.scraper.processar_lote_contratos(
                    contratos,
                    self.db,
                    progress_callback=self.update_import_progress
                )

                self.log_import("\n=== RESULTADO ===")
                self.log_import(f"Total processados: {stats['total']}")
                self.log_import(f"✓ Inseridos: {stats['inseridos']}")
                self.log_import(f"⊗ Duplicados: {stats['duplicados']}")
                self.log_import(f"✗ Inválidos: {stats['invalidos']}")

                # Verificar alertas
                self.log_import("\nA verificar figuras de interesse...")
                self.update_import_progress(100, "A verificar alertas...")
                alertas = self.alerts_manager.verificar_novos_contratos(contratos)
                self.log_import(f"Gerados {len(alertas)} alertas\n")

                messagebox.showinfo("Sucesso",
                    f"Importação concluída!\n\n"
                    f"Inseridos: {stats['inseridos']}\n"
                    f"Duplicados: {stats['duplicados']}\n"
                    f"Alertas: {len(alertas)}")

                # Atualizar dashboard
                self.root.after(0, self.atualizar_dashboard)

            elif fonte == 'api':
                self.log_import("=== IMPORTAÇÃO VIA API ===\n")
                self.log_import("A importação via API oficial requer credenciais do IMPIC")
                self.log_import("\nPara obter acesso à API:")
                self.log_import("  1. Aceder a https://www.base.gov.pt")
                self.log_import("  2. Contactar o IMPIC para solicitar credenciais")
                self.log_import("  3. Configurar as credenciais na aplicação")
                self.log_import("\nPor agora, use:")
                self.log_import("  • 'Dados Abertos' (download automático do Portal BASE)")
                self.log_import("  • 'Ficheiro CSV' (importação manual)")

        except Exception as e:
            logger.error(f"Erro na importação: {e}")
            self.log_import(f"\nERRO: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na importação: {e}"))

    def log_import(self, mensagem: str):
        """Adiciona mensagem ao log de importação"""
        self.import_log.insert(tk.END, mensagem + "\n")
        self.import_log.see(tk.END)
        self.import_log.update()

    def update_import_progress(self, percentage: float, status: str):
        """Atualiza a barra de progresso da importação (thread-safe)"""
        def _update():
            # Esconder spinner em várias situações
            should_hide_spinner = (
                percentage > 0 or  # Progresso real começou
                percentage >= 100 or  # Concluído
                "cancelada" in status.lower() or  # Cancelado
                "erro" in status.lower()  # Erro
            )

            if should_hide_spinner and self.import_spinner.winfo_ismapped():
                self.import_spinner.stop()
                self.import_spinner.pack_forget()

            # Atualizar barra de progresso
            self.import_progressbar['value'] = percentage
            self.import_progress_label['text'] = f"{percentage:.1f}% - {status}"

        self.root.after(0, _update)

    # ==================== MÉTODOS DE MENU ====================

    def exportar_resultados(self):
        """Exporta resultados da pesquisa para Excel"""
        # Verificar se há resultados
        if not self.resultados_tree.get_children():
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar")
            return

        # Selecionar local para salvar
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            import pandas as pd

            # Coletar dados da treeview
            dados = []
            for child in self.resultados_tree.get_children():
                valores = self.resultados_tree.item(child)['values']
                dados.append(valores)

            # Criar DataFrame
            colunas = ['ID', 'Adjudicante', 'Adjudicatária', 'Valor', 'Data', 'Tipo de Procedimento']
            df = pd.DataFrame(dados, columns=colunas)

            # Exportar
            df.to_excel(filepath, index=False)

            messagebox.showinfo("Sucesso", f"Dados exportados para {filepath}")
            self.update_status(f"Exportado: {filepath}")

        except Exception as e:
            logger.error(f"Erro ao exportar: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def atualizar_dados(self):
        """Atualiza todos os dados da aplicação"""
        self.update_status("A atualizar dados...")
        self.atualizar_dashboard()
        self.atualizar_lista_figuras()
        self.atualizar_lista_alertas()
        messagebox.showinfo("Sucesso", "Dados atualizados!")

    def limpar_cache(self):
        """Limpa o cache da aplicação"""
        resposta = messagebox.askyesno(
            "Confirmar",
            "Esta operação irá limpar dados temporários.\nDeseja continuar?"
        )

        if resposta:
            self.update_status("Cache limpo")
            messagebox.showinfo("Sucesso", "Cache limpo com sucesso!")

    def mostrar_sobre(self):
        """Mostra informações sobre a aplicação"""
        current_version = get_current_version()
        about_text = f"""
Monitor de Contratos Públicos
Versão {current_version}

Aplicação para monitorização de contratos públicos
portugueses do Portal BASE (www.base.gov.pt)

Desenvolvida com Python e Tkinter

Funcionalidades:
• Pesquisa de contratos com filtros avançados
• Gestão de figuras de interesse
• Sistema de alertas automáticos
• Análise de conexões entre entidades
• Exportação para Excel
• Visualização de ligações em grafo

© 2025
        """

        messagebox.showinfo("Sobre", about_text)

    def verificar_atualizacoes(self):
        """Verifica se há atualizações disponíveis no GitHub"""
        self.update_status("A verificar atualizações...")

        try:
            # Executar verificação em thread separada para não bloquear UI
            def _check():
                update_info = check_for_updates()

                def _show_result():
                    if update_info:
                        # Nova versão disponível
                        msg = f"""
Nova versão disponível!

Versão atual: {update_info['current_version']}
Nova versão: {update_info['version']}

Notas da versão:
{update_info['release_notes'][:300]}...

Deseja abrir a página de download?
                        """
                        if messagebox.askyesno("Atualização Disponível", msg):
                            import webbrowser
                            webbrowser.open(update_info['download_url'])
                    else:
                        # Já está atualizado
                        current = get_current_version()
                        messagebox.showinfo(
                            "Atualizado",
                            f"Você já está usando a versão mais recente!\n\nVersão: {current}"
                        )

                    self.update_status("Pronto")

                self.root.after(0, _show_result)

            thread = threading.Thread(target=_check, daemon=True)
            thread.start()

        except Exception as e:
            logger.error(f"Erro ao verificar atualizações: {e}")
            messagebox.showerror("Erro", f"Erro ao verificar atualizações:\n{e}")
            self.update_status("Pronto")

    # ==================== MÉTODOS DE GRAFO DE LIGAÇÕES ====================

    def atualizar_grafo_ligacoes(self):
        """Atualiza e desenha o grafo de ligações"""
        self.update_status("A carregar ligações...")

        try:
            # Limpar canvas
            self.connections_canvas.delete('all')

            # Obter dados de ligações
            # 1. Ligações de contratos (vermelho): empresa - câmara municipal
            contratos = self.db.pesquisar_contratos({})

            # 2. Associações pessoa-empresa (preto)
            associacoes = self.associations_manager.listar_associacoes()

            # Criar estrutura de nós e arestas
            nodes = {}  # {nome: {x, y, tipo}}
            edges_contratos = []  # [(empresa, camaras, count)]
            edges_associacoes = []  # [(pessoa, empresa)]

            # Processar contratos (agrupar por adjudicatária)
            contratos_por_par = {}
            for contrato in contratos[:500]:  # Limitar a 500 para performance
                empresa = contrato.get('adjudicataria', '')
                camara = contrato.get('adjudicante', '')

                if empresa and camara:
                    nodes[empresa] = {'tipo': 'empresa'}
                    nodes[camara] = {'tipo': 'camara'}

                    par = (empresa, camara)
                    contratos_por_par[par] = contratos_por_par.get(par, 0) + 1

            for (empresa, camara), count in contratos_por_par.items():
                edges_contratos.append((empresa, camara, count))

            # Processar associações
            for assoc in associacoes:
                pessoa_id = assoc.get('pessoa_id')
                empresa_id = assoc.get('empresa_id')

                if pessoa_id and empresa_id:
                    pessoa = self.associations_manager.obter_pessoa(pessoa_id)
                    empresa = self.associations_manager.obter_empresa(empresa_id)

                    if pessoa and empresa:
                        pessoa_nome = pessoa.get('nome', '')
                        empresa_nome = empresa.get('nome', '')

                        if pessoa_nome and empresa_nome:
                            nodes[pessoa_nome] = {'tipo': 'pessoa'}
                            nodes[empresa_nome] = {'tipo': 'empresa'}
                            edges_associacoes.append((pessoa_nome, empresa_nome))

            # Calcular layout do grafo (circular simples)
            self.desenhar_grafo(nodes, edges_contratos, edges_associacoes)

            self.update_status(f"Grafo carregado: {len(nodes)} nós, {len(edges_contratos)} contratos, {len(edges_associacoes)} associações")

        except Exception as e:
            logger.error(f"Erro ao atualizar grafo: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar grafo: {e}")

    def desenhar_grafo(self, nodes, edges_contratos, edges_associacoes):
        """Desenha o grafo no canvas"""
        import math

        if not nodes:
            self.connections_canvas.create_text(
                400, 300,
                text="Nenhuma ligação para visualizar\nImporte dados primeiro",
                font=('Arial', 12),
                fill='gray'
            )
            return

        # Tamanho do canvas expandido
        canvas_width = max(1600, len(nodes) * 100)
        canvas_height = max(1200, len(nodes) * 80)

        # Configurar scrollregion
        self.connections_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

        # Layout circular
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        radius = min(canvas_width, canvas_height) * 0.35

        node_positions = {}
        node_list = list(nodes.keys())

        for i, node_name in enumerate(node_list):
            angle = (2 * math.pi * i) / len(node_list)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            node_positions[node_name] = (x, y)

        # Desenhar arestas de contratos (vermelho)
        for empresa, camara, count in edges_contratos:
            if empresa in node_positions and camara in node_positions:
                x1, y1 = node_positions[empresa]
                x2, y2 = node_positions[camara]

                # Espessura baseada no número de contratos
                width = min(1 + count / 5, 8)

                self.connections_canvas.create_line(
                    x1, y1, x2, y2,
                    fill='red',
                    width=width,
                    tags='edge_contrato'
                )

        # Desenhar arestas de associações (preto)
        for pessoa, empresa in edges_associacoes:
            if pessoa in node_positions and empresa in node_positions:
                x1, y1 = node_positions[pessoa]
                x2, y2 = node_positions[empresa]

                self.connections_canvas.create_line(
                    x1, y1, x2, y2,
                    fill='black',
                    width=2,
                    tags='edge_associacao'
                )

        # Desenhar nós
        for node_name, (x, y) in node_positions.items():
            node_tipo = nodes[node_name]['tipo']

            # Cores por tipo
            if node_tipo == 'pessoa':
                color = '#3498db'  # Azul
            elif node_tipo == 'empresa':
                color = '#2ecc71'  # Verde
            else:  # camara
                color = '#e74c3c'  # Vermelho

            # Círculo
            radius_node = 15
            self.connections_canvas.create_oval(
                x - radius_node, y - radius_node,
                x + radius_node, y + radius_node,
                fill=color,
                outline='black',
                width=2,
                tags='node'
            )

            # Texto (nome abreviado se muito longo)
            display_name = node_name[:30] + '...' if len(node_name) > 30 else node_name
            self.connections_canvas.create_text(
                x, y - 25,
                text=display_name,
                font=('Arial', 8),
                tags='node_label'
            )

    def zoom_in_grafo(self):
        """Aumenta o zoom do grafo"""
        self.grafo_zoom *= 1.2
        self.aplicar_zoom_grafo()

    def zoom_out_grafo(self):
        """Diminui o zoom do grafo"""
        self.grafo_zoom /= 1.2
        self.aplicar_zoom_grafo()

    def reset_zoom_grafo(self):
        """Reseta o zoom do grafo"""
        self.grafo_zoom = 1.0
        self.aplicar_zoom_grafo()

    def aplicar_zoom_grafo(self):
        """Aplica o zoom atual ao canvas"""
        self.connections_canvas.scale('all', 0, 0, self.grafo_zoom, self.grafo_zoom)

    # ==================== MÉTODOS AUXILIARES ====================

    def update_status(self, mensagem: str):
        """Atualiza a barra de status"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=mensagem)
            self.root.update()

    def on_closing(self):
        """Método chamado ao fechar a aplicação"""
        if messagebox.askokcancel("Sair", "Deseja sair da aplicação?"):
            self.db.close()
            self.root.destroy()


# ==================== FUNÇÃO PRINCIPAL ====================

def main():
    """Função principal para iniciar a aplicação"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )

    # Criar janela principal
    root = tk.Tk()

    # Iniciar aplicação
    app = ContratosPublicosGUI(root)

    # Loop principal
    root.mainloop()


if __name__ == "__main__":
    main()
