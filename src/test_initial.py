import unittest
import psycopg2
import toml

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
            port = config['database']['port']
        )
        cls.connection.autocommit = True
        cls.cursor = cls.connection.cursor()

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


if __name__ == "__main__":
    unittest.main()
