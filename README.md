Compteur d'Impact Carbone - Projet ATLAS (CFA EnSup-LR) 
Ce programme Python a été conçu pour le Hackathon 2026. Il permet de mesurer en temps réel la consommation électrique et l'empreinte carbone d'une machine. Il cible particulièrement l'impact lié à la manipulation de fichiers (lecture SSD et transfert réseau) lors de l'utilisation de services d'intelligence artificielle.

Fonctionnalités
Mesure adaptative : Identification automatique des composants (CPU, GPU, RAM) via la bibliothèque CodeCarbon pour un calcul de puissance basé sur le matériel réel.

Analyse des flux locaux : Surveillance des entrées/sorties du disque SSD et de la carte réseau avec la bibliothèque psutil.

Conversions automatiques : Transformation de l'énergie en Watt-heures (Wh) et du CO2 en grammes (g).

Interface épurée : Suppression des logs techniques pour n'afficher que les données essentielles de consommation.

Installation et Configuration
1. Création de l'environnement virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances :

Bash
# Création de l'environnement virtuel
python3 -m venv venv

# Activation de l'environnement (Linux/macOS)
source venv/bin/activate
2. Installation des dépendances
Une fois l'environnement activé, installez les bibliothèques requises :

Bash
pip install codecarbon psutil
3. Permissions (Utilisateurs Linux)
Pour permettre au programme de lire directement la consommation des processeurs Intel (interface RAPL), vous devez accorder les droits de lecture :

Bash
sudo chmod -R a+r /sys/class/powercap/intel-rapl/*
Utilisation
Pour lancer le programme de suivi :

Bash
python Consomation.py
Format de sortie
Les données sont actualisées toutes les 2 secondes :

Plaintext
Energie Cumulee: 0.0452 Wh
CO2 rejete: 0.0023 g
------------------------------
Methodologie
Le calcul repose sur deux piliers :

Consommation hardware : Mesure de la puissance dissipée par le CPU et la RAM en temps réel. En l'absence de capteurs accessibles, le programme bascule sur une estimation basée sur le TDP (Thermal Design Power) du modèle détecté.

Empreinte carbone : Application du facteur d'intensité carbone du mix électrique français (environ 52g CO2/kWh), conformément aux données de l'ADEME.

Structure du projet
HackathonPCPerformanceTracker : Classe principale gérant le cycle de vie du tracker.

Gestion des flux : Utilisation de redirections de sortie pour garantir un affichage sans pollution visuelle par les messages d'information système.