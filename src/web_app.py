import os
from pathlib import Path

os.environ["ANONYMIZED_TELEMETRY"] = "False"

import httpx
import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from ollama import Client, ResponseError

from src.chatbot import (
    DEFAULT_PERSIST_DIR,
    OLLAMA_BASE_URL,
    _fingerprint_sources,
    answer_question,
    prepare_vectorstore,
)
from src.ingestion import DEFAULT_SOURCE_DIR, PROJECT_ROOT

CHAT_MODEL = os.environ.get("SAE_CHAT_MODEL", "llama3")
EMBEDDING_MODEL = os.environ.get("SAE_EMBEDDING_MODEL", "nomic-embed-text")


def _configured_path(environment_variable: str, default: Path) -> Path:
    configured_path = os.environ.get(environment_variable)
    if configured_path is None:
        return default
    path = Path(configured_path)
    return path if path.is_absolute() else PROJECT_ROOT / path


SOURCE_DIR = _configured_path("SAE_SOURCE_DIR", DEFAULT_SOURCE_DIR)
PERSIST_DIR = _configured_path("SAE_PERSIST_DIR", DEFAULT_PERSIST_DIR)


class ChatbotSetupError(RuntimeError):
    pass


def _check_ollama_models() -> None:
    try:
        response = Client(host=OLLAMA_BASE_URL).list()
    except (httpx.HTTPError, ResponseError) as error:
        raise ChatbotSetupError(
            f"Impossible de contacter Ollama sur {OLLAMA_BASE_URL}. "
            "Vérifie qu'Ollama est démarré."
        ) from error

    installed_models = {
        model["name"]
        for model in response.get("models", [])
        if isinstance(model, dict) and isinstance(model.get("name"), str)
    }
    required_models = {CHAT_MODEL, EMBEDDING_MODEL}
    missing_models = {
        model if ":" in model else f"{model}:latest"
        for model in required_models
        if (model if ":" in model else f"{model}:latest") not in installed_models
    }
    if missing_models:
        pull_commands = "\n".join(
            f"ollama pull {model.removesuffix(':latest')}"
            for model in sorted(missing_models)
        )
        raise ChatbotSetupError(
            "Modèle(s) Ollama manquant(s) : "
            f"{', '.join(sorted(missing_models))}.\n"
            "Télécharge-les depuis un terminal :\n"
            f"{pull_commands}"
        )


@st.cache_resource(show_spinner=False)
def _load_chatbot(source_fingerprint: str):
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )
    vectorstore = prepare_vectorstore(SOURCE_DIR, PERSIST_DIR, embeddings)
    chat_model = ChatOllama(
        model=CHAT_MODEL,
        temperature=0,
        base_url=OLLAMA_BASE_URL,
    )
    return vectorstore, chat_model


def main() -> None:
    st.set_page_config(
        page_title="Assistant SAE",
        page_icon="📚",
        layout="centered",
    )
    st.title("Assistant SAE — BUT Informatique")
    st.caption(
        "Pose une question sur les consignes de la SAE. "
        "Les réponses s'appuient sur les PDF et citent leurs sources."
    )

    with st.sidebar:
        st.subheader("À propos")
        st.write("Créé par Aicha, alias diqraa.")
        st.markdown("[Me contacter par e-mail](mailto:aicha.dabo@etu.u-pec.fr)")
        st.divider()
        st.header("Documents")
        if SOURCE_DIR.is_dir():
            pdf_files = sorted(SOURCE_DIR.rglob("*.pdf"))
            if pdf_files:
                st.write(f"{len(pdf_files)} PDF trouvé(s)")
                with st.expander("Afficher les documents"):
                    for pdf_file in pdf_files:
                        st.write(pdf_file.relative_to(SOURCE_DIR).as_posix())
            else:
                st.warning("Aucun PDF dans le dossier source.")
        else:
            st.warning("Le dossier des PDF est introuvable.")
        st.divider()
        st.write(f"Modèle de chat : `{CHAT_MODEL}`")
        st.write(f"Modèle d'embeddings : `{EMBEDDING_MODEL}`")
        st.caption(
            "Ollama doit fonctionner sur cet ordinateur. "
            "Les modèles et les documents restent locaux."
        )

    pdf_files = sorted(SOURCE_DIR.rglob("*.pdf")) if SOURCE_DIR.is_dir() else []
    if not pdf_files:
        st.info(
            "Ajoute les PDF officiels de la SAE dans le dossier source pour "
            "activer le chat."
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ex. Quelles sont les dates des jalons ?",
        disabled=not pdf_files,
    )
    if question is None or not question.strip():
        return

    question = question.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    history = [
        (message["content"], st.session_state.messages[index + 1]["content"])
        for index, message in enumerate(st.session_state.messages[:-1])
        if message["role"] == "user"
        and index + 1 < len(st.session_state.messages)
        and st.session_state.messages[index + 1]["role"] == "assistant"
    ]

    with st.chat_message("assistant"):
        try:
            _check_ollama_models()
            with st.spinner(
                "Recherche dans les documents et préparation de la réponse..."
            ):
                source_fingerprint = _fingerprint_sources(SOURCE_DIR)
                vectorstore, chat_model = _load_chatbot(source_fingerprint)
                answer = answer_question(question, vectorstore, chat_model, history)
        except ChatbotSetupError as error:
            st.error(str(error))
            return
        except (httpx.HTTPError, ResponseError, ValueError) as error:
            st.error(f"Le chatbot n'a pas pu répondre : {error}")
            return
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


main()
