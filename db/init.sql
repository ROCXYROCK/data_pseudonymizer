-- Datenbank anlegen und auswählen
CREATE DATABASE medizinische_db;
\c medizinische_db;

-- Tabelle Patient
CREATE TABLE Patient (
    patient_id INTEGER PRIMARY KEY,
    name BYTEA NOT NULL,
    geburtstag BYTEA NOT NULL,
    email BYTEA NOT NULL,
    telefonnummer BYTEA NOT NULL,
    krankenversicherung VARCHAR(255) CHECK (krankenversicherung IN ('AOK', 'TK', 'BKK', 'IKK', 'DAK-Gesundheit', 'KKH', 'BARMER', 'HELA-VERSICHERUNG', 'Union Krankenversicherung', 'SVG', 'Allianz', 'AXA', 'Debeka', 'DKV', 'HUK-COBURG', 'Signal Iduna', 'LVM', 'Concordia', 'Münchener Verein', 'Barmenia')),
    versicherungsnummer BYTEA NOT NULL
);

-- Tabelle Arzt
CREATE TABLE Arzt (
    arzt_id INTEGER PRIMARY KEY,
    name BYTEA NOT NULL,
    fachgebiet VARCHAR(255) NOT NULL,
    lizenznummer BYTEA NOT NULL
);

-- Tabelle Termin
CREATE TABLE Termin (
    termin_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES Patient(patient_id) ON DELETE CASCADE,
    arzt_id INTEGER REFERENCES Arzt(arzt_id) ON DELETE CASCADE,
    datum DATE CHECK (datum >= '2022-01-01'), -- Korrektur hier
    zeit TIME NOT NULL,
    status BYTEA NOT NULL
);

-- Tabelle Videokonsultation
CREATE TABLE Videokonsultation (
    konsultation_id SERIAL PRIMARY KEY,
    termin_id INTEGER REFERENCES Termin(termin_id) ON DELETE CASCADE,
    startzeit BYTEA NOT NULL,
    endzeit BYTEA NOT NULL,
    video BOOLEAN NOT NULL
);

-- Tabelle Verschreibung
CREATE TABLE Verschreibung (
    verschreibung_id SERIAL PRIMARY KEY,
    konsultation_id INTEGER REFERENCES Videokonsultation(konsultation_id) ON DELETE CASCADE,
    medikament BYTEA NOT NULL,
    dosierung_value NUMERIC(5, 2),  -- numerische Dosierung
    dosierung_unit VARCHAR(10) CHECK (dosierung_unit IN ('ml', 'mg')), -- Einheit der Dosierung
    anweisung BYTEA NOT NULL
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;
