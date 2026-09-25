from database import (
    inicializar_banco_local,
    migrar_dados_para_nuvem,
    migrar_dados_da_nuvem,
    alternar_modo_banco,
)
from views.aba_categorias import AbaCategorias
from views.aba_contas_cartoes import AbaContasCartoes
from views.aba_despesas_cartao import AbaDespesasCartao
from views.aba_graficos import AbaGraficos
from views.aba_lancamentos import AbaLancamentos
from views.aba_resumo import AbaResumo
import tkinter as tk
from tkinter import ttk, messagebox


class ControleGastosApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Controle de Gastos e Finanças")

    inicializar_banco_local()
    alternar_modo_banco("local")

    self.root.state("zoomed")
    self.root.configure(bg="#F0F0F0")

    style = ttk.Style()
    style.theme_use("clam")

    # Cabeçalho superior
    frame_cabecalho = tk.Frame(root, bg="#F0F0F0")
    frame_cabecalho.pack(fill="x", padx=10, pady=10)

    lbl_titulo = tk.Label(
        frame_cabecalho,
        text="Controle Financeiro (Local)",
        font=("Arial", 18, "bold"),
        bg="#F0F0F0",
        fg="#1A365D",
    )
    lbl_titulo.pack(side="left")

    # Botão de Fechar Aplicação
    btn_fechar = tk.Button(
        frame_cabecalho,
        text="Fechar Aplicação",
        bg="#C53030",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=12,
        pady=5,
        command=self.root.destroy,
    )
    btn_fechar.pack(side="right")

    # Botão Migrar para a Nuvem
    btn_migrar_nuvem = tk.Button(
        frame_cabecalho,
        text="☁ Enviar p/ Nuvem",
        bg="#2B6CB0",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=10,
        pady=5,
        command=self.executar_migracao_para_nuvem,
    )
    btn_migrar_nuvem.pack(side="right", padx=5)

    # Botão Migrar da Nuvem para o Local
    btn_migrar_local = tk.Button(
        frame_cabecalho,
        text="📥 Baixar da Nuvem",
        bg="#2F855A",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=10,
        pady=5,
        command=self.executar_migracao_da_nuvem,
    )
    btn_migrar_local.pack(side="right", padx=5)

    # Sistema de Abas (Notebook)
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

    self.frame_resumo = ttk.Frame(self.notebook)
    self.frame_graficos = ttk.Frame(self.notebook)
    self.frame_contas_cartoes = ttk.Frame(self.notebook)
    self.frame_despesas_cartao = ttk.Frame(self.notebook)
    self.frame_categorias = ttk.Frame(self.notebook)
    self.frame_lancamentos = ttk.Frame(self.notebook)

    self.notebook.add(self.frame_resumo, text=" 📊 Resumo ")
    self.notebook.add(self.frame_graficos, text=" 📈 Gráficos ")
    self.notebook.add(self.frame_contas_cartoes, text="   Contas/Cartões   ")
    self.notebook.add(self.frame_despesas_cartao, text="   Despesas de Cartão   ")
    self.notebook.add(self.frame_categorias, text="   Categorias   ")
    self.notebook.add(self.frame_lancamentos, text="   Lançamentos   ")

    self.aba_resumo = AbaResumo(self.frame_resumo)
    self.aba_graficos = AbaGraficos(self.frame_graficos)
    self.aba_contas_cartoes = AbaContasCartoes(self.frame_contas_cartoes)
    self.aba_despesas_cartao = AbaDespesasCartao(self.frame_despesas_cartao)
    self.aba_categorias = AbaCategorias(self.frame_categorias)
    self.aba_lancamentos = AbaLancamentos(self.frame_lancamentos)

    self.notebook.bind("<<NotebookTabChanged>>", self.ao_trocar_aba)

  def executar_migracao_para_nuvem(self):
    if messagebox.askyesno(
        "Confirmar Envio",
        "Deseja enviar os dados do banco local para a nuvem (Supabase)?",
    ):
      migrar_dados_para_nuvem()

  def executar_migracao_da_nuvem(self):
    if messagebox.askyesno(
        "Confirmar Download",
        "Deseja baixar e importar os dados do Supabase para o seu banco local?",
    ):
      migrar_dados_da_nuvem()
      # Atualiza todas as abas ativas após o download
      for aba in [
          self.aba_resumo,
          self.aba_graficos,
          self.aba_contas_cartoes,
          self.aba_despesas_cartao,
          self.aba_categorias,
          self.aba_lancamentos,
      ]:
        if hasattr(aba, "recarregar"):
          aba.recarregar()

  def ao_trocar_aba(self, event):
    tab_selecionada = self.notebook.index(self.notebook.select())
    abas_map = {
        0: self.aba_resumo,
        1: self.aba_graficos,
        2: self.aba_contas_cartoes,
        3: self.aba_despesas_cartao,
        4: self.aba_categorias,
        5: self.aba_lancamentos,
    }
    aba_atual = abas_map.get(tab_selecionada)
    if aba_atual and hasattr(aba_atual, "recarregar"):
      aba_atual.recarregar()


if __name__ == "__main__":
  root = tk.Tk()
  app = ControleGastosApp(root)
  root.mainloop()