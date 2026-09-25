from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar_banco
from utils import aplicar_mascara_data, is_data_valida

class AbaDespesasCartao:
    def __init__(self, parent):
        self.parent = parent
        self.despesa_selecionada_id = None
        self.filtro_status_valor = "Ambos"
        
        self.coluna_ordenacao = "l.data_lancamento"
        self.ordem_ascendente = True  # Padrão ordenado da mais antiga/recente por data

        # Formulário (Esquerda)
        frame_form = tk.LabelFrame(parent, text=" Despesa no Cartão ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=12, pady=12)
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        # Cartão
        tk.Label(frame_form, text="Cartão de Crédito:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.cb_cartao = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_cartao.pack(anchor="w", pady=(0, 6))
        self.cb_cartao.bind("<<ComboboxSelected>>", lambda e: self.carregar_dados())

        # Valor (Digitação livre e formatação em tempo real)
        tk.Label(frame_form, text="Valor da Despesa:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.var_valor = tk.StringVar(value="0,00")
        self.txt_valor = tk.Entry(frame_form, textvariable=self.var_valor, width=32, font=("Arial", 10))
        self.txt_valor.pack(anchor="w", pady=(0, 6))
        self.txt_valor.bind("<FocusIn>", self.ao_focar_valor)
        self.txt_valor.bind("<KeyRelease>", self.ao_digitar_valor)
        self.txt_valor.bind("<FocusOut>", self.formatar_ao_sair_valor)
        self.txt_valor.bind("<Return>", self.ao_pressionar_enter_valor)

        # Checkbox Parcelado
        self.var_parcelado = tk.BooleanVar(value=False)
        self.chk_parcelado = tk.Checkbutton(frame_form, text="Parcelado", variable=self.var_parcelado, bg="#F0F0F0", font=("Arial", 9, "bold"), command=self.alternar_parcelamento)
        self.chk_parcelado.pack(anchor="w", pady=(2, 4))

        # Combobox de Opções de Parcelas (2x até 12x)
        self.lbl_qtd_parcelas = tk.Label(frame_form, text="Número de vezes:", bg="#F0F0F0", font=("Arial", 9))
        self.cb_parcelas = ttk.Combobox(frame_form, width=30, state="readonly")

        # Data da Compra
        tk.Label(frame_form, text="Data da Compra (DD/MM/AAAA):", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.var_data = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.var_data.trace_add("write", lambda *args: aplicar_mascara_data(None, self.var_data))
        self.txt_data = tk.Entry(frame_form, textvariable=self.var_data, width=32, font=("Arial", 10))
        self.txt_data.pack(anchor="w", pady=(0, 6))

        # Descrição
        tk.Label(frame_form, text="Descrição:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_desc = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_desc.pack(anchor="w", pady=(0, 6))

        # Categoria
        tk.Label(frame_form, text="Categoria:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.cb_cat = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_cat.pack(anchor="w", pady=(0, 6))
        self.cb_cat.bind("<<ComboboxSelected>>", self.ao_mudar_categoria)

        # Subcategoria
        tk.Label(frame_form, text="Subcategoria:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.cb_sub = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_sub.pack(anchor="w", pady=(0, 6))

        # Repetir (Qtd de vezes)
        tk.Label(frame_form, text="Repetir (Qtd de vezes):", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_repetir = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_repetir.insert(0, "1")
        self.txt_repetir.pack(anchor="w", pady=(0, 12))

        # Botões de Ação Principais
        frame_botoes = tk.Frame(frame_form, bg="#F0F0F0")
        frame_botoes.pack(anchor="w", pady=(0, 6))

        self.btn_salvar = tk.Button(frame_botoes, text="Cadastrar Despesa", bg="#C53030", fg="white", font=("Arial", 9, "bold"), command=self.salvar_ou_alterar)
        self.btn_salvar.pack(side="left", padx=(0, 4))

        self.btn_excluir = tk.Button(frame_botoes, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), command=self.excluir_despesa)
        self.btn_excluir.pack(side="left", padx=(0, 4))
        self.btn_excluir.pack_forget()

        self.btn_limpar = tk.Button(frame_botoes, text="Limpar", font=("Arial", 9), command=self.limpar_campos)
        self.btn_limpar.pack(side="left")

        # Botão Especial para Quitar Fatura do Período
        self.btn_pagar_fatura = tk.Button(frame_form, text="Pagar Fatura do Cartão Selecionado", bg="#2F855A", fg="white", font=("Arial", 9, "bold"), width=32, command=self.pagar_fatura_periodo)
        self.btn_pagar_fatura.pack(anchor="w", pady=5)

        widgets_enter = [self.cb_cartao, self.chk_parcelado, self.cb_parcelas, self.txt_data, self.txt_desc, self.cb_cat, self.cb_sub, self.txt_repetir]
        for widget in widgets_enter:
            widget.bind("<Return>", lambda e, w=widget: self.pular_proximo_campo(w))

        # Painel Direito (Tabela com Barra de Rolagem e Filtros)
        frame_direito = tk.Frame(parent, bg="#F0F0F0")
        frame_direito.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        header_tabela = tk.Frame(frame_direito, bg="#F0F0F0")
        header_tabela.pack(fill="x", pady=(0, 5))
        tk.Label(header_tabela, text="Lançamentos no Cartão de Crédito", font=("Arial", 11, "bold"), bg="#F0F0F0").pack(side="left")

        # Filtros de Status
        self.var_filtro = tk.StringVar(value="Ambos")
        tk.Radiobutton(header_tabela, text="Ambos", variable=self.var_filtro, value="Ambos", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right")
        tk.Radiobutton(header_tabela, text="Pago", variable=self.var_filtro, value="Pago", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right", padx=10)
        tk.Radiobutton(header_tabela, text="Pendente", variable=self.var_filtro, value="Pendente", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right")

        # Container exclusivo para a Tabela e sua Barra de Rolagem
        frame_tabela_container = tk.Frame(frame_direito, bg="#F0F0F0")
        frame_tabela_container.pack(side="top", fill="both", expand=True, pady=(0, 5))

        colunas = ("Data", "Cartao", "Descricao", "Categoria", "Subcategoria", "Valor", "Status")
        self.tabela = ttk.Treeview(frame_tabela_container, columns=colunas, show="headings", height=16)
        
        self.tabela.tag_configure("tag_despesa_pendente", foreground="#C53030", font=("Arial", 9))
        self.tabela.tag_configure("tag_despesa_pago", foreground="#2F855A", font=("Arial", 9))
        self.tabela.tag_configure("tag_separador_fatura", background="#E2E8F0", font=("Arial", 9, "bold"), foreground="#1A365D")

        self.colunas_sql_map = {
            "Data": "l.data_lancamento",
            "Cartao": "ct.nome",
            "Descricao": "l.descricao",
            "Categoria": "c.descricao",
            "Subcategoria": "s.descricao",
            "Valor": "l.valor",
            "Status": "l.recebido"
        }

        for col in colunas:
            self.tabela.heading(col, text=col, command=lambda c=col: self.ordenar_por_coluna(c))

        self.tabela.column("Data", width=95, anchor="center")
        self.tabela.column("Cartao", width=110, anchor="w")
        self.tabela.column("Descricao", width=160, anchor="w")
        self.tabela.column("Categoria", width=100, anchor="w")
        self.tabela.column("Subcategoria", width=100, anchor="w")
        self.tabela.column("Valor", width=90, anchor="e")
        self.tabela.column("Status", width=75, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela_container, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tabela.bind("<Double-1>", self.selecionar_registro)

        # Painel de Total da Fatura / Exibição
        frame_total = tk.Frame(frame_direito, bg="white", bd=1, relief="solid", padx=10, pady=8)
        frame_total.pack(fill="x", pady=(5, 0))

        self.lbl_total_fatura = tk.Label(frame_total, text="R$ 0,00", font=("Arial", 11, "bold"), fg="#C53030", bg="white")
        tk.Label(frame_total, text="Valor Total (Filtrado / Exibido):", font=("Arial", 8, "bold"), fg="#718096", bg="white").pack(anchor="w")
        self.lbl_total_fatura.pack(anchor="w")

        self.map_cartao = {}
        self.map_cat = {}
        self.map_sub = {}

        self.carregar_combos()
        self.carregar_dados()
        self.atualizar_opcoes_parcelas()

    def ao_focar_valor(self, event=None):
        if self.var_valor.get() == "0,00":
            self.var_valor.set("")

    def ao_digitar_valor(self, event=None):
        texto = self.var_valor.get()
        if not texto:
            return
        digitos = "".join(filter(str.isdigit, texto))
        if not digitos:
            self.var_valor.set("")
            return
        val = float(digitos) / 100.0
        val_str = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.var_valor.set(val_str)
        try:
            self.txt_valor.icursor(tk.END)
        except Exception:
            pass
        self.atualizar_opcoes_parcelas()

    def formatar_ao_sair_valor(self, event=None):
        texto = self.var_valor.get().strip()
        if not texto:
            self.var_valor.set("0,00")
            self.atualizar_opcoes_parcelas()
            return
        limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            val = float(limpo)
            val_str = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.var_valor.set(val_str)
        except ValueError:
            self.var_valor.set("0,00")
        self.atualizar_opcoes_parcelas()

    def ao_pressionar_enter_valor(self, event=None):
        self.formatar_ao_sair_valor()
        if self.var_parcelado.get():
            self.cb_parcelas.focus_set()
        else:
            self.txt_data.focus_set()

    def pular_proximo_campo(self, widget_atual):
        widgets_sequencia = [
            self.cb_cartao, self.txt_valor, self.chk_parcelado, self.cb_parcelas, 
            self.txt_data, self.txt_desc, self.cb_cat, self.cb_sub, 
            self.txt_repetir, self.btn_salvar
        ]
        try:
            idx = widgets_sequencia.index(widget_atual)
            proximo = widgets_sequencia[idx + 1]
            if proximo == self.cb_parcelas and not self.var_parcelado.get():
                proximo = self.txt_data
            proximo.focus_set()
        except Exception:
            pass

    def ordenar_por_coluna(self, coluna):
        coluna_sql = self.colunas_sql_map.get(coluna, "l.data_lancamento")
        if self.coluna_ordenacao == coluna_sql:
            self.ordem_ascendente = not self.ordem_ascendente
        else:
            self.coluna_ordenacao = coluna_sql
            self.ordem_ascendente = True

        seta = " ▲" if self.ordem_ascendente else " ▼"
        for col in self.colunas_sql_map.keys():
            if col == coluna:
                self.tabela.heading(col, text=f"{col}{seta}")
            else:
                self.tabela.heading(col, text=col)

        self.carregar_dados()

    def aplicar_filtro(self):
        self.filtro_status_valor = self.var_filtro.get()
        self.carregar_dados()

    def alternar_parcelamento(self):
        if self.var_parcelado.get():
            self.lbl_qtd_parcelas.pack(anchor="w", pady=(2, 0), before=self.txt_data)
            self.cb_parcelas.pack(anchor="w", pady=(0, 6), before=self.txt_data)
            self.atualizar_opcoes_parcelas()
        else:
            self.lbl_qtd_parcelas.pack_forget()
            self.cb_parcelas.pack_forget()

    def atualizar_opcoes_parcelas(self, *args):
        val_str = self.var_valor.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            total = float(val_str) if val_str else 0.0
        except ValueError:
            total = 0.0

        opcoes = []
        for i in range(2, 13):
            v_parc = total / i
            v_str = f"R$ {v_parc:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            opcoes.append(f"{i}x de {v_str}")

        self.cb_parcelas['values'] = opcoes
        if opcoes and not self.cb_parcelas.get():
            self.cb_parcelas.set(opcoes[0])

    def carregar_combos(self):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT id, nome, principal FROM cartoes ORDER BY nome;")
                cartoes = cursor.fetchall()
                tem_coluna_principal = True
            except Exception:
                conn.rollback()
                cursor.execute("SELECT id, nome FROM cartoes ORDER BY nome;")
                cartoes = cursor.fetchall()
                tem_coluna_principal = False

            self.map_cartao.clear()
            lista_cartoes = []
            cartao_principal_nome = None

            for item in cartoes:
                if tem_coluna_principal:
                    cid, cnome, principal = item
                    if principal:
                        cartao_principal_nome = cnome
                else:
                    cid, cnome = item

                self.map_cartao[cnome] = str(cid)
                lista_cartoes.append(cnome)

            self.cb_cartao['values'] = lista_cartoes
            
            if cartao_principal_nome and not self.cb_cartao.get() and not self.despesa_selecionada_id:
                self.cb_cartao.set(cartao_principal_nome)
            elif lista_cartoes and not self.cb_cartao.get() and not self.despesa_selecionada_id:
                self.cb_cartao.set(lista_cartoes[0])

            cursor.execute("SELECT id_categoria, descricao FROM categorias ORDER BY descricao;")
            cats = cursor.fetchall()
            self.map_cat.clear()
            lista_cats = []
            for cid, cdesc in cats:
                self.map_cat[cdesc] = str(cid)
                lista_cats.append(cdesc)
            self.cb_cat['values'] = lista_cats

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar combos cartão: {e}")

    def ao_mudar_categoria(self, event=None):
        cat_nome = self.cb_cat.get()
        cat_id = self.map_cat.get(cat_nome)
        self.cb_sub.set("")
        self.cb_sub['values'] = []
        self.map_sub.clear()

        if cat_id:
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("SELECT id_subcategoria, descricao FROM subcategorias WHERE id_categoria = %s ORDER BY descricao;", (cat_id,))
                subs = cursor.fetchall()
                cursor.close()
                conn.close()

                lista_subs = []
                for sid, sdesc in subs:
                    self.map_sub[sdesc] = str(sid)
                    lista_subs.append(sdesc)
                self.cb_sub['values'] = lista_subs
            except Exception as e:
                print(f"Erro ao carregar subcategorias: {e}")

    def carregar_dados(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            
            cartao_selecionado = self.cb_cartao.get()
            cartao_id = self.map_cartao.get(cartao_selecionado) if cartao_selecionado else None

            fechamento_dia = 24
            if cartao_id:
                cursor.execute("SELECT dia_fechamento FROM cartoes WHERE id = %s;", (cartao_id,))
                res_f = cursor.fetchone()
                if res_f and res_f[0]:
                    fechamento_dia = res_f[0]

            direcao = "ASC" if self.ordem_ascendente else "DESC"
            query = f"""
                SELECT l.id, l.valor, l.data_lancamento, l.descricao, l.recebido,
                       c.descricao AS cat_nome, s.descricao AS sub_nome, ct.nome AS cartao_nome 
                FROM lancamentos l
                JOIN cartoes ct ON l.id_cartao = ct.id
                LEFT JOIN categorias c ON l.id_categoria = c.id_categoria
                LEFT JOIN subcategorias s ON l.id_subcategoria = s.id_subcategoria
                WHERE 1=1
            """
            
            params = []
            if cartao_id:
                query += " AND l.id_cartao = %s"
                params.append(cartao_id)

            if self.filtro_status_valor == "Pago":
                query += " AND l.recebido = TRUE"
            elif self.filtro_status_valor == "Pendente":
                query += " AND l.recebido = FALSE"

            query += f" ORDER BY {self.coluna_ordenacao} {direcao}, l.id DESC;"

            cursor.execute(query, tuple(params) if params else None)
            dados = cursor.fetchall()
            cursor.close()
            conn.close()

            def obter_ciclo_data(d_date):
                f_dia = min(fechamento_dia, calendar.monthrange(d_date.year, d_date.month)[1])
                if d_date.day > f_dia:
                    r_next = d_date + relativedelta(months=1)
                    r_ano = r_next.year
                    r_mes = r_next.month
                else:
                    r_ano = d_date.year
                    r_mes = d_date.month
                
                max_dia_fim = calendar.monthrange(r_ano, r_mes)[1]
                fim_dia = min(fechamento_dia, max_dia_fim)
                fim = date(r_ano, r_mes, fim_dia)
                inicio = fim - relativedelta(months=1) + relativedelta(days=1)
                return (inicio, fim)

            ciclos_dict = {}
            soma_total = 0.0

            for item in dados:
                lid, lval, ldata, ldesc, lrec, lcat, lsub, lcartao = item
                val_num = float(lval or 0)
                soma_total += val_num

                if ldata:
                    d_date = ldata.date() if hasattr(ldata, 'date') else ldata
                    ciclo_chave = obter_ciclo_data(d_date)
                else:
                    ciclo_chave = (date(2000, 1, 1), date(2000, 1, 1))

                if ciclo_chave not in ciclos_dict:
                    ciclos_dict[ciclo_chave] = {"itens": [], "soma": 0.0}
                
                ciclos_dict[ciclo_chave]["itens"].append(item)
                ciclos_dict[ciclo_chave]["soma"] += val_num

            ciclos_ordenados = sorted(ciclos_dict.keys(), key=lambda x: x[0], reverse=not self.ordem_ascendente)

            primeiro_item_pendente_iid = None

            for ciclo in ciclos_ordenados:
                inicio, fim = ciclo
                dados_ciclo = ciclos_dict[ciclo]

                dados_ciclo["itens"].sort(key=lambda x: x[2] if x[2] else datetime.min, reverse=not self.ordem_ascendente)

                for item in dados_ciclo["itens"]:
                    lid, lval, ldata, ldesc, lrec, lcat, lsub, lcartao = item
                    data_str = ldata.strftime("%d/%m/%Y") if ldata else ""
                    val_num = float(lval or 0)
                    val_str = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    status_str = "Pago" if lrec else "Pendente"
                    tag_cor = "tag_despesa_pago" if lrec else "tag_despesa_pendente"
                    
                    iid = self.tabela.insert("", "end", values=(data_str, lcartao or "", ldesc or "", lcat or "", lsub or "", val_str, status_str), tags=(tag_cor, str(lid)))
                    
                    if status_str == "Pendente" and not primeiro_item_pendente_iid:
                        primeiro_item_pendente_iid = iid

                str_total_ciclo = f"R$ {dados_ciclo['soma']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lbl_ciclo_txt = f"TOTAL FATURA ({inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')})" if inicio != date(2000, 1, 1) else "TOTAL SEM DATA"
                self.tabela.insert("", "end", values=("---", "---", lbl_ciclo_txt, "---", "---", str_total_ciclo, "---"), tags=("tag_separador_fatura",))

            total_str = f"R$ {soma_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.lbl_total_fatura.config(text=total_str)

            if primeiro_item_pendente_iid:
                self.tabela.selection_set(primeiro_item_pendente_iid)
                self.tabela.focus(primeiro_item_pendente_iid)
                self.tabela.see(primeiro_item_pendente_iid)

        except Exception as e:
            print(f"Erro ao carregar despesas de cartão: {e}")

    def limpar_campos(self):
        self.despesa_selecionada_id = None
        self.carregar_combos()
        self.var_valor.set("0,00")
        self.var_parcelado.set(False)
        self.alternar_parcelamento()
        self.var_data.set(datetime.now().strftime("%d/%m/%Y"))
        self.txt_desc.delete(0, tk.END)
        self.cb_cat.set("")
        self.cb_sub.set("")
        self.txt_repetir.delete(0, tk.END)
        self.txt_repetir.insert(0, "1")
        self.btn_salvar.config(text="Cadastrar Despesa")
        self.btn_excluir.pack_forget()
        self.cb_cartao.focus_set()
        self.carregar_dados()

    def selecionar_registro(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        item_id = selecao[0]
        tags = self.tabela.item(item_id, "tags")
        if not tags or tags[0] == "tag_separador_fatura":
            return

        self.despesa_selecionada_id = tags[1]

        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT valor, data_lancamento, descricao, id_categoria, id_subcategoria, id_cartao, repeticoes FROM lancamentos WHERE id = %s;", (self.despesa_selecionada_id,))
            reg = cursor.fetchone()
            cursor.close()
            conn.close()

            if reg:
                valor, data_lanc, desc, id_cat, id_sub, id_cartao, repeticoes = reg
                
                for nome_c, id_c in self.map_cartao.items():
                    if str(id_c) == str(id_cartao):
                        self.cb_cartao.set(nome_c)
                        break

                val_str = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.var_valor.set(val_str)
                self.var_parcelado.set(False)
                self.alternar_parcelamento()
                self.var_data.set(data_lanc.strftime("%d/%m/%Y") if data_lanc else "")
                self.txt_desc.delete(0, tk.END)
                self.txt_desc.insert(0, desc or "")

                for nome_cat, id_c in self.map_cat.items():
                    if str(id_c) == str(id_cat):
                        self.cb_cat.set(nome_cat)
                        self.ao_mudar_categoria()
                        break

                if id_sub:
                    for nome_s, id_s in self.map_sub.items():
                        if str(id_s) == str(id_sub):
                            self.cb_sub.set(nome_s)
                            break

                self.txt_repetir.delete(0, tk.END)
                self.txt_repetir.insert(0, str(repeticoes or 1))

                self.btn_salvar.config(text="Salvar Alterações")
                self.btn_excluir.pack(side="left", padx=(0, 4))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar despesa: {e}")

    def salvar_ou_alterar(self):
        cartao_nome = self.cb_cartao.get()
        val_str = self.var_valor.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
        cat_nome = self.cb_cat.get()

        if not cartao_nome or not val_str or not cat_nome:
            messagebox.showwarning("Aviso", "Selecione o cartão, preencha o valor e a categoria!")
            return

        if not is_data_valida(self.var_data.get()):
            messagebox.showwarning("Aviso", "Data inválida!")
            return

        try:
            valor_total = float(val_str)
            d_parts = self.var_data.get().split("/")
            data_base = datetime(int(d_parts[2]), int(d_parts[1]), int(d_parts[0]))
            
            id_cartao = self.map_cartao.get(cartao_nome)
            id_cat = self.map_cat.get(cat_nome)
            id_sub = self.map_sub.get(self.cb_sub.get()) if self.cb_sub.get() else None
            desc_base = self.txt_desc.get().strip() or "Despesa Cartão"
            repeticoes = int(self.txt_repetir.get().strip() or 1)

            conn = conectar_banco()
            cursor = conn.cursor()

            if self.despesa_selecionada_id:
                cursor.execute("""
                    UPDATE lancamentos 
                    SET tipo = 'Despesa', valor = %s, data_lancamento = %s, 
                        descricao = %s, id_categoria = %s, id_subcategoria = %s, id_cartao = %s, repeticoes = %s
                    WHERE id = %s;
                """, (valor_total, data_base.strftime("%Y-%m-%d"), desc_base, id_cat, id_sub, id_cartao, repeticoes, self.despesa_selecionada_id))
                msg = "Despesa de cartão alterada com sucesso!"
            else:
                if self.var_parcelado.get():
                    texto_selecionado = self.cb_parcelas.get()
                    qtd_vezes = int(texto_selecionado.split("x")[0])
                    valor_parcela = valor_total / qtd_vezes

                    for i in range(qtd_vezes):
                        data_parcela = data_base + relativedelta(months=i)
                        desc_parcela = f"{desc_base} ({i+1}/{qtd_vezes})"
                        cursor.execute("""
                            INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_cartao, repeticoes)
                            VALUES ('Despesa', %s, FALSE, %s, %s, %s, %s, %s, %s);
                        """, (valor_parcela, data_parcela.strftime("%Y-%m-%d"), desc_parcela, id_cat, id_sub, id_cartao, qtd_vezes))
                    msg = f"Despesa parcelada em {qtd_vezes}x cadastrada com sucesso!"
                elif repeticoes > 1:
                    for i in range(repeticoes):
                        data_parcela = data_base + relativedelta(months=i)
                        desc_rep = f"{desc_base} ({i+1}/{repeticoes})"
                        cursor.execute("""
                            INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_cartao, repeticoes)
                            VALUES ('Despesa', %s, FALSE, %s, %s, %s, %s, %s, %s);
                        """, (valor_total, data_parcela.strftime("%Y-%m-%d"), desc_rep, id_cat, id_sub, id_cartao, repeticoes))
                    msg = f"Despesa repetida por {repeticoes} vezes cadastrada com sucesso!"
                else:
                    cursor.execute("""
                        INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_cartao, repeticoes)
                        VALUES ('Despesa', %s, FALSE, %s, %s, %s, %s, %s, %s);
                    """, (valor_total, data_base.strftime("%Y-%m-%d"), desc_base, id_cat, id_sub, id_cartao, 1))
                    msg = "Despesa de cartão cadastrada com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_dados()

            try:
                notebook_pai = self.parent.master
                for tab_widget in notebook_pai.winfo_children():
                    if hasattr(tab_widget, 'recarregar'):
                        tab_widget.recarregar()
            except Exception:
                pass
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar despesa de cartão: {ex}")

    def pagar_fatura_periodo(self):
        cartao_nome = self.cb_cartao.get()
        if not cartao_nome:
            messagebox.showwarning("Aviso", "Selecione o cartão de crédito!")
            return

        try:
            id_cartao = self.map_cartao.get(cartao_nome)
            conn = conectar_banco()
            cursor = conn.cursor()

            cursor.execute("SELECT dia_fechamento, dia_vencimento FROM cartoes WHERE id = %s;", (id_cartao,))
            cartao_info = cursor.fetchone()
            if not cartao_info:
                messagebox.showerror("Erro", "Cartão não encontrado!")
                cursor.close()
                conn.close()
                return

            c_fech, c_venc = cartao_info
            fechamento = c_fech or 24
            vencimento_dia = c_venc or 1

            # Buscar todas as despesas pendentes deste cartão
            cursor.execute("""
                SELECT id, valor, data_lancamento, descricao FROM lancamentos 
                WHERE id_cartao = %s AND recebido = FALSE ORDER BY data_lancamento ASC;
            """, (id_cartao,))
            despesas_pendentes = cursor.fetchall()

            if not despesas_pendentes:
                messagebox.showinfo("Informação", "Não há despesas pendentes para este cartão.")
                cursor.close()
                conn.close()
                return

            def obter_ciclo_data(d_date):
                f_dia = min(fechamento, calendar.monthrange(d_date.year, d_date.month)[1])
                if d_date.day > f_dia:
                    r_next = d_date + relativedelta(months=1)
                    r_ano = r_next.year
                    r_mes = r_next.month
                else:
                    r_ano = d_date.year
                    r_mes = d_date.month
                
                max_dia_fim = calendar.monthrange(r_ano, r_mes)[1]
                fim_dia = min(fechamento, max_dia_fim)
                fim = date(r_ano, r_mes, fim_dia)
                inicio = fim - relativedelta(months=1) + relativedelta(days=1)
                
                if vencimento_dia <= fechamento:
                    venc = date(r_ano, r_mes, 1) + relativedelta(months=1)
                else:
                    venc = date(r_ano, r_mes, 1)
                max_d_venc = calendar.monthrange(venc.year, venc.month)[1]
                vencimento = date(venc.year, venc.month, min(vencimento_dia, max_d_venc))
                
                return (inicio, fim, vencimento)

            # Agrupar despesas pendentes por período/ciclo
            ciclos_pendentes = {}
            for d_id, d_val, d_data, d_desc in despesas_pendentes:
                if not d_data:
                    continue
                d_date = d_data.date() if hasattr(d_data, 'date') else d_data
                chave_ciclo = obter_ciclo_data(d_date)

                if chave_ciclo not in ciclos_pendentes:
                    ciclos_pendentes[chave_ciclo] = {"ids": [], "valor_total": 0.0, "itens": []}
                
                ciclos_pendentes[chave_ciclo]["ids"].append(d_id)
                v_num = float(d_val or 0)
                ciclos_pendentes[chave_ciclo]["valor_total"] += v_num
                ciclos_pendentes[chave_ciclo]["itens"].append(
                    f"• {d_data.strftime('%d/%m/%Y')} - {d_desc}: R$ {v_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                )

            if not ciclos_pendentes:
                messagebox.showinfo("Informação", "Não há períodos pendentes para este cartão.")
                cursor.close()
                conn.close()
                return

            cursor.close()
            conn.close()

            # Criar janela de seleção do período
            janela_sel = tk.Toplevel(self.parent)
            janela_sel.title(f"Selecionar Período - {cartao_nome}")
            janela_sel.geometry("460x380")
            janela_sel.config(bg="#F0F0F0")
            janela_sel.grab_set()

            tk.Label(
                janela_sel, 
                text=f"Selecione o período da fatura a ser paga ({cartao_nome}):", 
                font=("Arial", 10, "bold"), 
                bg="#F0F0F0"
            ).pack(anchor="w", padx=15, pady=(15, 5))

            frame_listbox = tk.Frame(janela_sel, bg="#F0F0F0")
            frame_listbox.pack(fill="both", expand=True, padx=15, pady=5)

            scrollbar_sel = ttk.Scrollbar(frame_listbox, orient="vertical")
            listbox_ciclos = tk.Listbox(frame_listbox, font=("Arial", 10), yscrollcommand=scrollbar_sel.set, selectmode=tk.SINGLE, height=10)
            scrollbar_sel.config(command=listbox_ciclos.yview)

            listbox_ciclos.pack(side="left", fill="both", expand=True)
            scrollbar_sel.pack(side="right", fill="y")

            chaves_ordenadas = sorted(ciclos_pendentes.keys(), key=lambda x: x[0])
            for idx, (inicio, fim, vencimento) in enumerate(chaves_ordenadas):
                dados_c = ciclos_pendentes[(inicio, fim, vencimento)]
                val_str = f"R$ {dados_c['valor_total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                texto_item = f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')} | Venc: {vencimento.strftime('%m/%Y')} | Total: {val_str}"
                listbox_ciclos.insert(tk.END, texto_item)

            if chaves_ordenadas:
                listbox_ciclos.selection_set(0)

            def confirmar_pagamento_selecionado():
                selecao_lb = listbox_ciclos.curselection()
                if not selecao_lb:
                    messagebox.showwarning("Aviso", "Selecione um período na lista!", parent=janela_sel)
                    return
                
                idx_sel = selecao_lb[0]
                ciclo_escolhido = chaves_ordenadas[idx_sel]
                dados_escolhidos = ciclos_pendentes[ciclo_escolhido]

                inicio, fim, vencimento = ciclo_escolhido
                str_vencimento = vencimento.strftime("%m/%Y")

                resumo_itens = "\n".join(dados_escolhidos["itens"][:10])
                if len(dados_escolhidos["itens"]) > 10:
                    resumo_itens += f"\n... e mais {len(dados_escolhidos['itens']) - 10} item(ns)."

                msg_conf = (
                    f"Deseja pagar a fatura do cartão '{cartao_nome}'\n"
                    f"referente ao período ({inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')})\n"
                    f"com vencimento em: {str_vencimento}\n"
                    f"Valor Total: R$ {dados_escolhidos['valor_total']:,.2f}\n\n"
                    f"Registros incluídos:\n{resumo_itens}"
                )

                if messagebox.askyesno("Confirmar Pagamento", msg_conf, parent=janela_sel):
                    try:
                        conn_up = conectar_banco()
                        cursor_up = conn_up.cursor()

                        for d_id in dados_escolhidos["ids"]:
                            cursor_up.execute("""
                                UPDATE lancamentos 
                                SET recebido = TRUE 
                                WHERE id = %s;
                            """, (str(d_id),))

                        conn_up.commit()
                        cursor_up.close()
                        conn_up.close()

                        messagebox.showinfo("Sucesso", f"Fatura com vencimento em {str_vencimento} quitada com sucesso!", parent=janela_sel)
                        janela_sel.destroy()

                        try:
                            notebook_pai = self.parent.master
                            for tab_widget in notebook_pai.winfo_children():
                                if hasattr(tab_widget, 'recarregar'):
                                    tab_widget.recarregar()
                        except Exception:
                            pass

                        self.carregar_dados()
                    except Exception as err:
                        messagebox.showerror("Erro", f"Erro ao efetuar pagamento: {err}", parent=janela_sel)

            btn_conf_pagar = tk.Button(
                janela_sel, 
                text="Pagar Período Selecionado", 
                bg="#2F855A", 
                fg="white", 
                font=("Arial", 9, "bold"), 
                command=confirmar_pagamento_selecionado
            )
            btn_conf_pagar.pack(pady=15)

        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao carregar períodos da fatura: {ex}")

    def excluir_despesa(self):
        if not self.despesa_selecionada_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta despesa de cartão?"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lancamentos WHERE id = %s;", (self.despesa_selecionada_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Despesa excluída com sucesso!")
                self.limpar_campos()
                self.carregar_dados()

                try:
                    notebook_pai = self.parent.master
                    for tab_widget in notebook_pai.winfo_children():
                        if hasattr(tab_widget, 'recarregar'):
                            tab_widget.recarregar()
                except Exception:
                    pass
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir: {ex}")

    def recarregar(self):
        self.carregar_combos()
        self.carregar_dados()