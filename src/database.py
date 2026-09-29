import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
# Importation directe de votre fonction depuis votre fichier ingestion.py
from .ingestion import charger_et_decouper_documents

SOURCE_DIR = os.path.join("data", "source_pdfs")
VECTOR_DB_DIR = os.path.join("data", "vector_db")

def initialiser_base_vectorielle():
    """
    Initialise ou charge la base de donnees vectorielle locale ChromaDB
    en s'appuyant sur le decoupage de src/ingestion.py et le modele Llama 3.
    """
    # Utilisation de Llama 3 via Ollama pour transformer tous les blocs en vecteurs
    embeddings = OllamaEmbeddings(model="llama3")

    # Si la base de donnees locale contient deja l'indexation, on la charge
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print(f"Chargement de la base vectorielle existante depuis : {VECTOR_DB_DIR}")
        vector_db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)
        return vector_db

    print("Base vectorielle introuvable. Initialisation...")
    
    # 1. Appel direct de votre fonction pour recuperer les blocs de votre PDF de 75 pages
    chunks = charger_et_decouper_documents(SOURCE_DIR)
    
    if not chunks:
        print("Erreur : Aucun bloc de texte genere. Verifiez le dossier source.")
        return None

    # 2. Generation et sauvegarde locale dans ChromaDB
    print("Generation des embeddings et stockage dans ChromaDB...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    print(f"Base vectorielle cree et sauvegardee avec succes dans : {VECTOR_DB_DIR}")
    return vector_db

if __name__ == "__main__":
    db = initialiser_base_vectorielle()
