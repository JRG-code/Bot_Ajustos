"""
Sistema de Autocomplete Contextual Inteligente
Fornece sugestões baseadas em contexto e histórico
"""

import tkinter as tk
from typing import List, Callable, Optional
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    """
    Entry com autocomplete contextual inteligente

    Mostra sugestões baseadas no que está sendo digitado,
    filtrando por contexto (não mistura partidos com empresas, por exemplo)
    """

    def __init__(self, parent, suggestions_callback: Callable[[], List[str]],
                 *args, **kwargs):
        """
        Inicializa Entry com autocomplete

        Args:
            parent: Widget pai
            suggestions_callback: Função que retorna lista de sugestões
            *args, **kwargs: Argumentos para ttk.Entry
        """
        super().__init__(parent, *args, **kwargs)

        self.suggestions_callback = suggestions_callback
        self.listbox = None
        self.listbox_window = None

        # Bind eventos
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusOut>', self._hide_listbox)
        self.bind('<Down>', self._on_arrow_down)
        self.bind('<Up>', self._on_arrow_up)
        self.bind('<Return>', self._on_return)
        self.bind('<Escape>', self._on_escape)

    def _on_key_release(self, event):
        """Atualiza sugestões quando usuário digita"""
        # Ignorar teclas especiais
        if event.keysym in ['Down', 'Up', 'Return', 'Escape', 'Left', 'Right',
                            'Home', 'End', 'Prior', 'Next', 'Tab']:
            return

        valor = self.get().strip()

        if len(valor) < 1:
            self._hide_listbox()
            return

        # Obter sugestões do callback
        todas_sugestoes = self.suggestions_callback()

        # Filtrar sugestões que começam com o valor digitado (case-insensitive)
        sugestoes_filtradas = [
            s for s in todas_sugestoes
            if s.lower().startswith(valor.lower())
        ]

        if sugestoes_filtradas:
            self._show_listbox(sugestoes_filtradas)
        else:
            self._hide_listbox()

    def _show_listbox(self, sugestoes: List[str]):
        """Mostra listbox com sugestões"""
        # Criar ou atualizar listbox
        if not self.listbox:
            self.listbox_window = tk.Toplevel(self.master)
            self.listbox_window.wm_overrideredirect(True)  # Sem borda de janela
            self.listbox_window.lift()

            # Frame para listbox e scrollbar
            frame = ttk.Frame(self.listbox_window)
            frame.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.listbox = tk.Listbox(
                frame,
                height=min(8, len(sugestoes)),
                yscrollcommand=scrollbar.set
            )
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.listbox.yview)

            # Bind eventos da listbox
            self.listbox.bind('<Button-1>', self._on_select)
            self.listbox.bind('<Return>', self._on_select)

        # Limpar e popular listbox
        self.listbox.delete(0, tk.END)
        for sugestao in sugestoes[:20]:  # Limitar a 20 sugestões
            self.listbox.insert(tk.END, sugestao)

        # Atualizar altura
        self.listbox.config(height=min(8, len(sugestoes)))

        # Posicionar listbox abaixo do Entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()

        self.listbox_window.geometry(f"{width}x{min(200, len(sugestoes) * 25)}+{x}+{y}")

        # Selecionar primeira sugestão
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def _hide_listbox(self, event=None):
        """Esconde listbox de sugestões"""
        if self.listbox_window:
            self.listbox_window.destroy()
            self.listbox_window = None
            self.listbox = None

    def _on_arrow_down(self, event):
        """Navegar para baixo na lista"""
        if self.listbox and self.listbox.size() > 0:
            current = self.listbox.curselection()
            if current:
                index = current[0]
                if index < self.listbox.size() - 1:
                    self.listbox.selection_clear(index)
                    self.listbox.selection_set(index + 1)
                    self.listbox.activate(index + 1)
                    self.listbox.see(index + 1)
            return 'break'

    def _on_arrow_up(self, event):
        """Navegar para cima na lista"""
        if self.listbox and self.listbox.size() > 0:
            current = self.listbox.curselection()
            if current:
                index = current[0]
                if index > 0:
                    self.listbox.selection_clear(index)
                    self.listbox.selection_set(index - 1)
                    self.listbox.activate(index - 1)
                    self.listbox.see(index - 1)
            return 'break'

    def _on_return(self, event):
        """Selecionar sugestão com Enter"""
        if self.listbox and self.listbox.curselection():
            self._on_select(event)
            return 'break'

    def _on_escape(self, event):
        """Fechar sugestões com Escape"""
        self._hide_listbox()
        return 'break'

    def _on_select(self, event):
        """Quando usuário seleciona uma sugestão"""
        if self.listbox and self.listbox.curselection():
            index = self.listbox.curselection()[0]
            valor = self.listbox.get(index)
            self.delete(0, tk.END)
            self.insert(0, valor)
            self._hide_listbox()
            self.focus_set()


