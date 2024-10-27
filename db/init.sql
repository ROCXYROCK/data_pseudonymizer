-- Datenbank anlegen und auswählen
CREATE DATABASE medizinische_db;
\c medizinische_db;

-- Tabelle Patient
CREATE TABLE Patient (
    patient_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    geburtstag TIMESTAMP CHECK (geburtstag >= '1910-01-01'),
    email VARCHAR(255) CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    telefonnummer VARCHAR(20) CHECK (telefonnummer ~ '^0[1-9][0-9]{8,9}$'),
    krankenversicherung VARCHAR(255) CHECK (krankenversicherung IN ('AOK', 'TK', 'BKK', 'IKK', 'DAK-Gesundheit', 'KKH', 'BARMER', 'HELA-VERSICHERUNG', 'Union Krankenversicherung', 'SVG', 'Allianz', 'AXA', 'Debeka', 'DKV', 'HUK-COBURG', 'Signal Iduna', 'LVM', 'Concordia', 'Münchener Verein', 'Barmenia')),
    versicherungsnummer CHAR(12) CHECK (versicherungsnummer ~ '^[0-9]{12}$')
);

-- Tabelle Arzt
CREATE TABLE Arzt (
    arzt_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    fachgebiet VARCHAR(255) NOT NULL,
    lizenznummer VARCHAR(9) CHECK ( lizenznummer ~ '^[0-9]{9}$')
);

-- Tabelle Termin
CREATE TABLE Termin (
    termin_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES Patient(patient_id) ON DELETE CASCADE,
    arzt_id INTEGER REFERENCES Arzt(arzt_id) ON DELETE CASCADE,
    datum DATE CHECK (datum >= '2022-01-01'), -- Korrektur hier
    zeit TIME NOT NULL,
    status VARCHAR(50) CHECK (status IN ('geplant', 'abgesagt', 'stattgefunden')) -- Korrektur hier
);

-- Tabelle Videokonsultation
CREATE TABLE Videokonsultation (
    konsultation_id SERIAL PRIMARY KEY,
    termin_id INTEGER REFERENCES Termin(termin_id) ON DELETE CASCADE,
    startzeit TIMESTAMP CHECK (startzeit >= '2022-01-01'),
    endzeit TIMESTAMP CHECK (startzeit < endzeit),
    video BOOLEAN NOT NULL
);

-- Tabelle Verschreibung
CREATE TABLE Verschreibung (
    verschreibung_id SERIAL PRIMARY KEY,
    konsultation_id INTEGER REFERENCES Videokonsultation(konsultation_id) ON DELETE CASCADE,
    medikament VARCHAR(255),
    dosierung_value NUMERIC(5, 2),  -- numerische Dosierung
    dosierung_unit VARCHAR(10) CHECK (dosierung_unit IN ('ml', 'mg')), -- Einheit der Dosierung
    anweisung TEXT
);
