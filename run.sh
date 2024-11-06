#!/bin/bash

# Generiere oder definiere den Secret Key und setze ihn als Umgebungsvariable
export SECRET_KEY=$(python -c 'import os; print(os.urandom(64).hex())')

sleep 2

python /app/src/filler.py


python /app/src/test_initial.py
