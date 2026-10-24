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

    def test_tasks_include_dispatch_header_fields(self):
        code, res = self.api("/api/tasks?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertTrue(res.get("ok"), res)
        tasks = res["data"]["tasks"]
        self.assertTrue(tasks, "no tasks in ledger")
        for t in tasks:
            for key in ("branch", "worktree", "model"):
                self.assertIn(key, t, f"{t.get('id')} missing {key}")
        with_header = [t for t in tasks if t.get("worktree") or t.get("branch")]
        self.assertTrue(with_header, "no task exposes Branch/Worktree header fields")


class TestStudioShell(StudioApiCase):
    def shell_html(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            return resp.read().decode("utf-8")

    def test_index_topnav_and_views(self):
        html = self.shell_html()
        for marker in (
            'class="topnav"',
            'data-tab="explorer"',
            'data-tab="kanban"',
            'id="taskTotalBadge"',
            'data-tab="analytics"',
            'data-tab="capacity"',
            'class="kanban-grid"',
            'id="stageFilters"',
        ):
            self.assertIn(marker, html)

    def test_index_topnav_has_only_four_core_tabs(self):
        html = self.shell_html()
        self.assertEqual(html.count('data-tab="'), 4, html[:2000])
        for removed in ('data-tab="graft"', 'data-tab="creator"', 'data-tab="guide"'):
            self.assertNotIn(removed, html)

    def test_index_resizers_and_editor_tabs_bar(self):
        html = self.shell_html()
        for marker in (
            'id="sidebarResizer"',
            'id="chatResizer"',
            'resizer-grip',
            'id="editorTabsBar"',
        ):
            self.assertIn(marker, html)

    def test_index_model_selector_dropdown(self):
        html = self.shell_html()
        for marker in ('id="chatModelPill"', 'id="chatModelDropdown"', 'model-dropdown'):
            self.assertIn(marker, html)

    def test_studio_js_splitter_persistence_and_models(self):
        js = self.shell_asset("studio.js")
        for marker in (
            'af_sidebar_width',
            'af_chat_width',
            'localStorage',
            'gemini-4-argon-high',
            'claude-opus-4-6-thinking',
            'gpt-5-5-high',
        ):
            self.assertIn(marker, js)

    def test_studio_css_topnav_no_horizontal_scroll(self):
        css = self.shell_asset("studio.css")
        block = css.split(".topnav-menu", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-x: hidden", block)

    def shell_asset(self, name):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/{name}") as resp:
            return resp.read().decode("utf-8")

    def test_index_sidebar_and_chat_cockpit(self):
        html = self.shell_html()
        for marker in (
            "ACTIVE WORKSPACE",
            'id="btnOpenAttachModal"',
            'id="btnOpenCreateModal"',
            'id="projectAccordion"',
            'id="explorerBreadcrumbs"',
            'id="explorerCodeView"',
            'class="chat-stream"',
            'class="chat-composer"',
            'id="chatModelPill"',
            'id="inspectorTaskSelect"',
        ):
            self.assertIn(marker, html)




class TestTaskSynthesisAndPool(StudioApiCase):
    def test_synthesize_generates_task_pool_from_dialogue(self):
        code, res = self.api(
            "/api/task/synthesize",
            method="POST",
            body={
                "project": str(studio.REPO_ROOT),
                "thread": "research",
                "model": "gemini-4-argon-high",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "1. Architect AST blast-radius synthesis in studio.py using resolve_graft and graft_blast_radius. "
                            "2. Add unit tests in test_studio.py to verify task pool registration."
                        ),
                    }
                ],
            },
        )
        self.assertEqual(code, 200, res)
        self.assertTrue(res.get("ok"), res)
        tasks = res.get("tasks", [])
        self.assertGreaterEqual(len(tasks), 2, res)
        self.assertEqual(res.get("pool"), tasks)
        self.assertIn("blast_radius", res)
        self.assertIsInstance(res["blast_radius"].get("affected_files"), list)
        self.assertTrue(res["blast_radius"]["affected_files"], "blast radius should include affected files")
        for t in tasks:
            self.assertRegex(t.get("id", ""), r"^T-\d+$")
            self.assertTrue(t.get("title"))
            self.assertTrue(t.get("stage"))
            self.assertIn(t.get("role"), ("developer", "tester", "deployer"))
            self.assertIn(t.get("effort"), ("low", "medium", "high", "max"))
            self.assertIn(t.get("model"), ("swe-2-high", "gemini-4-argon-high"))
            self.assertTrue(t.get("allowed_files"))
            self.assertTrue(t.get("criteria"))
            self.assertTrue(any(str(c).startswith("C-01:") for c in t["criteria"]))

    def test_synthesize_complexity_floor_vs_escalation(self):
        code, res = self.api(
            "/api/task/synthesize",
            method="POST",
            body={
                "project": str(studio.REPO_ROOT),
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "1. Design complex multi-file AST knowledge graph architecture and cross-cutting security gate synthesis across studio.py, graft.py, gate.py, and index.html. "
                            "2. Update minor CSS badge label in studio.css."
                        ),
                    }
                ],
            },
        )
        self.assertEqual(code, 200, res)
        tasks = res.get("tasks", [])
        self.assertGreaterEqual(len(tasks), 2)
        models = {t["model"] for t in tasks}
        self.assertIn("gemini-4-argon-high", models)
        self.assertIn("swe-2-high", models)

    def test_synthesize_leverages_graft_blast_radius(self):
        from unittest.mock import patch

        with patch.object(
            studio.graft,
            "graft_blast_radius",
            return_value=[".agentsflower/tools/graft.py", ".agentsflower/tools/studio.py"],
        ) as mock_br:
            code, res = self.api(
                "/api/task/synthesize",
                method="POST",
                body={
                    "project": str(studio.REPO_ROOT),
                    "messages": [{"role": "user", "content": "Refactor resolve_graft in graft.py"}],
                },
            )
            self.assertEqual(code, 200, res)
            self.assertTrue(mock_br.called)
            self.assertIn(".agentsflower/tools/graft.py", res["blast_radius"]["affected_files"])

    def test_synthesize_rejects_unregistered_project(self):
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api(
                "/api/task/synthesize",
                method="POST",
                body={"project": td, "messages": [{"role": "user", "content": "Build feature"}]},
            )
            self.assertEqual(code, 403)
            self.assertFalse(res.get("ok", True))

    def test_batch_register_pool_commits_ledger_and_generates_files(self):
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "pool_proj"
            flow = proj / ".agentsflower"
            (flow / "state").mkdir(parents=True)
            (flow / "tasks").mkdir(parents=True)
            studio.save_attached_project(str(proj))
            try:
                pool = [
                    {
                        "id": "T-201",
                        "title": "Implement conversational thread switcher",
                        "stage": "7",
                        "role": "developer",
                        "tool": "devin",
                        "model": "swe-2-high",
                        "effort": "medium",
                        "goal": "Add thread switcher in chat header.",
                        "allowed_files": [".agentsflower/studio/index.html", ".agentsflower/studio/studio.js"],
                        "criteria": [
                            "C-01: Header switches between Research and task threads.",
                            "C-02: Unit tests pass.",
                        ],
                    },
                    {
                        "id": "T-202",
                        "title": "Synthesize task pool with AST blast radius",
                        "stage": "7",
                        "role": "developer",
                        "tool": "devin",
                        "model": "gemini-4-argon-high",
                        "effort": "high",
                        "goal": "Implement /api/task/synthesize endpoint.",
                        "allowed_files": [".agentsflower/tools/studio.py"],
                        "criteria": [
                            "C-01: Endpoint returns synthesized task pool.",
                        ],
                    },
                ]
                code, res = self.api(
                    "/api/task/pool/register",
                    method="POST",
                    body={"project": str(proj), "tasks": pool},
                )
                self.assertEqual(code, 200, res)
                self.assertTrue(res.get("ok"), res)
                self.assertEqual(res.get("registered"), ["T-201", "T-202"])
                self.assertEqual(len(res.get("files", [])), 2)
                ledger_text = (flow / "state" / "tasks.md").read_text(encoding="utf-8")
                self.assertIn("| T-201 |", ledger_text)
                self.assertIn("| T-202 |", ledger_text)
                self.assertIn("Implement conversational thread switcher", ledger_text)
                self.assertIn("Synthesize task pool with AST blast radius", ledger_text)
                t201_files = list((flow / "tasks").glob("T-201-*.md"))
                t202_files = list((flow / "tasks").glob("T-202-*.md"))
                self.assertEqual(len(t201_files), 1)
                self.assertEqual(len(t202_files), 1)
                t202_text = t202_files[0].read_text(encoding="utf-8")
                self.assertIn("Model: gemini-4-argon-high", t202_text)
                self.assertIn("Effort: high", t202_text)
                self.assertIn("- [ ] C-01: Endpoint returns synthesized task pool.", t202_text)
            finally:
                try:
                    attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                    attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                    studio.ATTACHED_FILE.write_text(
                        json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                except Exception:
                    pass

    def test_task_context_endpoint_returns_contract_files_log_and_diff(self):
        code, tasks_res = self.api("/api/tasks?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertTrue(tasks_res.get("ok"))
        first_id = tasks_res["data"]["tasks"][0]["id"]
        code, res = self.api(
            "/api/task/context?" + self.q({"project": str(studio.REPO_ROOT), "id": first_id})
        )
        self.assertEqual(code, 200, res)
        self.assertTrue(res.get("ok"), res)
        self.assertEqual(res["task"]["id"], first_id)
        self.assertIn("allowed_files", res["task"])
        self.assertIn("criteria", res["task"])
        self.assertIn("recent_log", res)
        self.assertIn("git", res)

    def test_conversational_inception_ui_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            "Research &amp; Inception",
            'id="btnSynthesizeTasks"',
            "Synthesize Tasks from Discussion",
        ):
            self.assertIn(marker, html)

        for marker in (
            "/api/task/synthesize",
            "/api/task/pool/register",
            "/api/task/context",
            "Approve & Register Pool in Ledger",
            "task-pool-card",
            "Research & Inception",
        ):
            self.assertIn(marker, js)

        for marker in (".task-pool-card", ".btn-synthesize", ".btn-approve-pool"):
            self.assertIn(marker, css)


if __name__ == "__main__":
    unittest.main()
