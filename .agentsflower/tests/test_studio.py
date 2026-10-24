"""Unit tests for the AgentsFlower Studio local web UI backend (studio.py)."""
import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import HTTPServer
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import studio


class StudioApiCase(unittest.TestCase):
    """HTTP-level tests against a real StudioHandler instance on an ephemeral port."""

    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), studio.StudioHandler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def api(self, path, method="GET", body=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            url, data=data, method=method, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except Exception:
                return e.code, {}

    def q(self, params):
        return urllib.parse.urlencode(params)


class TestProjectTree(StudioApiCase):
    def test_tree_lists_repo_root(self):
        code, res = self.api("/api/project/tree?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertEqual(code, 200)
        self.assertTrue(res.get("ok"), res)
        names = {e["name"] for e in res["entries"]}
        self.assertIn(".agentsflower", names)
        self.assertIn("AGENTS.md", names)

    def test_tree_dirs_before_files_and_types(self):
        code, res = self.api("/api/project/tree?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertTrue(res.get("ok"), res)
        types = [e["type"] for e in res["entries"]]
        self.assertEqual(types, sorted(types, key=lambda t: 0 if t == "dir" else 1))
        entry = next(e for e in res["entries"] if e["name"] == ".agentsflower")
        self.assertEqual(entry["type"], "dir")

    def test_tree_subdirectory(self):
        code, res = self.api(
            "/api/project/tree?" + self.q({"project": str(studio.REPO_ROOT), "path": ".agentsflower"})
        )
        self.assertTrue(res.get("ok"), res)
        names = {e["name"] for e in res["entries"]}
        self.assertIn("tools", names)
        self.assertIn("studio", names)

    def test_tree_rejects_parent_traversal(self):
        for bad in ("..", "../..", ".agentsflower/../../..", "..\\.."):
            code, res = self.api(
                "/api/project/tree?" + self.q({"project": str(studio.REPO_ROOT), "path": bad})
            )
            self.assertFalse(res.get("ok", True), f"traversal accepted: {bad}")

    def test_tree_rejects_absolute_path(self):
        code, res = self.api(
            "/api/project/tree?"
            + self.q({"project": str(studio.REPO_ROOT), "path": str(Path(studio.REPO_ROOT).parent)})
        )
        self.assertFalse(res.get("ok", True))

    def test_tree_rejects_unregistered_project(self):
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api("/api/project/tree?" + self.q({"project": td}))
            self.assertFalse(res.get("ok", True))

    def test_tree_rejects_missing_dir(self):
        code, res = self.api(
            "/api/project/tree?"
            + self.q({"project": str(studio.REPO_ROOT), "path": "no-such-dir-xyz"})
        )
        self.assertFalse(res.get("ok", True))


class TestFileRead(StudioApiCase):
    def test_read_version_file(self):
        code, res = self.api(
            "/api/file/read?"
            + self.q({"project": str(studio.REPO_ROOT), "path": ".agentsflower/VERSION"})
        )
        self.assertEqual(code, 200)
        self.assertTrue(res.get("ok"), res)
        self.assertIn("content", res)
        self.assertRegex(res["content"].strip(), r"^\d+\.\d+\.\d+$")
        self.assertFalse(res.get("truncated", False))

    def test_read_rejects_parent_traversal(self):
        for bad in ("../AGENTS.md", "../../outside.txt", ".agentsflower/../../CLAUDE.md"):
            code, res = self.api(
                "/api/file/read?" + self.q({"project": str(studio.REPO_ROOT), "path": bad})
            )
            self.assertFalse(res.get("ok", True), f"traversal accepted: {bad}")

    def test_read_rejects_absolute_path_outside_root(self):
        outside = str(Path(studio.REPO_ROOT).parent / "AGENTS.md")
        code, res = self.api(
            "/api/file/read?" + self.q({"project": str(studio.REPO_ROOT), "path": outside})
        )
        self.assertFalse(res.get("ok", True))

    def test_read_rejects_missing_file(self):
        code, res = self.api(
            "/api/file/read?"
            + self.q({"project": str(studio.REPO_ROOT), "path": "no-such-file-xyz.md"})
        )
        self.assertFalse(res.get("ok", True))

    def test_read_rejects_directory(self):
        code, res = self.api(
            "/api/file/read?" + self.q({"project": str(studio.REPO_ROOT), "path": ".agentsflower"})
        )
        self.assertFalse(res.get("ok", True))

    def test_read_rejects_unregistered_project(self):
        with tempfile.TemporaryDirectory() as td:
            secret = Path(td) / "secret.txt"
            secret.write_text("classified", encoding="utf-8")
            code, res = self.api(
                "/api/file/read?" + self.q({"project": td, "path": "secret.txt"})
            )
            self.assertFalse(res.get("ok", True))
            self.assertNotIn("classified", json.dumps(res))


class TestProjectGit(StudioApiCase):
    def test_git_summary_for_repo(self):
        code, res = self.api("/api/project/git?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertEqual(code, 200)
        self.assertTrue(res.get("ok"), res)
        self.assertTrue(res.get("is_git"), res)
        self.assertIn("branch", res)


class TestAuthorizationGate(StudioApiCase):
    def _git_init(self, path):
        subprocess.run(
            ["git", "init", "-q", "-b", "main", str(path)],
            check=True, capture_output=True,
        )

    def test_create_refused_without_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "proj"
            target.mkdir()
            self._git_init(target)
            code, res = self.api(
                "/api/project/create", method="POST", body={"path": str(target)}
            )
            self.assertFalse(res.get("ok", True), res)
            self.assertTrue(res.get("requires_authorization"), res)
            self.assertFalse(
                (target / ".agentsflower").exists(),
                "install ran without explicit authorization",
            )

    def test_update_refused_without_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api(
                "/api/project/update", method="POST", body={"path": td}
            )
            self.assertFalse(res.get("ok", True), res)
            self.assertTrue(res.get("requires_authorization"), res)

    def test_create_with_authorization_installs(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "proj"
            target.mkdir()
            self._git_init(target)
            code, res = self.api(
                "/api/project/create",
                method="POST",
                body={"path": str(target), "authorized": True},
            )
            self.assertTrue(res.get("ok"), res)
            self.assertTrue((target / ".agentsflower" / "VERSION").is_file())
            try:
                attached = json.loads(
                    studio.ATTACHED_FILE.read_text(encoding="utf-8")
                )
                attached = [p for p in attached if str(target) not in p]
                studio.ATTACHED_FILE.write_text(
                    json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            except Exception:
                pass


class TestTasksPayload(StudioApiCase):
    def test_tasks_include_criteria_details(self):
        code, res = self.api("/api/tasks?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertTrue(res.get("ok"), res)
        tasks = res["data"]["tasks"]
        with_criteria = [t for t in tasks if t.get("criteria")]
        self.assertTrue(with_criteria, "no task exposes a criteria checklist")
        c = with_criteria[0]["criteria"][0]
        self.assertIn("id", c)
        self.assertIn("text", c)
        self.assertIn("done", c)


if __name__ == "__main__":
    unittest.main()
