import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database import conectar_banco  # Reutiliza a sua conexão existente

# Configuração da página otimizada para celular
st.set_page_config(page_title="Finanças - Lançamento Rápido", page_icon="💳", layout="centered")

st.markdown("## 💳 Lançamento no Cartão")
st.write("Insira rapidamente suas despesas de rua direto pelo celular.")

# Função para carregar cartões e categorias do banco
@st.cache_data(ttl=10)
def carregar_dados_auxiliares():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Busca cartões
        cursor.execute("SELECT id, nome FROM cartoes ORDER BY nome;")
        cartoes = {nome: cid for cid, nome in cursor.fetchall()}
        
        # Busca categorias de despesa
        cursor.execute("SELECT id_categoria, descricao FROM categorias ORDER BY descricao;")
        categorias = {desc: cid for cid, desc in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        return cartoes, categorias
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return {}, {}

cartoes_dict, categorias_dict = carregar_dados_auxiliares()

if not cartoes_dict:
    st.warning("Nenhum cartão cadastrado. Cadastre pelo menos um cartão no sistema desktop primeiro.")
else:
    with st.form("form_despesa_celular", clear_on_submit=True):
        # 1. Cartão
        cartao_escolhido = st.selectbox("Cartão de Crédito", options=list(cartoes_dict.keys()))
        
        # 2. Valor
        valor_str = st.text_input("Valor da Despesa (R$)", value="0,00")
        
        # 3. Data da Compra
        data_compra = st.date_input("Data da Compra", value=datetime.now())
        
        # 4. Descrição
        descricao = st.text_input("Descrição / Estabelecimento")
        
        # 5. Categoria
        categoria_escolhida = st.selectbox("Categoria", options=list(categorias_dict.keys()) if categorias_dict else ["Geral"])
        
        # 6. Opção de Parcelamento
        parcelado = st.checkbox("Parcelar compra?")
        qtd_vezes = 1
        if parcelado:
            qtd_vezes = st.selectbox("Número de vezes", options=list(range(2, 13)), format_func=lambda x: f"{x}x")

        # Botão de Envio
        submitted = st.form_submit_button("Cadastrar Despesa", use_container_width=True)

        if submitted:
            try:
                # Tratamento do valor monetário
                limpo = valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
                valor_total = float(limpo)
                
                if valor_total <= 0:
                    st.error("O valor da despesa deve ser maior que zero!")
                else:
                    id_cartao = cartoes_dict[cartao_escolhido]
                    id_cat = categorias_dict.get(categoria_escolhida)
                    desc_base = descricao.strip() if descricao.strip() else "Despesa Cartão"
                    
                    conn = conectar_banco()
                    cursor = conn.cursor()

                    if parcelado and qtd_vezes > 1:
                        valor_parcela = valor_total / qtd_vezes
                        for i in range(qtd_vezes):
                            data_parcela = data_compra + relativedelta(months=i)
                            desc_parcela = f"{desc_base} ({i+1}/{qtd_vezes})"
                            cursor.execute("""
                                INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_cartao, repeticoes)
                                VALUES ('Despesa', %s, FALSE, %s, %s, %s, %s, %s);
                            """, (valor_parcela, data_parcela.strftime("%Y-%m-%d"), desc_parcela, id_cat, id_cartao, qtd_vezes))
                        sucesso_msg = f"Despesa parcelada em {qtd_vezes}x cadastrada com sucesso!"
                    else:
                        cursor.execute("""
                            INSERT INTO lancamentos (tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_cartao, repeticoes)
                            VALUES ('Despesa', %s, FALSE, %s, %s, %s, %s, 1);
                        """, (valor_total, data_compra.strftime("%Y-%m-%d"), desc_base, id_cat, id_cartao))
                        sucesso_msg = "Despesa de cartão cadastrada com sucesso!"

                    conn.commit()
                    cursor.close()
                    conn.close()

                    st.success(sucesso_msg)
            except ValueError:
                st.error("Formato de valor inválido! Use números (ex: 45.90 ou 45,90).")
            except Exception as ex:
                st.error(f"Erro ao salvar no banco de dados: {ex}")

# Rodapé informativo
st.markdown("---")
st.caption("💡 Dica: No seu celular, abra este app no navegador e selecione a opção **'Adicionar à Tela Inicial'** para usá-lo como um aplicativo.")