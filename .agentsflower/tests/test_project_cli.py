"""Unit tests for AgentsFlower Project Management CLI."""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import cli
import studio


class TestProjectCLI(unittest.TestCase):
    def test_project_list_exit_zero(self):
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = cli.main(["project", "list"])
            self.assertEqual(code, 0)
            output = fake_out.getvalue()
            self.assertIn("Workspaces & Discovered Projects", output)

    def test_project_attach_validates_path(self):
        with tempfile.TemporaryDirectory() as td:
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = cli.main(["project", "attach", td])
                self.assertEqual(code, 0)
                output = fake_out.getvalue()
                self.assertIn("Attached project", output)

    def test_project_attach_missing_path(self):
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = cli.main(["project", "attach"])
            self.assertEqual(code, 1)

    def test_project_unknown_subcommand(self):
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = cli.main(["project", "unknown_subcmd_xyz"])
            self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
