@echo off
REM === Active l'environnement virtuel et exécute le script Python ===

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

REM Exécute le script Python
python .\main.py
IF ERRORLEVEL 1 (
    echo [ERREUR] L'exécution de main.py a échoué
    exit /b 1
)

REM Fin
echo [SUCCÈS] Script terminé avec succès
