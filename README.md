# Chat LM Studio (Streamlit)

Application de chat basée sur **LM Studio** avec :
- gestion multi-conversations
- support de fichiers (PDF, CSV, Excel, DOCX, TXT)
- suivi de consommation énergétique (CO₂ / Wh)

---

## Fonctionnalités

- Multi-chat (sessions indépendantes)
- Upload et analyse de fichiers
- Historique de conversation
- Paramétrage des tokens
- Tracking des émissions carbone (CodeCarbon)

---

## Structure du projet
```
project/
│
├── main.py         # Point d'entrée principal
├── config.py       # Configuration (API, constantes)
├── api.py          # Appels à LM Studio
├── utils.py        # Fonctions utilitaires
├── file_reader.py  # Lecture des fichiers
├── ui.py           # Interface Streamlit (sidebar, session)
└── tracker.py      # Tracking carbone
```

---

## Installation

### 1. Cloner le projet
```bash
git clone <repo_url>
cd project
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Exemple de `requirements.txt`
```
streamlit
requests
pandas
python-docx
PyPDF2
codecarbon
openpyxl
```

---

## Configuration

Modifier `config.py` :
```python
BASE_URL = "http://localhost:1234/v1"
API_KEY = "your-api-key"
```

> Assure-toi que LM Studio est lancé avec l'API activée.

---

## Lancer l'application
```bash
streamlit run main.py
```

---

## Formats de fichiers supportés

- CSV
- Excel (.xlsx)
- PDF
- Word (.docx)
- TXT

---

## Tracking énergétique

Le projet utilise **CodeCarbon** pour estimer :
- émissions de CO₂
- consommation énergétique (Wh)

Formule utilisée :
```
Wh = (CO₂ / 0.4) * 1000
```

Les résultats sont affichés dans la sidebar.

---

## Fonctionnement

1. L'utilisateur pose une question
2. Les fichiers (si présents) sont injectés dans le prompt
3. Requête envoyée à LM Studio
4. Réponse affichée
5. Émissions carbone mesurées

---

## Améliorations possibles

- Streaming des réponses (type ChatGPT)
- Sauvegarde des chats (JSON / DB)
- Support multi-modèles
- Gestion sécurisée des clés API
- Dashboard énergétique avancé

---

## Limitations

- Dépend de LM Studio local
- Lecture PDF basique (pas d'OCR)
- Pas de persistance des données

---

## Licence

Projet libre d'utilisation — à adapter selon ton besoin.

---

Projet généré et optimisé pour la clarté et la modularité.
