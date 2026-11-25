import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import main


class CLITests(unittest.TestCase):
    def test_main_can_exit_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            original_path = main.DB_PATH
            main.DB_PATH = Path(folder) / "database.json"
            try:
                output = StringIO()
                with patch("builtins.input", side_effect=["6"]):
                    with redirect_stdout(output):
                        main.main()
                self.assertIn("Goodbye", output.getvalue())
            finally:
                main.DB_PATH = original_path

    def test_cli_can_register_an_animal_and_persist_it(self):
        with tempfile.TemporaryDirectory() as folder:
            original_path = main.DB_PATH
            main.DB_PATH = Path(folder) / "database.json"
            answers = [
                "1",       # Main: Animal Management
                "1",       # Animal: Register
                "1",       # Dog
                "Max",     # Name
                "3",       # Age
                "male",    # Gender
                "Labrador",# Breed
                "8",       # Back from animal menu
                "6",       # Exit
            ]
            try:
                output = StringIO()
                with patch("builtins.input", side_effect=answers):
                    with redirect_stdout(output):
                        main.main()
                database = main.DB_PATH.read_text(encoding="utf-8")
                self.assertIn('"name": "Max"', database)
                self.assertIn("Animal registered successfully", output.getvalue())
            finally:
                main.DB_PATH = original_path


if __name__ == "__main__":
    unittest.main()
