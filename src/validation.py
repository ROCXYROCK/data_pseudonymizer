import toml

# Erlaubte Fachgruppen
allowed_specialties = toml.load('cfg/db.toml')['fachgebiete']

def is_valid_specialty(specialty):
    """Überprüft, ob die eingegebene Fachgruppe gültig ist."""
    return specialty in allowed_specialties