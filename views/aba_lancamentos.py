import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database import conectar_banco
from utils import aplicar_mascara_valor, aplicar_mascara_data, is_data_valida

class AbaLancamentos:
    def __init__(self, parent):
        self.parent = parent
        self.lancamento_selecionado_id = None
        self.filtro_status_valor = "Ambos"
        
        self.coluna_ordenacao = "l.data_lancamento"
        self.ordem_ascendente = True

        # Painel Esquerdo (Formulário)
        frame_form = tk.LabelFrame(parent, text=" Novo Lançamento ", font=("Arial", 10, "bold"), bg="#F0F0F0", padx=12, pady=12)
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        # Tipo
        tk.Label(frame_form, text="Tipo de Lançamento:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.cb_tipo = ttk.Combobox(frame_form, values=["Receita", "Despesa", "Transferência"], width=30, state="readonly")
        self.cb_tipo.set("Receita")
        self.cb_tipo.pack(anchor="w", pady=(0, 6))
        self.cb_tipo.bind("<<ComboboxSelected>>", self.ao_mudar_tipo)

        # Valor
        self.lbl_valor = tk.Label(frame_form, text="Valor da Receita:", bg="#F0F0F0", font=("Arial", 9))
        self.lbl_valor.pack(anchor="w", pady=(2, 0))
        self.var_valor = tk.StringVar(value="0,00")
        self.var_valor.trace_add("write", lambda *args: aplicar_mascara_valor(None, self.var_valor))
        self.txt_valor = tk.Entry(frame_form, textvariable=self.var_valor, width=32, font=("Arial", 10))
        self.txt_valor.pack(anchor="w", pady=(0, 6))

        # Checkbox Status (Recebido / Pago)
        self.var_status = tk.BooleanVar(value=True)
        self.chk_status = tk.Checkbutton(frame_form, text="Recebido", variable=self.var_status, bg="#F0F0F0", font=("Arial", 9, "bold"))
        self.chk_status.pack(anchor="w", pady=(2, 6))

        # Data
        tk.Label(frame_form, text="Data (DD/MM/AAAA):", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.var_data = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.var_data.trace_add("write", lambda *args: aplicar_mascara_data(None, self.var_data))
        self.txt_data = tk.Entry(frame_form, textvariable=self.var_data, width=32, font=("Arial", 10))
        self.txt_data.pack(anchor="w", pady=(0, 6))

        # Descrição
        tk.Label(frame_form, text="Descrição:", bg="#F0F0F0", font=("Arial", 9)).pack(anchor="w", pady=(2, 0))
        self.txt_desc = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_desc.pack(anchor="w", pady=(0, 6))

        # Categoria
        self.lbl_cat = tk.Label(frame_form, text="Categoria:", bg="#F0F0F0", font=("Arial", 9))
        self.lbl_cat.pack(anchor="w", pady=(2, 0))
        self.cb_cat = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_cat.pack(anchor="w", pady=(0, 6))
        self.cb_cat.bind("<<ComboboxSelected>>", self.ao_mudar_categoria)

        # Subcategoria
        self.lbl_sub = tk.Label(frame_form, text="Subcategoria:", bg="#F0F0F0", font=("Arial", 9))
        self.lbl_sub.pack(anchor="w", pady=(2, 0))
        self.cb_sub = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_sub.pack(anchor="w", pady=(0, 6))

        # Conta Bancária
        self.lbl_conta = tk.Label(frame_form, text="Conta Bancária:", bg="#F0F0F0", font=("Arial", 9))
        self.lbl_conta.pack(anchor="w", pady=(2, 0))
        self.cb_conta = ttk.Combobox(frame_form, width=30, state="readonly")
        self.cb_conta.pack(anchor="w", pady=(0, 6))

        # Conta de Destino (Para Transferência)
        self.lbl_conta_destino = tk.Label(frame_form, text="Conta de Destino:", bg="#F0F0F0", font=("Arial", 9))
        self.cb_conta_destino = ttk.Combobox(frame_form, width=30, state="readonly")

        # Repetir
        self.lbl_repetir = tk.Label(frame_form, text="Repetir (Qtd de vezes):", bg="#F0F0F0", font=("Arial", 9))
        self.lbl_repetir.pack(anchor="w", pady=(2, 0))
        self.txt_repetir = tk.Entry(frame_form, width=32, font=("Arial", 10))
        self.txt_repetir.insert(0, "1")
        self.txt_repetir.pack(anchor="w", pady=(0, 12))

        # Botões de Ação (Fixos no rodapé do formulário)
        frame_botoes = tk.Frame(frame_form, bg="#F0F0F0")
        frame_botoes.pack(anchor="w", pady=(5, 0))

        self.btn_salvar = tk.Button(frame_botoes, text="Cadastrar Receita", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), command=self.salvar_ou_alterar)
        self.btn_salvar.pack(side="left", padx=(0, 4))

        self.btn_excluir = tk.Button(frame_botoes, text="Excluir", bg="#C53030", fg="white", font=("Arial", 9, "bold"), command=self.excluir_lancamento)
        self.btn_excluir.pack(side="left", padx=(0, 4))
        self.btn_excluir.pack_forget()

        self.btn_limpar = tk.Button(frame_botoes, text="Limpar", font=("Arial", 9), command=self.limpar_campos)
        self.btn_limpar.pack(side="left")

        # Sequência de foco via ENTER
        self.sequencia_foco = [
            self.cb_tipo, self.txt_valor, self.chk_status, self.txt_data,
            self.txt_desc, self.cb_cat, self.cb_sub, self.cb_conta,
            self.txt_repetir, self.btn_salvar
        ]
        for i, widget in enumerate(self.sequencia_foco):
            widget.bind("<Return>", lambda e, idx=i: self.pular_para_proximo(idx))

        # Painel Direito (Tabela, Filtros e Saldos)
        frame_direito = tk.Frame(parent, bg="#F0F0F0")
        frame_direito.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        header_tabela = tk.Frame(frame_direito, bg="#F0F0F0")
        header_tabela.pack(fill="x", pady=(0, 5))
        tk.Label(header_tabela, text="Últimos Lançamentos", font=("Arial", 11, "bold"), bg="#F0F0F0").pack(side="left")

        # Botão para Ocultar/Exibir Colunas
        btn_config_colunas = tk.Button(header_tabela, text="⚙ Colunas", font=("Arial", 8, "bold"), command=self.abrir_config_colunas)
        btn_config_colunas.pack(side="right", padx=(10, 0))

        self.var_filtro = tk.StringVar(value="Ambos")
        tk.Radiobutton(header_tabela, text="Ambos", variable=self.var_filtro, value="Ambos", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right")
        tk.Radiobutton(header_tabela, text="Recebido/Pago", variable=self.var_filtro, value="Recebido/Pago", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right", padx=10)
        tk.Radiobutton(header_tabela, text="Pendente", variable=self.var_filtro, value="Pendente", bg="#F0F0F0", command=self.aplicar_filtro).pack(side="right")

        # Sub-cabeçalho para Filtro por Conta Bancária
        sub_header_conta = tk.Frame(frame_direito, bg="#F0F0F0")
        sub_header_conta.pack(fill="x", pady=(0, 8))
        
        tk.Label(sub_header_conta, text="Filtrar por Conta:", font=("Arial", 9, "bold"), bg="#F0F0F0", fg="#1A365D").pack(side="left", padx=(0, 5))
        self.cb_filtro_conta = ttk.Combobox(sub_header_conta, width=35, state="readonly")
        self.cb_filtro_conta.pack(side="left")
        self.cb_filtro_conta.bind("<<ComboboxSelected>>", lambda e: self.carregar_dados())

        # Frame exclusivo para a Tabela + Barra de Rolagem (mantém a rolagem contida corretamente)
        frame_tabela_container = tk.Frame(frame_direito, bg="#F0F0F0")
        frame_tabela_container.pack(side="top", fill="both", expand=True, pady=(0, 5))

        # Tabela (Treeview)
        self.colunas_nomes = ("Data", "Descricao", "Tipo", "Categoria", "Subcategoria", "Conta", "Valor", "Saldo", "Status")
        self.tabela = ttk.Treeview(frame_tabela_container, columns=self.colunas_nomes, show="headings", height=15)
        
        self.colunas_visiveis = {col: tk.BooleanVar(value=True) for col in self.colunas_nomes}

        # Tags de Cores com fonte padronizada (Arial, 9)
        self.tabela.tag_configure("tag_vermelho", foreground="#C53030", font=("Arial", 9, "bold")) 
        self.tabela.tag_configure("tag_azul", foreground="#2B6CB0", font=("Arial", 9, "bold"))              
        self.tabela.tag_configure("tag_padrao", foreground="#000000", font=("Arial", 9))

        self.colunas_sql_map = {
            "Data": "l.data_lancamento",
            "Descricao": "l.descricao",
            "Tipo": "l.tipo",
            "Categoria": "c.descricao",
            "Subcategoria": "s.descricao",
            "Conta": "ct.instituicao",
            "Valor": "l.valor",
            "Saldo": "l.data_lancamento",
            "Status": "l.recebido"
        }

        for col in self.colunas_nomes:
            self.tabela.heading(col, text=col, command=lambda c=col: self.ordenar_por_coluna(c))

        self.tabela.heading("Data", text="Data ▲")

        self.tabela.column("Data", width=80, anchor="center")
        self.tabela.column("Descricao", width=130, anchor="w")
        self.tabela.column("Tipo", width=75, anchor="center")
        self.tabela.column("Categoria", width=90, anchor="w")
        self.tabela.column("Subcategoria", width=90, anchor="w")
        self.tabela.column("Conta", width=90, anchor="w")
        self.tabela.column("Valor", width=85, anchor="e")
        self.tabela.column("Saldo", width=85, anchor="e")
        self.tabela.column("Status", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabela_container, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        # Empacotamento correto dentro do container isolado
        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tabela.bind("<Double-1>", self.selecionar_registro)

        # Painel de Saldos (Fica logo abaixo da tabela com margem limpa)
        frame_saldos = tk.Frame(frame_direito, bg="white", bd=1, relief="solid", padx=10, pady=8)
        frame_saldos.pack(side="bottom", fill="x")

        self.lbl_saldo_efetivo = tk.Label(frame_saldos, text="R$ 0,00", font=("Arial", 11, "bold"), fg="#2F855A", bg="white")
        self.lbl_titulo_efetivo = tk.Label(frame_saldos, text="Saldo Atual na Conta (Até Hoje):", font=("Arial", 8, "bold"), fg="#718096", bg="white")
        self.lbl_titulo_efetivo.pack(anchor="w")
        self.lbl_saldo_efetivo.pack(anchor="w")

        self.lbl_saldo_previsto = tk.Label(frame_saldos, text="R$ 0,00", font=("Arial", 11, "bold"), fg="#2B6CB0", bg="white")
        self.lbl_titulo_previsto = tk.Label(frame_saldos, text="Saldo Total Previsto (Geral):", font=("Arial", 8, "bold"), fg="#718096", bg="white")
        self.lbl_titulo_previsto.pack(anchor="w", pady=(5, 0))
        self.lbl_saldo_previsto.pack(anchor="w")

        self.map_cat = {}
        self.map_cat_rev = {}
        self.map_conta = {}
        self.map_conta_rev = {}
        self.map_sub = {}

        self.carregar_combos()
        self.carregar_dados()

    def abrir_config_colunas(self):
        janela_cfg = tk.Toplevel(self.parent)
        janela_cfg.title("Configurar Colunas")
        janela_cfg.geometry("240x330")
        janela_cfg.config(bg="#F0F0F0")
        janela_cfg.grab_set()

        tk.Label(janela_cfg, text="Selecione as colunas visíveis:", font=("Arial", 9, "bold"), bg="#F0F0F0").pack(anchor="w", padx=15, pady=(15, 10))

        for col in self.colunas_nomes:
            chk = tk.Checkbutton(janela_cfg, text=col, variable=self.colunas_visiveis[col], bg="#F0F0F0", font=("Arial", 9), command=self.atualizar_colunas_visiveis)
            chk.pack(anchor="w", padx=20, pady=2)

        tk.Button(janela_cfg, text="Fechar", bg="#2B6CB0", fg="white", font=("Arial", 9, "bold"), command=janela_cfg.destroy).pack(pady=15)

    def atualizar_colunas_visiveis(self):
        visiveis = [col for col in self.colunas_nomes if self.colunas_visiveis[col].get()]
        self.tabela.configure(displaycolumns=visiveis)

    def normalizar_data(self, d):
        if not d:
            return datetime.min
        if isinstance(d, datetime):
            return d
        return datetime(d.year, d.month, d.day)

    def pular_para_proximo(self, indice_atual):
        proximo_indice = (indice_atual + 1) % len(self.sequencia_foco)
        self.sequencia_foco[proximo_indice].focus_set()

    def ordenar_por_coluna(self, coluna):
        if coluna == "Saldo":
            return
        
        coluna_sql = self.colunas_sql_map.get(coluna, "l.data_lancamento")
        if self.coluna_ordenacao == coluna_sql:
            self.ordem_ascendente = not self.ordem_ascendente
        else:
            self.coluna_ordenacao = coluna_sql
            self.ordem_ascendente = True

        seta = " ▲" if self.ordem_ascendente else " ▼"
        for col in self.colunas_nomes:
            if col == coluna:
                self.tabela.heading(col, text=f"{col}{seta}")
            else:
                self.tabela.heading(col, text=col)

        self.carregar_dados()

    def ao_mudar_tipo(self, event=None):
        tipo = self.cb_tipo.get()
        if tipo == "Despesa":
            self.chk_status.config(text="Pago")
            self.lbl_valor.config(text="Valor da Despesa:")
            self.lbl_cat.pack(anchor="w", pady=(2, 0))
            self.cb_cat.pack(anchor="w", pady=(0, 6))
            self.lbl_sub.pack(anchor="w", pady=(2, 0))
            self.cb_sub.pack(anchor="w", pady=(0, 6))
            self.lbl_conta.config(text="Conta Bancária:")
            self.lbl_conta_destino.pack_forget()
            self.cb_conta_destino.pack_forget()
            if not self.lancamento_selecionado_id:
                self.btn_salvar.config(text="Cadastrar Despesa", bg="#C53030")
        elif tipo == "Receita":
            self.chk_status.config(text="Recebido")
            self.lbl_valor.config(text="Valor da Receita:")
            self.lbl_cat.pack(anchor="w", pady=(2, 0))
            self.cb_cat.pack(anchor="w", pady=(0, 6))
            self.lbl_sub.pack(anchor="w", pady=(2, 0))
            self.cb_sub.pack(anchor="w", pady=(0, 6))
            self.lbl_conta.config(text="Conta Bancária:")
            self.lbl_conta_destino.pack_forget()
            self.cb_conta_destino.pack_forget()
            if not self.lancamento_selecionado_id:
                self.btn_salvar.config(text="Cadastrar Receita", bg="#2B6CB0")
        else: # Transferência
            self.chk_status.config(text="Realizada")
            self.lbl_valor.config(text="Valor da Transferência:")
            self.lbl_cat.pack_forget()
            self.cb_cat.pack_forget()
            self.lbl_sub.pack_forget()
            self.cb_sub.pack_forget()
            self.lbl_conta.config(text="Conta de Origem:")
            self.lbl_conta_destino.pack(anchor="w", pady=(2, 0))
            self.cb_conta_destino.pack(anchor="w", pady=(0, 6))
            if not self.lancamento_selecionado_id:
                self.btn_salvar.config(text="Cadastrar Transferência", bg="#D69E2E")

    def carregar_combos(self):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT id_categoria, descricao FROM categorias ORDER BY descricao;")
            cats = cursor.fetchall()
            self.map_cat.clear()
            self.map_cat_rev.clear()
            lista_cats = []
            for cid, cdesc in cats:
                self.map_cat[cdesc] = str(cid)
                self.map_cat_rev[str(cid)] = cdesc
                lista_cats.append(cdesc)
            self.cb_cat['values'] = lista_cats

            cursor.execute("SELECT id, instituicao, principal FROM contas ORDER BY instituicao;")
            contas = cursor.fetchall()
            self.map_conta.clear()
            self.map_conta_rev.clear()
            lista_contas = []
            conta_principal_nome = None

            for ctt_id, inst, principal in contas:
                self.map_conta[inst] = str(ctt_id)
                self.map_conta_rev[str(ctt_id)] = inst
                lista_contas.append(inst)
                if principal:
                    conta_principal_nome = inst

            self.cb_conta['values'] = lista_contas
            self.cb_conta_destino['values'] = lista_contas
            
            if conta_principal_nome and not self.cb_conta.get() and not self.lancamento_selecionado_id:
                self.cb_conta.set(conta_principal_nome)
            if lista_contas and not self.cb_conta_destino.get() and len(lista_contas) > 1:
                self.cb_conta_destino.set(lista_contas[1])
            elif lista_contas and not self.cb_conta_destino.get():
                self.cb_conta_destino.set(lista_contas[0])

            lista_filtro_conta = ["Todas as Contas"] + lista_contas
            self.cb_filtro_conta['values'] = lista_filtro_conta
            if not self.cb_filtro_conta.get():
                self.cb_filtro_conta.set("Todas as Contas")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro ao carregar combos: {e}")

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

    def aplicar_filtro(self):
        self.filtro_status_valor = self.var_filtro.get()
        self.carregar_dados()

    def carregar_dados(self):
        for row in self.tabela.get_children():
            self.tabela.delete(row)
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            conta_filtro_nome = self.cb_filtro_conta.get()
            id_conta_filtro = self.map_conta.get(conta_filtro_nome) if conta_filtro_nome and conta_filtro_nome != "Todas as Contas" else None

            direcao_sql = "ASC" if self.ordem_ascendente else "DESC"

            query_normais = f"""
                SELECT l.id, l.tipo, l.valor, l.recebido, l.data_lancamento, l.descricao, 
                       c.descricao AS cat_nome, s.descricao AS sub_nome, l.id_conta, ct.instituicao AS conta_nome, NULL as id_cartao 
                FROM lancamentos l
                LEFT JOIN categorias c ON l.id_categoria = c.id_categoria
                LEFT JOIN subcategorias s ON l.id_subcategoria = s.id_subcategoria
                LEFT JOIN contas ct ON l.id_conta = ct.id
                WHERE l.id_cartao IS NULL
            """
            params_normais = []
            if id_conta_filtro:
                query_normais += " AND l.id_conta = %s"
                params_normais.append(id_conta_filtro)

            if self.filtro_status_valor in ["Recebido/Pago"]:
                query_normais += " AND l.recebido = TRUE"
            elif self.filtro_status_valor == "Pendente":
                query_normais += " AND l.recebido = FALSE"

            query_normais += f" ORDER BY {self.coluna_ordenacao} {direcao_sql}, l.id DESC"

            cursor.execute(query_normais, tuple(params_normais) if params_normais else None)
            dados_normais = cursor.fetchall()

            dados_faturas = []
            if not id_conta_filtro:
                cursor.execute("""
                    SELECT l.id, l.valor, l.recebido, l.data_lancamento, ct.id, ct.nome, ct.dia_fechamento, ct.dia_vencimento
                    FROM lancamentos l
                    JOIN cartoes ct ON l.id_cartao = ct.id
                """)
                despesas_cartao = cursor.fetchall()

                faturas_agrupadas = {}
                for d_id, d_val, d_rec, d_data, c_id, c_nome, c_fech, c_venc in despesas_cartao:
                    if not d_data:
                        continue
                    
                    dia_compra = d_data.day
                    fechamento = c_fech or 1
                    vencimento_dia = c_venc or 10

                    if dia_compra <= fechamento:
                        base_venc = datetime(d_data.year, d_data.month, 1) + relativedelta(months=1)
                    else:
                        base_venc = datetime(d_data.year, d_data.month, 1) + relativedelta(months=2)

                    data_vencimento = datetime(base_venc.year, base_venc.month, vencimento_dia)
                    
                    d_data_dt = self.normalizar_data(d_data)
                    if data_vencimento < d_data_dt:
                        data_vencimento = data_vencimento + relativedelta(months=1)

                    chave = (c_id, data_vencimento)

                    if chave not in faturas_agrupadas:
                        faturas_agrupadas[chave] = {
                            "cartao_nome": c_nome,
                            "data_venc": data_vencimento,
                            "valor_total": 0.0,
                            "todas_pagas": True
                        }
                    
                    faturas_agrupadas[chave]["valor_total"] += float(d_val or 0)
                    if not d_rec:
                        faturas_agrupadas[chave]["todas_pagas"] = False

                for chave, fat in faturas_agrupadas.items():
                    dados_faturas.append((
                        f"fat_{chave[0]}_{fat['data_venc'].strftime('%Y%m')}",
                        "Despesa",
                        fat["valor_total"],
                        fat["todas_pagas"],
                        fat["data_venc"],
                        f"Fatura Cartão: {fat['cartao_nome']}",
                        "Cartão de Crédito",
                        "",
                        None,
                        f"Cartão: {fat['cartao_nome']}",
                        chave[0]
                    ))

                faturas_filtradas = []
                for fat in dados_faturas:
                    recebido = fat[3]
                    if self.filtro_status_valor == "Recebido/Pago" and not recebido:
                        continue
                    if self.filtro_status_valor == "Pendente" and recebido:
                        continue
                    faturas_filtradas.append(fat)
                dados_faturas = faturas_filtradas

            cursor.close()
            conn.close()

            dados = list(dados_normais) + dados_faturas

            if not dados:
                self.calcular_saldos(id_conta_filtro)
                return

            dados_exibicao = sorted(dados, key=lambda x: self.normalizar_data(x[4]), reverse=(not self.ordem_ascendente))

            conn_hist = conectar_banco()
            cur_hist = conn_hist.cursor()
            q_hist = "SELECT tipo, valor, data_lancamento FROM lancamentos WHERE id_cartao IS NULL"
            p_hist = []
            if id_conta_filtro:
                q_hist += " AND id_conta = %s"
                p_hist.append(id_conta_filtro)
            cur_hist.execute(q_hist, tuple(p_hist) if p_hist else None)
            todos_banco = cur_hist.fetchall()
            cur_hist.close()
            conn_hist.close()

            menor_data_tela = self.normalizar_data(dados_exibicao[0][4]) if self.ordem_ascendente else self.normalizar_data(dados_exibicao[-1][4])

            saldo_acumulado = 0.0
            for b_tipo, b_val, b_data in todos_banco:
                dt_b = self.normalizar_data(b_data)
                if dt_b < menor_data_tela:
                    val_n = float(b_val or 0)
                    if b_tipo in ["Despesa", "Transferência"]:
                        saldo_acumulado -= val_n
                    else:
                        saldo_acumulado += val_n

            if not self.ordem_ascendente:
                saldo_acumulado = 0.0
                for b_tipo, b_val, _ in todos_banco:
                    val_n = float(b_val or 0)
                    if b_tipo in ["Despesa", "Transferência"]:
                        saldo_acumulado -= val_n
                    else:
                        saldo_acumulado += val_n

            for item in dados_exibicao:
                lid, ltipo, lval, lrec, ldata, ldesc, lcat, lsub, lconta_id, lconta_nome, lcartao = item
                data_str = ldata.strftime("%d/%m/%Y") if ldata else ""
                val_num = float(lval or 0)

                if self.ordem_ascendente:
                    if ltipo in ["Despesa", "Transferência"]:
                        saldo_acumulado -= val_num
                    else:
                        saldo_acumulado += val_num
                    saldo_linha = saldo_acumulado
                else:
                    saldo_linha = saldo_acumulado
                    if ltipo in ["Despesa", "Transferência"]:
                        saldo_acumulado += val_num
                    else:
                        saldo_acumulado -= val_num

                if lrec:
                    status_str = "Pago" if ltipo == "Despesa" else ("Realizada" if ltipo == "Transferência" else "Recebido")
                else:
                    status_str = "Pendente"

                val_str = f"R$ {val_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                saldo_str = f"R$ {saldo_linha:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                if saldo_linha < 0:
                    tag_linha = "tag_vermelho"
                elif lrec:
                    tag_linha = "tag_azul"
                else:
                    tag_linha = "tag_padrao"

                self.tabela.insert("", "end", values=(data_str, ldesc or "", ltipo or "", lcat or "", lsub or "", lconta_nome or "", val_str, saldo_str, status_str), tags=(tag_linha, str(lid)))

            self.calcular_saldos(id_conta_filtro)
        except Exception as e:
            print(f"Erro ao carregar lançamentos: {e}")

    def calcular_saldos(self, id_conta=None):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            if id_conta:
                cursor.execute("SELECT tipo, SUM(valor) FROM lancamentos WHERE recebido = TRUE AND data_lancamento <= CURRENT_DATE AND id_conta = %s GROUP BY tipo;", (id_conta,))
                efetivo = cursor.fetchall()
                cursor.execute("SELECT tipo, SUM(valor) FROM lancamentos WHERE id_conta = %s GROUP BY tipo;", (id_conta,))
                previsto = cursor.fetchall()
                nome_conta_sel = self.cb_filtro_conta.get()
                self.lbl_titulo_efetivo.config(text=f"Saldo Atual na Conta '{nome_conta_sel}' (Até Hoje):")
                self.lbl_titulo_previsto.config(text=f"Saldo Total Previsto para '{nome_conta_sel}':")
            else:
                cursor.execute("SELECT tipo, SUM(valor) FROM lancamentos WHERE recebido = TRUE AND data_lancamento <= CURRENT_DATE GROUP BY tipo;")
                efetivo = cursor.fetchall()
                cursor.execute("SELECT tipo, SUM(valor) FROM lancamentos GROUP BY tipo;")
                previsto = cursor.fetchall()
                self.lbl_titulo_efetivo.config(text="Saldo Atual Geral (Até Hoje):")
                self.lbl_titulo_previsto.config(text="Saldo Total Previsto (Geral):")

            cursor.close()
            conn.close()

            rec_ef = sum([r[1] for r in efetivo if r[0] == 'Receita'])
            des_ef = sum([r[1] for r in efetivo if r[0] in ['Despesa', 'Transferência']])
            saldo_ef = rec_ef - des_ef

            rec_pr = sum([r[1] for r in previsto if r[0] == 'Receita'])
            des_pr = sum([r[1] for r in previsto if r[0] in ['Despesa', 'Transferência']])
            saldo_pr = rec_pr - des_pr

            self.lbl_saldo_efetivo.config(text=f"R$ {saldo_ef:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.lbl_saldo_previsto.config(text=f"R$ {saldo_pr:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        except Exception as e:
            print(f"Erro saldos: {e}")

    def limpar_campos(self):
        self.lancamento_selecionado_id = None
        self.cb_tipo.set("Receita")
        self.ao_mudar_tipo()
        self.var_valor.set("0,00")
        self.var_status.set(True)
        self.var_data.set(datetime.now().strftime("%d/%m/%Y"))
        self.txt_desc.delete(0, tk.END)
        self.cb_cat.set("")
        self.cb_sub.set("")
        self.cb_conta.set("")
        self.cb_conta_destino.set("")
        self.txt_repetir.delete(0, tk.END)
        self.txt_repetir.insert(0, "1")
        self.btn_salvar.config(text="Cadastrar Receita", bg="#2B6CB0")
        self.btn_excluir.pack_forget()
        self.carregar_combos()
        self.cb_tipo.focus_set()

    def selecionar_registro(self, event):
        selecao = self.tabela.selection()
        if not selecao:
            return
        item_id = selecao[0]
        tags = self.tabela.item(item_id, "tags")
        if not tags:
            return

        lid = tags[-1]
        if str(lid).startswith("fat_"):
            messagebox.showinfo("Informação", "Esta é uma fatura consolidada de cartão. Para alterá-la, gerencie os lançamentos individuais na aba 'Despesas de Cartão'.")
            return

        self.lancamento_selecionado_id = lid

        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_conta, repeticoes, id_conta_destino 
                FROM lancamentos WHERE id = %s;
            """, (self.lancamento_selecionado_id,))
            reg = cursor.fetchone()
            cursor.close()
            conn.close()

            if reg:
                tipo, valor, recebido, data_lanc, desc, id_cat, id_sub, id_conta, repeticoes, id_conta_dest = reg

                self.cb_tipo.set(tipo)
                self.ao_mudar_tipo()
                
                val_str = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.var_valor.set(val_str)
                self.var_status.set(bool(recebido))
                self.var_data.set(data_lanc.strftime("%d/%m/%Y") if data_lanc else "")
                
                self.txt_desc.delete(0, tk.END)
                self.txt_desc.insert(0, desc or "")

                if tipo != "Transferência":
                    cat_nome = self.map_cat_rev.get(str(id_cat), "")
                    self.cb_cat.set(cat_nome)
                    self.ao_mudar_categoria()

                    if id_sub:
                        for nome_s, id_s in self.map_sub.items():
                            if str(id_s) == str(id_sub):
                                self.cb_sub.set(nome_s)
                                break
                    else:
                        self.cb_sub.set("")
                else:
                    dest_nome = self.map_conta_rev.get(str(id_conta_dest), "")
                    self.cb_conta_destino.set(dest_nome)

                conta_nome = self.map_conta_rev.get(str(id_conta), "")
                self.cb_conta.set(conta_nome)

                self.txt_repetir.delete(0, tk.END)
                self.txt_repetir.insert(0, str(repeticoes or 1))

                cor_botao = "#C53030" if tipo == "Despesa" else ("#D69E2E" if tipo == "Transferência" else "#D69E2E")
                self.btn_salvar.config(text="Salvar Alterações", bg=cor_botao)
                self.btn_excluir.pack(side="left", padx=(0, 4))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar registro: {e}")

    def salvar_ou_alterar(self):
        val_str = self.var_valor.get().replace(".", "").replace(",", ".")
        conta_nome = self.cb_conta.get()
        tipo = self.cb_tipo.get()

        if not val_str or not conta_nome:
            messagebox.showwarning("Aviso", "Preencha o valor e a conta!")
            return

        if tipo != "Transferência" and not self.cb_cat.get():
            messagebox.showwarning("Aviso", "Preencha a categoria!")
            return

        if tipo == "Transferência" and not self.cb_conta_destino.get():
            messagebox.showwarning("Aviso", "Selecione a conta de destino!")
            return

        if tipo == "Transferência" and self.cb_conta.get() == self.cb_conta_destino.get():
            messagebox.showwarning("Aviso", "A conta de origem e a conta de destino não podem ser iguais!")
            return

        if not is_data_valida(self.var_data.get()):
            messagebox.showwarning("Aviso", "Data inválida!")
            return

        try:
            valor = float(val_str)
            recebido = self.var_status.get()
            d_parts = self.var_data.get().split("/")
            data_base = datetime(int(d_parts[2]), int(d_parts[1]), int(d_parts[0]))
            data_str_sql = data_base.strftime("%Y-%m-%d")

            desc = self.txt_desc.get().strip() or tipo
            id_conta = self.map_conta.get(conta_nome)

            conn = conectar_banco()
            cursor = conn.cursor()

            if tipo == "Transferência":
                id_conta_dest = self.map_conta.get(self.cb_conta_destino.get())
                desc_saida = f"Transferência enviada para {self.cb_conta_destino.get()}"
                desc_entrada = f"Transferência recebida de {conta_nome}"
                if desc and desc != "Transferência":
                    desc_saida = f"Transf: {desc}"
                    desc_entrada = f"Transf: {desc}"

                if self.lancamento_selecionado_id:
                    cursor.execute("""
                        UPDATE lancamentos 
                        SET tipo = 'Transferência', valor = %s, recebido = %s, data_lancamento = %s, 
                            descricao = %s, id_conta = %s, id_conta_destino = %s, id_categoria = NULL, id_subcategoria = NULL 
                        WHERE id = %s;
                    """, (valor, recebido, data_str_sql, desc_saida, id_conta, id_conta_dest, self.lancamento_selecionado_id))
                    
                    cursor.execute("""
                        UPDATE lancamentos 
                        SET tipo = 'Receita', valor = %s, recebido = %s, data_lancamento = %s, 
                            descricao = %s, id_conta = %s, id_conta_destino = NULL 
                        WHERE id_conta_destino = %s AND data_lancamento = %s;
                    """, (valor, recebido, data_str_sql, desc_entrada, id_conta_dest, self.lancamento_selecionado_id))
                    
                    msg = "Transferência alterada com sucesso!"
                else:
                    cursor.execute("""
                        INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_conta, id_conta_destino)
                        VALUES ('Transferência', %s, %s, %s, %s, %s, %s) RETURNING id;
                    """, (valor, recebido, data_str_sql, desc_saida, id_conta, id_conta_dest))
                    novo_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_conta, id_conta_destino)
                        VALUES ('Receita', %s, %s, %s, %s, %s, %s);
                    """, (valor, recebido, data_str_sql, desc_entrada, id_conta_dest, novo_id))

                    msg = "Transferência cadastrada com sucesso!"
            else:
                id_cat = self.map_cat.get(self.cb_cat.get())
                id_sub = self.map_sub.get(self.cb_sub.get()) if self.cb_sub.get() else None

                if self.lancamento_selecionado_id:
                    cursor.execute("""
                        UPDATE lancamentos 
                        SET tipo = %s, valor = %s, recebido = %s, data_lancamento = %s, 
                            descricao = %s, id_categoria = %s, id_subcategoria = %s, id_conta = %s, id_conta_destino = NULL 
                        WHERE id = %s;
                    """, (tipo, valor, recebido, data_str_sql, desc, id_cat, id_sub, id_conta, self.lancamento_selecionado_id))
                    msg = "Lançamento alterado com sucesso!"
                else:
                    repeticoes = int(self.txt_repetir.get().strip() or 1)
                    for i in range(repeticoes):
                        data_parcela = data_base + relativedelta(months=i)
                        desc_final = f"{desc} ({i+1}/{repeticoes})" if repeticoes > 1 else desc
                        
                        cursor.execute("""
                            INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_conta, repeticoes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """, (tipo, valor, recebido, data_parcela.strftime("%Y-%m-%d"), desc_final, id_cat, id_sub, id_conta, repeticoes))
                    msg = "Lançamento(s) cadastrado(s) com sucesso!"

            conn.commit()
            cursor.close()
            conn.close()

            messagebox.showinfo("Sucesso", msg)
            self.limpar_campos()
            self.carregar_dados()
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao salvar: {ex}")

    def excluir_lancamento(self):
        if not self.lancamento_selecionado_id:
            return
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este lançamento?"):
            try:
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lancamentos WHERE id = %s;", (self.lancamento_selecionado_id,))
                conn.commit()
                cursor.close()
                conn.close()

                messagebox.showinfo("Sucesso", "Lançamento excluído com sucesso!")
                self.limpar_campos()
                self.carregar_dados()
            except Exception as ex:
                messagebox.showerror("Erro", f"Erro ao excluir: {ex}")

    def recarregar(self):
        self.carregar_combos()
        self.carregar_dados()