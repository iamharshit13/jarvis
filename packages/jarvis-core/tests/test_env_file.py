import os
import tempfile
import unittest
from pathlib import Path

from jarvis_core.config.env_file import load_env_file, parse_env_line


class EnvFileTests(unittest.TestCase):
    def test_parse_env_line_supports_plain_and_quoted_values(self) -> None:
        self.assertEqual(parse_env_line("JARVIS_MODEL_PROVIDER=mock"), ("JARVIS_MODEL_PROVIDER", "mock"))
        self.assertEqual(parse_env_line('MODEL_NAME="openai/gpt-oss-20b"'), ("MODEL_NAME", "openai/gpt-oss-20b"))
        self.assertEqual(parse_env_line("# ignored"), (None, ""))

    def test_load_env_file_sets_missing_values_without_overriding_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "JARVIS_TEST_FROM_FILE=file-value",
                        "JARVIS_TEST_FROM_SHELL=file-value",
                    ]
                ),
                encoding="utf-8",
            )

            os.environ.pop("JARVIS_TEST_FROM_FILE", None)
            os.environ["JARVIS_TEST_FROM_SHELL"] = "shell-value"

            loaded_path = load_env_file(start_dir=Path(temp_dir))

            self.assertEqual(loaded_path, env_path.resolve())
            self.assertEqual(os.environ["JARVIS_TEST_FROM_FILE"], "file-value")
            self.assertEqual(os.environ["JARVIS_TEST_FROM_SHELL"], "shell-value")

            os.environ.pop("JARVIS_TEST_FROM_FILE", None)
            os.environ.pop("JARVIS_TEST_FROM_SHELL", None)


if __name__ == "__main__":
    unittest.main()
