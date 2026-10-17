"""mcp_server.py without the SDK: input validation, read-only handlers, the
missing-SDK diagnostic and the privileged-tool opt-in surface. These tests run
in the core stdlib suite; the real stdio handshake is check_mcp.py."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import mcp_server  # noqa: E402

HAVE_SDK = True
try:
    import mcp  # noqa: F401
    import mcp_types  # noqa: F401
except ImportError:
    HAVE_SDK = False


class ValidationTests(unittest.TestCase):
    def test_task_id_is_strict(self):
        for bad in ("", "T-", "T-abc", "t-1", "T-1; rm -rf /", "../x", "T-12345", None, 5):
            self.assertFalse(mcp_server.get_task(bad)["ok"], bad)
            self.assertFalse(mcp_server.run_gate(bad, "verify")["ok"], bad)
            self.assertFalse(mcp_server.accept_task(bad)["ok"], bad)

    def test_get_task_reads_a_contract(self):
        r = mcp_server.get_task("T-005")
        self.assertTrue(r["ok"], r)
        self.assertTrue(r["file"].startswith(".agentflow/tasks/T-005"))
        self.assertIn("T-005", r["content"])

    def test_get_task_missing(self):
        self.assertFalse(mcp_server.get_task("T-999")["ok"])

    def test_run_gate_check_type_enum(self):
        self.assertFalse(mcp_server.run_gate("T-005", "stage")["ok"])
        self.assertFalse(mcp_server.run_gate("T-005", "drop table")["ok"])

    def test_run_gate_calls_real_gate(self):
        # `task` only parses the Task File: a cheap, real gate subprocess
        r = mcp_server.run_gate("T-005", "task")
        self.assertIsInstance(r["exit_code"], int)
        self.assertEqual(r["check"], "task")
        self.assertIn("log", r)

    def test_query_ledger_bounds_and_role_enum(self):
        for bad in (0, -1, 201, "5", 5.5, True, None):
            self.assertFalse(mcp_server.query_ledger(limit=bad)["ok"], bad)
        self.assertFalse(mcp_server.query_ledger(limit=10, filter_role="root")["ok"])
        r = mcp_server.query_ledger(limit=5)
        self.assertTrue(r["ok"])
        self.assertLessEqual(r["count"], 5)
        r = mcp_server.query_ledger(limit=200, filter_role="developer")
        self.assertTrue(r["ok"])
        self.assertTrue(all(t["Role"] == "developer" for t in r["tasks"]))

    def test_status_is_read_only_snapshot(self):
        r = mcp_server.status()
        self.assertTrue(r["ok"])
        self.assertIn("agentflow_version", r)
        self.assertIn("open", r["tasks"])

    def test_accept_task_validates_before_running(self):
        # a bad id returns an error dict; accept.py is never invoked for it
        r = mcp_server.accept_task("nonsense")
        self.assertFalse(r["ok"])
        self.assertNotIn("exit_code", r)


class MissingSdkTests(unittest.TestCase):
    def test_build_server_diagnostic_without_sdk(self):
        with patch.dict(sys.modules, {"mcp": None, "mcp_types": None}):
            with self.assertRaises(mcp_server.SdkMissing) as stop:
                mcp_server.build_server()
        self.assertIn("pip install", str(stop.exception))

    def test_main_reports_missing_sdk_on_stderr(self):
        err = io.StringIO()
        with patch.dict(sys.modules, {"mcp": None, "mcp_types": None}), \
                contextlib.redirect_stderr(err):
            code = mcp_server.main([])
        self.assertEqual(code, 2)
        self.assertIn("agentflow-sdlc[mcp]", err.getvalue())


@unittest.skipUnless(HAVE_SDK, "optional mcp SDK not installed in this interpreter")
class ServerSurfaceTests(unittest.TestCase):
    def names(self, server):
        return sorted(t.name for t in server._tool_manager.list_tools())

    def test_default_surface_has_no_accept(self):
        self.assertEqual(self.names(mcp_server.build_server()),
                         ["agentflow_get_task", "agentflow_query_ledger",
                          "agentflow_run_gate", "agentflow_status"])

    def test_opt_in_adds_accept(self):
        self.assertIn("agentflow_accept_task",
                      self.names(mcp_server.build_server(enable_orchestrator=True)))

    def test_annotations_do_not_mark_gate_read_only(self):
        tools = {t.name: t for t in mcp_server.build_server()._tool_manager.list_tools()}
        for name in ("agentflow_status", "agentflow_get_task", "agentflow_query_ledger"):
            self.assertTrue(tools[name].annotations.read_only_hint, name)
        self.assertFalse(tools["agentflow_run_gate"].annotations.read_only_hint)


if __name__ == "__main__":
    unittest.main()
