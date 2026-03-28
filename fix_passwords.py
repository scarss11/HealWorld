"""
Actualiza passwords de usuarios de prueba en Supabase/PostgreSQL.
Ejecutar UNA SOLA VEZ después de crear las tablas.

Uso:
    python fix_passwords.py
"""
import os
from dotenv import load_dotenv
import psycopg2
from werkzeug.security import generate_password_hash

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
    dbname=os.getenv('DB_NAME', 'postgres'),
    port=int(os.getenv('DB_PORT', 5432)),
    sslmode='require'
)

cur = conn.cursor()
hashed = generate_password_hash('password123')
cur.execute("UPDATE usuarios SET password = %s", (hashed,))
conn.commit()
print(f"Passwords actualizados para todos los usuarios")
print(f"Contrasena de prueba: password123")
cur.close()
conn.close()
