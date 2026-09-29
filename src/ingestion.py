import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def charger_et_decouper_documents(directory_path):
    """
    1. Vérifie si le dossier existe et contient des fichiers PDF.
    2. Charge les documents PDF.
    3. Découpe les documents en blocs de texte (chunks) pour garder le contexte
    4. Retourne la liste des chunks générés.
    """
    # Vérification de l'existence du dossier de documents
    if not os.path.exists(directory_path) or not os.listdir(directory_path):
        print(f" Le dossier '{directory_path}' est vide ou n'existe pas.")
        print(" Déposez vos PDF de consignes de SAE dedans avant le lancement du script.")
        return []

    print(f" Chargement des documents depuis : {directory_path}...")
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()
    print(f" {len(documents)} pages de documents chargées avec succès.")

    # Configuration du découpage (Chunking) pour garder le contexte des consignes
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # Taille idéale pour que Llama 3 traite bien l'information
        chunk_overlap=150,     # Chevauchement pour ne pas couper une phrase importante en deux
        length_function=len
    )

    print(" Découpage en chunks")
    chunks = text_splitter.split_documents(documents)
    print(f"Nombre total de blocs générés : {len(chunks)}")
    
    return chunks

if __name__ == "__main__":
    SOURCE_DIR = os.path.join("data", "source_pdfs")
    
