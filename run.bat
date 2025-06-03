@echo off
REM === Active l'environnement virtuel, installe les dépendances et exécute le script Python ===

REM Vérifie si l'environnement virtuel existe
IF NOT EXIST ".\venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouvé: .\venv\Scripts\activate.bat
    exit /b 1
)

REM Active l'environnement virtuel
call ".\venv\Scripts\activate.bat"
IF ERRORLEVEL 1 (
    echo [ERREUR] Échec de l'activation de l'environnement virtuel
    exit /b 1
)

REM Installe les dépendances
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo [ERREUR] L'installation des dépendances a échoué
    exit /b 1
)

REM Exécute le script Python
python .\main.py
IF ERRORLEVEL 1 (
    echo [ERREUR] L'exécution de main.py a échoué
    exit /b 1
)

REM Fin
echo [SUCCÈS] Script terminé avec succès
