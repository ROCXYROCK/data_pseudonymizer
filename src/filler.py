"""
Dieses Skript enthält die Funktionalität, um eine PostgreSQL-Datenbank mit verschlüsselten, synthetischen Daten zu befüllen.
Die Daten werden mit der pgcrypto-Erweiterung verschlüsselt, um DSGVO-konforme Datenspeicherung zu gewährleisten.
"""

import datetime
import random
import os
from faker import Faker
import toml
from db_handler import connect_to_db

fake = Faker()

# Konfigurationsdaten aus der config.toml-Datei laden
config = toml.load('cfg/config.toml')['validator']
krankenkassen = config['krankenkassen']
fachgebiete = config['fachgebiete']
fachgebiete_werte = config['fachgebiete'].values()
medikamente = config['medikamente']
dosierungseinheit = config['dosierungseinheit']

# Überprüfen, ob der Secret Key gesetzt ist, da er für die Datenverschlüsselung benötigt wird
if 'SECRET_KEY' not in os.environ:
    raise ValueError('SECRET_KEY Umgebungsvariable ist nicht gesetzt')

secret_key = os.environ.get('SECRET_KEY')


def generate_unique_id_patient(cursor):
    """Generiert eine eindeutige 8-stellige ID für Patienten."""
    while True:
        new_id = f"{random.randint(10000000, 99999999)}"
        cursor.execute("SELECT COUNT(*) FROM Patient WHERE patient_id = %s", (new_id,))
        if cursor.fetchone()[0] == 0:
            return new_id

def generate_unique_id_arzt(cursor):
    """Generiert eine eindeutige 8-stellige ID für Ärzte."""
    while True:
        new_id = f"{random.randint(10000000, 99999999)}"
        cursor.execute("SELECT COUNT(*) FROM Arzt WHERE arzt_id = %s", (new_id,))
        if cursor.fetchone()[0] == 0:
            return new_id

##### Arzt Tabelle #####

def calculate_check_digit(lizenznummer):
    """
    Berechnet die Prüfziffer für eine Arztnummer.
    
    Prüfziffer-Berechnung:
    1. Die ersten 6 Ziffern werden abwechselnd mit 4 und 9 multipliziert.
    2. Die Summe der Produkte wird gebildet.
    3. Die Prüfziffer ist das Ergebnis von (10 - (Summe % 10)) % 10.
    
    :param lizenznummer: Die ersten 6 Ziffern der Arztnummer
    :return: Die berechnete Prüfziffer
    """
    weights = [4, 9] * 3  # Abwechselndes Muster
    total = sum(int(lizenznummer[i]) * weights[i] for i in range(6))
    check_digit = (10 - (total % 10)) % 10
    return check_digit

def add_doctor(cursor):
    """
    Fügt einen neuen Arzt in die Datenbank ein.

    Generiert eine eindeutige Arzt-ID, zufällige Daten wie Name, Fachgebiet und Lizenznummer
    und fügt die Daten in die `Arzt`-Tabelle der Datenbank ein.

    :param cursor: Der Datenbank-Cursor zur Ausführung von SQL-Anweisungen
    """
    arzt_id = generate_unique_id_arzt(cursor)
    name = fake.name()
    
    # Generiere eine zufällige Fachgruppen-Nummer und mappe auf das Fachgebiet
    fachgebiet_nummer = f"{random.randint(1, 99):02d}"
    fachgebiet = fachgebiete[fachgebiet_nummer]
    
    while True:
        # Generiere Lizenznummer mit Prüfziffer und Fachgruppen-Nummer
        lizenznummer = f"{fake.random_int(100000, 999999):06d}"
        check_digit = calculate_check_digit(lizenznummer)
        lizenznummer += str(check_digit) + str(fachgebiet_nummer)

        if len(lizenznummer) == 9:
            break

    # Einfügen des Arztes in die Datenbank
    cursor.execute("""
        INSERT INTO Arzt (arzt_id, name, fachgebiet, lizenznummer) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), %s, pgp_sym_encrypt(%s, %s));
    """, (arzt_id, name, secret_key, fachgebiet, lizenznummer, secret_key))


##### Tabelle Patient #####

def generate_phone_number():
    """
    Generiert eine zufällige Telefonnummer im Format 0XXXXXXXXX (10-11 Ziffern).
    
    Die erste Ziffer muss zwischen 1 und 9 liegen, gefolgt von 8-9 weiteren Ziffern.

    :return: Ein String, der die generierte Telefonnummer darstellt
    """
    first_digit = random.randint(1, 9)
    rest_digits = [str(random.randint(0, 9)) for _ in range(random.randint(8, 9))]
    return f"0{first_digit}{''.join(rest_digits)}"

def add_patient(cursor):
    """
    Fügt einen neuen Patienten in die Datenbank ein.

    Generiert zufällige Patientendaten wie Name, Geburtsdatum, E-Mail, Telefonnummer,
    Krankenversicherung und Versicherungsnummer und fügt diese in die `Patient`-Tabelle ein.

    :param cursor: Der Datenbank-Cursor zur Ausführung von SQL-Anweisungen
    """
    patient_id = generate_unique_id_patient(cursor)
    name = fake.name()
    geburtstag = str(fake.date_of_birth(minimum_age=0, maximum_age=98).strftime('%Y-%m-%dT%H:%M:%S'))
    email = fake.email(safe=True)
    telefonnummer = generate_phone_number()
    krankenversicherung = random.choice(krankenkassen)
    versicherungsnummer = f"{fake.random_int(100000000000, 999999999999):012d}"

    cursor.execute("""
        INSERT INTO Patient (patient_id, name, geburtstag, email, telefonnummer, krankenversicherung, versicherungsnummer) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), %s, pgp_sym_encrypt(%s, %s));
    """, (patient_id, name, secret_key, geburtstag, secret_key, email, secret_key, telefonnummer, secret_key, krankenversicherung, versicherungsnummer, secret_key))


