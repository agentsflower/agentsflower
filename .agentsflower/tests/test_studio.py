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
            'id="chatModelSelector"',
            'id="chatModelPill"',
            'class="composer-spacer"',
            'id="btnChatSend"',
            'id="threadSelector"',
            'id="threadPill"',
        ):
            self.assertIn(marker, html)
        for removed in (
            'id="activeProjectChip"',
            'class="search-box"',
            'id="globalSearchInput"',
            'id="btnQuickCreate"',
            'id="btnChatNew"',
            'id="btnChatRefresh"',
            'id="btnChatPlus"',
            'id="btnSynthesizeTasks"',
        ):
            self.assertNotIn(removed, html)




class TestAnalyticsRoadmapContract(StudioApiCase):
    """Analytics & Roadmap view: toolbar contract, embedded dashboard harmonization."""

    def dash_asset(self, name):
        with urllib.request.urlopen(
            f"http://127.0.0.1:{self.port}/dashboard/{name}"
        ) as resp:
            return resp.read().decode("utf-8")

    def test_analytics_toolbar_subtabs_and_actions(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        for marker in (
            'id="view-analytics"',
            'data-sub="index"',
            'data-sub="graph"',
            'data-sub="roadmap"',
            "Tasks & Overview",
            "Gantt & Dependency Graph",
            "Roadmap & Milestones",
            'id="analyticsBuiltStamp"',
            'id="btnDashThemeToggle"',
            'id="btnRebuildDashboard"',
            "Rebuild Analytics",
            'id="btnOpenExternalDashboard"',
            "Open Fullscreen",
            'id="analyticsFrame"',
        ):
            self.assertIn(marker, html)
        # mockup shows the Gantt sub-tab active by default
        self.assertIn('class="btn-subtab active" data-sub="graph"', html)

    def test_workspace_subheader_and_persistent_sidebar(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        for marker in ('id="workspaceSubheader"', 'id="workspacePath"'):
            self.assertIn(marker, html)
        # the workspace sidebar lives outside the analytics view panel:
        # it stays mounted (and visible) whatever sub-view is active
        self.assertLess(html.index('class="sidebar"'), html.index('id="view-analytics"'))
        section = html.split('id="view-analytics"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn('class="sidebar"', section)

    def test_studio_js_embedded_query_and_dashboard_bridge(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        for marker in (
            "embedded=1",
            "dash-meta",
            "dash-theme",
            "btnDashThemeToggle",
            "analyticsBuiltStamp",
            "analyticsSubTab",
            "getElementById('hdr')",
            ".style.display = 'none'",
        ):
            self.assertIn(marker, js)
        # the fullscreen link must NOT carry the embedded flag - standalone view keeps #hdr
        href_lines = [l for l in js.splitlines() if "btnOpenExternalDashboard.href" in l]
        self.assertTrue(href_lines, "external dashboard link never assigned")
        for l in href_lines:
            self.assertNotIn("embedded", l)

    def test_dashboard_embedded_hides_hdr_and_dark_palette(self):
        cjs = self.dash_asset("common.js")
        for marker in ("embedded", "dash-meta", "dash-theme", "postMessage"):
            self.assertIn(marker, cjs)
        ccss = self.dash_asset("common.css")
        for marker in ("[data-embedded]", "#hdr", "#111625", "#161c2d", "display:none!important", "margin-top:0!important"):
            self.assertIn(marker, ccss)

    def test_gantt_layout_contract_markers(self):
        tpl = self.dash_asset("graph_template.html")
        for marker in (
            'id="fbar"',
            'id="fchosen"',
            'id="ctl"',
            'id="ganttOnly"',
            'id="vGantt"',
            'id="vBoard"',
            'id="vSum"',
            'id="asof"',
            'id="play"',
            'id="nowBtn"',
            'id="gl"',
            'id="gr"',
            'id="detail"',
            'id="legend"',
        ):
            self.assertIn(marker, tpl)



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

        self.assertIn("Research &amp; Inception", html)
        for removed in (
            'id="btnSynthesizeTasks"',
            'id="btnChatNew"',
            'id="btnChatRefresh"',
            'id="btnChatPlus"',
        ):
            self.assertNotIn(removed, html)

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

    def test_synthesize_stage_topology_orders_dependencies_without_inversions(self):
        code, res = self.api(
            "/api/task/synthesize",
            method="POST",
            body={
                "project": str(studio.REPO_ROOT),
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "1. Add unit tests in test_studio.py to verify stage synthesis and skill badges. "
                            "2. Render skill pills in studio.js and studio.css after step 3. "
                            "3. Implement core stage topology and skills index parser in studio.py."
                        ),
                    }
                ],
            },
        )
        self.assertEqual(code, 200, res)
        self.assertTrue(res.get("ok"), res)
        tasks = res.get("tasks", [])
        self.assertEqual(len(tasks), 3, tasks)

        stages = [int(t["stage"]) for t in tasks]
        self.assertEqual(stages, sorted(stages), "Tasks must be ordered by non-decreasing stage number")
        self.assertEqual(stages[0], 1)
        self.assertGreater(stages[-1], stages[0])

        stage_by_id = {t["id"]: int(t["stage"]) for t in tasks}
        idx_by_id = {t["id"]: idx for idx, t in enumerate(tasks)}
        for t in tasks:
            self.assertRegex(str(t.get("stage_label", "")), r"^Stage \d{2}$")
            deps = t.get("depends_on") or []
            for dep_id in deps:
                self.assertIn(dep_id, stage_by_id)
                self.assertLess(
                    stage_by_id[dep_id],
                    int(t["stage"]),
                    f"Prerequisite {dep_id} must be in a lower stage than dependent {t['id']}",
                )
                self.assertLess(idx_by_id[dep_id], idx_by_id[t["id"]])

        self.assertIn("studio.py", tasks[0]["title"])
        self.assertIn("test_studio.py", tasks[-1]["title"])

    def test_synthesize_autonomous_skills_mapping_heuristics_and_blast_radius(self):
        code, res = self.api(
            "/api/task/synthesize",
            method="POST",
            body={
                "project": str(studio.REPO_ROOT),
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "1. Build Chrome extension manifest.json and MV3 service worker lifecycle. "
                            "2. Redesign UI layout and dark mode typography in studio.css and index.html. "
                            "3. Optimize SEO metadata, schema.org JSON-LD, and llms.txt citability. "
                            "4. Run performance benchmarks and latency profiling."
                        ),
                    }
                ],
            },
        )
        self.assertEqual(code, 200, res)
        tasks = res.get("tasks", [])
        self.assertEqual(len(tasks), 4, tasks)

        by_kw = {}
        for t in tasks:
            self.assertIsInstance(t.get("skills"), list)
            low = t["goal"].lower()
            if "manifest.json" in low:
                by_kw["mv3"] = t["skills"]
            elif "studio.css" in low:
                by_kw["ui"] = t["skills"]
            elif "llms.txt" in low:
                by_kw["seo"] = t["skills"]
            elif "benchmark" in low:
                by_kw["perf"] = t["skills"]

        self.assertIn("chrome-extension-mv3", by_kw.get("mv3", []))
        self.assertIn("frontend-art-direction", by_kw.get("ui", []))
        self.assertIn("geo-seo-audit", by_kw.get("seo", []))
        self.assertIn("perf-benchmark", by_kw.get("perf", []))

        from unittest.mock import patch
        with patch.object(
            studio.graft,
            "graft_blast_radius",
            return_value=[".agentsflower/studio/studio.css", ".agentsflower/studio/index.html"],
        ):
            code2, res2 = self.api(
                "/api/task/synthesize",
                method="POST",
                body={
                    "project": str(studio.REPO_ROOT),
                    "messages": [{"role": "user", "content": "Refactor module tokens"}],
                },
            )
            self.assertEqual(code2, 200, res2)
            self.assertIn("frontend-art-direction", res2["tasks"][0].get("skills", []))

    def test_batch_register_pool_preserves_skills_in_generated_task_files(self):
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "skills_pool_proj"
            flow = proj / ".agentsflower"
            (flow / "state").mkdir(parents=True)
            (flow / "tasks").mkdir(parents=True)
            studio.save_attached_project(str(proj))
            try:
                pool = [
                    {
                        "id": "T-301",
                        "title": "Polish UI cards in studio.css",
                        "stage": 1,
                        "role": "developer",
                        "tool": "devin",
                        "model": "swe-2-high",
                        "effort": "medium",
                        "skills": ["frontend-art-direction"],
                        "goal": "Update card styles in studio.css.",
                        "allowed_files": [".agentsflower/studio/studio.css"],
                        "criteria": ["C-01: Card styles updated."],
                    },
                    {
                        "id": "T-302",
                        "title": "Generate llms.txt and SEO tags",
                        "stage": 2,
                        "depends": "T-301",
                        "role": "developer",
                        "tool": "devin",
                        "model": "swe-2-high",
                        "effort": "medium",
                        "skills": ["geo-seo-audit"],
                        "goal": "Add llms.txt and structured metadata.",
                        "allowed_files": ["llms.txt"],
                        "criteria": ["C-01: llms.txt generated."],
                    },
                ]
                code, res = self.api(
                    "/api/task/pool/register",
                    method="POST",
                    body={"project": str(proj), "tasks": pool},
                )
                self.assertEqual(code, 200, res)
                self.assertTrue(res.get("ok"), res)
                t301_text = next((flow / "tasks").glob("T-301-*.md")).read_text(encoding="utf-8")
                t302_text = next((flow / "tasks").glob("T-302-*.md")).read_text(encoding="utf-8")
                self.assertIn("Skills: frontend-art-direction", t301_text)
                self.assertIn("Stage: 1", t301_text)
                self.assertIn("Skills: geo-seo-audit", t302_text)
                self.assertIn("Stage: 2", t302_text)
                self.assertIn("Depends on: T-301", t302_text)
            finally:
                try:
                    attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                    attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                    studio.ATTACHED_FILE.write_text(
                        json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                except Exception:
                    pass

    def test_task_pool_card_ui_renders_skill_badges(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")
        for marker in ("skill-badge", "skill-pill", "t.skills"):
            self.assertIn(marker, js)
        for marker in (".skill-badge", ".skill-pill"):
            self.assertIn(marker, css)


DEVIN_MODELS_OUT = """\
Available models (2 families)

SWE-2 (swe-2)
  aliases: swe
  swe-2-high                                                              SWE-2 High  [262K context, Free]
  swe-2-max                                                               SWE-2 Max  [262K context, Free]

GPT-5.5 (gpt-5.5)
  gpt-5-5-high                                                            GPT-5.5 High Thinking  [272K context, $5 / 1M Input \u00b7 $0.5 / 1M Cached input \u00b7 $30 / 1M Output]
"""

AGY_MODELS_OUT = (
    "Fetching available models...\n"
    "gemini-3.8-flash-high\tGemini 3.8 Flash (High)\n"
    "claude-opus-4-6-thinking\tClaude Opus 4.6 (Thinking)\n"
)


class TestCapacityHub(StudioApiCase):
    """Live CLI probe and default worker model endpoints (/api/capacity/*)."""

    def setUp(self):
        self._cache = dict(studio._capacity_probe_cache)
        self._pcache = dict(studio._platform_probe_cache)
        studio._capacity_probe_cache.update(at=0.0, data=None)
        studio._platform_probe_cache.clear()

    def tearDown(self):
        studio._capacity_probe_cache.update(self._cache)
        studio._platform_probe_cache.clear()
        studio._platform_probe_cache.update(self._pcache)

    @staticmethod
    def _fake_which(name):
        return f"/fake/bin/{name}.exe" if name in ("devin", "claude", "codex", "agy") else None

    @staticmethod
    def _fake_run(argv, timeout=None):
        exe = Path(str(argv[0])).name.lower()
        args = list(argv[1:])
        if exe.startswith("codex"):
            if args == ["--version"]:
                return 0, "codex-cli 1.2.3"
            if args == ["login", "status"]:
                return 0, "Logged in using ChatGPT"
            if args == ["models"]:
                return None, ""  # no catalog command: falls back to configured catalog
        if exe.startswith("devin"):
            if args == ["auth", "status"]:
                return 0, "Logged in (via Devin).\nUser: tester"
            if args == ["--version"]:
                return 0, "devin 9.9.9"
            if args == ["models", "list"]:
                return 0, DEVIN_MODELS_OUT
        if exe.startswith("claude"):
            if args == ["--version"]:
                return 0, "9.9.9 (Claude Code)"
            if args == ["auth", "status"]:
                return 0, json.dumps({"loggedIn": True, "subscriptionType": "pro"})
            if args == ["models"]:
                return 0, "Failed to authenticate: OAuth session expired"
        if exe.startswith("agy"):
            if args == ["--version"]:
                return 0, "9.9.9"
            if args == ["models"]:
                return 0, AGY_MODELS_OUT
        return None, ""

    @staticmethod
    def _fake_ollama(path, timeout=3):
        if path == "/api/tags":
            return {"models": [{"name": "qwen2.5-coder:7b", "size": 4000000000,
                                "details": {"family": "qwen2", "parameter_size": "7.6B"}}]}
        if path == "/api/version":
            return {"version": "0.5.0"}
        return None

    def _probe_patches(self):
        from unittest.mock import patch
        return (
            patch.object(studio.shutil, "which", side_effect=self._fake_which),
            patch.object(studio, "_probe_run", side_effect=self._fake_run),
            patch.object(studio, "_fetch_ollama_json", side_effect=self._fake_ollama),
        )

    def test_probe_scans_platforms_and_serves_cache(self):
        pw, pr, po = self._probe_patches()
        with pw, pr as run_mock, po:
            code, res = self.api("/api/capacity/probe")
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertFalse(res.get("cached", True))
            platforms = {p["key"]: p for p in res["platforms"]}
            self.assertEqual(set(platforms), {"devin", "claude", "codex", "agy", "ollama"})

            codex = platforms["codex"]
            self.assertEqual(codex["status"], "active")
            self.assertTrue(codex["authenticated"])
            self.assertEqual(codex["version"], "codex-cli 1.2.3")
            # No CLI catalog command: models come from the configured model-options catalog.
            self.assertEqual({m["id"] for m in codex["models"]}, {"gpt-6.1-sol", "gpt-6-astra"})

            devin = platforms["devin"]
            self.assertEqual(devin["status"], "active")
            self.assertEqual(devin["status_label"], "Active & Authenticated")
            self.assertEqual(devin["version"], "devin 9.9.9")
            ids = {m["id"] for m in devin["models"]}
            self.assertIn("swe-2-high", ids)
            swe = next(m for m in devin["models"] if m["id"] == "swe-2-high")
            self.assertTrue(swe["free"])
            self.assertEqual(swe["context"], "262K context")
            gpt = next(m for m in devin["models"] if m["id"] == "gpt-5-5-high")
            self.assertFalse(gpt["free"])
            self.assertIn("$5 / 1M Input", gpt["pricing"])

            claude = platforms["claude"]
            self.assertEqual(claude["status"], "limited")
            self.assertEqual(claude["version"], "9.9.9 (Claude Code)")
            self.assertIn("Failed to authenticate", claude["note"])

            agy = platforms["agy"]
            self.assertEqual(agy["status"], "active")
            self.assertIn("claude-opus-4-6-thinking", {m["id"] for m in agy["models"]})

            ollama = platforms["ollama"]
            self.assertEqual(ollama["status"], "active")
            self.assertTrue(all(m["free"] for m in ollama["models"]))
            self.assertEqual([m["id"] for m in res["local_free"]["installed"]],
                             ["qwen2.5-coder:7b"])
            self.assertTrue(res["local_free"]["suggested"])

            calls = run_mock.call_count
            code2, res2 = self.api("/api/capacity/probe")
            self.assertEqual(code2, 200)
            self.assertTrue(res2.get("cached"))
            self.assertEqual(run_mock.call_count, calls)

    def test_probe_marks_missing_platforms(self):
        from unittest.mock import patch
        with patch.object(studio.shutil, "which", return_value=None), \
                patch.object(studio, "_fetch_ollama_json", return_value=None):
            code, res = self.api("/api/capacity/probe")
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"))
            for p in res["platforms"]:
                self.assertEqual(p["status"], "missing", p)
                self.assertEqual(p["status_label"], "Not Installed")
            self.assertEqual(res["local_free"]["installed"], [])

    def test_probe_single_platform_returns_only_that_platform(self):
        pw, pr, po = self._probe_patches()
        with pw, pr as run_mock, po as ollama_mock:
            code, res = self.api("/api/capacity/probe?" + self.q({"platform": "agy"}))
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertFalse(res.get("cached", True))
            self.assertEqual([p["key"] for p in res["platforms"]], ["agy"])
            self.assertEqual(res["platform"]["key"], "agy")
            self.assertEqual(res["platform"]["status"], "active")
            self.assertIn("claude-opus-4-6-thinking",
                          {m["id"] for m in res["platform"]["models"]})
            for c in run_mock.call_args_list:
                argv = c.args[0] if c.args else c[0][0]
                self.assertIn("agy", Path(str(argv[0])).name.lower())
            ollama_mock.assert_not_called()

    def test_probe_single_platform_codex_catalog_fallback(self):
        pw, pr, po = self._probe_patches()
        with pw, pr, po:
            code, res = self.api("/api/capacity/probe?" + self.q({"platform": "codex"}))
            self.assertEqual(code, 200, res)
            p = res["platform"]
            self.assertEqual(p["key"], "codex")
            self.assertTrue(p["authenticated"])
            self.assertEqual({m["id"] for m in p["models"]}, {"gpt-6.1-sol", "gpt-6-astra"})

    def test_probe_single_platform_missing_marks_status(self):
        from unittest.mock import patch
        with patch.object(studio.shutil, "which", return_value=None):
            code, res = self.api("/api/capacity/probe?" + self.q({"platform": "devin"}))
            self.assertEqual(code, 200, res)
            p = res["platform"]
            self.assertEqual(p["status"], "missing")
            self.assertEqual(p["status_label"], "Not Installed")
            self.assertEqual(p["models"], [])

    def test_probe_single_platform_serves_own_cache(self):
        pw, pr, po = self._probe_patches()
        with pw, pr as run_mock, po as ollama_mock:
            code, res = self.api("/api/capacity/probe?" + self.q({"platform": "ollama"}))
            self.assertEqual(code, 200, res)
            self.assertEqual(res["platform"]["key"], "ollama")
            self.assertEqual([m["id"] for m in res["platform"]["models"]],
                             ["qwen2.5-coder:7b"])
            calls, ocalls = run_mock.call_count, ollama_mock.call_count
            code2, res2 = self.api("/api/capacity/probe?" + self.q({"platform": "ollama"}))
            self.assertEqual(code2, 200)
            self.assertTrue(res2.get("cached"))
            self.assertEqual(run_mock.call_count, calls)
            self.assertEqual(ollama_mock.call_count, ocalls)
            # A different platform key still probes live.
            code3, res3 = self.api("/api/capacity/probe?" + self.q({"platform": "agy"}))
            self.assertEqual(code3, 200)
            self.assertFalse(res3.get("cached", True))
            self.assertGreater(run_mock.call_count, calls)

    def test_probe_single_platform_rejects_unknown_key(self):
        code, res = self.api("/api/capacity/probe?" + self.q({"platform": "bogus"}))
        self.assertEqual(code, 400)
        self.assertFalse(res.get("ok", True))

    def test_probe_rejects_unregistered_project(self):
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api("/api/capacity/probe?" + self.q({"project": td}))
            self.assertEqual(code, 403)
            self.assertFalse(res.get("ok", True))

    def test_default_model_persists_in_model_options(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "hub_proj"
            docs = proj / ".agentsflower" / "docs"
            docs.mkdir(parents=True)
            (docs / "model-options.json").write_text(
                json.dumps({"options": {"x": {"tool": "devin"}}}, indent=2),
                encoding="utf-8")
            studio.save_attached_project(str(proj))
            try:
                code, res = self.api(
                    "/api/capacity/default-model", method="POST",
                    body={"project": str(proj), "model": "swe-2-high", "tool": "devin"})
                self.assertEqual(code, 200, res)
                self.assertTrue(res.get("ok"), res)
                self.assertEqual(res["default_model"]["model"], "swe-2-high")

                cfg = json.loads((docs / "model-options.json").read_text(encoding="utf-8"))
                self.assertEqual(cfg["default_worker_model"]["model"], "swe-2-high")
                self.assertEqual(cfg["default_worker_model"]["tool"], "devin")
                self.assertIn("x", cfg["options"])

                with patch.object(studio.shutil, "which", return_value=None), \
                        patch.object(studio, "_fetch_ollama_json", return_value=None):
                    code, res2 = self.api(
                        "/api/capacity/probe?" + self.q({"project": str(proj)}))
                    self.assertEqual(code, 200, res2)
                    self.assertEqual(res2["default_model"]["model"], "swe-2-high")
            finally:
                try:
                    attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                    attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                    studio.ATTACHED_FILE.write_text(
                        json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                    )
                except Exception:
                    pass

    def test_default_model_rejects_bad_input(self):
        code, res = self.api(
            "/api/capacity/default-model", method="POST",
            body={"project": str(studio.REPO_ROOT), "model": "x; rm -rf /", "tool": "devin"})
        self.assertEqual(code, 400)
        self.assertFalse(res.get("ok", True))
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api(
                "/api/capacity/default-model", method="POST",
                body={"project": td, "model": "swe-2-high"})
            self.assertEqual(code, 403)
            self.assertFalse(res.get("ok", True))

    def test_capacity_hub_ui_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            'id="view-capacity"',
            'id="toolsCapacityGrid"',
            'id="defaultWorkerModelPill"',
            'id="localModelsInstalled"',
            'id="localModelsSuggested"',
            'id="btnCapacityRefresh"',
            "Free &amp; Local Offline Models",
        ):
            self.assertIn(marker, html)

        for marker in (
            "/api/capacity/probe",
            "/api/capacity/default-model",
            "status-badge",
            "setDefaultWorkerModel",
            "local_free",
            "capacity-card-header",
            "capacity-card-status-row",
            "platform-enable-toggle",
        ):
            self.assertIn(marker, js)

        for marker in (".status-badge", ".local-model-item", ".btn-set-default",
                       ".capacity-card-header", ".capacity-card-status-row",
                       "minmax(320px"):
            self.assertIn(marker, css)

    def test_chat_platform_selector_ui_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            'id="chatPlatformSelector"',
            'id="chatPlatformPill"',
            'id="chatPlatformDropdown"',
            'id="chatPlatformStatus"',
            'id="chatModelSelector"',
            'id="chatModelPill"',
            'id="chatModelDropdown"',
        ):
            self.assertIn(marker, html)

        for marker in (
            "CHAT_PLATFORMS",
            "probeChatPlatform",
            "selectChatPlatform",
            "platform=",
            "af_chat_platform",
            "af_chat_model",
            "platform-status-pill",
        ):
            self.assertIn(marker, js)

        for marker in (".platform-pill", ".platform-status-pill", ".model-empty"):
            self.assertIn(marker, css)


OPENROUTER_MODELS_PAYLOAD = {
    "data": [
        {"id": "openai/gpt-4o", "name": "OpenAI: GPT-4o", "context_length": 128000,
         "pricing": {"prompt": "0.0000025", "completion": "0.00001"}},
        {"id": "anthropic/claude-3.7-sonnet", "name": "Anthropic: Claude 3.7 Sonnet",
         "context_length": 200000, "pricing": {"prompt": "0.000003"}},
    ]
}


class TestProviderEngineAndProjectState(StudioApiCase):
    """T-167: provider engine (OpenRouter / OpenAI-compatible), masked secrets,
    per-project platform/model activation state."""

    def setUp(self):
        self._attached = (studio.ATTACHED_FILE.read_text(encoding="utf-8")
                          if studio.ATTACHED_FILE.is_file() else None)
        self._cache = dict(studio._capacity_probe_cache)
        self._pcache = dict(studio._platform_probe_cache)
        studio._capacity_probe_cache.update(at=0.0, data=None, scope=None)
        studio._platform_probe_cache.clear()

    def tearDown(self):
        if self._attached is None:
            studio.ATTACHED_FILE.unlink(missing_ok=True)
        else:
            studio.ATTACHED_FILE.write_text(self._attached, encoding="utf-8")
        studio._capacity_probe_cache.clear()
        studio._capacity_probe_cache.update(self._cache)
        studio._platform_probe_cache.clear()
        studio._platform_probe_cache.update(self._pcache)

    @staticmethod
    def _attach(td, name):
        proj = Path(td) / name
        (proj / ".agentsflower" / "state").mkdir(parents=True)
        studio.save_attached_project(str(proj))
        return proj

    def test_codex_models_come_from_live_cli(self):
        """`codex models` output is parsed dynamically, ahead of the configured catalog."""
        def fake_run(argv, timeout=None):
            exe = Path(str(argv[0])).name.lower()
            args = list(argv[1:])
            if exe.startswith("codex"):
                if args == ["--version"]:
                    return 0, "codex-cli 9.8.7"
                if args == ["login", "status"]:
                    return 0, "Logged in using ChatGPT"
                if args == ["models"]:
                    return 0, "gpt-live-1\ngpt-live-2  fast variant"
            return None, ""

        from unittest.mock import patch
        with patch.object(studio.shutil, "which",
                          side_effect=lambda n: f"/fake/{n}.exe" if n == "codex" else None), \
                patch.object(studio, "_probe_run", side_effect=fake_run), \
                patch.object(studio, "_fetch_ollama_json", return_value=None):
            code, res = self.api("/api/capacity/probe?" + self.q({"platform": "codex"}))
        self.assertEqual(code, 200, res)
        p = res["platform"]
        self.assertEqual(p["key"], "codex")
        self.assertTrue(p["authenticated"])
        self.assertEqual(p["version"], "codex-cli 9.8.7")
        self.assertEqual({m["id"] for m in p["models"]}, {"gpt-live-1", "gpt-live-2"})

    def test_mask_api_key(self):
        self.assertEqual(studio.mask_api_key("sk-or-v1-secret"), "sk-or-••••••••")
        self.assertEqual(studio.mask_api_key("abc"), "••••••••")
        self.assertEqual(studio.mask_api_key(""), "")

    def test_provider_add_openrouter_fetches_models_and_masks_key(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "prov_proj")
            seen = {}

            def fake_req(url, api_key, timeout=None):
                seen["url"], seen["key"] = url, api_key
                return OPENROUTER_MODELS_PAYLOAD

            from unittest.mock import patch
            with patch.object(studio, "_provider_request", side_effect=fake_req):
                code, res = self.api("/api/capacity/provider/add", method="POST", body={
                    "project": str(proj), "name": "OpenRouter",
                    "api_key": "sk-or-v1-testsecret123"})
            self.assertEqual(code, 200, res)
            self.assertTrue(res["ok"], res)
            self.assertEqual(seen["url"], studio.OPENROUTER_BASE_URL + "/models")
            self.assertEqual(seen["key"], "sk-or-v1-testsecret123")

            prov = res["provider"]
            self.assertEqual(prov["id"], "openrouter")
            self.assertEqual(prov["kind"], "openrouter")
            self.assertEqual(prov["api_key_masked"], "sk-or-••••••••")
            self.assertNotIn("testsecret123", json.dumps(res, ensure_ascii=False))
            ids = {m["id"] for m in prov["models"]}
            self.assertEqual(ids, {"openai/gpt-4o", "anthropic/claude-3.7-sonnet"})
            gpt = next(m for m in prov["models"] if m["id"] == "openai/gpt-4o")
            self.assertEqual(gpt["context"], "128,000 context")
            self.assertIn("/ 1M prompt", gpt["pricing"])

            # Raw credential lives only in the git-ignored secrets file.
            state_dir = proj / ".agentsflower" / "state"
            secrets = json.loads((state_dir / ".secrets.json").read_text(encoding="utf-8"))
            self.assertEqual(secrets["providers"]["openrouter"]["api_key"],
                             "sk-or-v1-testsecret123")
            state_text = (state_dir / "project-models.json").read_text(encoding="utf-8")
            self.assertNotIn("testsecret123", state_text)
            self.assertIn("openrouter",
                          json.loads(state_text)["providers"])
            gitignore = (proj / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".agentsflower/state/.secrets.json", gitignore)

    def test_provider_add_custom_base_url_and_verify_failure(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "prov_fail")
            from unittest.mock import patch
            with patch.object(studio, "_provider_request",
                              side_effect=urllib.error.URLError("refused")):
                code, res = self.api("/api/capacity/provider/add", method="POST", body={
                    "project": str(proj), "name": "Corp GW",
                    "kind": "openai-compatible",
                    "base_url": "https://gw.corp.example/v1",
                    "api_key": "corp-key-123456"})
            self.assertEqual(code, 502, res)
            self.assertFalse(res["ok"])
            self.assertFalse((proj / ".agentsflower" / "state" / ".secrets.json").exists())
            self.assertEqual(studio.load_project_state(proj)["providers"], {})

            code, res = self.api("/api/capacity/provider/add", method="POST", body={
                "project": str(proj), "name": "nokey"})
            self.assertEqual(code, 400)
            self.assertFalse(res["ok"])

    def test_provider_remove_purges_credentials(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "prov_rm")
            from unittest.mock import patch
            with patch.object(studio, "_provider_request",
                              return_value=OPENROUTER_MODELS_PAYLOAD):
                code, res = self.api("/api/capacity/provider/add", method="POST", body={
                    "project": str(proj), "name": "openrouter",
                    "api_key": "sk-or-v1-abcdefgh"})
                self.assertTrue(res["ok"], res)
                code, res = self.api("/api/capacity/provider/remove", method="POST", body={
                    "project": str(proj), "id": "openrouter"})
            self.assertEqual(code, 200, res)
            self.assertTrue(res["ok"], res)
            self.assertNotIn("openrouter", studio.load_project_secrets(proj)["providers"])
            self.assertNotIn("openrouter", studio.load_project_state(proj)["providers"])
            code, res = self.api("/api/capacity/provider/remove", method="POST", body={
                "project": str(proj), "id": "openrouter"})
            self.assertEqual(code, 404)

    def test_project_toggle_persists_and_scopes_to_project(self):
        with tempfile.TemporaryDirectory() as td:
            proj_a = self._attach(td, "proj_a")
            proj_b = self._attach(td, "proj_b")

            code, res = self.api("/api/capacity/project-toggle", method="POST", body={
                "project": str(proj_a), "platform": "devin", "enabled": False})
            self.assertEqual(code, 200, res)
            self.assertFalse(res["state"]["platforms"]["devin"]["enabled"])
            code, res = self.api("/api/capacity/project-toggle", method="POST", body={
                "project": str(proj_a), "platform": "devin",
                "model": "swe-2-high", "enabled": False})
            self.assertTrue(res["ok"], res)

            persisted = json.loads(
                (proj_a / ".agentsflower" / "state" / "project-models.json")
                .read_text(encoding="utf-8"))
            self.assertFalse(persisted["platforms"]["devin"]["enabled"])
            self.assertFalse(persisted["models"]["devin"]["swe-2-high"]["enabled"])

            code, res = self.api("/api/capacity/project-state?" + self.q({"project": str(proj_b)}))
            self.assertEqual(code, 200, res)
            self.assertEqual(res["state"]["platforms"], {})
            self.assertEqual(res["state"]["models"], {})

            from unittest.mock import patch
            patches = (patch.object(studio.shutil, "which",
                                    side_effect=TestCapacityHub._fake_which),
                       patch.object(studio, "_probe_run",
                                    side_effect=TestCapacityHub._fake_run),
                       patch.object(studio, "_fetch_ollama_json",
                                    side_effect=TestCapacityHub._fake_ollama))
            with patches[0], patches[1], patches[2]:
                code, res = self.api("/api/capacity/probe?" + self.q({"project": str(proj_a)}))
                self.assertEqual(code, 200, res)
                devin = next(p for p in res["platforms"] if p["key"] == "devin")
                self.assertFalse(devin["enabled"])
                # T-175: a deactivated platform is not probed - no CLI runs, no models
                self.assertEqual(devin["models"], [])
                self.assertIn("deactivated for this project", devin["note"])

                code, res_b = self.api("/api/capacity/probe?" + self.q({"project": str(proj_b)}))
                self.assertEqual(code, 200, res_b)
                devin_b = next(p for p in res_b["platforms"] if p["key"] == "devin")
                self.assertTrue(devin_b["enabled"])
                self.assertTrue(all(m["enabled"] for m in devin_b["models"]))

    def test_probe_skips_deactivated_platform_and_provider(self):
        """T-175: enabled:false platforms/providers are never probed - no CLI
        subprocess, no provider network call; the entry reports deactivated."""
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "skip_proj")
            studio.save_project_state(proj, {
                "platforms": {"devin": {"enabled": False},
                              "openrouter": {"enabled": False}},
                "models": {},
                "providers": {"openrouter": {
                    "id": "openrouter", "name": "OpenRouter",
                    "kind": "openrouter", "base_url": studio.OPENROUTER_BASE_URL,
                    "models": [{"id": "cached/m1"}]}},
            })
            from unittest.mock import patch
            with patch.object(studio.shutil, "which",
                              side_effect=TestCapacityHub._fake_which), \
                    patch.object(studio, "_probe_run",
                                 side_effect=TestCapacityHub._fake_run) as run_mock, \
                    patch.object(studio, "_fetch_ollama_json",
                                 side_effect=TestCapacityHub._fake_ollama), \
                    patch.object(studio, "_provider_request") as req_mock:
                code, res = self.api(
                    "/api/capacity/probe?" + self.q({"project": str(proj)}))
            self.assertEqual(code, 200, res)
            platforms = {p["key"]: p for p in res["platforms"]}
            devin = platforms["devin"]
            self.assertFalse(devin["enabled"])
            self.assertIn("deactivated for this project", devin["note"])
            prov = platforms["openrouter"]
            self.assertTrue(prov["provider"])
            self.assertFalse(prov["enabled"])
            self.assertIn("deactivated for this project", prov["note"])
            self.assertEqual([m["id"] for m in prov["models"]], ["cached/m1"])
            # enabled platforms still probed live
            self.assertEqual(platforms["codex"]["status"], "active")
            for c in run_mock.call_args_list:
                argv = c.args[0] if c.args else c[0][0]
                self.assertNotIn("devin", Path(str(argv[0])).name.lower())
            req_mock.assert_not_called()

    def test_probe_single_platform_respects_deactivation(self):
        """T-175: ?platform=<key> on a deactivated platform runs no CLI probe."""
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "skip_one")
            studio.save_project_state(proj, {
                "platforms": {"agy": {"enabled": False}},
                "models": {}, "providers": {}})
            from unittest.mock import patch
            with patch.object(studio.shutil, "which",
                              side_effect=TestCapacityHub._fake_which), \
                    patch.object(studio, "_probe_run",
                                 side_effect=TestCapacityHub._fake_run) as run_mock:
                code, res = self.api("/api/capacity/probe?" + self.q(
                    {"project": str(proj), "platform": "agy"}))
            self.assertEqual(code, 200, res)
            p = res["platform"]
            self.assertEqual(p["key"], "agy")
            self.assertFalse(p["enabled"])
            self.assertIn("deactivated for this project", p["note"])
            run_mock.assert_not_called()

    def test_probe_includes_provider_with_live_models(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "prov_probe")

            def fake_req(url, api_key, timeout=None):
                return OPENROUTER_MODELS_PAYLOAD

            from unittest.mock import patch
            with patch.object(studio, "_provider_request", side_effect=fake_req), \
                    patch.object(studio.shutil, "which", return_value=None), \
                    patch.object(studio, "_fetch_ollama_json", return_value=None):
                self.api("/api/capacity/provider/add", method="POST", body={
                    "project": str(proj), "name": "openrouter",
                    "api_key": "sk-or-v1-zxcvbnm1"})
                code, res = self.api("/api/capacity/probe?" + self.q({"project": str(proj)}))
            self.assertEqual(code, 200, res)
            keys = {p["key"] for p in res["platforms"]}
            self.assertIn("openrouter", keys)
            prov = next(p for p in res["platforms"] if p["key"] == "openrouter")
            self.assertTrue(prov["provider"])
            self.assertTrue(prov["enabled"])
            self.assertEqual(prov["api_key_masked"], "sk-or-••••••••")
            self.assertIn("openai/gpt-4o", {m["id"] for m in prov["models"]})
            self.assertNotIn("zxcvbnm1", json.dumps(res, ensure_ascii=False))
            self.assertIn("openrouter", res["project_state"]["providers"])

    def test_project_toggle_rejects_bad_input(self):
        code, res = self.api("/api/capacity/project-toggle", method="POST", body={
            "project": str(studio.REPO_ROOT), "platform": "x; rm -rf /"})
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api("/api/capacity/project-toggle", method="POST", body={
                "project": td, "platform": "devin"})
            self.assertEqual(code, 403)
            code, res = self.api("/api/capacity/provider/add", method="POST", body={
                "project": td, "name": "x", "api_key": "k" * 12})
            self.assertEqual(code, 403)

    def test_quota_hub_ui_markers(self):
        """T-169: the capacity view ships auto-scan, toggle and provider-modal hooks."""
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/index.html") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        # Connect Custom Provider button + modal (name, kind, base url, masked key).
        for marker in ("btnConnectProvider", "modalProviderBackdrop",
                       "inputProviderName", "inputProviderKind",
                       "inputProviderBaseUrl", "inputProviderKey"):
            self.assertIn(marker, html)
        self.assertIn('type="password" id="inputProviderKey"', html)
        self.assertIn("https://openrouter.ai/api/v1", html)

        # Auto-scan on tab open + skeleton while probing.
        self.assertIn("tabName === 'capacity'", js)
        self.assertIn("renderCapacitySkeleton", js)
        self.assertIn("capacity-skeleton", js)

        # Platform/model toggles -> project-toggle; provider add/remove endpoints.
        for marker in ("platform-enable-toggle", "model-enable-toggle",
                       "toggleCapacityItem", "/api/capacity/project-toggle",
                       "/api/capacity/provider/add", "/api/capacity/provider/remove",
                       "btn-remove-provider", "applyProjectStateToCapacity"):
            self.assertIn(marker, js)

        for marker in (".af-switch", ".sk-line", "capacityScanShimmer",
                       ".platform-disabled", ".model-disabled",
                       ".provider-modal-status", ".btn-remove-provider"):
            self.assertIn(marker, css)

    def test_repo_gitignore_covers_secrets_file(self):
        text = (studio.REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".agentsflower/state/.secrets.json", text)
        self.assertIn(".agentflow/state/.secrets.json", text)


