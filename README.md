# Hackaton
ATLAS - Indicateur d'Impact Énergétique

Présentation du ProjetDans le cadre du 7ème Hackathon de l'entrepreneuriat de l'IUT de Béziers (2026) , notre groupe (filière Réseaux & Télécoms) a développé un outil de mesure d'impact environnemental pour le projet ATLAS du CFA EnSup-LR.

L'objectif est de sensibiliser les apprentis et les formateurs sur le fait que chaque action numérique (évaluation de compétences, envoi de preuves) a un coût énergétique réel.

Concept TechniqueNotre solution décompose la consommation d'une requête IA en trois couches distinctes, comme identifié lors de notre phase de conception :
Transport (Réseau) : Calcul modulable selon la taille du fichier et la technologie d'accès (WiFi, 4G, Fibre).
Consommation PC Perso : Mesure réelle de l'activité CPU/RAM lors de l'upload et du traitement local via la bibliothèque CodeCarbon.
Inférence IA & Stockage : Estimation de l'énergie consommée par les serveurs de l'IA (Claude) pour l'analyse des compétences et le stockage à long terme des documents (PDF, vidéos, photos).
Installation Prérequis Python 3.13+ 
Un environnement virtuel configuré (.venv)

Installation des dépendancesBash# Activation de l'environnement (Linux)
source .venv/bin/activate

# Installation de CodeCarbon et des utilitaires
pip install codecarbon os math
UtilisationLe script interactif demande le chemin d'un document (preuve de compétence) et la technologie réseau utilisée pour simuler une requête ATLAS.Bashpython main.py

Affichage du bilan en Wh et en gCO2e.
Formules de CalculÉnergie Réseau : 
Énergie IA : 

ÉquipeÉtudiants - IUT de Béziers.
Sujet proposé par : Maeva Gisdal (CFA EnSup-LR).