##### Termin-Tabelle #####

def add_appointment(cursor):
    """
    Fügt einen neuen Termin in die Datenbank ein.

    Wählt zufällige Patienten- und Arztdaten aus bestehenden Einträgen, generiert ein zufälliges
    Datum und eine zufällige Uhrzeit für den Termin und fügt die Daten in die `Termin`-Tabelle ein.

    :param cursor: Der Datenbank-Cursor zur Ausführung von SQL-Anweisungen
    :return: Das Datum und die Zeit des erstellten Termins
    """
    cursor.execute("SELECT patient_id FROM Patient")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT arzt_id FROM Arzt")
    arzt = cursor.fetchall()

    patient_id = random.choice(patients)[0]
    arzt_id = random.choice(arzt)[0]
    
    datum = fake.date_between(start_date='-2y', end_date='now').strftime('%Y-%m-%d')
    hour = random.randint(8, 16)
    minute = random.choice([0, 15, 30, 45])
    zeit = f"{hour:02d}:{minute:02d}"

    cursor.execute("""
        INSERT INTO Termin (patient_id, arzt_id, datum, zeit, status) 
        VALUES (%s, %s, %s, %s, pgp_sym_encrypt(%s, %s));
    """, (patient_id, arzt_id, datum, zeit, random.choice(['geplant', 'abgesagt', 'stattgefunden']), secret_key))

    return datum, zeit


##### Videokonsultation-Tabelle #####

def add_videoconsultation(cursor):
    """
    Fügt eine Videokonsultation in die Datenbank ein, verknüpft mit einem bestehenden Termin.

    Wählt zufällig einen Termin aus und erstellt eine Start- und Endzeit für die Videokonsultation.

    :param cursor: Der Datenbank-Cursor zur Ausführung von SQL-Anweisungen
    """
    cursor.execute("SELECT termin_id FROM Termin")
    valid_termin_ids = [row[0] for row in cursor.fetchall()]
    
    if not valid_termin_ids:
        print("Keine gültigen Termine vorhanden.")
        return

    termin_id = random.choice(valid_termin_ids)
    cursor.execute("SELECT datum, zeit FROM Termin WHERE termin_id = %s", (termin_id,))
    datum, zeit = cursor.fetchone()
    
    startzeit = datetime.datetime.combine(datum, zeit)
    endzeit = startzeit + datetime.timedelta(minutes=random.randint(10, 120))
    video = fake.boolean()

    cursor.execute("""
        INSERT INTO Videokonsultation (termin_id, startzeit, endzeit, video) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), %s);
    """, (termin_id, startzeit.strftime('%Y-%m-%dT%H:%M:%S'), secret_key, endzeit.strftime('%Y-%m-%dT%H:%M:%S'), secret_key, video))


##### Verschreibung-Tabelle #####

def add_prescription(cursor, num_appointments):
    """
    Fügt eine Verschreibung für eine Videokonsultation in die Datenbank ein.

    Wählt zufällige Werte für Medikament, Dosierung und Anweisung und fügt diese in die `Verschreibung`-Tabelle ein.

    :param cursor: Der Datenbank-Cursor zur Ausführung von SQL-Anweisungen
    :param num_appointments: Anzahl der Konsultationen
    """
    konsultation_id = random.randint(1, num_appointments)
    medikament = random.choice(medikamente)
    dosierung_value = fake.random_int(min=1, max=100)
    dosierung_unit = random.choice(dosierungseinheit)

    cursor.execute("""
        INSERT INTO Verschreibung (konsultation_id, medikament, dosierung_value, dosierung_unit, anweisung) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), %s, %s, pgp_sym_encrypt(%s, %s));
    """, (konsultation_id, medikament, secret_key, dosierung_value, dosierung_unit, fake.text(), secret_key))


# Hauptfunktion zum Füllen der Datenbank
def fill_database(num_patients=1000, num_doctors=20, num_appointments=3000):
    """
    Füllt die Datenbank mit synthetischen Daten für Patienten, Ärzte, Termine, Videokonsultationen und Verschreibungen.
    :param num_patients: Anzahl der zu erstellenden Patienteneinträge
    :param num_doctors: Anzahl der zu erstellenden Arzteinträge
    :param num_appointments: Anzahl der zu erstellenden Termine
    """
    connection = connect_to_db()
    cursor = connection.cursor()

    for _ in range(num_patients):
        add_patient(cursor)

    for _ in range(num_doctors):
        add_doctor(cursor)

    connection.commit()

    for _ in range(num_appointments):
        add_appointment(cursor)

    connection.commit()

    for _ in range(num_appointments):
        add_videoconsultation(cursor)

    for _ in range(num_appointments):
        add_prescription(cursor, num_appointments)

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    fill_database()