class TestModelQuotaHubIntegration(StudioApiCase):
    """T-171: the per-project activation state constrains the chat composer,
    task inception (/api/task/synthesize) and pool registration, and the stale
    default worker model gets a warning pill plus a fallback offer."""

    def setUp(self):
        self._attached = (studio.ATTACHED_FILE.read_text(encoding="utf-8")
                          if studio.ATTACHED_FILE.is_file() else None)

    def tearDown(self):
        if self._attached is None:
            studio.ATTACHED_FILE.unlink(missing_ok=True)
        else:
            studio.ATTACHED_FILE.write_text(self._attached, encoding="utf-8")

    @staticmethod
    def _attach(td, name):
        proj = Path(td) / name
        (proj / ".agentsflower" / "state").mkdir(parents=True)
        studio.save_attached_project(str(proj))
        return proj

    @staticmethod
    def _write_default_model(proj, model, tool):
        docs = proj / ".agentsflower" / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "model-options.json").write_text(
            json.dumps({"options": {},
                        "default_worker_model": {"model": model, "tool": tool}},
                       indent=2),
            encoding="utf-8")

    def test_whitelist_helpers_honor_platform_and_model_flags(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "wl_proj")
            studio.save_project_state(proj, {
                "platforms": {"claude": {"enabled": False}},
                "models": {"devin": {"swe-2-high": {"enabled": False},
                                     "gpt-5-5-high": {"enabled": True}}},
                "providers": {}})
            state = studio.load_project_state(proj)
            self.assertFalse(
                studio.project_model_allowed(state, "claude", "claude-opus-4-6-thinking"))
            self.assertFalse(
                studio.project_model_allowed(state, "devin", "swe-2-high"))
            self.assertTrue(
                studio.project_model_allowed(state, "devin", "gpt-5-5-high"))
            # an unflagged model on an enabled platform inherits 'enabled'
            self.assertTrue(
                studio.project_model_allowed(state, "devin", "unflagged-model"))
            tool, model = studio.project_model_fallback(proj, "devin", "swe-2-high")
            self.assertEqual((tool, model), ("devin", "gpt-5-5-high"))

    def test_dynamic_toggle_updates_inception_model_pool(self):
        """Changing project settings immediately updates the models the
        task creator/synthesizer may assign."""
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "dyn_proj")
            self._write_default_model(proj, "qwen2.5-coder", "ollama")
            body = {
                "project": str(proj), "model": "swe-2-high",
                "messages": [{"role": "user",
                              "content": "1. Fix a minor css badge label in studio.css."}],
            }
            code, res = self.api("/api/task/synthesize", method="POST", body=body)
            self.assertEqual(code, 200, res)
            self.assertEqual(res["tasks"][0]["model"], "swe-2-high")
            self.assertFalse(res["tasks"][0].get("model_warning"))

            code, res = self.api("/api/capacity/project-toggle", method="POST", body={
                "project": str(proj), "platform": "devin",
                "model": "swe-2-high", "enabled": False})
            self.assertEqual(code, 200, res)
            self.assertFalse(res["state"]["models"]["devin"]["swe-2-high"]["enabled"])

            code, res = self.api("/api/task/synthesize", method="POST", body=body)
            self.assertEqual(code, 200, res)
            task = res["tasks"][0]
            self.assertNotEqual(task["model"], "swe-2-high")
            # the persisted project default is the nearest activated fallback
            self.assertEqual((task["tool"], task["model"]), ("ollama", "qwen2.5-coder"))
            self.assertIn("swe-2-high", task["model_warning"])
            self.assertIn("qwen2.5-coder", task["model_warning"])

            # Re-activating restores the requested selection.
            code, res = self.api("/api/capacity/project-toggle", method="POST", body={
                "project": str(proj), "platform": "devin",
                "model": "swe-2-high", "enabled": True})
            self.assertTrue(res["ok"], res)
            code, res = self.api("/api/task/synthesize", method="POST", body=body)
            self.assertEqual(res["tasks"][0]["model"], "swe-2-high")
            self.assertFalse(res["tasks"][0].get("model_warning"))

    def test_register_pool_writes_activated_fallback_model(self):
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "reg_proj")
            (proj / ".agentsflower" / "tasks").mkdir(parents=True)
            studio.save_project_state(proj, {
                "platforms": {},
                "models": {"devin": {"swe-2-high": {"enabled": False},
                                     "gpt-5-5-high": {"enabled": True}}},
                "providers": {}})
            code, res = self.api("/api/task/pool/register", method="POST", body={
                "project": str(proj),
                "tasks": [{
                    "title": "Scoped css fix",
                    "goal": "Fix a minor css badge label.",
                    "tool": "devin", "model": "swe-2-high", "effort": "medium",
                    "allowed_files": [".agentsflower/studio/studio.css"],
                    "criteria": ["C-01: fix applied"],
                }],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res["ok"], res)
            task = res["tasks"][0]
            self.assertEqual(task["model"], "gpt-5-5-high")
            self.assertTrue(task["model_warning"])
            text = (proj / task["file"]).read_text(encoding="utf-8")
            self.assertIn("Model: gpt-5-5-high", text)
            self.assertNotIn("Model: swe-2-high", text)
            plan = json.loads((proj / task["plan_file"]).read_text(encoding="utf-8"))
            self.assertEqual(plan["model"], "gpt-5-5-high")
            self.assertTrue(plan["model_warning"])

    def test_deactivated_platform_keeps_request_with_warning(self):
        """A project-deactivated platform yields no activated fallback: the
        guard reports a warning instead of silently resurrecting the model."""
        with tempfile.TemporaryDirectory() as td:
            proj = self._attach(td, "off_proj")
            studio.save_project_state(proj, {
                "platforms": {"devin": {"enabled": False}},
                "models": {}, "providers": {}})
            tool, model, warning = studio.enforce_project_model_whitelist(
                proj, "devin", "swe-2-high")
            self.assertTrue(warning)
            self.assertIn("deactivated", warning)
            self.assertIn("no activated fallback", warning)

    def test_chat_composer_filter_and_default_warning_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        # Composer model list honors per-project activation flags only.
        self.assertIn("p.enabled === false", js)
        self.assertIn("m.enabled !== false", js)
        self.assertIn("deactivated for this project", js)
        # Stale default worker model -> warning pill + nearest activated fallback.
        for marker in ("defaultModelIssue", "nearestActivatedModel",
                       "status-badge", "limited"):
            self.assertIn(marker, js)


class TestStudioChatEngine(StudioApiCase):
    """Tests for T-153: Live CLI Chat Execution Engine (POST /api/chat)."""

    def test_chat_dispatches_to_cli_platforms(self):
        from unittest.mock import patch

        calls = []

        def fake_which(name):
            return f"/fake/bin/{name}"

        def fake_chat_run(argv, cwd=None, timeout=studio.CHAT_EXEC_TIMEOUT):
            calls.append((list(argv), cwd, timeout))
            exe = Path(str(argv[0])).name.lower()
            if exe == "agy":
                stream = "\n".join([
                    json.dumps({"type": "init", "model": "claude-opus-4-6-thinking"}),
                    json.dumps({"type": "assistant", "content": "Antigravity stream reply"}),
                    json.dumps({"type": "result", "usage": {"input_tokens": 12, "output_tokens": 8}}),
                ])
                return 0, stream, False
            return 0, f"Reply from {exe}", False

        with patch.object(studio.shutil, "which", side_effect=fake_which), \
                patch.object(studio, "_chat_run", side_effect=fake_chat_run):
            # 1. devin
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "model": "swe-2-high",
                "thread": "research",
                "messages": [{"role": "user", "content": "Explain studio architecture"}],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertEqual(res.get("reply"), "Reply from devin")
            self.assertEqual(res.get("model"), "swe-2-high")
            self.assertIsInstance(res.get("usage"), dict)
            devin_argv, _, devin_timeout = calls[-1]
            self.assertEqual(Path(devin_argv[0]).name, "devin")
            self.assertIn("-p", devin_argv)
            self.assertEqual(devin_timeout, 30)

            # 2. claude
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "claude",
                "model": "claude-sonnet-4",
                "thread": "research",
                "messages": [{"role": "user", "content": "Check gate rules"}],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertEqual(res.get("reply"), "Reply from claude")
            claude_argv, _, _ = calls[-1]
            self.assertEqual(Path(claude_argv[0]).name, "claude")
            self.assertIn("-p", claude_argv)

            # 3. codex
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "codex",
                "model": "gpt-6.1-sol",
                "thread": "research",
                "messages": [{"role": "user", "content": "Review ledger transitions"}],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertEqual(res.get("reply"), "Reply from codex")
            codex_argv, _, _ = calls[-1]
            self.assertEqual(Path(codex_argv[0]).name, "codex")
            self.assertEqual(codex_argv[1], "exec")

            # 4. agy (stream-json)
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "agy",
                "model": "claude-opus-4-6-thinking",
                "thread": "research",
                "messages": [{"role": "user", "content": "Analyze blast radius"}],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertEqual(res.get("reply"), "Antigravity stream reply")
            self.assertEqual(res["usage"].get("input_tokens"), 12)
            agy_argv, _, _ = calls[-1]
            self.assertEqual(Path(agy_argv[0]).name, "agy")
            self.assertIn("-p", agy_argv)
            self.assertIn("--output-format", agy_argv)
            self.assertIn("stream-json", agy_argv)

    def test_chat_dispatches_to_ollama_local_adapter(self):
        from unittest.mock import patch

        captured = {}

        def fake_chat_completion(model_info, messages, temperature=0.2, timeout=30.0):
            captured["model_info"] = model_info
            captured["messages"] = messages
            captured["timeout"] = timeout
            return {
                "ok": True,
                "content": "Local Qwen response",
                "raw": {"prompt_eval_count": 24, "eval_count": 10},
            }

        with patch.object(studio.local_adapter, "chat_completion", side_effect=fake_chat_completion):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "ollama",
                "model": "qwen2.5-coder:7b",
                "thread": "research",
                "messages": [
                    {"role": "user", "content": "First question"},
                    {"role": "assistant", "content": "First answer"},
                    {"role": "user", "content": "Follow-up question"},
                ],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertEqual(res.get("reply"), "Local Qwen response")
            self.assertEqual(res.get("model"), "qwen2.5-coder:7b")
            self.assertEqual(captured["model_info"]["id"], "qwen2.5-coder:7b")
            self.assertEqual(captured["timeout"], 30)
            roles = [m["role"] for m in captured["messages"]]
            self.assertIn("user", roles)
            self.assertIn("assistant", roles)

    def test_chat_packages_thread_context_and_history_into_prompt(self):
        from unittest.mock import patch

        prompts = []

        def fake_chat_run(argv, cwd=None, timeout=30):
            prompts.append(argv)
            return 0, "Contextual reply", False

        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", side_effect=fake_chat_run):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "model": "swe-2-high",
                "thread": "T-153",
                "messages": [
                    {"role": "user", "content": "Earlier user turn about studio.py"},
                    {"role": "assistant", "content": "Earlier assistant analysis"},
                    {"role": "user", "content": "Now explain timeout handling"},
                ],
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            argv = prompts[-1]
            joined = " ".join(argv)
            self.assertIn("T-153", joined)
            self.assertIn("Earlier user turn about studio.py", joined)
            self.assertIn("Earlier assistant analysis", joined)
            self.assertIn("Now explain timeout handling", joined)

    def test_chat_subprocess_timeout_terminates_process(self):
        from unittest.mock import MagicMock, patch

        fake_proc = MagicMock()
        fake_proc.pid = 42424
        fake_proc.communicate.side_effect = subprocess.TimeoutExpired(cmd=["devin"], timeout=30)

        with patch.object(studio.subprocess, "Popen", return_value=fake_proc), \
                patch.object(studio, "_kill_probe_tree") as kill_tree_mock:
            rc, out, timed_out = studio._chat_run(["/fake/bin/devin", "-p", "hi"], timeout=30)
            self.assertIsNone(rc)
            self.assertTrue(timed_out)
            self.assertIn("timed out", out.lower())
            kill_tree_mock.assert_called_once_with(42424)
            fake_proc.kill.assert_called_once()

        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", return_value=(None, "CLI execution timed out after 30s", True)):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "model": "swe-2-high",
                "thread": "research",
                "messages": [{"role": "user", "content": "long query"}],
            })
            self.assertEqual(code, 504, res)
            self.assertFalse(res.get("ok", True))
            self.assertTrue(res.get("timed_out"))
            self.assertIn("timed out", res.get("error", "").lower())

    def test_chat_error_handling_and_validation(self):
        from unittest.mock import patch

        # Unregistered project -> 403
        with tempfile.TemporaryDirectory() as td:
            code, res = self.api("/api/chat", method="POST", body={
                "project": td,
                "tool": "devin",
                "messages": [{"role": "user", "content": "hi"}],
            })
            self.assertEqual(code, 403)
            self.assertFalse(res.get("ok", True))

        # Unsupported tool -> 400
        code, res = self.api("/api/chat", method="POST", body={
            "project": str(studio.REPO_ROOT),
            "tool": "unknown_cli",
            "messages": [{"role": "user", "content": "hi"}],
        })
        self.assertEqual(code, 400)
        self.assertFalse(res.get("ok", True))

        # Empty messages -> 400
        code, res = self.api("/api/chat", method="POST", body={
            "project": str(studio.REPO_ROOT),
            "tool": "devin",
            "messages": [],
        })
        self.assertEqual(code, 400)
        self.assertFalse(res.get("ok", True))

        # Missing CLI binary -> 400
        with patch.object(studio.shutil, "which", return_value=None):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "claude",
                "messages": [{"role": "user", "content": "hi"}],
            })
            self.assertEqual(code, 400)
            self.assertFalse(res.get("ok", True))
            self.assertIn("not found", res.get("error", "").lower())

        # Non-zero CLI exit -> 502
        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", return_value=(1, "Authentication failed", False)):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "messages": [{"role": "user", "content": "hi"}],
            })
            self.assertEqual(code, 502)
            self.assertFalse(res.get("ok", True))
            self.assertIn("Authentication failed", res.get("error", ""))

    def test_chat_ui_live_execution_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            "/api/chat",
            "CHAT_TIMEOUT_MS",
            "30000",
            "AbortController",
            "thinking-dots",
            "state.chatPlatform",
        ):
            self.assertIn(marker, js)

        for marker in (".thinking-dots", ".chat-bubble.assistant.thinking", ".chat-bubble.assistant.error"):
            self.assertIn(marker, css)


