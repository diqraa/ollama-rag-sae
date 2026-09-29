from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = PROJECT_ROOT / "data" / "sources_pdfs"
LEGACY_SOURCE_DIR = PROJECT_ROOT / "data" / "source_pdfs"
if not DEFAULT_SOURCE_DIR.is_dir() and LEGACY_SOURCE_DIR.is_dir():
    DEFAULT_SOURCE_DIR = LEGACY_SOURCE_DIR


def charger_et_decouper_documents(directory_path: str | Path):
    """Charge les PDF d'un répertoire et les découpe en passages avec métadonnées."""
    directory = Path(directory_path)
    if not directory.is_dir():
        raise FileNotFoundError(
            f"Le dossier de documents '{directory}' n'existe pas. "
            "Ajoutez les PDF de SAE dans data/sources_pdfs."
        )

    pdf_files = list(directory.rglob("*.pdf"))
    if not pdf_files:
        raise ValueError(
            f"Aucun PDF trouvé dans '{directory}'. "
            "Ajoutez les PDF de SAE dans data/sources_pdfs."
        )

    loader = PyPDFDirectoryLoader(str(directory), recursive=True)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)
    if not chunks:
        raise ValueError(
            f"Aucun texte exploitable n'a été extrait des PDF dans '{directory}'."
        )

    return chunks
