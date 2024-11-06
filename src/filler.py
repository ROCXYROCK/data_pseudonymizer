# sicherstellen, dass die Daten unique sind z.b. alle IDs

import datetime
import random
import os
from faker import Faker
import toml
from db_handler import connect_to_db

fake = Faker()

# Erlaubte Krankenkassen und Fachgebiete
config = toml.load('cfg/config.toml')['validator']
krankenkassen = config['krankenkassen']
fachgebiete = config['fachgebiete']
fachgebiete_werte = config['fachgebiete'].values()
medikamente = config['medikamente']
dosierungseinheit = config['dosierungseinheit']

# Generieren des SECRET_KEY, falls er nicht gesetzt ist
if 'SECRET_KEY' not in os.environ:
    raise ValueError('SECRET_KEY nicht gesetzt')

secret_key = os.environ.get('SECRET_KEY')


def generate_unique_id(cursor):
    while True:
        # Generiere eine zufällige 8-stellige Zahl
        new_id = f"{random.randint(10000000, 99999999)}"
        cursor.execute("SELECT COUNT(*) FROM Patient WHERE patient_id = %s", (new_id,))
        if cursor.fetchone()[0] == 0:
            return new_id

##### Arzt Tabelle

# Funktion zur Berechnung der Prüfziffer für die Lizenznummer der Ärzte
def calculate_check_digit(lizenznummer):
    """
    Berechnet die Prüfziffer der 8-stelligen Arztnummer

    Die Prüfziffer wird nach der folgenden Formel berechnet:
    1. Die ersten 6 Ziffern werden mit den Gewichten 4, 9, 4, 9, 4, 9 multipliziert
    2. Die Summe der multiplizierten Ziffern wird berechnet
    3. Die Prüfziffer wird als 10 minus dem Rest der Summe modulo 10 berechnet

    :param lizenznummer: Die 8-stellige Arztnummer
    :return: Die Prüfziffer der Arztnummer
    """

    weights = [4, 9] * 3  # Abwechselnd 4 und 9 für die ersten 6 Ziffern
    total = sum(int(lizenznummer[i]) * weights[i] for i in range(6))
    check_digit = (10 - (total % 10)) % 10
    return check_digit

def add_doctor(cursor):
    """
    Fügt einen neuen Arzt in die Datenbank ein.

    Diese Funktion generiert eine eindeutige Arzt-ID, einen zufälligen Namen,
    ein Fachgebiet und eine Lizenznummer für einen neuen Arzt und fügt diesen
    Datensatz in die Tabelle `Arzt` der Datenbank ein.

    :param cursor: Der Datenbank-Cursor, der für die Ausführung von SQL-Anweisungen verwendet wird.
    """
    arzt_id = generate_unique_id(cursor)
    name = fake.name()
    
    # Zufällige Fachgruppen-Nummer generieren
    fachgebiet_nummer = f"{random.randint(1, 99):02d}"  # Generiert eine Nummer von 01 bis 99
    fachgebiet = fachgebiete[fachgebiet_nummer]  # Mappen der Nummer auf das Fachgebiet
    
    while(True):
        # Lizenznummer generieren
        lizenznummer = f"{fake.random_int(100000, 999999):06d}"  # Erzeugt die ersten 6 Ziffern
        check_digit = calculate_check_digit(lizenznummer)

        lizenznummer += str(check_digit) + str(fachgebiet_nummer)  # Hinzufügen der Prüfziffer und der Fachgruppen-Nummer

        # Überprüfen, ob die Lizenznummer die CHECK-Bedingung erfüllt
        if (len(lizenznummer) == 9 and lizenznummer[:6].isdigit() and (lizenznummer[6:9].isdigit() and int(lizenznummer[6:9]) in range(1, 100))):
            break

    # Einfügen in die Datenbank
    cursor.execute("""
        INSERT INTO Arzt (arzt_id, name, fachgebiet, lizenznummer) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), %s, pgp_sym_encrypt(%s, %s));
    """, (arzt_id, name, secret_key, fachgebiet, lizenznummer, secret_key))








##### Tabelle Patient

def generate_phone_number():
    # Generiere die Telefonnummer im Format 0XXXXXXXXX (10-11 Ziffern)
    """
    Generates a random phone number in the format 0XXXXXXXXX (10-11 digits).

    The first digit is between 1 and 9, followed by 8 or 9 random digits.

    :return: A string representing the generated phone number.
    """
    first_digit = random.randint(1, 9)  # Erster Ziffer muss zwischen 1 und 9 sein
    rest_digits = [str(random.randint(0, 9)) for _ in range(random.randint(8, 9))]  # 8 oder 9 Ziffern
    return f"0{first_digit}{''.join(rest_digits)}"



def add_patient(cursor):
    """
    Fügt einen neuen Patienten in die Datenbank ein.

    Diese Funktion generiert eine eindeutige Patienten-ID, einen zufälligen Namen, ein Geburtsdatum, eine E-Mail-Adresse, eine Telefonnummer, eine Krankenversicherung und eine Versicherungsnummer für einen neuen Patienten und fügt diesen
    Datensatz in die Tabelle `Patient` der Datenbank ein.

    :param cursor: Der Datenbank-Cursor, der für die Ausführung von SQL-Anweisungen verwendet wird.
    """
    patient_id = generate_unique_id(cursor)
    name = fake.name()
    geburtstag = str(fake.date_of_birth(minimum_age=0, maximum_age=98).strftime('%Y-%m-%dT%H:%M:%S'))
    email = fake.email(safe=True)  # 'safe=True' reduziert das Risiko von ungültigen E-Mails
    telefonnummer = generate_phone_number()  # Verwende die neue Telefonnummerngenerierungsfunktion
    krankenversicherung = random.choice(krankenkassen)  # Liste der Krankenversicherungen
    # Erzeugt eine 12-stellige Versicherungsnummer
    versicherungsnummer = f"{fake.random_int(100000000000, 999999999999):012d}"

    cursor.execute("""
        INSERT INTO Patient (patient_id, name, geburtstag, email, telefonnummer, krankenversicherung, versicherungsnummer) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), %s, pgp_sym_encrypt(%s, %s));
    """, (patient_id, name, secret_key, geburtstag, secret_key, email, secret_key, telefonnummer, secret_key, krankenversicherung, versicherungsnummer, secret_key))