class TestStructuredThreadSwitcher(StudioApiCase):
    """T-175: two-section thread switcher - Researches (folders) above
    stage-grouped Implementations, under one instant search bar."""

    def shell_assets(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")
        return html, js, css

    def test_header_shell_has_thread_switcher_not_select(self):
        html, _, _ = self.shell_assets()
        for marker in (
            'id="threadSelector"',
            'id="threadPill"',
            'id="threadDropdown"',
            'role="menu"',
            "Research &amp; Inception",
        ):
            self.assertIn(marker, html)
        self.assertNotIn('id="inspectorTaskSelect"', html)
        self.assertNotIn('class="chat-task-select"', html)

    def test_dropdown_builds_two_sections_with_search(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "thread-search",
            "threadSearchInput",
            "thread-list",
            "fillThreadList",
            "data-search",
            "state.threadFilter",
            "Research & Inception",
            "(General Chat)",
            "thread-section-header",
            "researches-header",
            "implementations-header",
            "🔍 Researches",
            "⚙️ Implementations",
            "buildThreadSection",
            "data-collapse-key",
            "toggleThreadCollapse",
            "threadCollapsed",
            "buildCollapsibleHeader",
            "threadSearchText",
        ):
            self.assertIn(marker, js)
        self.assertNotIn("chat-task-select", js)

    def test_research_section_supports_folders(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "📁 + Folder",
            "addResearchFolder",
            "researchFolders",
            "buildFolderGroup",
            "thread-folder-group",
            "thread-folder-header",
            "researchFolderName",
        ):
            self.assertIn(marker, js)

    def test_implementations_group_tasks_by_stage(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "groupTasksByStage",
            "buildStageGroup",
            "thread-stage-group",
            "thread-stage-header",
            "stageLabel",
        ):
            self.assertIn(marker, js)

    def test_task_items_show_id_title_and_status(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "thread-item-id",
            "thread-item-title",
            "thread-item-status",
            "threadStatusClass",
            "data-thread",
            "' — '",
        ):
            self.assertIn(marker, js)

    def test_project_switch_resets_research_state(self):
        """C-04: switching projects clears research state and reloads it scoped."""
        _, js, _ = self.shell_assets()
        for marker in (
            "state.threads = { research: [] }",
            "state.researchMeta = {}",
            "loadResearchThreads(path)",
            "/api/research/update?project=",
            "/api/research/create?project=",
            "/api/research/list",
        ):
            self.assertIn(marker, js)

    def test_thread_items_selection_and_click_handlers(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "thread-item",
            "data-thread",
            "state.inspectorTaskId",
            "selectThread",
            "addResearchThread",
            "closeThreadDropdown",
            "renderInspector()",
            "' — '",
        ):
            self.assertIn(marker, js)

    def test_keyboard_navigation_and_dismiss(self):
        _, js, _ = self.shell_assets()
        for marker in (
            "keydown",
            "ArrowDown",
            "ArrowUp",
            "Enter",
            "Escape",
            "threadFocusables",
        ):
            self.assertIn(marker, js)

    def test_css_two_section_styles(self):
        _, _, css = self.shell_assets()
        for marker in (
            ".thread-selector-wrap",
            ".thread-pill",
            ".thread-dropdown",
            ".thread-search",
            ".thread-list",
            ".thread-item",
            ".thread-item.active",
            ".thread-item-status",
            ".thread-section",
            ".thread-section-header",
            ".researches-header",
            ".implementations-header",
            ".thread-stage-group",
            ".thread-stage-header",
            ".thread-folder-group",
            ".thread-folder-header",
            ".thread-count",
            ".collapsed",
            "backdrop-filter",
            "#134e9e",
            "transition",
        ):
            self.assertIn(marker, css)
        self.assertNotIn(".chat-task-select", css)


class TestResearchThreads(StudioApiCase):
    """Tests for T-157: multi-research threads, folders, persistence, context forking."""

    def _temp_store(self):
        """Redirect the research store to a temp dir so tests never touch real project state."""
        from unittest.mock import patch

        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        store = Path(td.name) / "state" / "research"
        patcher = patch.object(studio, "research_store_dir", return_value=store)
        patcher.start()
        self.addCleanup(patcher.stop)
        return store

    def _chat(self, thread, messages, **extra):
        from unittest.mock import patch

        body = {
            "project": str(studio.REPO_ROOT),
            "tool": "devin",
            "model": "swe-2-high",
            "thread": thread,
            "messages": messages,
        }
        body.update(extra)
        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", return_value=(0, "Research reply", False)):
            return self.api("/api/chat", method="POST", body=body)

    def test_create_autonames_and_persists_threads(self):
        store = self._temp_store()
        code, res = self.api("/api/research/create", method="POST",
                             body={"project": str(studio.REPO_ROOT)})
        self.assertEqual(code, 200, res)
        self.assertTrue(res.get("ok"), res)
        t1 = res["thread"]
        self.assertEqual(t1["id"], "research-001")
        self.assertEqual(t1["name"], "Task Research - 001")
        self.assertTrue((store / "research-001.json").is_file())

        code, res = self.api("/api/research/create", method="POST",
                             body={"project": str(studio.REPO_ROOT)})
        self.assertEqual(res["thread"]["id"], "research-002")
        self.assertEqual(res["thread"]["name"], "Task Research - 002")

        code, res = self.api("/api/research/list?" + self.q({"project": str(studio.REPO_ROOT)}))
        self.assertEqual(code, 200, res)
        ids = [t["id"] for t in res["threads"]]
        self.assertEqual(ids, ["research-001", "research-002"])

    def test_rename_and_folder_grouping(self):
        store = self._temp_store()
        for _ in range(2):
            self.api("/api/research/create", method="POST", body={"project": str(studio.REPO_ROOT)})

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-001",
            "name": "Alpha spike", "folder": "Architecture",
        })
        self.assertEqual(code, 200, res)
        self.assertEqual(res["thread"]["name"], "Alpha spike")
        self.assertEqual(res["thread"]["folder"], "Architecture")

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-002", "folder": "UI Design",
        })
        self.assertEqual(res["thread"]["folder"], "UI Design")

        code, res = self.api("/api/research/thread?" + self.q({
            "project": str(studio.REPO_ROOT), "id": "research-001"}))
        self.assertEqual(res["thread"]["name"], "Alpha spike")
        self.assertEqual(res["thread"]["folder"], "Architecture")

        code, res = self.api("/api/research/list?" + self.q({"project": str(studio.REPO_ROOT)}))
        folders = {t["id"]: t["folder"] for t in res["threads"]}
        self.assertEqual(folders["research-001"], "Architecture")
        self.assertEqual(folders["research-002"], "UI Design")

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-001", "folder": "",
        })
        self.assertEqual(res["thread"]["folder"], "")
        rec = json.loads((store / "research-001.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["folder"], "")

    def test_update_rejects_bad_input(self):
        self._temp_store()
        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT),
        })
        self.assertEqual(code, 400)

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-099", "name": "x",
        })
        self.assertEqual(code, 200, res)
        self.assertEqual(res["thread"]["id"], "research-099")
        self.assertEqual(res["thread"]["name"], "x")

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "../outside", "name": "x",
        })
        self.assertEqual(code, 400)

        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-099", "refs": "not-a-list",
        })
        self.assertEqual(code, 400)

        self.api("/api/research/create", method="POST", body={"project": str(studio.REPO_ROOT)})
        code, res = self.api("/api/research/update", method="POST", body={
            "project": str(studio.REPO_ROOT), "id": "research-001", "name": "   ",
        })
        self.assertEqual(code, 400)

        with tempfile.TemporaryDirectory() as td:
            code, res = self.api("/api/research/create", method="POST", body={"project": td})
            self.assertEqual(code, 403)

    def test_chat_persists_thread_history(self):
        store = self._temp_store()
        self.api("/api/research/create", method="POST", body={"project": str(studio.REPO_ROOT)})

        code, res = self._chat("research-001", [{"role": "user", "content": "First question"}])
        self.assertEqual(code, 200, res)
        rec = json.loads((store / "research-001.json").read_text(encoding="utf-8"))
        roles = [m["role"] for m in rec["messages"]]
        self.assertEqual(roles, ["user", "assistant"])
        self.assertEqual(rec["messages"][0]["content"], "First question")
        self.assertEqual(rec["messages"][1]["content"], "Research reply")

        code, res = self._chat("research-001", [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "Research reply"},
            {"role": "user", "content": "Second question"},
        ])
        self.assertEqual(code, 200, res)
        rec = json.loads((store / "research-001.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rec["messages"]), 4)
        self.assertEqual(rec["messages"][2]["content"], "Second question")

    def test_chat_persist_is_opt_in_for_new_threads(self):
        store = self._temp_store()
        code, res = self._chat("research-007", [{"role": "user", "content": "hi"}])
        self.assertEqual(code, 200, res)
        self.assertFalse((store / "research-007.json").exists())

        code, res = self._chat("research-007", [{"role": "user", "content": "hi"}], persist=True)
        self.assertEqual(code, 200, res)
        rec = json.loads((store / "research-007.json").read_text(encoding="utf-8"))
        self.assertEqual(rec["id"], "research-007")
        self.assertEqual(rec["name"], "Task Research - 007")

        code, res = self._chat("research", [{"role": "user", "content": "hi"}])
        self.assertEqual(code, 200, res)
        self.assertFalse((store / "research.json").exists())

    def test_refs_and_inline_tokens_inject_context_summary(self):
        self._temp_store()
        code, res = self._chat("research-001", [{"role": "user", "content": "Chose Postgres for storage"}],
                               persist=True)
        self.assertEqual(code, 200, res)

        prompts = []

        def fake_chat_run(argv, cwd=None, timeout=30):
            prompts.append(" ".join(argv))
            return 0, "ok", False

        from unittest.mock import patch
        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", side_effect=fake_chat_run):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "thread": "research-002",
                "persist": True,
                "refs": ["research-001", "T-013"],
                "messages": [{"role": "user", "content": "Compare approaches"}],
            })
        self.assertEqual(code, 200, res)
        prompt = prompts[-1]
        self.assertIn("Referenced context", prompt)
        self.assertIn("research-001", prompt)
        self.assertIn("Postgres", prompt)
        self.assertIn("T-013", prompt)

        prompts.clear()
        with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                patch.object(studio, "_chat_run", side_effect=fake_chat_run):
            code, res = self.api("/api/chat", method="POST", body={
                "project": str(studio.REPO_ROOT),
                "tool": "devin",
                "thread": "research-002",
                "messages": [{"role": "user", "content": "Now fork from Research-001, Ref: T-013"}],
            })
        self.assertEqual(code, 200, res)
        prompt = prompts[-1]
        self.assertIn("Referenced context", prompt)
        self.assertIn("research-001", prompt)
        self.assertIn("T-013", prompt)

    def test_create_with_fork_from_links_parent(self):
        self._temp_store()
        self.api("/api/research/create", method="POST", body={"project": str(studio.REPO_ROOT)})
        code, res = self.api("/api/research/create", method="POST", body={
            "project": str(studio.REPO_ROOT),
            "fork_from": "Research-001",
            "folder": "Architecture",
        })
        self.assertEqual(code, 200, res)
        t = res["thread"]
        self.assertEqual(t["id"], "research-002")
        self.assertEqual(t["parent"], "research-001")
        self.assertIn("research-001", t["refs"])
        self.assertEqual(t["folder"], "Architecture")

    def test_research_threads_scoped_per_project(self):
        """T-175: research records resolve strictly under each target project's
        own state/research/ store; project B never sees project A threads."""
        attached = (studio.ATTACHED_FILE.read_text(encoding="utf-8")
                    if studio.ATTACHED_FILE.is_file() else None)
        try:
            with tempfile.TemporaryDirectory() as td:
                proj_a = Path(td) / "proj_a"
                proj_b = Path(td) / "proj_b"
                for p in (proj_a, proj_b):
                    (p / ".agentsflower" / "state").mkdir(parents=True)
                    studio.save_attached_project(str(p))
                code, res = self.api("/api/research/create", method="POST",
                                     body={"project": str(proj_a)})
                self.assertEqual(code, 200, res)
                self.assertEqual(res["thread"]["id"], "research-001")
                store_a = proj_a / ".agentsflower" / "state" / "research"
                store_b = proj_b / ".agentsflower" / "state" / "research"
                self.assertTrue((store_a / "research-001.json").is_file())
                self.assertFalse((store_b / "research-001.json").exists())
                code, res = self.api(
                    "/api/research/list?" + self.q({"project": str(proj_a)}))
                self.assertEqual([t["id"] for t in res["threads"]], ["research-001"])
                code, res = self.api(
                    "/api/research/list?" + self.q({"project": str(proj_b)}))
                self.assertEqual(res["threads"], [])
                code, res = self.api("/api/research/update", method="POST", body={
                    "project": str(proj_b), "id": "research-001", "name": "B-only"})
                self.assertEqual(code, 200, res)
                self.assertTrue((store_b / "research-001.json").is_file())
                rec_a = json.loads((store_a / "research-001.json")
                                   .read_text(encoding="utf-8"))
                self.assertNotEqual(rec_a["name"], "B-only")
        finally:
            if attached is None:
                studio.ATTACHED_FILE.unlink(missing_ok=True)
            else:
                studio.ATTACHED_FILE.write_text(attached, encoding="utf-8")

    def test_multi_research_ui_markers(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")
        for marker in (
            "/api/research/create",
            "/api/research/update",
            "/api/research/list",
            "Task Research - ",
            "thread-rename-input",
            "startRenameThread",
            "extractRefsFromText",
            "researchMeta",
            "ref-chip",
            "researchForkSelect",
            "persist: isResearch",
        ):
            self.assertIn(marker, js)
        for marker in (
            ".thread-rename-input",
            ".ref-chip",
            ".research-ctl-select",
        ):
            self.assertIn(marker, css)


class TestTaskChatAndStageCollisionGuard(StudioApiCase):
    """Tests for T-161: Implementations manual-creation guard, task-level chat context, and DAG stage move collision checker."""

    def _make_stage_project(self, td: str) -> tuple[Path, Path]:
        proj = Path(td) / "stage_dag_proj"
        flow = proj / ".agentsflower"
        (flow / "state").mkdir(parents=True)
        (flow / "tasks").mkdir(parents=True)
        studio.save_attached_project(str(proj))
        self.addCleanup(lambda: self._detach_project(proj))
        return proj, flow

    def _detach_project(self, proj: Path):
        try:
            if studio.ATTACHED_FILE.is_file():
                attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                studio.ATTACHED_FILE.write_text(
                    json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                )
        except Exception:
            pass

    def test_implementations_manual_creation_disabled_in_ui_and_api(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        # The "+" affordance in the flat switcher only creates research threads;
        # implementation tasks can only come from synthesis, never manual add.
        for marker in (
            "thread-add",
            "addResearchThread",
            "/api/task/move-stage",
            "moveTaskStage",
            "taskWorktreeStatus",
        ):
            self.assertIn(marker, js)
        self.assertNotIn("data-manual-create", js)

        code, res = self.api("/api/task/create", method="POST", body={
            "project": str(studio.REPO_ROOT),
            "id": "T-999",
            "title": "Manual unauthorized task",
            "stage": "7",
        })
        self.assertEqual(code, 403, res)
        self.assertFalse(res.get("ok", True))
        self.assertIn("synthesis", res.get("error", "").lower())

    def test_task_level_chat_loads_contract_criteria_and_worktree_status(self):
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_stage_project(td)
            pool = [
                {
                    "id": "T-001",
                    "title": "Implement core stage parser",
                    "stage": 1,
                    "role": "developer",
                    "tool": "devin",
                    "model": "swe-2-high",
                    "effort": "high",
                    "goal": "Parse DAG stage dependencies and validate stage transitions.",
                    "allowed_files": [".agentsflower/tools/studio.py"],
                    "criteria": [
                        "C-01: DAG dependencies parsed from ledger and task files.",
                        "C-02: Stage transitions validated before mutation.",
                    ],
                }
            ]
            code, reg = self.api("/api/task/pool/register", method="POST", body={
                "project": str(proj),
                "tasks": pool,
            })
            self.assertEqual(code, 200, reg)

            code, ctx = self.api("/api/task/context?" + self.q({"project": str(proj), "id": "T-001"}))
            self.assertEqual(code, 200, ctx)
            self.assertTrue(ctx.get("ok"), ctx)
            self.assertEqual(ctx["task"]["id"], "T-001")
            self.assertEqual(ctx["task"]["stage"], "1")
            self.assertIn(".agentsflower/tools/studio.py", ctx["task"]["allowed_files"])
            self.assertEqual(len(ctx["task"]["criteria"]), 2)
            self.assertIn("worktree_status", ctx)
            self.assertIn("status", ctx["worktree_status"])
            self.assertIn("exists", ctx["worktree_status"])

            prompts = []

            def fake_chat_run(argv, cwd=None, timeout=30):
                prompts.append(" ".join(argv))
                return 0, "Scope adjustment noted for T-001", False

            with patch.object(studio.shutil, "which", return_value="/fake/bin/devin"), \
                    patch.object(studio, "_chat_run", side_effect=fake_chat_run):
                code, chat_res = self.api("/api/chat", method="POST", body={
                    "project": str(proj),
                    "tool": "devin",
                    "model": "swe-2-high",
                    "thread": "T-001",
                    "messages": [
                        {"role": "user", "content": "Clarify C-02 scope for T-001 stage transitions"}
                    ],
                })
            self.assertEqual(code, 200, chat_res)
            self.assertTrue(chat_res.get("ok"), chat_res)
            self.assertEqual(chat_res.get("thread"), "T-001")
            prompt = prompts[-1]
            self.assertIn("T-001", prompt)
            self.assertIn("Parse DAG stage dependencies", prompt)
            self.assertIn("C-01:", prompt)
            self.assertIn("C-02:", prompt)
            self.assertIn("Worktree", prompt)

    def test_move_stage_blocks_dependency_inversion_and_same_stage_collision(self):
        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_stage_project(td)
            pool = [
                {
                    "id": "T-002",
                    "title": "Base schema task",
                    "stage": 1,
                    "depends": "none",
                    "goal": "Create base schema.",
                    "allowed_files": ["schema.py"],
                    "criteria": ["C-01: Schema created."],
                },
                {
                    "id": "T-014",
                    "title": "Dependent migration task",
                    "stage": 2,
                    "depends": "T-002",
                    "goal": "Run migration after T-002.",
                    "allowed_files": ["migrate.py"],
                    "criteria": ["C-01: Migration complete."],
                },
                {
                    "id": "T-020",
                    "title": "Downstream verification task",
                    "stage": 3,
                    "depends": "T-014",
                    "goal": "Verify migration output.",
                    "allowed_files": ["test_migrate.py"],
                    "criteria": ["C-01: Verification pass."],
                },
            ]
            code, reg = self.api("/api/task/pool/register", method="POST", body={
                "project": str(proj),
                "tasks": pool,
            })
            self.assertEqual(code, 200, reg)

            # 1. Moving T-014 (depends on T-002 in Stage 01) into Stage 01 -> blocked
            code, res = self.api("/api/task/move-stage", method="POST", body={
                "project": str(proj),
                "id": "T-014",
                "stage": 1,
            })
            self.assertEqual(code, 400, res)
            self.assertFalse(res.get("ok", True))
            self.assertTrue(res.get("collision"), res)
            self.assertIn(
                "Cannot move T-014 to Stage 01: depends on T-002 in Stage 01",
                res.get("error", ""),
            )

            # 2. Moving T-020 (depends on T-014 in Stage 02) into Stage 01 -> blocked (inversion)
            code, res2 = self.api("/api/task/move-stage", method="POST", body={
                "project": str(proj),
                "id": "T-020",
                "stage": 1,
            })
            self.assertEqual(code, 400, res2)
            self.assertFalse(res2.get("ok", True))
            self.assertIn(
                "Cannot move T-020 to Stage 01: depends on T-014 in Stage 02",
                res2.get("error", ""),
            )

            # 3. Moving T-002 (required by T-014 in Stage 02) into Stage 02 or Stage 03 -> blocked
            code, res3 = self.api("/api/task/move-stage", method="POST", body={
                "project": str(proj),
                "id": "T-002",
                "stage": 3,
            })
            self.assertEqual(code, 400, res3)
            self.assertFalse(res3.get("ok", True))
            self.assertTrue(res3.get("collision"), res3)
            self.assertIn("Cannot move T-002 to Stage 03", res3.get("error", ""))
            self.assertIn("T-014", res3.get("error", ""))

            # Confirm ledger and Task Files were NOT mutated by rejected moves
            t014_file = next((flow / "tasks").glob("T-014-*.md"))
            self.assertIn("Stage: 2", t014_file.read_text(encoding="utf-8"))
            tasks_after = studio.get_tasks_data(str(proj))["tasks"]
            stages_map = {t["id"]: t["stage"] for t in tasks_after}
            self.assertEqual(stages_map, {"T-002": "1", "T-014": "2", "T-020": "3"})

    def test_move_stage_detects_cyclic_dependencies_in_dag(self):
        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_stage_project(td)
            pool = [
                {
                    "id": "T-010",
                    "title": "Alpha node",
                    "stage": 1,
                    "depends": "T-012",
                    "goal": "Alpha.",
                    "allowed_files": ["a.py"],
                    "criteria": ["C-01: Alpha."],
                },
                {
                    "id": "T-011",
                    "title": "Beta node",
                    "stage": 2,
                    "depends": "T-010",
                    "goal": "Beta.",
                    "allowed_files": ["b.py"],
                    "criteria": ["C-01: Beta."],
                },
                {
                    "id": "T-012",
                    "title": "Gamma node",
                    "stage": 3,
                    "depends": "T-011",
                    "goal": "Gamma.",
                    "allowed_files": ["c.py"],
                    "criteria": ["C-01: Gamma."],
                },
            ]
            self.api("/api/task/pool/register", method="POST", body={
                "project": str(proj),
                "tasks": pool,
            })

            code, res = self.api("/api/task/move-stage", method="POST", body={
                "project": str(proj),
                "id": "T-010",
                "stage": 4,
            })
            self.assertEqual(code, 400, res)
            self.assertFalse(res.get("ok", True))
            self.assertTrue(res.get("collision"), res)
            self.assertEqual(res.get("collision_type"), "cycle")
            self.assertIn("cyclic dependency", res.get("error", "").lower())
            self.assertTrue(res.get("cycle"), res)

    def test_valid_stage_move_atomically_updates_ledger_and_task_file(self):
        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_stage_project(td)
            pool = [
                {
                    "id": "T-002",
                    "title": "Base schema task",
                    "stage": 1,
                    "depends": "none",
                    "goal": "Create base schema.",
                    "allowed_files": ["schema.py"],
                    "criteria": ["C-01: Schema created."],
                },
                {
                    "id": "T-014",
                    "title": "Dependent migration task",
                    "stage": 2,
                    "depends": "T-002",
                    "goal": "Run migration after T-002.",
                    "allowed_files": ["migrate.py"],
                    "criteria": ["C-01: Migration complete."],
                },
                {
                    "id": "T-020",
                    "title": "Downstream verification task",
                    "stage": 4,
                    "depends": "T-014",
                    "goal": "Verify migration output.",
                    "allowed_files": ["test_migrate.py"],
                    "criteria": ["C-01: Verification pass."],
                },
            ]
            self.api("/api/task/pool/register", method="POST", body={
                "project": str(proj),
                "tasks": pool,
            })

            # Moving T-014 from Stage 2 to Stage 3 is valid (Stage 1 < Stage 3 < Stage 4)
            code, res = self.api("/api/task/move-stage", method="POST", body={
                "project": str(proj),
                "id": "T-014",
                "stage": 3,
            })
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)
            self.assertFalse(res.get("collision", True))
            self.assertEqual(res.get("task_id"), "T-014")
            self.assertEqual(res.get("from_stage"), 2)
            self.assertEqual(res.get("to_stage"), 3)
            self.assertEqual(res.get("stage_label"), "Stage 03")

            # Verify Task File updated atomically
            t014_file = next((flow / "tasks").glob("T-014-*.md"))
            t014_text = t014_file.read_text(encoding="utf-8")
            self.assertIn("Stage: 3", t014_text)
            self.assertNotIn("Stage: 2", t014_text)

            # Verify tasks.md ledger updated atomically
            tasks_after = studio.get_tasks_data(str(proj))["tasks"]
            stages_map = {t["id"]: t["stage"] for t in tasks_after}
            self.assertEqual(stages_map["T-014"], "3")


class TestJevTokenBudgetEstimator(StudioApiCase):
    """Tests for T-163: Jev Token & Budget Estimator for Task Pool Synthesis (Plan Model)."""

    def _make_plan_project(self, td: str) -> tuple[Path, Path]:
        proj = Path(td) / "plan_model_proj"
        flow = proj / ".agentsflower"
        (flow / "state").mkdir(parents=True)
        (flow / "tasks").mkdir(parents=True)
        (flow / "docs").mkdir(parents=True)
        studio.save_attached_project(str(proj))
        self.addCleanup(lambda: self._detach_project(proj))
        return proj, flow

    def _detach_project(self, proj: Path):
        try:
            if studio.ATTACHED_FILE.is_file():
                attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                studio.ATTACHED_FILE.write_text(
                    json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                )
        except Exception:
            pass

    def test_output_token_tiers_and_input_token_blast_radius_scaling(self):
        import plan_route

        self.assertEqual(plan_route.estimate_output_tokens("low"), 1000)
        self.assertEqual(plan_route.estimate_output_tokens("medium"), 4000)
        self.assertEqual(plan_route.estimate_output_tokens("high"), 12000)
        self.assertEqual(plan_route.estimate_output_tokens("max"), 24000)

        small_in = plan_route.estimate_input_tokens(
            "Short prompt",
            blast_files=[".agentsflower/VERSION"],
            root=studio.REPO_ROOT,
        )
        large_in = plan_route.estimate_input_tokens(
            "Long architectural prompt " * 80,
            blast_files=[".agentsflower/tools/studio.py", ".agentsflower/tools/plan_route.py"],
            root=studio.REPO_ROOT,
        )
        self.assertGreater(small_in, 0)
        self.assertGreater(large_in, small_in)

        est = studio.estimate_task_budget(
            prompt_text="Implement Jev token estimator",
            blast_files=[".agentsflower/tools/studio.py"],
            effort="high",
            model="gemini-4-argon-high",
            tool="devin",
            root=studio.REPO_ROOT,
        )
        self.assertEqual(est["planned_output_tokens"], 12000)
        self.assertGreater(est["planned_input_tokens"], 0)
        self.assertEqual(
            est["planned_tokens"],
            est["planned_input_tokens"] + est["planned_output_tokens"],
        )

    def test_model_pricing_rate_lookup_and_cost_calculation(self):
        import plan_route

        # Devin swe-2 free
        swe = plan_route.estimate_task_budget(
            prompt_text="Routine floor task",
            blast_files=[".agentsflower/VERSION"],
            effort="medium",
            model="swe-2-high",
            tool="devin",
            root=studio.REPO_ROOT,
        )
        self.assertEqual(swe["planned_cost_usd"], 0.0)
        self.assertTrue(swe["free"])

        # Local Ollama $0
        ollama = plan_route.estimate_task_budget(
            prompt_text="Offline local task",
            blast_files=[".agentsflower/VERSION"],
            effort="low",
            model="qwen2.5-coder",
            tool="ollama",
            root=studio.REPO_ROOT,
        )
        self.assertEqual(ollama["planned_cost_usd"], 0.0)
        self.assertTrue(ollama["free"])

        # Claude Opus $15/M
        opus_rate = plan_route.lookup_model_pricing("claude-opus-5.5", tool="claude")
        self.assertEqual(opus_rate["rate_per_1m"], 15.0)
        opus = plan_route.estimate_task_budget(
            prompt_text="Complex cross-cutting refactor",
            blast_files=[".agentsflower/tools/studio.py"],
            effort="max",
            model="claude-opus-5.5",
            tool="claude",
            root=studio.REPO_ROOT,
        )
        expected_opus_cost = round(opus["planned_tokens"] * 15.0 / 1_000_000, 6)
        self.assertEqual(opus["planned_output_tokens"], 24000)
        self.assertAlmostEqual(opus["planned_cost_usd"], expected_opus_cost, places=6)
        self.assertGreater(opus["planned_cost_usd"], 0.0)

        # Custom config pricing override from model-options.json structure
        custom_cfg = {
            "options": {
                "custom-pro": {
                    "tool": "devin",
                    "model": "custom-pro-v1",
                    "pricing": {"input_per_1m": 4.0, "output_per_1m": 20.0},
                }
            }
        }
        custom_est = plan_route.estimate_task_budget(
            prompt_text="Custom model task",
            blast_files=[],
            effort="low",
            model="custom-pro-v1",
            tool="devin",
            config=custom_cfg,
        )
        expected_custom = round(
            (custom_est["planned_input_tokens"] * 4.0 + custom_est["planned_output_tokens"] * 20.0) / 1_000_000,
            6,
        )
        self.assertAlmostEqual(custom_est["planned_cost_usd"], expected_custom, places=6)

    def test_synthesize_populates_planned_tokens_and_cost_usd(self):
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
                            "1. Architect complex multi-file AST knowledge graph synthesis across studio.py, plan_route.py, and graft.py. "
                            "2. Update minor CSS badge label in studio.css."
                        ),
                    }
                ],
            },
        )
        self.assertEqual(code, 200, res)
        self.assertTrue(res.get("ok"), res)
        tasks = res.get("tasks", [])
        self.assertGreaterEqual(len(tasks), 2)

        for t in tasks:
            self.assertIn("planned_input_tokens", t)
            self.assertIn("planned_output_tokens", t)
            self.assertIn("planned_tokens", t)
            self.assertIn("planned_cost_usd", t)
            self.assertGreater(t["planned_input_tokens"], 0)
            self.assertIn(t["planned_output_tokens"], (1000, 4000, 12000, 24000))
            self.assertEqual(
                t["planned_tokens"],
                t["planned_input_tokens"] + t["planned_output_tokens"],
            )
            if t["model"] == "swe-2-high":
                self.assertEqual(t["planned_cost_usd"], 0.0)
            else:
                self.assertGreater(t["planned_cost_usd"], 0.0)

        self.assertEqual(res.get("planned_tokens"), sum(t["planned_tokens"] for t in tasks))
        self.assertAlmostEqual(
            res.get("planned_cost_usd", 0.0),
            round(sum(t["planned_cost_usd"] for t in tasks), 6),
            places=6,
        )

    def test_batch_register_writes_plan_json_and_task_headers(self):
        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_plan_project(td)
            pool = [
                {
                    "id": "T-401",
                    "title": "Architect token estimator in plan_route.py",
                    "stage": 7,
                    "role": "developer",
                    "tool": "devin",
                    "model": "gemini-4-argon-high",
                    "effort": "high",
                    "goal": "Implement token and cost estimation in plan_route.py and studio.py.",
                    "allowed_files": [".agentsflower/tools/plan_route.py", ".agentsflower/tools/studio.py"],
                    "criteria": ["C-01: Token and cost estimation implemented."],
                },
                {
                    "id": "T-402",
                    "title": "Add unit tests for token estimator",
                    "stage": 7,
                    "depends": "T-401",
                    "role": "developer",
                    "tool": "devin",
                    "model": "swe-2-high",
                    "effort": "medium",
                    "goal": "Verify token estimation in test_studio.py.",
                    "allowed_files": [".agentsflower/tests/test_studio.py"],
                    "criteria": ["C-01: Unit tests pass."],
                },
            ]
            code, res = self.api(
                "/api/task/pool/register",
                method="POST",
                body={"project": str(proj), "tasks": pool},
            )
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)

            plan_401_path = flow / "tasks" / "T-401.plan.json"
            plan_402_path = flow / "tasks" / "T-402.plan.json"
            self.assertTrue(plan_401_path.is_file(), "T-401.plan.json must be created")
            self.assertTrue(plan_402_path.is_file(), "T-402.plan.json must be created")

            p401 = json.loads(plan_401_path.read_text(encoding="utf-8"))
            p402 = json.loads(plan_402_path.read_text(encoding="utf-8"))
            self.assertEqual(p401["task_id"], "T-401")
            self.assertEqual(p401["planned_output_tokens"], 12000)
            self.assertEqual(p401["planned_tokens"], p401["planned_input_tokens"] + p401["planned_output_tokens"])
            self.assertGreater(p401["planned_cost_usd"], 0.0)

            self.assertEqual(p402["task_id"], "T-402")
            self.assertEqual(p402["planned_output_tokens"], 4000)
            self.assertEqual(p402["planned_cost_usd"], 0.0)

            t401_md = next((flow / "tasks").glob("T-401-*.md")).read_text(encoding="utf-8")
            self.assertIn("Planned tokens:", t401_md)
            self.assertIn("Planned cost USD:", t401_md)

    def test_task_pool_card_ui_renders_token_and_cost_badges(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            "planned_tokens",
            "planned_cost_usd",
            "token-badge",
            "cost-badge",
            "formatTokenCount",
            "formatUsdCost",
        ):
            self.assertIn(marker, js)
        for marker in (".token-badge", ".cost-badge", ".pool-budget-summary"):
            self.assertIn(marker, css)


