#!/bin/bash

# === Active l'environnement virtuel et exécute le script Python ===

# Vérifie si le script d'activation existe
if [ ! -f "./venv/bin/activate" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé: ./venv/bin/activate"
    exit 1
fi

# Active l'environnement virtuel
source ./venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERREUR] Échec de l'activation de l'environnement virtuel"
    exit 1
fi

# Exécute le script Python
python ./main.py
if [ $? -ne 0 ]; then
    echo "[ERREUR] L'exécution de main.py a échoué"
    exit 1
fi

# Fin
echo "[SUCCÈS] Script terminé avec succès"
