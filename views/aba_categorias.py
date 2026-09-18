import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_banco

class AbaCategorias:
    def __init__(self, parent):
        self.parent = parent
        self.categoria_selecionada_id = None
        self.subcategoria_selecionada_id = None

        # --- PAINEL ESQUERDO: CATEGORIAS ---
        frame_cat_form = tk.LabelFrame(parent, text=" Gerenciar Categorias ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=10, pady=10)
        frame_cat_form.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(frame_cat_form, text="Nome da Categoria:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_cat_nome = tk.Entry(frame_cat_form, width=28, font=("Arial", 10))
        self.txt_cat_nome.pack(anchor="w", pady=(0, 6))

        # Botões Categoria
        botoes_cat = tk.Frame(frame_cat_form, bg="#F0F0F0")
        botoes_cat.pack(anchor="w", pady=(0, 10))

        self.btn_cat_salvar = tk.Button(botoes_cat, text="Cadastrar", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), width=8, command=self.salvar_categoria)
        self.btn_cat_salvar.pack(side="left", padx=(0, 4))

        self.btn_cat_excluir = tk.Button(botoes_cat, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), width=7, command=self.excluir_categoria)
        self.btn_cat_excluir.pack(side="left", padx=(0, 4))
        self.btn_cat_excluir.pack_forget()

        self.btn_cat_limpar = tk.Button(botoes_cat, text="Limpar", font=("Arial", 9), width=7, command=self.limpar_cat)
        self.btn_cat_limpar.pack(side="left")

        # Tabela Categorias
        col_cat = ("Categoria",)
        self.tabela_cat = ttk.Treeview(frame_cat_form, columns=col_cat, show="headings", height=14)
        self.tabela_cat.heading("Categoria", text="Categorias Cadastradas")
        self.tabela_cat.column("Categoria", width=210, anchor="w")
        self.tabela_cat.pack(side="top", fill="both", expand=True, pady=(5, 0))
        
        # Eventos para selecionar/filtrar ao navegar com teclado ou mouse
        self.tabela_cat.bind("<Double-1>", self.selecionar_categoria)
        self.tabela_cat.bind("<<TreeviewSelect>>", self.ao_selecionar_linha_categoria)

        # --- PAINEL DIREITO: SUBCATEGORIAS ---
        frame_sub_form = tk.LabelFrame(parent, text=" Gerenciar Subcategorias ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=10, pady=10)
        frame_sub_form.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_sub_form, text="Categoria Pai:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.cb_cat_pai = ttk.Combobox(frame_sub_form, width=32, state="readonly")
        self.cb_cat_pai.pack(anchor="w", pady=(0, 6))

        tk.Label(frame_sub_form, text="Nome da Subcategoria:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_sub_nome = tk.Entry(frame_sub_form, width=34, font=("Arial", 10))
        self.txt_sub_nome.pack(anchor="w", pady=(0, 6))

        # Botões Subcategoria
        botoes_sub = tk.Frame(frame_sub_form, bg="#F0F0F0")
        botoes_sub.pack(anchor="w", pady=(0, 10))

        self.btn_sub_salvar = tk.Button(botoes_sub, text="Cadastrar", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), width=9, command=self.salvar_subcategoria)
        self.btn_sub_salvar.pack(side="left", padx=(0, 4))

        self.btn_sub_excluir = tk.Button(botoes_sub, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), width=8, command=self.excluir_subcategoria)
        self.btn_sub_excluir.pack(side="left", padx=(0, 4))
        self.btn_sub_excluir.pack_forget()

        self.btn_sub_limpar = tk.Button(botoes_sub, text="Limpar", font=("Arial", 9), width=8, command=self.limpar_sub)
        self.btn_sub_limpar.pack(side="left")

        # Tabela Subcategorias (Colunas invertidas: Categoria Pai primeiro)
        col_sub = ("Categoria Pai", "Subcategoria")
        self.tabela_sub = ttk.Treeview(frame_sub_form, columns=col_sub, show="headings", height=12)
        self.tabela_sub.heading("Categoria Pai", text="Categoria Pai")
        self.tabela_sub.heading("Subcategoria", text="Subcategoria")
        self.tabela_sub.column("Categoria Pai", width=180, anchor="w")
        self.tabela_sub.column("Subcategoria", width=180, anchor="w")
        self.tabela_sub.pack(side="top", fill="both", expand=True, pady=(5, 0))
        
        self.tabela_sub.bind("<Double-1>", self.selecionar_subcategoria)

        self.map_cat = {}
        self.map_cat_rev = {}

        self.carregar_dados()

    def carregar_dados(self):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            # Carrega Categorias
            cursor.execute("SELECT id_categoria, descricao FROM categorias ORDER BY descricao;")
            cats = cursor.fetchall()
            self.map_cat.clear()
            self.map_cat_rev.clear()
            lista_cats = []

            for cid, cdesc in cats:
                self.map_cat[cdesc] = str(cid)
                self.map_cat_rev[str(cid)] = cdesc
                lista_cats.append(cdesc)

            self.cb_cat_pai['values'] = lista_cats

            cursor.close()
            conn.close()

            self.popular_tabela_categorias(cats)
            self.carregar_subcategorias()
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")

    def popular_tabela_categorias(self, cats):
        for row in self.tabela_cat.get_children():
            self.tabela_cat.delete(row)
        for cid, cdesc in cats:
            self.tabela_cat.insert("", "end", values=(cdesc,), tags=(str(cid),))

    def carregar_subcategorias(self, id_categoria_filtro=None):
        for row in self.tabela_sub.get_children():
            self.tabela_sub.delete(row)

        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            if id_categoria_filtro:
                cursor.execute("""
                    SELECT s.id_subcategoria, s.descricao, c.descricao, s.id_categoria
                    FROM subcategorias s
                    JOIN categorias c ON s.id_categoria = c.id_categoria
                    WHERE s.id_categoria = %s
                    ORDER BY s.descricao;
                """, (id_categoria_filtro,))
            else:
                cursor.execute("""
                    SELECT s.id_subcategoria, s.descricao, c.descricao, s.id_categoria
                    FROM subcategorias s
                    JOIN categorias c ON s.id_categoria = c.id_categoria
                    ORDER BY s.descricao;
                """)

            subs = cursor.fetchall()
            for sid, sdesc, cdesc, cid in subs:
                # Ordem invertida nos values: cdesc (Categoria Pai) primeiro, sdesc (Subcategoria) depois
                self.tabela_sub.insert("", "end", values=(cdesc, sdesc), tags=(str(sid), str(cid)))

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar subcategorias: {e}")

    def ao_selecionar_linha_categoria(self, event):
        """Filtra as subcategorias automaticamente ao navegar pelas categorias com o mouse ou teclado."""
        selecao = self.tabela_cat.selection()
        if not selecao:
            self.carregar_subcategorias()
            return
        
        item_id = selecao[0]
        tags = self.tabela_cat.item(item_id, "tags")
        if not tags:
            return

        id_cat = tags[0]
        self.carregar_subcategorias(id_categoria_filtro=id_cat)

    def limpar_cat(self):
        self.categoria_selecionada_id = None
        self.txt_cat_nome.delete(0, tk.END)
        self.btn_cat_salvar.config(text="Cadastrar", bg="#2B6CB0")
        self.btn_cat_excluir.pack_forget()
        self.txt_cat_nome.focus_set()
        self.carregar_subcategorias() # Restaura todas as subcategorias ao limpar seleção

    def limpar_sub(self):
        self.subcategoria_selecionada_id = None
        self.cb_cat_pai.set("")
        self.txt_sub_nome.delete(0, tk.END)
        self.btn_sub_salvar.config(text="Cadastrar", bg="#2B6CB0")
        self.btn_sub_excluir.pack_forget()

    def selecionar_categoria(self, event):
        selecao = self.tabela_cat.selection()
        if not selecao:
            return
        item_id = selecao[0]
        tags = self.tabela_cat.item(item_id, "tags")
        if not tags:
            return

        self.categoria_selecionada_id = tags[0]
        
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT descricao FROM categorias WHERE id_categoria = %s;", (self.categoria_selecionada_id,))
            reg = cursor.fetchone()
            cursor.close()
            conn.close()

            if reg:
                self.txt_cat_nome.delete(0, tk.END)
                self.txt_cat_nome.insert(0, reg[0])
                self.btn_cat_salvar.config(text="Salvar", bg="#D69E2E")
                self.btn_cat_excluir.pack(side="left", padx=(0, 4))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar categoria: {e}")

    def selecionar_subcategoria(self, event):
        selecao = self.tabela_sub.selection()
        if not selecao:
            return
        item_id = selecao[0]
        tags = self.tabela_sub.item(item_id, "tags")
        if not tags:
            return

        self.subcategoria_selecionada_id = tags[0]
        id_cat_pai = tags[1]

        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT descricao FROM subcategorias WHERE id_subcategoria = %s;", (self.subcategoria_selecionada_id,))
            reg = cursor.fetchone()
            cursor.close()
            conn.close()

            if reg:
                self.txt_sub_nome.delete(0, tk.END)
                self.txt_sub_nome.insert(0, reg[0])
                
                nome_pai = self.map_cat_rev.get(str(id_cat_pai), "")
                self.cb_cat_pai.set(nome_pai)

                self.btn_sub_salvar.config(text="Salvar", bg="#D69E2E")
                self.btn_sub_excluir.pack(side="left", padx=(0, 4))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar subcategoria: {e}")

    def salvar_categoria(self):
        nome = self.txt_cat_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite o nome da categoria!")
            return

        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            if self.categoria_selecionada_id:
                cursor.execute("UPDATE categorias SET descricao = %s WHERE id_categoria = %s;", (nome, self.categoria_selecionada_id))
                msg = "Categoria alterada com sucesso!"
            else:
                cursor.execute("INSERT INTO categorias (descricao) VALUES (%s);", (nome,))
                msg = "Categoria cadastrada com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_cat()
            self.carregar_dados()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar categoria: {ex}")

    def excluir_categoria(self):
        if not self.categoria_selecionada_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta categoria? (Subcategorias associadas também podem ser afetadas)"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categorias WHERE id_categoria = %s;", (self.categoria_selecionada_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!")
                self.limpar_cat()
                self.carregar_dados()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir categoria: {ex}")

    def salvar_subcategoria(self):
        cat_pai_nome = self.cb_cat_pai.get()
        sub_nome = self.txt_sub_nome.get().strip()

        if not cat_pai_nome or not sub_nome:
            messagebox.showwarning("Aviso", "Selecione a categoria pai e informe o nome da subcategoria!")
            return

        try:
            id_cat = self.map_cat.get(cat_pai_nome)
            conn = conectar_banco()
            cursor = conn.cursor()

            if self.subcategoria_selecionada_id:
                cursor.execute("""
                    UPDATE subcategorias 
                    SET descricao = %s, id_categoria = %s 
                    WHERE id_subcategoria = %s;
                """, (sub_nome, id_cat, self.subcategoria_selecionada_id))
                msg = "Subcategoria alterada com sucesso!"
            else:
                cursor.execute("""
                    INSERT INTO subcategorias (descricao, id_categoria) 
                    VALUES (%s, %s);
                """, (sub_nome, id_cat))
                msg = "Subcategoria cadastrada com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_sub()
            self.carregar_dados()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar subcategoria: {ex}")

    def excluir_subcategoria(self):
        if not self.subcategoria_selecionada_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta subcategoria?"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM subcategorias WHERE id_subcategoria = %s;", (self.subcategoria_selecionada_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Subcategoria excluída com sucesso!")
                self.limpar_sub()
                self.carregar_dados()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir subcategoria: {ex}")

    def recarregar(self):
        self.carregar_dados()