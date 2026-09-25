from database import conectar_banco
import tkinter as tk
from tkinter import messagebox, ttk
from utils import aplicar_mascara_valor


class AbaContasCartoes:

  def __init__(self, parent):
    self.parent = parent
    self.conta_selecionada_id = None
    self.cartao_selecionado_id = None

    # Container Principal Dividido em Esquerda (Formulários) e Direita (Tabelas)
    frame_esq = tk.Frame(parent, bg="#F0F0F0")
    frame_esq.pack(side="left", fill="y", padx=10, pady=10)

    frame_dir = tk.Frame(parent, bg="#F0F0F0")
    frame_dir.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # ==========================================
    # 1. SEÇÃO DE CONTAS (ESQUERDA - TOPO)
    # ==========================================
    form_contas = tk.LabelFrame(
        frame_esq,
        text=" Gerenciar Contas ",
        font=("Arial", 9, "bold"),
        bg="#F0F0F0",
        padx=10,
        pady=8,
    )
    form_contas.pack(fill="x", pady=(0, 10))

    tk.Label(
        form_contas, text="Instituição Bancária:", bg="#F0F0F0", font=("Arial", 8)
    ).pack(anchor="w", pady=(2, 0))
    self.txt_instituicao = tk.Entry(form_contas, width=32, font=("Arial", 9))
    self.txt_instituicao.pack(anchor="w", pady=(0, 4))

    tk.Label(
        form_contas, text="Saldo Inicial:", bg="#F0F0F0", font=("Arial", 8)
    ).pack(anchor="w", pady=(2, 0))
    self.var_saldo = tk.StringVar(value="0,00")
    self.var_saldo.trace_add(
        "write", lambda *args: aplicar_mascara_valor(None, self.var_saldo)
    )
    self.txt_saldo = tk.Entry(
        form_contas, textvariable=self.var_saldo, width=32, font=("Arial", 9)
    )
    self.txt_saldo.pack(anchor="w", pady=(0, 4))

    self.var_principal_conta = tk.BooleanVar(value=False)
    self.chk_principal_conta = tk.Checkbutton(
        form_contas,
        text="Conta Principal",
        variable=self.var_principal_conta,
        bg="#F0F0F0",
        font=("Arial", 8, "bold"),
    )
    self.chk_principal_conta.pack(anchor="w", pady=(0, 6))

    botoes_conta = tk.Frame(form_contas, bg="#F0F0F0")
    botoes_conta.pack(anchor="w", pady=(2, 0))

    self.btn_salvar_conta = tk.Button(
        botoes_conta,
        text="Cad. Conta",
        bg="#2B6CB0",
        fg="white",
        font=("Arial", 8, "bold"),
        width=9,
        command=self.salvar_ou_alterar_conta,
    )
    self.btn_salvar_conta.pack(side="left", padx=(0, 3))

    self.btn_excluir_conta = tk.Button(
        botoes_conta,
        text="Excluir",
        bg="#C53030",
        fg="white",
        font=("Arial", 8, "bold"),
        width=7,
        command=self.excluir_conta,
    )
    self.btn_excluir_conta.pack(side="left", padx=(0, 3))
    self.btn_excluir_conta.pack_forget()

    self.btn_limpar_conta = tk.Button(
        botoes_conta,
        text="Limpar",
        font=("Arial", 8),
        width=7,
        command=self.limpar_campos_conta,
    )
    self.btn_limpar_conta.pack(side="left")

    # ==========================================
    # 2. SEÇÃO DE CARTÕES (ESQUERDA - BAIXO)
    # ==========================================
    form_cartoes = tk.LabelFrame(
        frame_esq,
        text=" Gerenciar Cartões ",
        font=("Arial", 9, "bold"),
        bg="#F0F0F0",
        padx=10,
        pady=8,
    )
    form_cartoes.pack(fill="x")

    tk.Label(
        form_cartoes, text="Nome do Cartão:", bg="#F0F0F0", font=("Arial", 8)
    ).pack(anchor="w", pady=(2, 0))
    self.txt_nome_cartao = tk.Entry(form_cartoes, width=32, font=("Arial", 9))
    self.txt_nome_cartao.pack(anchor="w", pady=(0, 4))

    tk.Label(
        form_cartoes, text="Dia de Fechamento:", bg="#F0F0F0", font=("Arial", 8)
    ).pack(anchor="w", pady=(2, 0))
    self.txt_fechamento = tk.Entry(form_cartoes, width=32, font=("Arial", 9))
    self.txt_fechamento.pack(anchor="w", pady=(0, 4))

    tk.Label(
        form_cartoes, text="Dia de Vencimento:", bg="#F0F0F0", font=("Arial", 8)
    ).pack(anchor="w", pady=(2, 0))
    self.txt_vencimento = tk.Entry(form_cartoes, width=32, font=("Arial", 9))
    self.txt_vencimento.pack(anchor="w", pady=(0, 4))

    self.var_principal_cartao = tk.BooleanVar(value=False)
    self.chk_principal_cartao = tk.Checkbutton(
        form_cartoes,
        text="Cartão Principal",
        variable=self.var_principal_cartao,
        bg="#F0F0F0",
        font=("Arial", 8, "bold"),
    )
    self.chk_principal_cartao.pack(anchor="w", pady=(0, 6))

    botoes_cartao = tk.Frame(form_cartoes, bg="#F0F0F0")
    botoes_cartao.pack(anchor="w", pady=(2, 0))

    self.btn_salvar_cartao = tk.Button(
        botoes_cartao,
        text="Cad. Cartão",
        bg="#2B6CB0",
        fg="white",
        font=("Arial", 8, "bold"),
        width=9,
        command=self.salvar_ou_alterar_cartao,
    )
    self.btn_salvar_cartao.pack(side="left", padx=(0, 3))

    self.btn_excluir_cartao = tk.Button(
        botoes_cartao,
        text="Excluir",
        bg="#C53030",
        fg="white",
        font=("Arial", 8, "bold"),
        width=7,
        command=self.excluir_cartao,
    )
    self.btn_excluir_cartao.pack(side="left", padx=(0, 3))
    self.btn_excluir_cartao.pack_forget()

    self.btn_limpar_cartao = tk.Button(
        botoes_cartao,
        text="Limpar",
        font=("Arial", 8),
        width=7,
        command=self.limpar_campos_cartao,
    )
    self.btn_limpar_cartao.pack(side="left")

    # ==========================================
    # 3. TABELA DE CONTAS (DIREITA - TOPO)
    # ==========================================
    tk.Label(
        frame_dir,
        text="Contas Cadastradas",
        font=("Arial", 10, "bold"),
        bg="#F0F0F0",
    ).pack(anchor="w", pady=(0, 2))

    colunas_contas = ("Instituicao", "SaldoIni", "SaldoAt", "Principal")
    self.tabela_contas = ttk.Treeview(
        frame_dir, columns=colunas_contas, show="headings", height=8
    )
    self.tabela_contas.heading("Instituicao", text="Instituição")
    self.tabela_contas.heading("SaldoIni", text="Saldo Inicial")
    self.tabela_contas.heading("SaldoAt", text="Saldo Atual")
    self.tabela_contas.heading("Principal", text="Principal")

    self.tabela_contas.column("Instituicao", width=180, anchor="w")
    self.tabela_contas.column("SaldoIni", width=95, anchor="e")
    self.tabela_contas.column("SaldoAt", width=95, anchor="e")
    self.tabela_contas.column("Principal", width=70, anchor="center")
    self.tabela_contas.pack(fill="x", pady=(0, 10))
    self.tabela_contas.bind("<Double-1>", self.selecionar_conta)

    # ==========================================
    # 4. TABELA DE CARTÕES (DIREITA - BAIXO)
    # ==========================================
    tk.Label(
        frame_dir,
        text="Cartões Cadastrados",
        font=("Arial", 10, "bold"),
        bg="#F0F0F0",
    ).pack(anchor="w", pady=(0, 2))

    colunas_cartoes = ("Nome", "Fechamento", "Vencimento", "Principal")
    self.tabela_cartoes = ttk.Treeview(
        frame_dir, columns=colunas_cartoes, show="headings", height=8
    )
    for col in colunas_cartoes:
      self.tabela_cartoes.heading(col, text=col)

    self.tabela_cartoes.column("Nome", width=140, anchor="w")
    self.tabela_cartoes.column("Fechamento", width=85, anchor="center")
    self.tabela_cartoes.column("Vencimento", width=85, anchor="center")
    self.tabela_cartoes.column("Principal", width=70, anchor="center")
    self.tabela_cartoes.pack(fill="x")
    self.tabela_cartoes.bind("<Double-1>", self.selecionar_cartao)

    self.carregar_dados()

  # --- MÉTODOS DE CONTAS ---
  def limpar_campos_conta(self):
    self.conta_selecionada_id = None
    self.txt_instituicao.delete(0, tk.END)
    self.var_saldo.set("0,00")
    self.var_principal_conta.set(False)
    self.btn_salvar_conta.config(text="Cad. Conta", bg="#2B6CB0")
    self.btn_excluir_conta.pack_forget()

  def selecionar_conta(self, event):
    selecao = self.tabela_contas.selection()
    if not selecao:
      return
    valores = self.tabela_contas.item(selecao[0], "values")
    tags = self.tabela_contas.item(selecao[0], "tags")
    if tags:
      self.conta_selecionada_id = tags[0]
      is_principal = bool(int(tags[1]))
      self.txt_instituicao.delete(0, tk.END)
      self.txt_instituicao.insert(0, valores[0])
      self.var_saldo.set(valores[1].replace("R$ ", ""))
      self.var_principal_conta.set(is_principal)
      self.btn_salvar_conta.config(text="Salvar", bg="#D69E2E")
      self.btn_excluir_conta.pack(side="left", padx=(0, 3))

  def salvar_ou_alterar_conta(self):
    inst = self.txt_instituicao.get().strip()
    val_str = self.var_saldo.get().replace(".", "").replace(",", ".")
    is_principal = self.var_principal_conta.get()

    if not inst or not val_str:
      messagebox.showwarning("Aviso", "Preencha a instituição e o saldo inicial!")
      return

    try:
      saldo = float(val_str)
      conn = conectar_banco()
      cursor = conn.cursor()
      if is_principal:
        cursor.execute("UPDATE contas SET principal = FALSE;")

      if self.conta_selecionada_id:
        cursor.execute(
            "UPDATE contas SET instituicao = %s, saldo_inicial = %s, principal ="
            " %s WHERE id = %s;",
            (inst, saldo, is_principal, self.conta_selecionada_id),
        )
        msg = "Conta alterada com sucesso!"
      else:
        cursor.execute(
            "INSERT INTO contas (instituicao, saldo_inicial, saldo_atual,"
            " principal) VALUES (%s, %s, %s, %s);",
            (inst, saldo, saldo, is_principal),
        )
        msg = "Conta cadastrada com sucesso!"

      conn.commit()
      cursor.close()
      conn.close()
      messagebox.showinfo("Sucesso", msg)
      self.limpar_campos_conta()
      self.carregar_dados()
    except Exception as ex:
      messagebox.showerror("Erro", f"Erro ao salvar conta: {ex}")

  def excluir_conta(self):
    if not self.conta_selecionada_id:
      return
    if messagebox.askyesno(
        "Confirmar", "Tem certeza que deseja excluir esta conta?"
    ):
      try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM contas WHERE id = %s;", (self.conta_selecionada_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
        self.limpar_campos_conta()
        self.carregar_dados()
      except Exception as ex:
        messagebox.showerror("Erro", f"Erro ao excluir conta: {ex}")

  # --- MÉTODOS DE CARTÕES ---
  def limpar_campos_cartao(self):
    self.cartao_selecionado_id = None
    self.txt_nome_cartao.delete(0, tk.END)
    self.txt_fechamento.delete(0, tk.END)
    self.txt_vencimento.delete(0, tk.END)
    self.var_principal_cartao.set(False)
    self.btn_salvar_cartao.config(text="Cad. Cartão", bg="#2B6CB0")
    self.btn_excluir_cartao.pack_forget()

  def selecionar_cartao(self, event):
    selecao = self.tabela_cartoes.selection()
    if not selecao:
      return
    tags = self.tabela_cartoes.item(selecao[0], "tags")
    if not tags:
      return
    self.cartao_selecionado_id = tags[0]
    try:
      conn = conectar_banco()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT nome, dia_fechamento, dia_vencimento, principal FROM cartoes"
          " WHERE id = %s;",
          (self.cartao_selecionado_id,),
      )
      reg = cursor.fetchone()
      cursor.close()
      conn.close()
      if reg:
        nome, fech, venc, principal = reg
        self.txt_nome_cartao.delete(0, tk.END)
        self.txt_nome_cartao.insert(0, nome or "")
        self.txt_fechamento.delete(0, tk.END)
        self.txt_fechamento.insert(0, str(fech or ""))
        self.txt_vencimento.delete(0, tk.END)
        self.txt_vencimento.insert(0, str(venc or ""))
        self.var_principal_cartao.set(bool(principal))
        self.btn_salvar_cartao.config(text="Salvar", bg="#D69E2E")
        self.btn_excluir_cartao.pack(side="left", padx=(0, 3))
    except Exception as e:
      messagebox.showerror("Erro", f"Erro ao selecionar cartão: {e}")

  def salvar_ou_alterar_cartao(self):
    nome = self.txt_nome_cartao.get().strip()
    fech_str = self.txt_fechamento.get().strip()
    venc_str = self.txt_vencimento.get().strip()
    is_principal = self.var_principal_cartao.get()

    if not nome or not fech_str or not venc_str:
      messagebox.showwarning("Aviso", "Preencha todos os campos do cartão!")
      return

    try:
      fechamento = int(fech_str)
      vencimento = int(venc_str)
      conn = conectar_banco()
      cursor = conn.cursor()
      if is_principal:
        cursor.execute("UPDATE cartoes SET principal = FALSE;")

      if self.cartao_selecionado_id:
        cursor.execute(
            """
                    UPDATE cartoes 
                    SET nome = %s, dia_fechamento = %s, dia_vencimento = %s, principal = %s 
                    WHERE id = %s;
                """,
            (
                nome,
                fechamento,
                vencimento,
                is_principal,
                self.cartao_selecionado_id,
            ),
        )
        msg = "Cartão alterado com sucesso!"
      else:
        cursor.execute(
            """
                    INSERT INTO cartoes (nome, dia_fechamento, dia_vencimento, principal)
                    VALUES (%s, %s, %s, %s);
                """,
            (nome, fechamento, vencimento, is_principal),
        )
        msg = "Cartão cadastrado com sucesso!"

      conn.commit()
      cursor.close()
      conn.close()
      messagebox.showinfo("Sucesso", msg)
      self.limpar_campos_cartao()
      self.carregar_dados()
    except ValueError:
      messagebox.showwarning(
          "Aviso", "Fechamento e Vencimento devem ser números inteiros!"
      )
    except Exception as ex:
      messagebox.showerror("Erro", f"Erro ao salvar cartão: {ex}")

  def excluir_cartao(self):
    if not self.cartao_selecionado_id:
      return
    if messagebox.askyesno(
        "Confirmar", "Tem certeza que deseja excluir este cartão?"
    ):
      try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM cartoes WHERE id = %s;", (self.cartao_selecionado_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Sucesso", "Cartão excluído com sucesso!")
        self.limpar_campos_cartao()
        self.carregar_dados()
      except Exception as ex:
        messagebox.showerror("Erro", f"Erro ao excluir cartão: {ex}")

  def carregar_dados(self):
    # Carregar Contas
    for row in self.tabela_contas.get_children():
      self.tabela_contas.delete(row)
    try:
      conn = conectar_banco()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, instituicao, saldo_inicial, saldo_atual, principal FROM"
          " contas ORDER BY principal DESC, instituicao;"
      )
      dados_c = cursor.fetchall()
      for cid, inst, sini, sat, principal in dados_c:
        sini_str = (
            f"R$ {sini:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        sat_str = (
            f"R$ {sat:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
        princ_str = "Sim" if principal else ""
        self.tabela_contas.insert(
            "",
            "end",
            values=(inst, sini_str, sat_str, princ_str),
            tags=(str(cid), str(int(bool(principal)))),
        )

      # Carregar Cartões
      for row in self.tabela_cartoes.get_children():
        self.tabela_cartoes.delete(row)
      cursor.execute(
          "SELECT id, nome, dia_fechamento, dia_vencimento, principal FROM"
          " cartoes ORDER BY nome;"
      )
      dados_ct = cursor.fetchall()
      cursor.close()
      conn.close()

      for cid, nome, fech, venc, principal in dados_ct:
        principal_str = "Sim" if principal else "Não"
        self.tabela_cartoes.insert(
            "",
            "end",
            values=(nome, fech, venc, principal_str),
            tags=(str(cid),),
        )
    except Exception as e:
      print(f"Erro ao carregar dados unificados: {e}")

  def recarregar(self):
    self.carregar_dados()