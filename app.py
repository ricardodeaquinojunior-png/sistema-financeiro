import tkinter as tk
from tkinter import ttk
from views.aba_resumo import AbaResumo
from views.aba_graficos import AbaGraficos
from views.aba_contas import AbaContas
from views.aba_cartoes import AbaCartoes
from views.aba_categorias import AbaCategorias
from views.aba_lancamentos import AbaLancamentos
from views.aba_despesas_cartao import AbaDespesasCartao

class ControleGastosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Gastos e Finanças")
        
        # Maximiza a janela para ocupar toda a tela do notebook (mantendo a barra de tarefas)
        self.root.state("zoomed")
        
        self.root.configure(bg="#F0F0F0")

        # Configurações gerais do estilo ttk
        style = ttk.Style()
        style.theme_use("clam")

        # Cabeçalho superior (Título + Botão Fechar alinhados na mesma linha)
        frame_cabecalho = tk.Frame(root, bg="#F0F0F0")
        frame_cabecalho.pack(fill="x", padx=10, pady=10)

        # Título principal à esquerda
        lbl_titulo = tk.Label(frame_cabecalho, text="Controle Financeiro", font=("Arial", 18, "bold"), bg="#F0F0F0", fg="#1A365D")
        lbl_titulo.pack(side="left")

        # Botão de Fechar Aplicação no canto superior direito
        btn_fechar = tk.Button(
            frame_cabecalho, 
            text="Fechar Aplicação", 
            bg="#C53030", 
            fg="white", 
            font=("Arial", 9, "bold"), 
            padx=12, 
            pady=5, 
            command=self.root.destroy
        )
        btn_fechar.pack(side="right")

        # Sistema de Abas (Notebook)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        # Instancia as abas
        self.frame_resumo = ttk.Frame(self.notebook)
        self.frame_graficos = ttk.Frame(self.notebook)
        self.frame_contas = ttk.Frame(self.notebook)
        self.frame_cartoes = ttk.Frame(self.notebook)
        self.frame_despesas_cartao = ttk.Frame(self.notebook)
        self.frame_categorias = ttk.Frame(self.notebook)
        self.frame_lancamentos = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_resumo, text=" 📊 Resumo ")
        self.notebook.add(self.frame_graficos, text=" 📈 Gráficos ")
        self.notebook.add(self.frame_contas, text="   Contas   ")
        self.notebook.add(self.frame_cartoes, text="   Cartões   ")
        self.notebook.add(self.frame_despesas_cartao, text="   Despesas de Cartão   ")
        self.notebook.add(self.frame_categorias, text="   Categorias   ")
        self.notebook.add(self.frame_lancamentos, text="   Lançamentos   ")

        # Constrói as views dentro de cada aba
        self.aba_resumo = AbaResumo(self.frame_resumo)
        self.aba_graficos = AbaGraficos(self.frame_graficos)
        self.aba_contas = AbaContas(self.frame_contas)
        self.aba_cartoes = AbaCartoes(self.frame_cartoes)
        self.aba_despesas_cartao = AbaDespesasCartao(self.frame_despesas_cartao)
        self.aba_categorias = AbaCategorias(self.frame_categorias)
        self.aba_lancamentos = AbaLancamentos(self.frame_lancamentos)

        # Evento ao trocar de aba (recarrega os dados automaticamente)
        self.notebook.bind("<<NotebookTabChanged>>", self.ao_trocar_aba)

    def ao_trocar_aba(self, event):
        tab_selecionada = self.notebook.index(self.notebook.select())
        
        # Mapeamento atualizado dos índices das abas com o método recarregar
        abas_map = {
            0: self.aba_resumo,
            1: self.aba_graficos,
            2: self.aba_contas,
            3: self.aba_cartoes,
            4: self.aba_despesas_cartao,
            5: self.aba_categorias,
            6: self.aba_lancamentos
        }
        
        aba_atual = abas_map.get(tab_selecionada)
        if aba_atual and hasattr(aba_atual, "recarregar"):
            aba_atual.recarregar()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControleGastosApp(root)
    root.mainloop()