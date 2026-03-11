import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo

HOST     = "pg-2e2874e2-rodrigoaiosa-skydatasoluction.l.aivencloud.com"
PORT     = "13191"
DATABASE = "BD_SKYDATA"
USER     = "avnadmin"
PASSWORD = "AVNS_LlZukuJoh_0Kbj0dhvK"
SSL_MODE = "require"

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

print("Migração - add coluna id_ref_proprio")
print(f"Data/hora: {datetime.now(FUSO_BRASIL).strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 50)

conn = None

try:
    conn = psycopg2.connect(
        host=HOST, port=PORT, database=DATABASE,
        user=USER, password=PASSWORD, sslmode=SSL_MODE
    )
    cursor = conn.cursor()
    print("✅ Conectado ao banco!")

    # Verifica se coluna já existe
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name='cad_contato_indicacao' AND column_name='id_ref_proprio'
    """)
    if cursor.fetchone():
        print("⚠️ Coluna 'id_ref_proprio' já existe.")
    else:
        cursor.execute("""
            ALTER TABLE cad_contato_indicacao
            ADD COLUMN id_ref_proprio VARCHAR(20);
        """)
        print("✅ Coluna 'id_ref_proprio' criada!")

    conn.commit()

except Exception as e:
    if conn: conn.rollback()
    print("❌ Erro:", e)

finally:
    if conn:
        cursor.close()
        conn.close()
        print("🔌 Conexão encerrada.")
