from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import calendar
import tkinter as tk
from tkinter import ttk
from database import conectar_banco


class AbaResumo:

  def __init__(self, parent):
    self.parent = parent
    self.categoria_selecionada_filtro = None

    # Container Principal com Rolagem ou Padding elegante
    self.main_frame = tk.Frame(parent, bg="#F0F0F0")
    self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Título de Boas-Vindas
    lbl_titulo = tk.Label(
        self.main_frame,
        text="Visão Geral do Sistema Financeiro",
        font=("Arial", 14, "bold"),
        bg="#F0F0F0",
        fg="#1A365D",
    )
    lbl_titulo.pack(anchor="w", pady=(0, 10))

    # --- 1. CARDS DE INDICADORES (KPIs) - MÊS ATUAL ---
    frame_cards = tk.Frame(self.main_frame, bg="#F0F0F0")
    frame_cards.pack(fill="x", pady=(0, 10))

    # Card Receitas do Mês
    self.card_receita = self.criar_card(
        frame_cards, "Receitas (Mês Atual)", "R$ 0,00", "#319795"
    )
    self.card_receita.pack(side="left", fill="x", expand=True, padx=(0, 5))

    # Card Despesas do Mês
    self.card_despesa = self.criar_card(
        frame_cards, "Despesas (Mês Atual)", "R$ 0,00", "#C53030"
    )
    self.card_despesa.pack(side="left", fill="x", expand=True, padx=5)

    # Card Contas Cadastradas (Dinâmico: uma linha por conta)
    self.card_contas = self.criar_card_contas(
        frame_cards, "Saldo Contas (Até Hoje)"
    )
    self.card_contas.pack(side="left", fill="x", expand=True, padx=5)

    # Card Cartões Cadastradas (Fatura Atual/Total)
    self.card_cartoes_val = self.criar_card(
        frame_cards, "Faturas / Cartões Atuais", "R$ 0,00", "#2B6CB0"
    )
    self.card_cartoes_val.pack(side="left", fill="x", expand=True, padx=(5, 0))

    # --- 2. PAINÉIS INFERIORES (2 Colunas) ---
    frame_inferior = tk.Frame(self.main_frame, bg="#F0F0F0")
    frame_inferior.pack(fill="both", expand=True)

    # Coluna Esquerda: Despesas por Categoria / Subcategoria (Unificada)
    frame_esq = tk.LabelFrame(
        frame_inferior,
        text=(
            " Despesas por Categoria / Subcategoria (Duplo clique"
            " expande/filtra, Duplo fora limpa) "
        ),
        font=("Arial", 10, "bold"),
        bg="#F0F0F0",
        padx=10,
        pady=10,
    )
    frame_esq.pack(side="left", fill="both", expand=True, padx=(0, 8))

    colunas_cat = ("Categoria", "Total Cat.", "Subcategoria", "Total Sub.")
    self.tabela_cat = ttk.Treeview(
        frame_esq, columns=colunas_cat, show="headings", height=10
    )

    for col in colunas_cat:
      self.tabela_cat.heading(
          col,
          text=col,
          command=lambda c=col: self.ordenar_tabela(
              self.tabela_cat, c, False
          ),
      )

    self.tabela_cat.column("Categoria", width=130, anchor="w")
    self.tabela_cat.column("Total Cat.", width=85, anchor="e")
    self.tabela_cat.column("Subcategoria", width=130, anchor="w")
    self.tabela_cat.column("Total Sub.", width=85, anchor="e")
    self.tabela_cat.pack(side="top", fill="both", expand=True)

    self.tabela_cat.bind("<Double-1>", self.ao_duplo_clique_categoria)

    frame_total_cat = tk.Frame(
        frame_esq, bg="white", bd=1, relief="solid", padx=8, pady=5
    )
    frame_total_cat.pack(fill="x", pady=(5, 0))
    tk.Label(
        frame_total_cat,
        text="Total Despesas:",
        font=("Arial", 8, "bold"),
        fg="#718096",
        bg="white",
    ).pack(side="left")
    self.lbl_total_cat = tk.Label(
        frame_total_cat,
        text="R$ 0,00",
        font=("Arial", 10, "bold"),
        fg="#C53030",
        bg="white",
    )
    self.lbl_total_cat.pack(side="right")

    # Coluna Direita: Movimentações por Período de Cartão ou Mês
    frame_dir = tk.LabelFrame(
        frame_inferior,
        text=" Movimentações por Período do Cartão / Mês ",
        font=("Arial", 10, "bold"),
        bg="#F0F0F0",
        padx=10,
        pady=10,
    )
    frame_dir.pack(side="right", fill="both", expand=True, padx=(8, 0))

    # Sub-barra de Filtros de Cartão e Ciclo
    frame_filtro_cartao = tk.Frame(frame_dir, bg="#F0F0F0")
    frame_filtro_cartao.pack(fill="x", pady=(0, 5))

    tk.Label(
        frame_filtro_cartao, text="Cartão:", font=("Arial", 8), bg="#F0F0F0"
    ).pack(side="left", padx=(0, 2))
    self.cb_filtro_cartao = ttk.Combobox(
        frame_filtro_cartao, width=15, state="readonly"
    )
    self.cb_filtro_cartao.pack(side="left", padx=(0, 5))
    self.cb_filtro_cartao.bind(
        "<<ComboboxSelected>>", self.ao_mudar_cartao_resumo
    )

    tk.Label(
        frame_filtro_cartao,
        text="Período/Ciclo:",
        font=("Arial", 8),
        bg="#F0F0F0",
    ).pack(side="left", padx=(0, 2))
    # Largura aumentada para 44 para evitar cortes no texto do período/fatura
    self.cb_filtro_ciclo = ttk.Combobox(
        frame_filtro_cartao, width=35, state="readonly"
    )
    self.cb_filtro_ciclo.pack(side="left", padx=(0, 5))
    self.cb_filtro_ciclo.bind(
        "<<ComboboxSelected>>",
        lambda e: self.carregar_movimentacoes_mes(
            self.categoria_selecionada_filtro
        ),
    )

    btn_limpar_cartao = tk.Button(
        frame_filtro_cartao,
        text="Limpar",
        font=("Arial", 8),
        command=self.limpar_filtro_cartao,
    )
    btn_limpar_cartao.pack(side="left")

    colunas_ult = ("Data", "Descrição", "Subcategoria", "Valor", "Status")
    self.tabela_ult = ttk.Treeview(
        frame_dir, columns=colunas_ult, show="headings", height=8
    )

    for col in colunas_ult:
      self.tabela_ult.heading(
          col,
          text=col,
          command=lambda c=col: self.ordenar_tabela(self.tabela_ult, c, False),
      )

    self.tabela_ult.column("Data", width=75, anchor="center")
    self.tabela_ult.column("Descrição", width=120, anchor="w")
    self.tabela_ult.column("Subcategoria", width=100, anchor="w")
    self.tabela_ult.column("Valor", width=85, anchor="e")
    self.tabela_ult.column("Status", width=65, anchor="center")
    self.tabela_ult.pack(side="top", fill="both", expand=True)

    self.tabela_ult.bind(
        "<Double-1>", lambda e: self.resetar_filtros_tabela()
    )

    frame_total_mov = tk.Frame(
        frame_dir, bg="white", bd=1, relief="solid", padx=8, pady=5
    )
    frame_total_mov.pack(fill="x", pady=(5, 0))
    tk.Label(
        frame_total_mov,
        text="Soma do Período/Filtro:",
        font=("Arial", 8, "bold"),
        fg="#718096",
        bg="white",
    ).pack(side="left")
    self.lbl_total_mov = tk.Label(
        frame_total_mov,
        text="R$ 0,00",
        font=("Arial", 10, "bold"),
        fg="#2B6CB0",
        bg="white",
    )
    self.lbl_total_mov.pack(side="right")

    self.map_cartoes = {}
    self.map_cartao_detalhes = {}
    self.ciclos_disponiveis_cache = []

    self.carregar_dados()

  def criar_card(self, parent, titulo, valor_inicial, cor_texto):
    card_frame = tk.Frame(
        parent, bg="white", bd=1, relief="solid", padx=10, pady=8
    )

    lbl_tit = tk.Label(
        card_frame,
        text=titulo,
        font=("Arial", 8, "bold"),
        fg="#718096",
        bg="white",
    )
    lbl_tit.pack(anchor="w")

    lbl_val = tk.Label(
        card_frame,
        text=valor_inicial,
        font=("Arial", 12, "bold"),
        fg=cor_texto,
        bg="white",
    )
    lbl_val.pack(anchor="w", pady=(2, 0))

    card_frame.lbl_valor = lbl_val
    return card_frame

  def criar_card_contas(self, parent, titulo):
    card_frame = tk.Frame(
        parent, bg="white", bd=1, relief="solid", padx=10, pady=8
    )

    lbl_tit = tk.Label(
        card_frame,
        text=titulo,
        font=("Arial", 8, "bold"),
        fg="#718096",
        bg="white",
    )
    lbl_tit.pack(anchor="w", pady=(0, 2))

    frame_linhas_contas = tk.Frame(card_frame, bg="white")
    frame_linhas_contas.pack(anchor="w", fill="x")

    card_frame.frame_linhas = frame_linhas_contas
    return card_frame

  def formatar_moeda(self, valor):
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

  def ordenar_tabela(self, treeview, coluna, reverse):
    l = [(treeview.set(k, coluna), k) for k in treeview.get_children("")]

    try:
      l.sort(
          key=lambda t: float(
              t[0]
              .replace("R$", "")
              .replace(".", "")
              .replace(",", ".")
              .strip()
          ),
          reverse=reverse,
      )
    except ValueError:
      try:
        l.sort(
            key=lambda t: datetime.strptime(t[0], "%d/%m/%Y"), reverse=reverse
        )
      except ValueError:
        l.sort(key=lambda t: t[0].lower(), reverse=reverse)

    for index, (val, k) in enumerate(l):
      treeview.move(k, "", index)

    seta = " ▼" if reverse else " ▲"
    for col in treeview["columns"]:
      if col == coluna:
        treeview.heading(
            col,
            text=f"{col}{seta}",
            command=lambda c=col: self.ordenar_tabela(treeview, c, not reverse),
        )
      else:
        treeview.heading(
            col,
            text=col,
            command=lambda c=col: self.ordenar_tabela(treeview, c, False),
        )

  def carregar_combos_cartoes(self):
    try:
      conn = conectar_banco()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, nome, dia_fechamento, dia_vencimento FROM cartoes ORDER BY"
          " nome;"
      )
      cartoes = cursor.fetchall()

      self.map_cartoes.clear()
      self.map_cartao_detalhes.clear()
      nomes_cartoes = []
      for cid, cnome, c_fech, c_venc in cartoes:
        self.map_cartoes[cnome] = cid
        self.map_cartao_detalhes[cid] = {
            "fechamento": c_fech or 24,
            "vencimento": c_venc or 1,
        }
        nomes_cartoes.append(cnome)

      self.cb_filtro_cartao["values"] = nomes_cartoes
      cursor.close()
      conn.close()
    except Exception as e:
      print(f"Erro ao carregar cartões no resumo: {e}")

  def carregar_dados(self):
    try:
      self.carregar_combos_cartoes()
      conn = conectar_banco()
      cursor = conn.cursor()

      # 1. Receitas e Despesas do Mês Atual
      mes_atual = datetime.now().strftime("%Y-%m")
      cursor.execute(
          """
                SELECT tipo, SUM(valor) FROM lancamentos 
                WHERE TO_CHAR(data_lancamento, 'YYYY-MM') = %s 
                GROUP BY tipo;
            """,
          (mes_atual,),
      )
      mes_dados = cursor.fetchall()

      rec_mes = sum([r[1] for r in mes_dados if r[0] == "Receita"])
      des_mes = sum([r[1] for r in mes_dados if r[0] == "Despesa"])

      self.card_receita.lbl_valor.config(text=self.formatar_moeda(rec_mes))
      self.card_despesa.lbl_valor.config(text=self.formatar_moeda(des_mes))

      # 2. Saldo atual acumulado de cada conta cadastrada até hoje
      for widget in self.card_contas.frame_linhas.winfo_children():
        widget.destroy()

      cursor.execute(
          "SELECT id, instituicao FROM contas ORDER BY instituicao;"
      )
      contas_db = cursor.fetchall()

      for c_id, c_inst in contas_db:
        cursor.execute(
            "SELECT tipo, SUM(valor) FROM lancamentos WHERE recebido = TRUE AND"
            " data_lancamento <= CURRENT_DATE AND id_conta = %s GROUP BY"
            " tipo;",
            (c_id,),
        )
        ef_c = cursor.fetchall()
        r_ef = sum([r[1] for r in ef_c if r[0] == "Receita"])
        d_ef = sum(
            [r[1] for r in ef_c if r[0] in ["Despesa", "Transferência"]]
        )
        s_ef = r_ef - d_ef

        lbl_linha = tk.Label(
            self.card_contas.frame_linhas,
            text=f"{c_inst}: {self.formatar_moeda(s_ef)}",
            font=("Arial", 9, "bold"),
            fg="#2F855A",
            bg="white",
        )
        lbl_linha.pack(anchor="w", pady=(1, 1))

      # 3. Valor atual das faturas/cartões do mês corrente
      cursor.execute(
          """
                SELECT SUM(valor) FROM lancamentos 
                WHERE id_cartao IS NOT NULL AND TO_CHAR(data_lancamento, 'YYYY-MM') = %s;
            """,
          (mes_atual,),
      )
      res_cartoes = cursor.fetchone()
      total_cartoes = float(res_cartoes[0] or 0) if res_cartoes else 0.0
      self.card_cartoes_val.lbl_valor.config(
          text=self.formatar_moeda(total_cartoes)
      )

      # 4. Carregar Tabela Esquerda (Categorias e Subcategorias)
      self.atualizar_tabela_categorias()

      # 5. Popula os ciclos do cartão padrão ou mês atual na tabela direita
      self.popular_combobox_ciclos()
      self.carregar_movimentacoes_mes()

      cursor.close()
      conn.close()
    except Exception as e:
      print(f"Erro ao carregar dados do resumo: {e}")

  def popular_combobox_ciclos(self):
    cartao_selecionado = self.cb_filtro_cartao.get()
    cartao_id = self.map_cartoes.get(cartao_selecionado)

    # Dicionário de tradução fixa de meses para Português
    meses_pt = {
        "January": "Janeiro",
        "February": "Fevereiro",
        "March": "Março",
        "April": "Abril",
        "May": "Maio",
        "June": "Junho",
        "July": "Julho",
        "August": "Agosto",
        "September": "Setembro",
        "October": "Outubro",
        "November": "Novembro",
        "December": "Dezembro",
    }

    ciclos = []
    if cartao_id:
      detalhes = self.map_cartao_detalhes.get(cartao_id, {"fechamento": 24})
      fechamento_dia = detalhes["fechamento"]

      try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT MIN(data_lancamento), MAX(data_lancamento) FROM lancamentos"
            " WHERE id_cartao = %s;",
            (cartao_id,),
        )
        res = cursor.fetchone()
        cursor.close()
        conn.close()

        def para_date(val):
          if not val:
            return None
          if hasattr(val, "date"):
            return val.date()
          return val

        min_data = (
            para_date(res[0])
            if res and res[0]
            else date.today() - relativedelta(months=3)
        )
        max_data = (
            para_date(res[1])
            if res and res[1]
            else date.today() + relativedelta(months=6)
        )

        curr_date = date(min_data.year, min_data.month, 1)
        end_date = date(max_data.year, max_data.month, 1) + relativedelta(
            months=2
        )

        while curr_date <= end_date:
          r_ano = curr_date.year
          r_mes = curr_date.month
          max_d_fim = calendar.monthrange(r_ano, r_mes)[1]
          data_fim = date(r_ano, r_mes, min(fechamento_dia, max_d_fim))
          data_ini = (
              data_fim - relativedelta(months=1) + relativedelta(days=1)
          )

          rotulo = (
              f"Fatura {data_fim.strftime('%m/%Y')}"
              f" ({data_ini.strftime('%d/%m/%Y')} a"
              f" {data_fim.strftime('%d/%m/%Y')})"
          )
          ciclos.append((rotulo, data_ini, data_fim))

          curr_date += relativedelta(months=1)
      except Exception as e:
        print(f"Erro ao gerar ciclos de cartão: {e}")
    else:
      hoje = date.today()
      for i in range(-3, 12):
        m_ref = hoje + relativedelta(months=i)
        # Formata o mês em inglês e substitui pelo correspondente em português
        rotulo_bruto = m_ref.strftime("%m/%Y (%B %Y)")
        rotulo = rotulo_bruto
        for eng, pt in meses_pt.items():
          rotulo = rotulo.replace(eng, pt)
        ciclos.append((rotulo, m_ref.strftime("%Y-%m")))

    self.ciclos_disponiveis_cache = ciclos
    self.cb_filtro_ciclo["values"] = [c[0] for c in ciclos]

    if ciclos:
      hoje_str = date.today().strftime("%m/%Y")
      selecionado = False
      for idx, c in enumerate(ciclos):
        if cartao_id and hoje_str in c[0]:
          self.cb_filtro_ciclo.current(idx)
          selecionado = True
          break
        elif not cartao_id and date.today().strftime("%Y-%m") in str(c[1]):
          self.cb_filtro_ciclo.current(idx)
          selecionado = True
          break
      if not selecionado and ciclos:
        self.cb_filtro_ciclo.current(0)

  def ao_mudar_cartao_resumo(self, event=None):
    self.popular_combobox_ciclos()
    self.carregar_movimentacoes_mes(self.categoria_selecionada_filtro)

  def atualizar_tabela_categorias(self):
    for row in self.tabela_cat.get_children():
      self.tabela_cat.delete(row)

    try:
      conn = conectar_banco()
      cursor = conn.cursor()
      mes_atual = datetime.now().strftime("%Y-%m")

      if self.categoria_selecionada_filtro:
        cursor.execute(
            """
                    SELECT c.descricao, s.descricao, SUM(l.valor) 
                    FROM lancamentos l
                    JOIN categorias c ON l.id_categoria = c.id_categoria
                    LEFT JOIN subcategorias s ON l.id_subcategoria = s.id_subcategoria
                    WHERE l.tipo = 'Despesa' AND TO_CHAR(l.data_lancamento, 'YYYY-MM') = %s AND c.descricao = %s
                    GROUP BY c.descricao, s.descricao
                    ORDER BY SUM(l.valor) DESC;
                """,
            (mes_atual, self.categoria_selecionada_filtro),
        )
        subs = cursor.fetchall()

        total_cat_filtrada = 0.0
        for c_desc, s_desc, s_val in subs:
          v_sub = float(s_val or 0)
          total_cat_filtrada += v_sub
          s_nome = s_desc if s_desc else "Geral / Sem Sub."
          self.tabela_cat.insert(
              "",
              "end",
              values=(
                  c_desc,
                  self.formatar_moeda(total_cat_filtrada),
                  s_nome,
                  self.formatar_moeda(v_sub),
              ),
          )

        self.lbl_total_cat.config(text=self.formatar_moeda(total_cat_filtrada))
      else:
        cursor.execute(
            """
                    SELECT c.descricao, SUM(l.valor) 
                    FROM lancamentos l
                    JOIN categorias c ON l.id_categoria = c.id_categoria
                    WHERE l.tipo = 'Despesa' AND TO_CHAR(l.data_lancamento, 'YYYY-MM') = %s
                    GROUP BY c.descricao
                    ORDER BY SUM(l.valor) DESC;
                """,
            (mes_atual,),
        )
        cats = cursor.fetchall()

        total_categorias = 0.0
        for cat_desc, cat_val in cats:
          v_cat = float(cat_val or 0)
          total_categorias += v_cat
          self.tabela_cat.insert(
              "",
              "end",
              values=(
                  cat_desc,
                  self.formatar_moeda(v_cat),
                  "",
                  "",
              ),
          )

        self.lbl_total_cat.config(text=self.formatar_moeda(total_categorias))

      cursor.close()
      conn.close()
    except Exception as e:
      print(f"Erro ao atualizar tabela de categorias: {e}")

  def carregar_movimentacoes_mes(self, categoria_nome=None):
    try:
      for row in self.tabela_ult.get_children():
        self.tabela_ult.delete(row)

      conn = conectar_banco()
      cursor = conn.cursor()

      cartao_selecionado = self.cb_filtro_cartao.get()
      cartao_id = self.map_cartoes.get(cartao_selecionado)
      ciclo_idx = self.cb_filtro_ciclo.current()

      query = """
                SELECT l.data_lancamento, l.descricao, s.descricao AS sub_desc, l.valor, l.recebido, l.tipo 
                FROM lancamentos l
                LEFT JOIN categorias c ON l.id_categoria = c.id_categoria
                LEFT JOIN subcategorias s ON l.id_subcategoria = s.id_subcategoria
                WHERE 1=1
            """
      params = []

      if cartao_id:
        query += " AND l.id_cartao = %s"
        params.append(cartao_id)

        if ciclo_idx >= 0 and ciclo_idx < len(self.ciclos_disponiveis_cache):
          _, d_ini, d_fim = self.ciclos_disponiveis_cache[ciclo_idx]
          query += (
              " AND l.data_lancamento >= %s AND l.data_lancamento <= %s"
          )
          params.extend([d_ini, d_fim])
      else:
        if ciclo_idx >= 0 and ciclo_idx < len(self.ciclos_disponiveis_cache):
          _, mes_str = self.ciclos_disponiveis_cache[ciclo_idx]
          query += (
              " AND TO_CHAR(l.data_lancamento, 'YYYY-MM') = %s AND"
              " l.id_cartao IS NULL"
          )
          params.append(mes_str)
        else:
          mes_atual = datetime.now().strftime("%Y-%m")
          query += (
              " AND TO_CHAR(l.data_lancamento, 'YYYY-MM') = %s AND"
              " l.id_cartao IS NULL"
          )
          params.append(mes_atual)

      if categoria_nome:
        query += " AND c.descricao = %s"
        params.append(categoria_nome)

      query += " ORDER BY l.data_lancamento DESC, l.id DESC;"

      cursor.execute(query, tuple(params))
      movimentos = cursor.fetchall()

      soma_movimentos = 0.0
      for data, desc, sub_desc, val, rec, tipo in movimentos:
        data_str = data.strftime("%d/%m/%Y") if data else ""
        sub_str = sub_desc if sub_desc else "-"
        status_str = "Pago/Rec." if rec else "Pendente"
        val_num = float(val or 0)

        soma_movimentos += val_num
        val_formatado = self.formatar_moeda(val_num)
        self.tabela_ult.insert(
            "",
            "end",
            values=(
                data_str,
                desc or "",
                sub_str,
                val_formatado,
                status_str,
            ),
        )

      self.lbl_total_mov.config(text=self.formatar_moeda(soma_movimentos))

      cursor.close()
      conn.close()
    except Exception as e:
      print(f"Erro ao carregar movimentações: {e}")

  def ao_duplo_clique_categoria(self, event):
    selecao = self.tabela_cat.selection()
    if not selecao:
      return
    item = self.tabela_cat.item(selecao[0])
    valores = item["values"]
    if not valores:
      return

    cat_nome = valores[0]

    if self.categoria_selecionada_filtro:
      self.categoria_selecionada_filtro = None
    else:
      self.categoria_selecionada_filtro = cat_nome

    self.atualizar_tabela_categorias()
    self.carregar_movimentacoes_mes(self.categoria_selecionada_filtro)

  def limpar_filtro_cartao(self):
    self.cb_filtro_cartao.set("")
    self.popular_combobox_ciclos()
    self.carregar_movimentacoes_mes(self.categoria_selecionada_filtro)

  def resetar_filtros_tabela(self):
    self.categoria_selecionada_filtro = None
    self.atualizar_tabela_categorias()
    self.carregar_movimentacoes_mes(None)

  def recarregar(self):
    self.categoria_selecionada_filtro = None
    self.carregar_dados()