class TestTelemetryFactAndCostDashboard(StudioApiCase):
    """Tests for T-165: Telemetry Fact Tracking and Studio Cost & ROI Dashboard (Plan vs Fact)."""

    def _make_cost_project(self, td: str) -> tuple[Path, Path]:
        proj = Path(td) / "cost_roi_proj"
        flow = proj / ".agentsflower"
        (flow / "state").mkdir(parents=True)
        (flow / "tasks" / ".runtime").mkdir(parents=True)
        (flow / "docs").mkdir(parents=True)
        studio.save_attached_project(str(proj))
        self.addCleanup(lambda: self._detach_project(proj))
        return proj, flow

    def _detach_project(self, proj: Path):
        try:
            if studio.ATTACHED_FILE.is_file():
                attached = json.loads(studio.ATTACHED_FILE.read_text(encoding="utf-8"))
                attached = [x for x in attached if str(proj.resolve()) != str(Path(x).resolve())]
                studio.ATTACHED_FILE.write_text(
                    json.dumps(attached, indent=2, ensure_ascii=False), encoding="utf-8"
                )
        except Exception:
            pass

    def test_analytics_costs_aggregates_plan_vs_fact_and_stages(self):
        with tempfile.TemporaryDirectory() as td:
            proj, flow = self._make_cost_project(td)
            pool = [
                {
                    "id": "T-501",
                    "title": "Implement telemetry parser",
                    "stage": 7,
                    "role": "developer",
                    "tool": "devin",
                    "model": "gemini-4-argon-high",
                    "effort": "high",
                    "planned_input_tokens": 4000,
                    "planned_output_tokens": 12000,
                    "planned_tokens": 16000,
                    "planned_cost_usd": 0.04,
                    "goal": "Parse worker runtime telemetry.",
                    "allowed_files": [".agentsflower/tools/studio.py"],
                    "criteria": ["C-01: Telemetry parsed."],
                },
                {
                    "id": "T-502",
                    "title": "Build Cost & ROI dashboard UI",
                    "stage": 7,
                    "depends": "T-501",
                    "role": "developer",
                    "tool": "claude",
                    "model": "claude-opus-5.5",
                    "effort": "max",
                    "planned_input_tokens": 6000,
                    "planned_output_tokens": 14000,
                    "planned_tokens": 20000,
                    "planned_cost_usd": 0.30,
                    "goal": "Render Plan vs Fact Cost dashboard.",
                    "allowed_files": [".agentsflower/studio/studio.js"],
                    "criteria": ["C-01: Dashboard rendered."],
                },
                {
                    "id": "T-503",
                    "title": "Run local verification suite",
                    "stage": 8,
                    "depends": "T-502",
                    "role": "tester",
                    "tool": "ollama",
                    "model": "qwen2.5-coder",
                    "effort": "low",
                    "planned_input_tokens": 2000,
                    "planned_output_tokens": 4000,
                    "planned_tokens": 6000,
                    "planned_cost_usd": 0.0,
                    "goal": "Run unit tests on local Ollama.",
                    "allowed_files": [".agentsflower/tests/test_studio.py"],
                    "criteria": ["C-01: Tests green."],
                },
            ]
            reg_code, reg_res = self.api(
                "/api/task/pool/register",
                method="POST",
                body={"project": str(proj), "tasks": pool},
            )
            self.assertEqual(reg_code, 200, reg_res)

            rt_dir = flow / "tasks" / ".runtime"
            # T-501: 12,000 actual tokens @ $2.50/1M = $0.03 (under plan $0.04 -> delta -$0.01 / -25%)
            (rt_dir / "T-501.json").write_text(
                json.dumps({
                    "taskId": "T-501",
                    "attempts": [
                        {
                            "n": 1,
                            "tool": "devin",
                            "requestedModel": "gemini-4-argon-high",
                            "effectiveModel": "gemini-4-argon-high",
                            "status": "exited",
                            "exitCode": 0,
                            "startedAt": "2026-10-25T05:00:00Z",
                            "finishedAt": "2026-10-25T05:02:30Z",
                            "input_tokens": 3000,
                            "output_tokens": 9000,
                            "model_calls": 2,
                        }
                    ],
                }),
                encoding="utf-8",
            )
            # T-502: 15,000 actual tokens @ $15.00/1M = $0.225 (under plan $0.30 -> delta -$0.075 / -25%)
            (rt_dir / "T-502.json").write_text(
                json.dumps({
                    "taskId": "T-502",
                    "attempts": [
                        {
                            "n": 1,
                            "tool": "claude",
                            "requestedModel": "claude-opus-5.5",
                            "status": "exited",
                            "exitCode": 0,
                            "startedAt": "2026-10-25T05:05:00Z",
                            "finishedAt": "2026-10-25T05:08:30Z",
                            "usage": {
                                "prompt_tokens": 5000,
                                "completion_tokens": 10000,
                            },
                            "model_calls": 3,
                        }
                    ],
                }),
                encoding="utf-8",
            )
            # T-503: 9,000 actual tokens on local Ollama @ $0.00/1M = $0.00
            (rt_dir / "T-503.json").write_text(
                json.dumps({
                    "taskId": "T-503",
                    "attempts": [
                        {
                            "n": 1,
                            "tool": "ollama",
                            "requestedModel": "qwen2.5-coder",
                            "status": "exited",
                            "exitCode": 0,
                            "startedAt": "2026-10-25T05:10:00Z",
                            "finishedAt": "2026-10-25T05:10:45Z",
                            "actual_tokens": 9000,
                            "model_calls": 1,
                        }
                    ],
                }),
                encoding="utf-8",
            )

            code, res = self.api("/api/analytics/costs?" + self.q({"project": str(proj)}))
            self.assertEqual(code, 200, res)
            self.assertTrue(res.get("ok"), res)

            tasks_map = {t["id"]: t for t in res.get("tasks", [])}
            self.assertEqual(set(tasks_map.keys()), {"T-501", "T-502", "T-503"})

            t501 = tasks_map["T-501"]
            self.assertEqual(t501["planned_tokens"], 16000)
            self.assertAlmostEqual(t501["planned_cost_usd"], 0.04, places=6)
            self.assertEqual(t501["actual_tokens"], 12000)
            self.assertAlmostEqual(t501["actual_cost_usd"], 0.03, places=6)
            self.assertAlmostEqual(t501["delta_usd"], -0.01, places=6)
            self.assertAlmostEqual(t501["delta_pct"], -25.0, places=2)
            self.assertAlmostEqual(t501["execution_time_seconds"], 150.0, places=1)
            self.assertEqual(t501["model_calls"], 2)

            t502 = tasks_map["T-502"]
            self.assertEqual(t502["planned_tokens"], 20000)
            self.assertAlmostEqual(t502["planned_cost_usd"], 0.30, places=6)
            self.assertEqual(t502["actual_tokens"], 15000)
            self.assertAlmostEqual(t502["actual_cost_usd"], 0.225, places=6)
            self.assertAlmostEqual(t502["delta_usd"], -0.075, places=6)
            self.assertAlmostEqual(t502["delta_pct"], -25.0, places=2)
            self.assertAlmostEqual(t502["execution_time_seconds"], 210.0, places=1)
            self.assertEqual(t502["model_calls"], 3)

            t503 = tasks_map["T-503"]
            self.assertEqual(t503["actual_tokens"], 9000)
            self.assertAlmostEqual(t503["actual_cost_usd"], 0.0, places=6)
            self.assertAlmostEqual(t503["delta_usd"], 0.0, places=6)
            self.assertTrue(t503["free"])

            summary = res.get("summary", {})
            self.assertAlmostEqual(summary["total_planned_usd"], 0.34, places=6)
            self.assertAlmostEqual(summary["total_actual_usd"], 0.255, places=6)
            self.assertAlmostEqual(summary["delta_usd"], -0.085, places=6)
            self.assertAlmostEqual(summary["net_savings_usd"], 0.085, places=6)
            self.assertEqual(summary["planned_tokens"], 42000)
            self.assertEqual(summary["actual_tokens"], 36000)
            self.assertAlmostEqual(summary["local_free_tokens_pct"], 25.0, places=1)
            self.assertAlmostEqual(summary["execution_time_seconds"], 405.0, places=1)
            self.assertEqual(summary["model_calls"], 6)

            stages = {str(s["stage"]): s for s in res.get("stages", [])}
            self.assertIn("7", stages)
            self.assertIn("8", stages)
            self.assertAlmostEqual(stages["7"]["planned_cost_usd"], 0.34, places=6)
            self.assertAlmostEqual(stages["7"]["actual_cost_usd"], 0.255, places=6)
            self.assertEqual(stages["7"]["task_count"], 2)
            self.assertEqual(stages["8"]["task_count"], 1)

    def test_analytics_costs_empty_telemetry_fallbacks_and_unknown_project(self):
        with tempfile.TemporaryDirectory() as td:
            # 1. Unregistered project -> 403
            unreg_code, unreg_res = self.api("/api/analytics/costs?" + self.q({"project": td}))
            self.assertEqual(unreg_code, 403, unreg_res)

            # 2. Empty initialized project -> zeroed fallbacks
            proj, flow = self._make_cost_project(td)
            code, empty_res = self.api("/api/analytics/costs?" + self.q({"project": str(proj)}))
            self.assertEqual(code, 200, empty_res)
            self.assertTrue(empty_res.get("ok"), empty_res)
            self.assertEqual(empty_res["tasks"], [])
            self.assertEqual(empty_res["stages"], [])
            self.assertEqual(empty_res["summary"]["total_planned_usd"], 0.0)
            self.assertEqual(empty_res["summary"]["total_actual_usd"], 0.0)
            self.assertEqual(empty_res["summary"]["net_savings_usd"], 0.0)
            self.assertEqual(empty_res["summary"]["local_free_tokens_pct"], 0.0)

            # 3. Planned task with no .runtime telemetry file -> actual=0, delta = -plan
            self.api(
                "/api/task/pool/register",
                method="POST",
                body={
                    "project": str(proj),
                    "tasks": [
                        {
                            "id": "T-510",
                            "title": "Planned task awaiting execution",
                            "stage": 7,
                            "role": "developer",
                            "tool": "devin",
                            "model": "gemini-4-argon-high",
                            "effort": "medium",
                            "planned_input_tokens": 2000,
                            "planned_output_tokens": 4000,
                            "planned_tokens": 6000,
                            "planned_cost_usd": 0.015,
                            "goal": "Await execution.",
                            "allowed_files": [".agentsflower/tools/studio.py"],
                            "criteria": ["C-01: Done."],
                        }
                    ],
                },
            )
            code2, res2 = self.api("/api/analytics/costs?" + self.q({"project": str(proj)}))
            self.assertEqual(code2, 200, res2)
            self.assertEqual(len(res2["tasks"]), 1)
            t510 = res2["tasks"][0]
            self.assertFalse(t510["has_telemetry"])
            self.assertEqual(t510["planned_tokens"], 6000)
            self.assertAlmostEqual(t510["planned_cost_usd"], 0.015, places=6)
            self.assertEqual(t510["actual_tokens"], 0)
            self.assertEqual(t510["actual_cost_usd"], 0.0)
            self.assertAlmostEqual(t510["delta_usd"], -0.015, places=6)
            self.assertEqual(t510["execution_time_seconds"], 0.0)
            self.assertEqual(t510["model_calls"], 0)

    def test_cost_and_roi_dashboard_subtab_in_analytics_view(self):
        """T-175: the Cost & ROI subtab is restored as a fourth analytics tab."""
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            html = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.js") as resp:
            js = resp.read().decode("utf-8")
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/studio.css") as resp:
            css = resp.read().decode("utf-8")

        for marker in (
            'data-sub="index"',
            'data-sub="graph"',
            'data-sub="roadmap"',
            'data-sub="costs"',
            'id="btnSubtabCosts"',
            "Cost &amp; ROI Dashboard",
            'id="costRoiDashboard"',
            'id="costTotalPlanned"',
            'id="costTotalActual"',
            'id="costNetSavings"',
            'id="costLocalFreePct"',
            'id="costStageDistribution"',
            'id="costTaskTableBody"',
        ):
            self.assertIn(marker, html)

        for marker in (
            "loadCostAnalytics",
            "renderCostDashboard",
            "costRoiDashboard",
            "costStageDistribution",
            "costTaskTableBody",
            "costAnalytics",
            "/api/analytics/costs",
            "state.analyticsSubTab === 'costs'",
        ):
            self.assertIn(marker, js)

        for marker in (
            ".cost-roi-dashboard",
            ".cost-summary-grid",
            ".cost-stage-bar",
            ".cost-task-table",
        ):
            self.assertIn(marker, css)


