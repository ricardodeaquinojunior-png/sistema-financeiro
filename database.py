import sqlite3
import psycopg2
from datetime import date, datetime
from tkinter import messagebox

SUPABASE_CONFIG = {
    "host": "aws-0-us-east-1.pooler.supabase.com",
    "database": "postgres",
    "user": "postgres.vihsucqqzeaestnynffz",
    "password": r"gPAc6c9P+_ZV2u$",
    "port": 6543,
}

MODO_BANCO = "local"


def alternar_modo_banco(modo):
  global MODO_BANCO
  if modo in ["local", "nuvem"]:
    MODO_BANCO = modo


class SQLiteCursorWrapper:
  """Traduz comandos do PostgreSQL para o SQLite e converte datas de texto para objetos date/datetime."""

  def __init__(self, cursor, connection):
    self.cursor = cursor
    self.connection = connection

  def execute(self, query, params=None):
    q = (
        query.replace("TO_CHAR(l.data_lancamento, 'YYYY-MM')", "strftime('%Y-%m', l.data_lancamento)")
        .replace("TO_CHAR(data_lancamento, 'YYYY-MM')", "strftime('%Y-%m', data_lancamento)")
    )
    q = q.replace("%s", "?")

    if params:
      params_convertidos = []
      for p in params:
        if isinstance(p, bool):
          params_convertidos.append(1 if p else 0)
        elif isinstance(p, date) and not isinstance(p, datetime):
          params_convertidos.append(p.strftime("%Y-%m-%d"))
        else:
          params_convertidos.append(p)
      params = tuple(params_convertidos)
      return self.cursor.execute(q, params)
    else:
      return self.cursor.execute(q)

  def _converter_linha(self, row):
    if not row:
      return row
    nova_linha = []
    for val in row:
      if isinstance(val, str):
        # Tenta converter strings de data no formato AAAA-MM-DD para o objeto date do Python
        if len(val) == 10 and val[4] == '-' and val[7] == '-':
          try:
            nova_linha.append(datetime.strptime(val, "%Y-%m-%d").date())
            continue
          except ValueError:
            pass
      nova_linha.append(val)
    return tuple(nova_linha)

  def fetchall(self):
    rows = self.cursor.fetchall()
    return [self._converter_linha(row) for row in rows]

  def fetchone(self):
    row = self.cursor.fetchone()
    return self._converter_linha(row)

  def close(self):
    self.cursor.close()


class SQLiteConnectionWrapper:
  def __init__(self, conn):
    self.conn = conn

  def cursor(self):
    return SQLiteCursorWrapper(self.conn.cursor(), self.conn)

  def commit(self):
    self.conn.commit()

  def rollback(self):
    self.conn.rollback()

  def close(self):
    self.conn.close()


