import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.chatbot import answer_question, prepare_vectorstore


class FakeVectorStore:
    collections: dict[str, list[Document]] = {}

    def __init__(self, collection_name: str, persist_directory: str, **kwargs):
        self.key = f"{persist_directory}:{collection_name}"
        self.documents = self.collections.setdefault(self.key, [])
        self.client_settings = kwargs.get("client_settings")

    def get(self, include=None):
        return {"ids": [str(index) for index in range(len(self.documents))]}

    def delete_collection(self):
        self.collections.pop(self.key, None)
        self.documents = []

    @classmethod
    def from_documents(
        cls, documents, collection_name: str, persist_directory: str, **kwargs
    ):
        store = cls(collection_name, persist_directory, **kwargs)
        store.documents.extend(documents)
        return store

    def similarity_search(self, query: str, k: int):
        return self.documents[:k]


class FakeChatModel:
    def invoke(self, messages):
        self.messages = messages
        return AIMessage(content="Réponse issue du contexte.")


class FakeSearchStore:
    def __init__(self, documents: list[Document]):
        self.documents = documents

    def similarity_search(self, query: str, k: int):
        return self.documents[:k]


class ChatbotTests(unittest.TestCase):
    def test_index_is_reused_when_source_pdf_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "sources"
            source_dir.mkdir()
            (source_dir / "sujet.pdf").write_bytes(b"pdf source")
            persist_dir = root / "index"
            chunks = [Document(page_content="Jalon le 15 mai.", metadata={})]
            FakeVectorStore.collections.clear()

            with (
                patch("src.chatbot.Chroma", FakeVectorStore),
                patch(
                    "src.chatbot.charger_et_decouper_documents", return_value=chunks
                ) as load_documents,
            ):
                first_store = prepare_vectorstore(source_dir, persist_dir, None)
                second_store = prepare_vectorstore(source_dir, persist_dir, None)

            self.assertEqual(load_documents.call_count, 1)
            self.assertEqual(len(first_store.get()["ids"]), 1)
            self.assertEqual(len(second_store.get()["ids"]), 1)
            self.assertFalse(first_store.client_settings.anonymized_telemetry)

    def test_changed_pdf_rebuilds_index_without_duplicate_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "sources"
            source_dir.mkdir()
            source_pdf = source_dir / "sujet.pdf"
            source_pdf.write_bytes(b"first version")
            persist_dir = root / "index"
            first_chunk = Document(page_content="Première version.", metadata={})
            second_chunk = Document(page_content="Version mise à jour.", metadata={})
            FakeVectorStore.collections.clear()

            with (
                patch("src.chatbot.Chroma", FakeVectorStore),
                patch(
                    "src.chatbot.charger_et_decouper_documents",
                    side_effect=[[first_chunk], [second_chunk]],
                ) as load_documents,
            ):
                prepare_vectorstore(source_dir, persist_dir, None)
                source_pdf.write_bytes(b"updated version")
                updated_store = prepare_vectorstore(source_dir, persist_dir, None)

            self.assertEqual(load_documents.call_count, 2)
            self.assertEqual(len(updated_store.get()["ids"]), 1)
            self.assertEqual(
                updated_store.similarity_search("version", k=1)[0].page_content,
                "Version mise à jour.",
            )

    def test_answer_cites_source_and_page(self):
        document = Document(
            page_content="Le jalon est prévu le 15 mai.",
            metadata={"source": "sujet.pdf", "page": 1},
        )
        chat_model = FakeChatModel()
        answer = answer_question(
            "Quelle est la date du jalon ?",
            FakeSearchStore([document]),
            chat_model,
            [],
        )

        self.assertIn("sujet.pdf, p. 2", answer)
        self.assertIn("Réponse issue du contexte.", answer)
        self.assertIn("Le jalon est prévu le 15 mai.", chat_model.messages[-1].content)


if __name__ == "__main__":
    unittest.main()
