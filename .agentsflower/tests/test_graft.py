"""Unit and integration tests for AgentsFlower Graft integration."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import graft
import mcp_server


class GraftResolverTests(unittest.TestCase):
    def test_resolve_graft_finds_in_path(self):
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda cmd: "/usr/local/bin/graft" if cmd == "graft" else None
            exe, err = graft.resolve_graft(auto_install=False)
            self.assertEqual(exe, "/usr/local/bin/graft")
            self.assertIsNone(err)

    def test_resolve_graft_auto_install_fails_when_npm_missing(self):
        with patch("shutil.which", return_value=None), patch.dict(os.environ, {"APPDATA": ""}):
            exe, err = graft.resolve_graft(auto_install=True)
            self.assertIsNone(exe)
            self.assertIn("npm is not found", err)

    def test_runtime_graph_dir_is_outside_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "fake_repo"
            repo.mkdir()
            rdir = graft.runtime_graph_dir(repo, flow_root=FLOW)
            self.assertTrue(rdir.is_dir())
            self.assertIn(".runtime", str(rdir))
            self.assertIn("graft", str(rdir))


class GraftCommandTests(unittest.TestCase):
    @patch("graft.run_graft_cmd")
    def test_graft_build(self, mock_cmd):
        mock_cmd.return_value = (0, "Built 12 files")
        res = graft.graft_build(Path("."))
        self.assertTrue(res["ok"])
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("Built", res["output"])

    @patch("graft.run_graft_cmd")
    def test_graft_query(self, mock_cmd):
        mock_cmd.return_value = (0, "match: src/app.py:42")
        res = graft.graft_query(Path("."), "where is app?")
        self.assertTrue(res["ok"])
        self.assertEqual(res["question"], "where is app?")

    @patch("graft.run_graft_cmd")
    def test_graft_symbols(self, mock_cmd):
        mock_cmd.return_value = (0, "def foo(): ...")
        res = graft.graft_symbols(Path("."), "src/app.py")
        self.assertTrue(res["ok"])
        self.assertEqual(res["file"], "src/app.py")

    @patch("graft.run_graft_cmd")
    def test_graft_impact_symbol(self, mock_cmd):
        mock_cmd.return_value = (0, json.dumps({
            "matches": [
                {"symbol": {"path": "src/app.py"}, "hits": [{"path": "src/caller.py"}]}
            ]
        }))
        res = graft.graft_impact(Path("."), "my_func")
        self.assertTrue(res["ok"])
        self.assertIsNotNone(res["data"])

    @patch("graft.graft_impact")
    def test_graft_blast_radius_extracts_paths(self, mock_impact):
        mock_impact.return_value = {
            "ok": True,
            "data": {
                "matches": [
                    {"symbol": {"path": "src/a.py"}, "hits": [{"path": "src/b.py"}]}
                ],
                "affected_files": ["src/c.py"]
            }
        }
        files = graft.graft_blast_radius(Path("."), ["my_symbol"])
        self.assertEqual(files, ["src/a.py", "src/b.py", "src/c.py"])


class GraftMcpServerTests(unittest.TestCase):
    def test_mcp_functions_wrap_graft(self):
        with patch("graft.graft_query") as mq, patch("graft.graft_impact") as mi, patch("graft.graft_symbols") as ms:
            mq.return_value = {"ok": True, "output": "results"}
            mi.return_value = {"ok": True, "data": {}}
            ms.return_value = {"ok": True, "output": "signatures"}

            r_q = mcp_server.graft_query("how to run?")
            self.assertTrue(r_q["ok"])

            r_i = mcp_server.graft_impact("some_symbol")
            self.assertTrue(r_i["ok"])

            r_s = mcp_server.graft_symbols("file.py")
            self.assertTrue(r_s["ok"])

    def test_mcp_validation(self):
        self.assertFalse(mcp_server.graft_query("")["ok"])
        self.assertFalse(mcp_server.graft_impact("")["ok"])
        self.assertFalse(mcp_server.graft_symbols("")["ok"])


if __name__ == "__main__":
    unittest.main()
