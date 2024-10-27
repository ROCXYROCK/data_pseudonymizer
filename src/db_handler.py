import psycopg2
import toml

config = toml.load('cfg/config.toml')

# Konfiguriere die Verbindung zur PostgreSQL-Datenbank
DB_HOST = config['database']['host']
DB_PORT = config['database']['port']
DB_NAME = config['database']['name']
DB_USER = config['database']['user']

def connect_to_db():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her."""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER
        )
        return connection
    except Exception as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None


conn = connect_to_db()
cursor = conn.cursor()

cursor.execute(f"SELECT * FROM information_schema.tables WHERE table_schema='public';")

tables = cursor.fetchall()

print("Tabellen in der Datenbank:")
for table in tables:
    print(f"- {table[2]}")
