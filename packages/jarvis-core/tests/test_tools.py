import tempfile
import unittest
from pathlib import Path

from jarvis_core.tools import ToolContext, build_builtin_registry


class ToolTests(unittest.TestCase):
    def test_builtin_registry_lists_tools(self) -> None:
        registry = build_builtin_registry()

        tool_names = {definition.name for definition in registry.definitions()}

        self.assertIn("current_time", tool_names)
        self.assertIn("list_directory", tool_names)
        self.assertIn("read_file", tool_names)
        self.assertIn("project_status", tool_names)

    def test_list_directory_and_read_file_are_limited_to_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text("DUMMY_ENV_VALUE=not-real", encoding="utf-8")
            (root / "notes.txt").write_text("hello", encoding="utf-8")
            registry = build_builtin_registry()
            context = ToolContext(root_dir=root)

            listing = registry.run("list_directory", {"path": "."}, context)
            content = registry.run("read_file", {"path": "notes.txt"}, context)

            self.assertIn("notes.txt", listing.content)
            self.assertNotIn(".env", listing.content)
            self.assertEqual(content.content, "hello")

            with self.assertRaises(ValueError):
                registry.run("read_file", {"path": "../outside.txt"}, context)

    def test_read_file_refuses_env_and_database_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text("DUMMY_ENV_VALUE=not-real", encoding="utf-8")
            (root / "jarvis.sqlite3").write_text("db", encoding="utf-8")
            registry = build_builtin_registry()
            context = ToolContext(root_dir=root)

            with self.assertRaises(ValueError):
                registry.run("read_file", {"path": ".env"}, context)

            with self.assertRaises(ValueError):
                registry.run("read_file", {"path": "jarvis.sqlite3"}, context)

    def test_unknown_tool_raises_helpful_error(self) -> None:
        registry = build_builtin_registry()

        with self.assertRaisesRegex(ValueError, "Unknown tool"):
            registry.run("missing", {}, ToolContext(root_dir=Path.cwd()))


if __name__ == "__main__":
    unittest.main()
