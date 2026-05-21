import tempfile
import unittest
from pathlib import Path

from jarvis_core.prompts import DEFAULT_SYSTEM_PROMPT, load_system_prompt


class PromptTests(unittest.TestCase):
    def test_load_system_prompt_returns_default_without_path(self) -> None:
        self.assertEqual(load_system_prompt(), DEFAULT_SYSTEM_PROMPT)

    def test_load_system_prompt_reads_custom_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_path = Path(temp_dir) / "system.md"
            prompt_path.write_text("Custom system prompt\n", encoding="utf-8")

            self.assertEqual(load_system_prompt(str(prompt_path)), "Custom system prompt")


if __name__ == "__main__":
    unittest.main()
