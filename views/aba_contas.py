import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_banco
from utils import aplicar_mascara_valor

class AbaContas:
    def __init__(self, parent):
        self.parent = parent
        self.conta_selecionada_id = None

        # Container Principal Esquerda (Formulário) e Direita (Tabela)
        frame_form = tk.LabelFrame(parent, text=" Gerenciar Contas ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=15, pady=15)
        frame_form.pack(side="left", fill="y", padx=15, pady=15)

        tk.Label(frame_form, text="Instituição Bancária:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(5, 0))
        self.txt_instituicao = tk.Entry(frame_form, width=35, font=("Arial", 10))
        self.txt_instituicao.pack(anchor="w", pady=(0, 10))

        tk.Label(frame_form, text="Saldo Inicial:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(5, 0))
        self.var_saldo = tk.StringVar(value="0,00")
        self.var_saldo.trace_add("write", lambda *args: aplicar_mascara_valor(None, self.var_saldo))
        self.txt_saldo = tk.Entry(frame_form, textvariable=self.var_saldo, width=35, font=("Arial", 10))
        self.txt_saldo.pack(anchor="w", pady=(0, 10))

        # Checkbox Conta Principal
        self.var_principal = tk.BooleanVar(value=False)
        self.chk_principal = tk.Checkbutton(frame_form, text="Conta Principal", variable=self.var_principal, bg="#F0F0F0", font=("Arial", 9, "bold"))
        self.chk_principal.pack(anchor="w", pady=(0, 15))

        # Botões de Ação
        frame_botoes = tk.Frame(frame_form, bg="#F0F0F0")
        frame_botoes.pack(anchor="w", pady=5)

        self.btn_salvar = tk.Button(frame_botoes, text="Cadastrar", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), width=10, command=self.salvar_ou_alterar)
        self.btn_salvar.pack(side="left", padx=(0, 5))

        self.btn_excluir = tk.Button(frame_botoes, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), width=8, command=self.excluir_conta)
        self.btn_excluir.pack(side="left", padx=(0, 5))
        self.btn_excluir.pack_forget()

        self.btn_limpar = tk.Button(frame_botoes, text="Limpar", font=("Arial", 9), width=8, command=self.limpar_campos)
        self.btn_limpar.pack(side="left")

        # Tabela (Treeview) à Direita
        frame_tabela = tk.Frame(parent, bg="#F0F0F0")
        frame_tabela.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        tk.Label(frame_tabela, text="Contas Cadastradas", font=("Arial", 11, "bold"), bg="#F0F0F0").pack(anchor="w", pady=(0, 5))

        colunas = ("Instituicao", "SaldoIni", "SaldoAt", "Principal")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=18)
        self.tabela.heading("Instituicao", text="Instituição")
        self.tabela.heading("SaldoIni", text="Saldo Inicial")
        self.tabela.heading("SaldoAt", text="Saldo Atual")
        self.tabela.heading("Principal", text="Principal")

        self.tabela.column("Instituicao", width=220, anchor="w")
        self.tabela.column("SaldoIni", width=110, anchor="e")
        self.tabela.column("SaldoAt", width=110, anchor="e")
        self.tabela.column("Principal", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tabela.bind("<Double-1>", self.selecionar_registro)
        self.carregar_dados()

    def limpar_campos(self):
        self.conta_selecionada_id = None
        self.txt_instituicao.delete(0, tk.END)
        self.var_saldo.set("0,00")
        self.var_principal.set(False)
        self.btn_salvar.config(text="Cadastrar", bg="#2B6CB0")
        self.btn_excluir.pack_forget()
        self.txt_instituicao.focus()

    def carregar_dados(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT id, instituicao, saldo_inicial, saldo_atual, principal FROM contas ORDER BY principal DESC, instituicao;")
            dados = cursor.fetchall()
            cursor.close()
            conn.close()

            for item in dados:
                cid, inst, sini, sat, principal = item
                sini_str = f"R$ {sini:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                sat_str = f"R$ {sat:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                princ_str = "Sim" if principal else ""
                self.tabela.insert("", "end", values=(inst, sini_str, sat_str, princ_str), tags=(str(cid), str(int(bool(principal)))))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar contas: {e}")

    def selecionar_registro(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        item_id = selecao[0]
        valores = self.tabela.item(item_id, "values")
        tags = self.tabela.item(item_id, "tags")
        
        if tags:
            self.conta_selecionada_id = tags[0]
            is_principal = bool(int(tags[1]))
            self.txt_instituicao.delete(0, tk.END)
            self.txt_instituicao.insert(0, valores[0])
            self.var_saldo.set(valores[1].replace("R$ ", ""))
            self.var_principal.set(is_principal)
            self.btn_salvar.config(text="Salvar", bg="#D69E2E")
            self.btn_excluir.pack(side="left", padx=(0, 5))

    def salvar_ou_alterar(self):
        inst = self.txt_instituicao.get().strip()
        val_str = self.var_saldo.get().replace(".", "").replace(",", ".")
        is_principal = self.var_principal.get()

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
                    "UPDATE contas SET instituicao = %s, saldo_inicial = %s, principal = %s WHERE id = %s;", 
                    (inst, saldo, is_principal, self.conta_selecionada_id)
                )
                msg = "Conta alterada com sucesso!"
            else:
                cursor.execute(
                    "INSERT INTO contas (instituicao, saldo_inicial, saldo_atual, principal) VALUES (%s, %s, %s, %s);", 
                    (inst, saldo, saldo, is_principal)
                )
                msg = "Conta cadastrada com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_dados()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar: {ex}")

    def excluir_conta(self):
        if not self.conta_selecionada_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta conta?"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM contas WHERE id = %s;", (self.conta_selecionada_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir: {ex}")

    def recarregar(self):
        self.carregar_dados()