# Funktion zum Hinzufügen eines Termins
def add_appointment(cursor):

    cursor.execute("SELECT patient_id FROM Patient")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT arzt_id FROM Arzt")
    arzt = cursor.fetchall()

    patient_id = random.choice(patients)[0]
    arzt_id = random.choice(arzt)[0]
    
    # Konvertiere die Strings in datetime-Objekte
    start_date = datetime.datetime.strptime('2022-01-01', '%Y-%m-%d')
    end_date = datetime.datetime.strptime('2024-12-31', '%Y-%m-%d')

    datum = fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d')
    
    # Generiere eine zufällige Zeit zwischen 8 und 16 Uhr
    hour = random.randint(8, 16)  # Stunden zwischen 8 und 16
    minute = random.choice([0, 15, 30, 45])  # Wähle Minuten in Viertelstunden
    zeit = f"{hour:02d}:{minute:02d}"  # Formatierung der Zeit

    cursor.execute("""
        INSERT INTO Termin (patient_id, arzt_id, datum, zeit, status) 
        VALUES (%s, %s, %s, %s, pgp_sym_encrypt(%s, %s));
    """, (patient_id, arzt_id, datum, zeit, random.choice(['geplant', 'abgesagt', 'stattgefunden']), secret_key))

    return datum, zeit  # Rückgabe von Datum und Zeit für die Videokonsultation



# Funktion zum Hinzufügen einer Videokonsultation
def add_videoconsultation(cursor):
    # Abfrage aller gültigen Termin-IDs
    cursor.execute("SELECT termin_id FROM Termin")
    valid_termin_ids = [row[0] for row in cursor.fetchall()]  # Hole alle gültigen IDs
    
    if not valid_termin_ids:
        print("Keine gültigen Termine vorhanden.")
        return  # Keine Termine vorhanden, daher zurückkehren

    # Wähle zufällig eine gültige termin_id
    termin_id = random.choice(valid_termin_ids)  # Wähle eine ID aus der Liste der gültigen IDs

    # Hier holen wir uns Datum und Zeit des entsprechenden Termins
    cursor.execute("SELECT datum, zeit FROM Termin WHERE termin_id = %s", (termin_id,))
    termin_data = cursor.fetchone()
    
    # Überprüfe, ob wir Daten erhalten haben
    if termin_data is None:
        print(f"Kein Termin mit ID {termin_id} gefunden.")
        return  # Falls kein Termin gefunden, zurückkehren

    datum, zeit = termin_data  # Tuple unpacking

    # Konvertiere die Zeit zu datetime für die Startzeit
    startzeit = datetime.datetime.combine(datum, zeit)
    endzeit = startzeit + datetime.timedelta(minutes=random.randint(10, 120)) 
    video = fake.boolean()

    cursor.execute("""
        INSERT INTO Videokonsultation (termin_id, startzeit, endzeit, video) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), pgp_sym_encrypt(%s, %s), %s);
    """, (termin_id, startzeit.strftime('%Y-%m-%dT%H:%M:%S'), secret_key, endzeit.strftime('%Y-%m-%dT%H:%M:%S'), secret_key, video))



# Funktion zum Hinzufügen einer Verschreibung
def add_prescription(cursor, num_appointments):
    konsultation_id = random.randint(1, num_appointments)
    medikament = random.choice(medikamente)  # Auswahl aus dem Medikamentenarray
    if medikament is None:
        raise ValueError("Kein Medikament ausgewählt – Medikamentenliste überprüfen.")
    dosierung_value = fake.random_int(min=1, max=100)  # Dosierungswert zwischen 1 und 100
    dosierung_unit = random.choice(dosierungseinheit)  # Auswahl aus Dosierungseinheiten

    cursor.execute("""
        INSERT INTO Verschreibung (konsultation_id, medikament, dosierung_value, dosierung_unit, anweisung) 
        VALUES (%s, pgp_sym_encrypt(%s, %s), %s, %s, pgp_sym_encrypt(%s, %s));
    """, (konsultation_id, medikament, secret_key, dosierung_value, dosierung_unit, fake.text(), secret_key))

# Hauptfunktion zum Füllen der Datenbank
def fill_database(num_patients=1000, num_doctors=20, num_appointments=3000):
    # Erstellen einer Verbindung zur Datenbank
    connection = connect_to_db()
    cursor = connection.cursor()

    # Patienten hinzufügen
    for _ in range(num_patients):
        add_patient(cursor)

    # Ärzte hinzufügen
    for _ in range(num_doctors):
        add_doctor(cursor)

    connection.commit()

    # Termine hinzufügen
    for _ in range(num_appointments):
        add_appointment(cursor)

    connection.commit()

    # Videokonsultationen hinzufügen
    for _ in range(num_appointments):
        add_videoconsultation(cursor)

    # Verschreibungen hinzufügen
    for _ in range(num_appointments):
        add_prescription(cursor, num_appointments)

    # Änderungen speichern und Verbindung schließen
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    fill_database()