class TestProjectNamingAndDashboardPlaceholder(StudioApiCase):
    """T-173: generic directory names get parent disambiguation, parent folders
    resolve to child flow roots, and unbuilt dashboards serve an HTML placeholder."""

    def setUp(self):
        self._attached = (studio.ATTACHED_FILE.read_text(encoding="utf-8")
                          if studio.ATTACHED_FILE.is_file() else None)

    def tearDown(self):
        if self._attached is None:
            studio.ATTACHED_FILE.unlink(missing_ok=True)
        else:
            studio.ATTACHED_FILE.write_text(self._attached, encoding="utf-8")

    def test_display_name_disambiguates_generic_dirs(self):
        for generic in ("code", "site", "v1", "v2"):
            self.assertEqual(
                studio.project_display_name(Path("AntiBrowser") / generic),
                f"AntiBrowser / {generic}",
            )
        self.assertEqual(
            studio.project_display_name(Path("workspace") / "MyProj"), "MyProj")

    def test_flow_root_resolves_code_and_src_children(self):
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / "AntiBrowser"
            child = parent / "code" / ".agentsflower"
            child.mkdir(parents=True)
            self.assertEqual(studio.get_project_flow_root(parent), child)
            self.assertTrue(studio.get_project_info(parent)["has_framework"])
        with tempfile.TemporaryDirectory() as td:
            parent = Path(td) / "SiteHost"
            child = parent / "src" / ".agentflow"
            child.mkdir(parents=True)
            self.assertEqual(studio.get_project_flow_root(parent), child)
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(studio.get_project_flow_root(Path(td)))

    def test_project_list_disambiguates_generic_name(self):
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "AntiBrowser" / "code"
            (proj / ".agentsflower" / "state").mkdir(parents=True)
            studio.save_attached_project(str(proj))
            code_, res = self.api("/api/projects")
            self.assertEqual(code_, 200, res)
            entry = next(p for p in res["projects"]
                         if Path(p["path"]).resolve() == proj.resolve())
            self.assertEqual(entry["name"], "AntiBrowser / code")
            self.assertTrue(entry["has_framework"])

    def test_dashboard_placeholder_for_unbuilt_project(self):
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "unbuilt_proj"
            (proj / ".agentsflower" / "state").mkdir(parents=True)
            studio.save_attached_project(str(proj))
            url = (f"http://127.0.0.1:{self.port}/dashboard/out/index.html?"
                   + self.q({"project": str(proj)}))
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(url)
            self.assertEqual(cm.exception.code, 404)
            self.assertIn("text/html", cm.exception.headers.get("Content-Type", ""))
            body = cm.exception.read().decode("utf-8")
            self.assertIn("<html", body.lower())
            self.assertIn("Dashboard not yet generated", body)
            self.assertIn("Rebuild Analytics", body)


if __name__ == "__main__":
    unittest.main()