def conectar_banco():
  if MODO_BANCO == "local":
    conn = sqlite3.connect("financeiro.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return SQLiteConnectionWrapper(conn)
  else:
    return psycopg2.connect(
        host=SUPABASE_CONFIG["host"],
        database=SUPABASE_CONFIG["database"],
        user=SUPABASE_CONFIG["user"],
        password=SUPABASE_CONFIG["password"],
        port=SUPABASE_CONFIG["port"],
    )


def inicializar_banco_local():
  """Cria ou recria as tabelas no SQLite local aceitando tipos textuais/UUIDs."""
  conn = sqlite3.connect("financeiro.db")
  cursor = conn.cursor()

  cursor.execute("PRAGMA foreign_keys = OFF;")

  cursor.execute("DROP TABLE IF EXISTS lancamentos;")
  cursor.execute("DROP TABLE IF EXISTS subcategorias;")
  cursor.execute("DROP TABLE IF EXISTS categorias;")
  cursor.execute("DROP TABLE IF EXISTS contas;")
  cursor.execute("DROP TABLE IF EXISTS cartoes;")

  cursor.execute("""
        CREATE TABLE categorias (
            id_categoria TEXT PRIMARY KEY,
            descricao TEXT NOT NULL
        );
    """)

  cursor.execute("""
        CREATE TABLE subcategorias (
            id_subcategoria TEXT PRIMARY KEY,
            descricao TEXT NOT NULL,
            id_categoria TEXT,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE CASCADE
        );
    """)

  cursor.execute("""
        CREATE TABLE contas (
            id TEXT PRIMARY KEY,
            instituicao TEXT NOT NULL,
            saldo_inicial REAL DEFAULT 0,
            saldo_atual REAL DEFAULT 0,
            principal BOOLEAN DEFAULT 0
        );
    """)

  cursor.execute("""
        CREATE TABLE cartoes (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            dia_fechamento INTEGER,
            dia_vencimento INTEGER,
            principal BOOLEAN DEFAULT 0
        );
    """)

  cursor.execute("""
        CREATE TABLE lancamentos (
            id TEXT PRIMARY KEY,
            tipo TEXT,
            valor REAL,
            recebido BOOLEAN DEFAULT 0,
            data_lancamento TEXT,
            descricao TEXT,
            id_categoria TEXT,
            id_subcategoria TEXT,
            id_conta TEXT,
            id_conta_destino TEXT,
            id_cartao TEXT,
            repeticoes INTEGER DEFAULT 1,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
            FOREIGN KEY (id_subcategoria) REFERENCES subcategorias(id_subcategoria),
            FOREIGN KEY (id_conta) REFERENCES contas(id),
            FOREIGN KEY (id_conta_destino) REFERENCES contas(id),
            FOREIGN KEY (id_cartao) REFERENCES cartoes(id)
        );
    """)

  cursor.execute("PRAGMA foreign_keys = ON;")
  conn.commit()
  cursor.close()
  conn.close()


def migrar_dados_para_nuvem():
  """Copia todos os dados do SQLite local para o Supabase (Nuvem)."""
  try:
    conn_local = sqlite3.connect("financeiro.db")
    conn_local.row_factory = sqlite3.Row
    cursor_local = conn_local.cursor()

    conn_nuvem = psycopg2.connect(
        host=SUPABASE_CONFIG["host"],
        database=SUPABASE_CONFIG["database"],
        user=SUPABASE_CONFIG["user"],
        password=SUPABASE_CONFIG["password"],
        port=SUPABASE_CONFIG["port"],
    )
    cursor_nuvem = conn_nuvem.cursor()

    # Migrar Categorias
    cursor_local.execute("SELECT * FROM categorias;")
    for cat in cursor_local.fetchall():
      cursor_nuvem.execute(
          "INSERT INTO categorias (id_categoria, descricao) VALUES (%s, %s)"
          " ON CONFLICT (id_categoria) DO NOTHING;",
          (str(cat["id_categoria"]), cat["descricao"]),
      )

    # Migrar Subcategorias
    cursor_local.execute("SELECT * FROM subcategorias;")
    for sub in cursor_local.fetchall():
      cursor_nuvem.execute(
          "INSERT INTO subcategorias (id_subcategoria, descricao, id_categoria)"
          " VALUES (%s, %s, %s) ON CONFLICT (id_subcategoria) DO NOTHING;",
          (str(sub["id_subcategoria"]), sub["descricao"], str(sub["id_categoria"]) if sub["id_categoria"] else None),
      )

    # Migrar Contas
    cursor_local.execute("SELECT * FROM contas;")
    for conta in cursor_local.fetchall():
      cursor_nuvem.execute(
          "INSERT INTO contas (id, instituicao, saldo_inicial, saldo_atual,"
          " principal) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO"
          " NOTHING;",
          (
              str(conta["id"]),
              conta["instituicao"],
              conta["saldo_inicial"],
              conta["saldo_atual"],
              bool(conta["principal"]),
          ),
      )

    # Migrar Cartões
    cursor_local.execute("SELECT * FROM cartoes;")
    for cartao in cursor_local.fetchall():
      cursor_nuvem.execute(
          "INSERT INTO cartoes (id, nome, dia_fechamento, dia_vencimento,"
          " principal) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO"
          " NOTHING;",
          (
              str(cartao["id"]),
              cartao["nome"],
              cartao["dia_fechamento"],
              cartao["dia_vencimento"],
              bool(cartao["principal"]),
          ),
      )

    # Migrar Lançamentos
    cursor_local.execute("SELECT * FROM lancamentos;")
    for l in cursor_local.fetchall():
      cursor_nuvem.execute(
          """
                INSERT INTO lancamentos (id, tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_conta, id_conta_destino, id_cartao, repeticoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """,
          (
              str(l["id"]),
              l["tipo"],
              l["valor"],
              bool(l["recebido"]),
              l["data_lancamento"],
              l["descricao"],
              str(l["id_categoria"]) if l["id_categoria"] else None,
              str(l["id_subcategoria"]) if l["id_subcategoria"] else None,
              str(l["id_conta"]) if l["id_conta"] else None,
              str(l["id_conta_destino"]) if l["id_conta_destino"] else None,
              str(l["id_cartao"]) if l["id_cartao"] else None,
              l["repeticoes"],
          ),
      )

    conn_nuvem.commit()
    cursor_local.close()
    conn_local.close()
    cursor_nuvem.close()
    conn_nuvem.close()

    messagebox.showinfo("Sucesso", "Dados migrados com sucesso para a nuvem (Supabase)!")
  except Exception as e:
    messagebox.showerror("Erro na Migração", f"Não foi possível migrar para a nuvem: {e}")


def migrar_dados_da_nuvem():
  """Baixa todos os dados do Supabase e insere no SQLite local de forma segura."""
  try:
    conn_nuvem = psycopg2.connect(
        host=SUPABASE_CONFIG["host"],
        database=SUPABASE_CONFIG["database"],
        user=SUPABASE_CONFIG["user"],
        password=SUPABASE_CONFIG["password"],
        port=SUPABASE_CONFIG["port"],
    )
    cursor_nuvem = conn_nuvem.cursor()

    conn_local = sqlite3.connect("financeiro.db")
    conn_local.execute("PRAGMA foreign_keys = OFF;")
    cursor_local = conn_local.cursor()

    # Baixar Categorias
    cursor_nuvem.execute("SELECT id_categoria, descricao FROM categorias;")
    for cat in cursor_nuvem.fetchall():
      cursor_local.execute(
          "INSERT OR IGNORE INTO categorias (id_categoria, descricao) VALUES (?, ?);",
          (str(cat[0]) if cat[0] is not None else None, str(cat[1]) if cat[1] is not None else ""),
      )

    # Baixar Subcategorias
    cursor_nuvem.execute("SELECT id_subcategoria, descricao, id_categoria FROM subcategorias;")
    for sub in cursor_nuvem.fetchall():
      cursor_local.execute(
          "INSERT OR IGNORE INTO subcategorias (id_subcategoria, descricao, id_categoria) VALUES (?, ?, ?);",
          (
              str(sub[0]) if sub[0] is not None else None,
              str(sub[1]) if sub[1] is not None else "",
              str(sub[2]) if sub[2] is not None else None,
          ),
      )

    # Baixar Contas
    cursor_nuvem.execute("SELECT id, instituicao, saldo_inicial, saldo_atual, principal FROM contas;")
    for conta in cursor_nuvem.fetchall():
      cursor_local.execute(
          "INSERT OR IGNORE INTO contas (id, instituicao, saldo_inicial, saldo_atual, principal) VALUES (?, ?, ?, ?, ?);",
          (
              str(conta[0]) if conta[0] is not None else None,
              str(conta[1]) if conta[1] is not None else "",
              float(conta[2]) if conta[2] is not None else 0.0,
              float(conta[3]) if conta[3] is not None else 0.0,
              1 if conta[4] else 0,
          ),
      )

    # Baixar Cartões
    cursor_nuvem.execute("SELECT id, nome, dia_fechamento, dia_vencimento, principal FROM cartoes;")
    for cartao in cursor_nuvem.fetchall():
      cursor_local.execute(
          "INSERT OR IGNORE INTO cartoes (id, nome, dia_fechamento, dia_vencimento, principal) VALUES (?, ?, ?, ?, ?);",
          (
              str(cartao[0]) if cartao[0] is not None else None,
              str(cartao[1]) if cartao[1] is not None else "",
              int(cartao[2]) if cartao[2] is not None else None,
              int(cartao[3]) if cartao[3] is not None else None,
              1 if cartao[4] else 0,
          ),
      )

    # Baixar Lançamentos
    cursor_nuvem.execute("""
        SELECT id, tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_conta, id_conta_destino, id_cartao, repeticoes 
        FROM lancamentos;
    """)
    for l in cursor_nuvem.fetchall():
      data_val = l[4]
      if isinstance(data_val, (date, datetime)):
        data_str = data_val.strftime("%Y-%m-%d")
      else:
        data_str = str(data_val) if data_val else None

      cursor_local.execute(
          """
            INSERT OR IGNORE INTO lancamentos (id, tipo, valor, recebido, data_lancamento, descricao, id_categoria, id_subcategoria, id_conta, id_conta_destino, id_cartao, repeticoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
          (
              str(l[0]) if l[0] is not None else None,
              str(l[1]) if l[1] is not None else "",
              float(l[2]) if l[2] is not None else 0.0,
              1 if l[3] else 0,
              data_str,
              str(l[5]) if l[5] is not None else "",
              str(l[6]) if l[6] is not None else None,
              str(l[7]) if l[7] is not None else None,
              str(l[8]) if l[8] is not None else None,
              str(l[9]) if l[9] is not None else None,
              str(l[10]) if l[10] is not None else None,
              int(l[11]) if l[11] is not None else 1,
          ),
      )

    conn_local.commit()
    cursor_nuvem.close()
    conn_nuvem.close()
    cursor_local.close()
    conn_local.close()

    messagebox.showinfo("Sucesso", "Dados baixados com sucesso da nuvem para o banco local!")
  except Exception as e:
    messagebox.showerror("Erro na Migração", f"Não foi possível baixar os dados da nuvem: {e}")