@echo off
echo ================================
echo     LANCEMENT DE L'API
echo ================================

:: Étape 1 - Installation des dépendances
echo [*] Installation des dépendances...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Étape 2 - Téléchargement des ressources NLTK
echo [*] Téléchargement des données NLTK (vader_lexicon)...
python -c "import nltk; nltk.download('vader_lexicon')"

:: Étape 3 - Lancement de l'API FastAPI avec uvicorn
echo [*] Lancement de l'API...
python -m uvicorn main:app --reload