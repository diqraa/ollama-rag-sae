import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from src.ingestion import PROJECT_ROOT


class WebAppTests(unittest.TestCase):
    def test_page_opens_chat_when_pdf_is_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir)
            (source_dir / "sujet.pdf").write_bytes(b"PDF de test")
            with patch.dict(os.environ, {"SAE_SOURCE_DIR": str(source_dir)}):
                app = AppTest.from_file(
                    str(PROJECT_ROOT / "src" / "web_app.py"),
                    default_timeout=30,
                ).run()

        self.assertFalse(app.exception)
        self.assertIn("Assistant SAE", app.title[0].value)
        self.assertEqual(len(app.chat_input), 1)
        self.assertFalse(app.chat_input[0].disabled)
        sidebar_markdown = [element.value for element in app.sidebar.markdown]
        self.assertTrue(
            any("Créé par Aicha, alias diqraa." in value for value in sidebar_markdown)
        )
        self.assertTrue(
            any("aicha.dabo@etu.u-pec.fr" in value for value in sidebar_markdown)
        )

    def test_page_disables_chat_when_no_pdf_is_available(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"SAE_SOURCE_DIR": temp_dir}):
                app = AppTest.from_file(
                    str(PROJECT_ROOT / "src" / "web_app.py"),
                    default_timeout=30,
                ).run()

        self.assertFalse(app.exception)
        self.assertEqual(len(app.chat_input), 1)
        self.assertTrue(app.chat_input[0].disabled)


if __name__ == "__main__":
    unittest.main()
