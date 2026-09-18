import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_banco

class AbaCartoes:
    def __init__(self, parent):
        self.parent = parent
        self.cartao_selecionado_id = None

        # Formulário (Esquerda)
        frame_form = tk.LabelFrame(parent, text=" Gerenciar Cartões ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=12, pady=12)
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        # Nome
        tk.Label(frame_form, text="Nome do Cartão:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_nome = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_nome.pack(anchor="w", pady=(0, 6))

        # Dia de Fechamento
        tk.Label(frame_form, text="Dia de Fechamento:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_fechamento = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_fechamento.pack(anchor="w", pady=(0, 6))

        # Dia de Vencimento
        tk.Label(frame_form, text="Dia de Vencimento:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_vencimento = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_vencimento.pack(anchor="w", pady=(0, 6))

        # Checkbox Cartão Principal
        self.var_principal = tk.BooleanVar(value=False)
        self.chk_principal = tk.Checkbutton(frame_form, text="Cartão Principal", variable=self.var_principal, bg="#F0F0F0", font=("Arial", 9, "bold"))
        self.chk_principal.pack(anchor="w", pady=(2, 12))

        # Botões de Ação
        frame_botoes = tk.Frame(frame_form, bg="#F0F0F0")
        frame_botoes.pack(anchor="w")

        self.btn_salvar = tk.Button(frame_botoes, text="Cadastrar", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), width=9, command=self.salvar_ou_alterar)
        self.btn_salvar.pack(side="left", padx=(0, 4))

        self.btn_excluir = tk.Button(frame_botoes, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), width=8, command=self.excluir_cartao)
        self.btn_excluir.pack(side="left", padx=(0, 4))
        self.btn_excluir.pack_forget()

        self.btn_limpar = tk.Button(frame_botoes, text="Limpar", font=("Arial", 9), width=8, command=self.limpar_campos)
        self.btn_limpar.pack(side="left")

        # Painel Direito (Tabela)
        frame_direito = tk.Frame(parent, bg="#F0F0F0")
        frame_direito.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_direito, text="Cartões Cadastrados", font=("Arial", 11, "bold"), bg="#F0F0F0").pack(anchor="w", pady=(0, 5))

        colunas = ("Nome", "Fechamento", "Vencimento", "Principal")
        self.tabela = ttk.Treeview(frame_direito, columns=colunas, show="headings", height=18)
        
        for col in colunas:
            self.tabela.heading(col, text=col)

        self.tabela.column("Nome", width=160, anchor="w")
        self.tabela.column("Fechamento", width=100, anchor="center")
        self.tabela.column("Vencimento", width=100, anchor="center")
        self.tabela.column("Principal", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(frame_direito, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tabela.bind("<Double-1>", self.selecionar_registro)

        self.carregar_dados()

    def carregar_dados(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, dia_fechamento, dia_vencimento, principal FROM cartoes ORDER BY nome;")
            dados = cursor.fetchall()
            cursor.close()
            conn.close()

            for cid, nome, fech, venc, principal in dados:
                principal_str = "Sim" if principal else "Não"
                self.tabela.insert("", "end", values=(nome, fech, venc, principal_str), tags=(str(cid),))
        except Exception as e:
            print(f"Erro ao carregar cartões: {e}")

    def limpar_campos(self):
        self.cartao_selecionado_id = None
        self.txt_nome.delete(0, tk.END)
        self.txt_fechamento.delete(0, tk.END)
        self.txt_vencimento.delete(0, tk.END)
        self.var_principal.set(False)
        self.btn_salvar.config(text="Cadastrar", bg="#2B6CB0")
        self.btn_excluir.pack_forget()
        self.txt_nome.focus_set()

    def selecionar_registro(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        item_id = selecao[0]
        tags = self.tabela.item(item_id, "tags")
        if not tags:
            return

        self.cartao_selecionado_id = tags[0]

        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, dia_fechamento, dia_vencimento, principal FROM cartoes WHERE id = %s;", (self.cartao_selecionado_id,))
            reg = cursor.fetchone()
            cursor.close()
            conn.close()

            if reg:
                nome, fech, venc, principal = reg
                self.txt_nome.delete(0, tk.END)
                self.txt_nome.insert(0, nome or "")
                self.txt_fechamento.delete(0, tk.END)
                self.txt_fechamento.insert(0, str(fech or ""))
                self.txt_vencimento.delete(0, tk.END)
                self.txt_vencimento.insert(0, str(venc or ""))
                self.var_principal.set(bool(principal))

                self.btn_salvar.config(text="Salvar", bg="#D69E2E")
                self.btn_excluir.pack(side="left", padx=(0, 4))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar cartão: {e}")

    def salvar_ou_alterar(self):
        nome = self.txt_nome.get().strip()
        fech_str = self.txt_fechamento.get().strip()
        venc_str = self.txt_vencimento.get().strip()
        is_principal = self.var_principal.get()

        if not nome or not fech_str or not venc_str:
            messagebox.showwarning("Aviso", "Preencha todos os campos do cartão!")
            return

        try:
            fechamento = int(fech_str)
            vencimento = int(venc_str)

            conn = conectar_banco()
            cursor = conn.cursor()

            # Se este cartão for marcado como principal, remove o status de principal dos outros
            if is_principal:
                cursor.execute("UPDATE cartoes SET principal = FALSE;")

            if self.cartao_selecionado_id:
                cursor.execute("""
                    UPDATE cartoes 
                    SET nome = %s, dia_fechamento = %s, dia_vencimento = %s, principal = %s 
                    WHERE id = %s;
                """, (nome, fechamento, vencimento, is_principal, self.cartao_selecionado_id))
                msg = "Cartão alterado com sucesso!"
            else:
                cursor.execute("""
                    INSERT INTO cartoes (nome, dia_fechamento, dia_vencimento, principal)
                    VALUES (%s, %s, %s, %s);
                """, (nome, fechamento, vencimento, is_principal))
                msg = "Cartão cadastrado com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_dados()
        except ValueError:
            messagebox.showwarning("Aviso", "Os dias de fechamento e vencimento devem ser números inteiros!")
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar cartão: {ex}")

    def excluir_cartao(self):
        if not self.cartao_selecionado_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cartão?"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cartoes WHERE id = %s;", (self.cartao_selecionado_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Cartão excluído com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir cartão: {ex}")

    def recarregar(self):
        self.carregar_dados()