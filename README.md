Simulateur d'Impact Énergétique IA

Ce projet est un outil de mesure et de projection de l'empreinte carbone lié à l'utilisation de l'Intelligence Artificielle et au fonctionnement de serveurs dédiés. Il a été conçu pour répondre aux besoins d'analyse d'impact environnemental (Réponse Appel d'Offre 2025 - CFA EnSup-LR).

Structure du Projet

Le programme est découpé en modules pour une meilleure lisibilité :
    - app.py : Le fichier principal. Il gère l'interface utilisateur Streamlit, les onglets et la navigation.
    - logic.py : Le moteur de calcul. Contient les formules mathématiques pour la consommation CPU/GPU, le stockage et les projections CO2.
    - utils.py : Utilitaires techniques, notamment la détection automatique du type de connexion réseau (Fibre vs WiFi).
    - styles.py : Gestion du design et injection de code CSS pour la traduction de l'interface en français.

Installation et Configuration
1. Prérequis
Assurez-vous d'avoir Python 3.9+ installé sur votre machine.

2. Création de l'environnement virtuel (Recommandé)
Il est préférable d'isoler les bibliothèques du projet pour éviter les conflits.

    A) Sur Windows :

python -m venv venv
venv\Scripts\activate

    B) Sur Mac/Linux :

python3 -m venv venv
source venv/bin/activate    

3. Installation des bibliothèques
Une fois l'environnement activé, installez les dépendances nécessaires :

Commande : ```pip install streamlit pandas psutil codecarbon```

    - streamlit : Pour l'interface web interactive.
    - pandas : Pour la manipulation des données et l'affichage des tableaux.
    - psutil : Pour l'analyse des composants système et du réseau.
    - codecarbon : Pour mesurer en temps réel la consommation électrique de votre processeur lors de l'analyse.

Lancement de l'application

Pour démarrer le simulateur, exécutez la commande suivante à la racine du dossier :

Commande : ```streamlit run app.py```

L'application s'ouvrira automatiquement dans votre navigateur par défaut (généralement à l'adresse http://localhost:8501).
