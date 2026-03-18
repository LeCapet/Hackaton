# Lancer le programme
Executer le programme qui est dans le dossier dist

# Claude Transport Meter

Petit outil desktop Python pour :

- lancer une session de mesure avec `START`
- suivre le trafic HTTPS attribuable à Claude
- cumuler les volumes upload / download
- détecter le type d'accès réseau local
- estimer un nombre de next hops
- calculer une énergie transport estimée et un CO2 estimé
- enregistrer un mini compte rendu de session
- afficher un graphique temps réel

## Fichiers principaux

- `app.py` : interface Tkinter + graphique live + enregistrement de session
- `tracker.py` : capture réseau via Scapy
- `network_info.py` : IP publique, DNS Claude, type réseau, géoloc, hops
- `impact.py` : calcul Wh + CO2
- `config.py` : constantes du projet

## Dépendances

```bash
python -m pip install -r requirements.txt