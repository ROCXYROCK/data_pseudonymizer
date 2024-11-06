import time
import psycopg2
import toml


config = toml.load('cfg/config.toml')

# Konfiguriere die Verbindung zur PostgreSQL-Datenbank
DB_HOST = config['database']['host']
DB_PORT = config['database']['port']
DB_NAME = config['database']['name']
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']

def connect_to_db():
    """Stellt eine Verbindung zur PostgreSQL-Datenbank her."""
    try:
        time.sleep(2)
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None