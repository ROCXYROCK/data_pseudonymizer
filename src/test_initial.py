import os
import unittest
from decimal import Decimal
import datetime
import psycopg2
import toml
#from filler import secret_key

config = toml.load('cfg/config.toml')

class TestDatabaseFilling(unittest.TestCase):
    """Testing the filling of the database"""
    @classmethod
    def setUpClass(cls):
        # Verbindet sich einmal mit der Datenbank, bevor alle Tests ausgeführt werden
        cls.connection = psycopg2.connect(
            host = config['database']['host'],
            database = config['database']['name'],
            user = config['database']['user'],
            port = config['database']['port'],
            password = config['database']['password']
        )
        cls.connection.autocommit = True
        cls.cursor = cls.connection.cursor()
        # Generieren des SECRET_KEY, falls er nicht gesetzt ist
        if 'SECRET_KEY' not in os.environ:
            raise ValueError('SECRET_KEY nicht gesetzt')

        cls.secret_key = os.environ.get('SECRET_KEY')
        
    @classmethod
    def tearDownClass(cls):
        # Schließt die Verbindung zur Datenbank nach allen Tests
        cls.cursor.close()
        cls.connection.close()


    #_______________________________________________________________________________________________
    # Testet, ob Tabellen nicht leer sind
    def check_table_not_empty(self, table_name):
        """Hilfsfunktion, die prüft, ob eine Tabelle Einträge enthält."""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = self.cursor.fetchone()[0]
        self.assertGreater(count, 0, f"Table {table_name} should not be empty but it is.")

    def test_patient_table(self):
        """Testet, ob die 'patient'-Tabelle nicht leer ist."""
        self.check_table_not_empty("patient")

    def test_termin_table(self):
        """Testet, ob die 'termin'-Tabelle nicht leer ist."""
        self.check_table_not_empty("termin")

    def test_arzt_table(self):
        """Testet, ob die 'arzt'-Tabelle nicht leer ist."""
        self.check_table_not_empty("arzt")

    def test_videokonsultation_table(self):
        """Testet, ob die 'videokonsultation'-Tabelle nicht leer ist."""
        self.check_table_not_empty("videokonsultation")

    def test_verschreibung_table(self):
        """Testet, ob die 'verschreibung'-Tabelle nicht leer ist."""
        self.check_table_not_empty("verschreibung")
    


    
    #_______________________________________________________________________________________________
    # Testet die Anzahl an Einträgen in den Tabellen
    def check_table_entry_count(self, table_name, expected_count):
        """Hilfsfunktion, die prüft, ob eine Tabelle die erwartete Anzahl an Einträgen enthält."""
        self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        actual_count = self.cursor.fetchone()[0]
        self.assertEqual(
            actual_count, expected_count, 
            f"Table '{table_name}' should have {expected_count} entries but has {actual_count}."
        )

    def test_count_patient_table(self):
        """Testet, ob die 'patient'-Tabelle die erwartete Anzahl an Einträgen enthält."""
        expected_patient_count = 1000
        self.check_table_entry_count("patient", expected_patient_count)

    def test_count_termin_table(self):
        """Testet, ob die 'termin'-Tabelle die erwartete Anzahl an Einträgen enthält."""
        expected_termin_count = 3000
        self.check_table_entry_count("termin", expected_termin_count)

    def test_count_arzt_table(self):
        """Testet, ob die 'arzt'-Tabelle die erwartete Anzahl an Einträgen enthält."""
        expected_arzt_count = 20
        self.check_table_entry_count("arzt", expected_arzt_count)

    def test_count_videokonsultation_table(self):
        """Testet, ob die 'videokonsultation'-Tabelle die erwartete Anzahl an Einträgen enthält."""
        expected_videokonsultation_count = 3000
        self.check_table_entry_count("videokonsultation", expected_videokonsultation_count)

    def test_count_verschreibung_table(self):
        """Testet, ob die 'verschreibung'-Tabelle die erwartete Anzahl an Einträgen enthält."""
        expected_verschreibung_count = 3000
        self.check_table_entry_count("verschreibung", expected_verschreibung_count)

    #_______________________________________________________________________________________________
    # Testet die SQL Queries in den Tabellen
    # Beispiel-SQL-Abfragen als Unit-Tests
    def test_aerzte_und_anzahl_letzte_woche(self):
        """Testet die Anzahl der Termine der Ärzte in der letzten Woche."""
        query = """
        SELECT a.arzt_id, pgp_sym_decrypt(a.name, %s) AS name, COUNT(t.termin_id) AS anzahl_termine
        FROM arzt a
        LEFT JOIN termin t ON a.arzt_id = t.arzt_id
        WHERE t.datum >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY a.arzt_id, a.name;
        """
        self.cursor.execute(query, (self.secret_key,))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 3)
            self.assertIsInstance(row[1], str)  # Name sollte entschlüsselt als String sein

    def test_patienten_mit_videokonsultationen_und_verschreibungen(self):
        """Testet die Zuordnung von Patienten zu Videokonsultationen"""
        query = """
        SELECT pgp_sym_decrypt(p.name::bytea, %s) AS name, pgp_sym_decrypt(v.startzeit::bytea, %s) AS startzeit
        FROM patient p
        JOIN termin t ON p.patient_id = t.patient_id
        JOIN videokonsultation v ON t.termin_id = v.termin_id
        """
        self.cursor.execute(query, (self.secret_key, self.secret_key))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)  # Name als entschlüsselter String
            self.assertIsInstance(row[1], str)  # Startzeit als entschlüsselter String

    def test_durchschnittliche_dauer_videokonsultationen_pro_arzt(self):
        """Testet die durchschnittliche Dauer der Videokonsultationen pro Arzt."""
        query = """
        SELECT pgp_sym_decrypt(a.name::bytea, %s) AS name, 
               AVG(EXTRACT(EPOCH FROM (pgp_sym_decrypt(v.endzeit::bytea, %s)::timestamp 
               - pgp_sym_decrypt(v.startzeit::bytea, %s)::timestamp)) / 60) AS durchschnittliche_dauer_minuten
        FROM arzt a
        JOIN termin t ON a.arzt_id = t.arzt_id
        JOIN videokonsultation v ON t.termin_id = v.termin_id
        GROUP BY a.name;
        """
        self.cursor.execute(query, (self.secret_key, self.secret_key, self.secret_key))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)  # Entschlüsselter Name als String
            self.assertIsInstance(row[1], Decimal)  # Durchschnittliche Dauer als float

    def test_patienten_ohne_videokonsultationen(self):
        """Testet die Patienten, die noch keine Videokonsultation hatten."""
        query = """
        SELECT p.patient_id, pgp_sym_decrypt(p.name::bytea, %s) AS name
        FROM patient p
        LEFT JOIN termin t ON p.patient_id = t.patient_id
        LEFT JOIN videokonsultation v ON t.termin_id = v.termin_id
        WHERE v.konsultation_id IS NULL;
        """
        self.cursor.execute(query, (self.secret_key,))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[1], str)  # Entschlüsselter Name als String

    def test_ärzte_mit_hoechster_anzahl_verschreibungen(self):
        """Testet die Ärzte mit der höchsten Anzahl an Verschreibungen."""
        query = """
        SELECT pgp_sym_decrypt(a.name::bytea, %s) AS name, COUNT(ver.verschreibung_id) AS anzahl_verschreibungen
        FROM arzt a
        JOIN termin t ON a.arzt_id = t.arzt_id
        JOIN videokonsultation v ON t.termin_id = v.termin_id
        JOIN verschreibung ver ON v.konsultation_id = ver.konsultation_id
        GROUP BY a.name
        ORDER BY anzahl_verschreibungen DESC
        LIMIT 5;
        """
        self.cursor.execute(query, (self.secret_key,))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)  # Entschlüsselter Name als String
            self.assertIsInstance(row[1], int)  # Anzahl Verschreibungen als Integer

    def test_patienten_und_naechste_termine(self):
        """Testet die nächsten anstehenden Termine der Patienten."""
        query = """
        SELECT pgp_sym_decrypt(p.name::bytea, %s) AS name, MIN(t.datum) AS naechster_termin
        FROM patient p
        JOIN termin t ON p.patient_id = t.patient_id
        WHERE t.datum > CURRENT_DATE
        GROUP BY p.name;
        """
        self.cursor.execute(query, (self.secret_key,))
        result = self.cursor.fetchall()
        self.assertIsInstance(result, list)
        for row in result:
            self.assertEqual(len(row), 2)
            self.assertIsInstance(row[0], str)  # Entschlüsselter Name als String
            self.assertIsInstance(row[1], (str, datetime.date) )  # Nächster Termin als Datum/String



if __name__ == "__main__":
    unittest.main(verbosity=2)
