import tkinter as tk
from tkinter import ttk
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database import conectar_banco

# Importações do Matplotlib para integração com Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AbaGraficos:
    def __init__(self, parent):
        self.parent = parent

        # Container principal com rolagem ou frame expansível
        self.main_frame = tk.Frame(parent, bg="#F0F0F0")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título da Aba
        lbl_titulo = tk.Label(self.main_frame, text="Painel de Análise Gráfica e Indicadores", font=("Arial", 14, "bold"), bg="#F0F0F0", fg="#1A365D")
        lbl_titulo.pack(anchor="w", pady=(0, 10))

        # Criando a Figura do Matplotlib com uma grade 2x2 (4 subplots)
        self.fig = Figure(figsize=(12, 7), facecolor="#F0F0F0")
        
        # 4 Subgráficos
        self.ax1 = self.fig.add_subplot(221) # Rosca: Despesas por Categoria
        self.ax2 = self.fig.add_subplot(222) # Barras: Receitas vs Despesas (Meses)
        self.ax3 = self.fig.add_subplot(223) # Linha: Evolução do Saldo
        self.ax4 = self.fig.add_subplot(224) # Barras Horiz: Cartões

        self.fig.tight_layout(pad=3.0)

        # Renderizando o canvas do Matplotlib dentro do Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Carrega os dados e desenha os gráficos
        self.carregar_graficos()

    def carregar_graficos(self):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()
            mes_atual = datetime.now().strftime("%Y-%m")

            # Limpa os eixos anteriores para redesenhar
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()
            self.ax4.clear()

            # ----------------------------------------------------
            # GRÁFICO 1: Rosca - Despesas por Categoria (Mês Atual)
            # ----------------------------------------------------
            cursor.execute("""
                SELECT c.descricao, SUM(l.valor) 
                FROM lancamentos l
                JOIN categorias c ON l.id_categoria = c.id_categoria
                WHERE l.tipo = 'Despesa' AND TO_CHAR(l.data_lancamento, 'YYYY-MM') = %s
                GROUP BY c.descricao
                ORDER BY SUM(l.valor) DESC;
            """, (mes_atual,))
            dados_cat = cursor.fetchall()

            if dados_cat:
                cats = [item[0] for item in dados_cat]
                valores_cat = [float(item[1]) for item in dados_cat]
                
                # Gráfico de Rosca (Donut)
                wedges, texts, autotexts = self.ax1.pie(
                    valores_cat, labels=cats, autopct='%1.1f%%', 
                    startangle=140, colors=["#C53030", "#DD6B20", "#D69E2E", "#319795", "#2B6CB0", "#805AD5"]
                )
                for text in texts + autotexts:
                    text.set_fontsize(8)
                # Buraco no meio para virar Rosca
                self.ax1.add_artist(matplotlib.patches.Circle((0,0), 0.70, fc='#F0F0F0'))
            else:
                self.ax1.text(0.5, 0.5, "Sem despesas no mês", horizontalalignment='center', verticalalignment='center', fontsize=10, color="#718096")
            
            self.ax1.set_title("Despesas por Categoria (Mês Atual)", fontsize=10, fontweight="bold", color="#1A365D")

            # ----------------------------------------------------
            # GRÁFICO 2: Barras - Receitas vs Despesas (Últimos 6 Meses)
            # ----------------------------------------------------
            meses_labels = []
            rec_valores = []
            des_valores = []

            for i in range(5, -1, -1):
                d_ref = datetime.now() - relativedelta(months=i)
                m_str = d_ref.strftime("%Y-%m")
                meses_labels.append(d_ref.strftime("%b/%Y"))

                cursor.execute("""
                    SELECT tipo, SUM(valor) FROM lancamentos 
                    WHERE TO_CHAR(data_lancamento, 'YYYY-MM') = %s 
                    GROUP BY tipo;
                """, (m_str,))
                res_mes = cursor.fetchall()
                
                r = sum([float(x[1]) for x in res_mes if x[0] == 'Receita'])
                d = sum([float(x[1]) for x in res_mes if x[0] == 'Despesa'])
                rec_valores.append(r)
                des_valores.append(d)

            x = range(len(meses_labels))
            largura = 0.35
            self.ax2.bar([p - largura/2 for p in x], rec_valores, width=largura, label="Receitas", color="#2F855A")
            self.ax2.bar([p + largura/2 for p in x], des_valores, width=largura, label="Despesas", color="#C53030")
            
            self.ax2.set_xticks(x)
            self.ax2.set_xticklabels(meses_labels, fontsize=8)
            self.ax2.legend(fontsize=8)
            self.ax2.set_title("Receitas x Despesas (Últimos 6 Meses)", fontsize=10, fontweight="bold", color="#1A365D")
            self.ax2.tick_params(axis='y', labelsize=8)

            # ----------------------------------------------------
            # GRÁFICO 3: Linha - Evolução do Saldo Acumulado (Mês Atual)
            # ----------------------------------------------------
            cursor.execute("""
                SELECT data_lancamento, tipo, valor FROM lancamentos 
                WHERE TO_CHAR(data_lancamento, 'YYYY-MM') = %s
                ORDER BY data_lancamento ASC;
            """, (mes_atual,))
            lanc_mes = cursor.fetchall()

            dias_x = []
            saldos_y = []
            saldo_acumulado = 0.0

            # Organiza por dia do mês
            diario = {}
            for data_l, tipo_l, val_l in lanc_mes:
                dia_key = data_l.strftime("%d/%m")
                if dia_key not in diario:
                    diario[dia_key] = 0.0
                if tipo_l == 'Receita':
                    diario[dia_key] += float(val_l or 0)
                else:
                    diario[dia_key] -= float(val_l or 0)

            for dia, val in diario.items():
                saldo_acumulado += val
                dias_x.append(dia)
                saldos_y.append(saldo_acumulado)

            if dias_x:
                self.ax3.plot(dias_x, saldos_y, marker='o', color="#2B6CB0", linewidth=2, markersize=4)
                self.ax3.axhline(0, color='gray', linestyle='--', linewidth=0.8)
                self.ax3.tick_params(axis='x', labelsize=7, rotation=30)
                self.ax3.tick_params(axis='y', labelsize=8)
            else:
                self.ax3.text(0.5, 0.5, "Sem movimentações no mês", horizontalalignment='center', verticalalignment='center', fontsize=10, color="#718096")

            self.ax3.set_title("Evolução do Saldo Diário (Mês Atual)", fontsize=10, fontweight="bold", color="#1A365D")
            self.ax3.grid(True, linestyle=":", alpha=0.6)

            # ----------------------------------------------------
            # GRÁFICO 4: Barras Horizontais - Comprometimento por Cartão
            # ----------------------------------------------------
            cursor.execute("""
                SELECT ct.nome, SUM(l.valor) 
                FROM lancamentos l
                JOIN cartoes ct ON l.id_cartao = ct.id
                WHERE l.recebido = FALSE
                GROUP BY ct.nome
                ORDER BY SUM(l.valor) ASC;
            """)
            dados_cartao = cursor.fetchall()

            if dados_cartao:
                nomes_cartoes = [item[0] for item in dados_cartao]
                valores_cartoes = [float(item[1]) for item in dados_cartao]

                self.ax4.barh(nomes_cartoes, valores_cartoes, color="#319795")
                self.ax4.tick_params(axis='both', labelsize=8)
            else:
                self.ax4.text(0.5, 0.5, "Sem faturas pendentes", horizontalalignment='center', verticalalignment='center', fontsize=10, color="#718096")

            self.ax4.set_title("Faturas/Despesas Pendentes por Cartão", fontsize=10, fontweight="bold", color="#1A365D")
            self.ax4.grid(axis='x', linestyle=":", alpha=0.6)

            cursor.close()
            conn.close()

            # Atualiza o desenho no Tkinter
            self.canvas.draw()

        except Exception as e:
            print(f"Erro ao gerar gráficos: {e}")

    def recarregar(self):
        """Método padrão chamado ao alternar para a aba ou atualizar."""
        self.carregar_graficos()