class SuggestionsManager:
    """
    Gestor de sugestões contextuais
    Mantém histórico de valores por contexto
    """

    def __init__(self, db_manager):
        """
        Inicializa gestor de sugestões

        Args:
            db_manager: Instância do DatabaseManager
        """
        self.db = db_manager
        self._cache = {}

    def get_partidos(self) -> List[str]:
        """Retorna lista de partidos políticos portugueses e os já usados"""
        # Partidos principais em Portugal
        partidos_base = [
            'PS', 'PSD', 'Chega', 'IL', 'BE', 'CDU', 'PCP', 'CDS-PP',
            'Livre', 'PAN', 'Partido Socialista', 'Partido Social Democrata'
        ]

        # Buscar partidos já usados na BD
        partidos_usados = self._get_valores_unicos('partido')

        # Combinar e remover duplicados
        todos_partidos = list(set(partidos_base + partidos_usados))
        todos_partidos.sort()

        return todos_partidos

    def get_cargos(self) -> List[str]:
        """Retorna lista de cargos governamentais comuns e os já usados"""
        cargos_base = [
            'Presidente da República',
            'Primeiro-Ministro',
            'Ministro',
            'Secretário de Estado',
            'Deputado',
            'Presidente da Câmara',
            'Vereador',
            'Presidente da Junta de Freguesia',
            'Deputado Municipal',
            'Eurodeputado',
            'Governador Civil',
            'Diretor-Geral',
            'Secretário Regional',
            'Ex-Ministro',
            'Ex-Presidente da Câmara',
            'Ex-Deputado'
        ]

        # Buscar cargos já usados
        cargos_usados = self._get_valores_unicos('cargo_governamental')

        todos_cargos = list(set(cargos_base + cargos_usados))
        todos_cargos.sort()

        return todos_cargos

    def get_empresas(self) -> List[str]:
        """Retorna lista de empresas já registadas como figuras de interesse"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT nome
            FROM figuras_interesse
            WHERE tipo = 'empresa' AND ativo = 1
            ORDER BY nome
        """)

        empresas = [row[0] for row in cursor.fetchall()]
        return empresas

    def get_pessoas(self) -> List[str]:
        """Retorna lista de pessoas já registadas como figuras de interesse"""
        cursor = self.db.connection.cursor()
        cursor.execute("""
            SELECT DISTINCT nome
            FROM figuras_interesse
            WHERE tipo = 'pessoa' AND ativo = 1
            ORDER BY nome
        """)

        pessoas = [row[0] for row in cursor.fetchall()]
        return pessoas

    def _get_valores_unicos(self, campo: str) -> List[str]:
        """
        Busca valores únicos de um campo na tabela figuras_interesse

        Args:
            campo: Nome do campo

        Returns:
            Lista de valores únicos (não vazios)
        """
        cursor = self.db.connection.cursor()
        cursor.execute(f"""
            SELECT DISTINCT {campo}
            FROM figuras_interesse
            WHERE {campo} IS NOT NULL AND {campo} != ''
            ORDER BY {campo}
        """)

        valores = [row[0] for row in cursor.fetchall()]
        return valores

    def limpar_cache(self):
        """Limpa cache de sugestões"""
        self._cache = {}
