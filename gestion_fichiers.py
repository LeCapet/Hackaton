# Projet Hackathon - CFA EnSup LR - Mars 2026
# Code permetant de lire différents types de fichiers (PDF, Word, Excel, CSV, TXT) et d'extraire leur contenu pour l'envoyer à l'API LM Studio

import pandas as pd
import docx
import PyPDF2


def lire_fichier(file):
    try:
        if file.type == "text/csv":
            df = pd.read_csv(file)
            return df.to_string()

        elif file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(file)
            return df.to_string()

        elif file.type == "application/pdf":
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])

        elif file.type.startswith("text"):
            return file.read().decode("utf-8")

        else:
            return f"[Fichier non supporté: {file.name}]"

    except Exception as e:
        return f"[Erreur lecture fichier {file.name}: {e}]"