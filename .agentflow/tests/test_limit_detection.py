"""limit_detection.py: which session-log tails are the tool's own provider/account
limit and which are a worker's report about the product's quotas, rate limits or
attack-test output. Shapes come from real logs (successful reports the old keyword
regex misclassified) and the observed AGY Individual-quota exhaustion. No external
provider calls."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FLOW = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLOW / "tools"))
import limit_detection as ld  # noqa: E402

# A successful report about application quotas.
DEVIN_SUCCESS_TAIL = (
    "Task T-003 complete. Final state verified:\n\n"
    "- **Commit**: `fbd8e2a` on `t-003-account-backend`, worktree clean\n"
    "- **Result** written to the main checkout task file only (not committed, as required)\n\n"
    "Done in this pass:\n"
    "- Fixed all draft defects: JWT `kid` fail-closed verification + real nonce validation; "
    "`youtube-transcript-api` 1.x API with bounded timeouts; atomic per-video quota "
    "reservation/release via `user_period_videos` + guarded upsert; atomic locked guest-trial "
    "claims and one-time transfer; Alembic migrations replacing `create_all`; HMAC-bound guest "
    "CSRF; production Host check; actual-bytes 64 KB body cap; caption-fetch concurrency bound; "
    "session revocation on login; open-redirect hardening; transcript dedup partial unique "
    "indexes; history retention purge; bulk per-item quota release and restart cleanup.\n"
    "- Removed the quota-free `dQw4w9WgXcQ` loophole and the port mismatch (now 4343 everywhere).\n"
    "- All checks pass: backend suite 41/41 (real temp PostgreSQL via Docker), pip-audit clean, "
    "`npm run check`/`test`/`build`/`audit` clean, `git diff --check` clean.\n"
)

# A successful tester report mentioning quota and 429.
TESTER_SUCCESS_TAIL = (
    "production secrets/cookie gaps, no OAuth browser binding, quota accounting correct. "
    "Probe E needs a redo: the bulk job was rejected upfront (429) because the user only had "
    "4 remaining slots for a 5-item batch — the starvation window was never exercised.\n\n"
    "All probes are complete and the worktree is still clean at the Verifies SHA. "
    "Result written. Final sanity checks: confirm the worktree is still clean and the task "
    "file content is intact.Artifact and evidence recorded in the Task File.\n"
)

ATTACK_TEST_OUTPUT = (
    "adversarial probes done: burst login returned 429 Too Many Requests after the fifth "
    "attempt, QUOTA_EXCEEDED surfaced on the sixth video, and the rate limit bypass probe "
    "was rejected as designed\n"
)

AGY_STREAM_ERROR = (
    '{"type":"system","subtype":"init","session_id":"s1"}\n'
    '{"type":"assistant","message":{"content":[{"type":"text","text":"Let me check the tests."}]}}\n'
    '{"type":"error","error":{"message":"RESOURCE_EXHAUSTED: Individual quota reached. '
    'Quota resets in 167h38m58s."}}\n'
)

AGY_STREAM_RESULT_REPORT = (
    '{"type":"assistant","message":{"content":[{"type":"text","text":"probing 429 and '
    'QUOTA_EXCEEDED handling"}]}}\n'
    '{"type":"result","subtype":"success","is_error":false,'
    '"result":"Done: per-video quota reservation fixed, QUOTA_EXCEEDED path tested."}\n'
)


class DetectTests(unittest.TestCase):
    def test_successful_reports_about_product_quotas_are_no_limit(self):
        for tail in (DEVIN_SUCCESS_TAIL, TESTER_SUCCESS_TAIL):
            self.assertIsNone(ld.detect(tail, exit_code=0), tail[-120:])

    def test_rate_limit_and_quota_words_in_a_report_are_no_limit(self):
        tail = ("Rate limits are per process; add proxy-level controls before exposure. "
                "Monthly quotas remain enforced per user.\n")
        self.assertIsNone(ld.detect(tail, exit_code=0))

    def test_application_attack_test_output_is_no_limit(self):
        self.assertIsNone(ld.detect(ATTACK_TEST_OUTPUT, exit_code=0))

    def test_unqualified_limit_words_on_a_failed_run_are_no_limit(self):
        self.assertIsNone(ld.detect("the rate limit middleware test failed\n", exit_code=1))
        self.assertIsNone(ld.detect("quota-free path crashed the session\n", exit_code=1))

    def test_retryable_connection_errors_are_no_limit(self):
        for tail in ("stream error: UNAVAILABLE: upstream connect error or disconnect/reset\n",
                     "dial tcp 10.0.0.1:443: connect: connection refused\n",
                     "POST https://api.example: 503 Service Unavailable, retrying\n",
                     "error: request timed out after 30s; the provider API is unreachable\n"):
            self.assertIsNone(ld.detect(tail, exit_code=1), tail)

    def test_quota_status_code_needs_a_failed_run_or_an_error_event(self):
        self.assertIsNone(ld.detect("verified: QUOTA_EXCEEDED path returns the code\n", exit_code=0))
        self.assertIsNone(ld.detect(AGY_STREAM_RESULT_REPORT, exit_code=0))
        self.assertIsNotNone(ld.detect("run failed mid-edit: RESOURCE_EXHAUSTED\n", exit_code=1))

    def test_observed_agy_quota_exhaustion_is_a_limit(self):
        self.assertIsNotNone(ld.detect(AGY_STREAM_ERROR, exit_code=1))
        self.assertIsNotNone(ld.detect(AGY_STREAM_ERROR, exit_code=0))  # outer error event
        self.assertIsNotNone(
            ld.detect("Error: RESOURCE_EXHAUSTED: Individual quota reached. "
                      "Quota resets in 167h38m58s.\n", exit_code=0))

    def test_provider_usage_limit_phrasing_is_a_limit_at_any_exit(self):
        for tail in ("ERROR: You've hit your usage limit. Try again at 3:30 PM.\n",
                     "Claude usage limit reached. Your limit resets 3:30pm\n",
                     "You have exceeded your monthly quota; the account is out of credits\n"):
            for code in (0, 1):
                self.assertIsNotNone(ld.detect(tail, exit_code=code), tail)

    def test_structured_quotes_of_strong_phrases_are_no_limit(self):
        # exit-0 structured assistant/tool output quoting strong provider-looking
        # phrases is nested data, not an outer error.
        tails = (
            '{"type":"assistant","message":{"content":[{"type":"text","text":'
            '"The system said: You\'ve hit your usage limit. Try again at 3:30 PM."}]}}\n',
            '{"type":"assistant","message":{"content":[{"type":"tool_use","input":'
            '"the account is out of credits"}]}}\n',
            '{"type":"result","subtype":"success","is_error":false,'
            '"result":"verified: your limit resets at midnight paths"}\n',
        )
        for tail in tails:
            for code in (0, 1):
                self.assertIsNone(ld.detect(tail, exit_code=code), tail)

    def test_test_output_quoting_api_failures_is_no_limit(self):
        # exit-1 test output quoting product API failures is quoted subject
        # matter at either exit code.
        tails = (
            "test failed: expected 200, got 429 You have exceeded your monthly "
            "quota; the account is out of credits\n",
            "FAIL: expected 200, got 429 RESOURCE_EXHAUSTED from the product API\n",
            "the mock responded: 'hit your usage limit'\n",
        )
        for tail in tails:
            for code in (0, 1):
                self.assertIsNone(ld.detect(tail, exit_code=code), tail)

    def test_unstructured_real_budget_failures_still_detect(self):
        # The provider's own last words keep counting: bare sentences, error
        # lines, and failure lines without quote framing.
        self.assertIsNotNone(ld.detect("out of credits\n", exit_code=0))
        self.assertIsNotNone(ld.detect("error: the account is out of credits\n", exit_code=0))
        self.assertIsNotNone(
            ld.detect("request failed: You have exceeded your monthly quota\n", exit_code=1))

    def test_disabled_subscription_and_window_exhaustion_are_limits(self):
        self.assertIsNotNone(ld.detect(
            "Your organization has disabled Claude subscription access for Claude Code. "
            "Use an Anthropic API key instead, or ask your admin to enable access\n", exit_code=0))
        self.assertIsNotNone(ld.detect("usage window exhausted for this account\n", exit_code=1))
        self.assertIsNotNone(ld.detect("error: usage window exhausted\n", exit_code=0))

    def test_detect_file_scans_the_tail_and_survives_missing_logs(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "T-9.1.log"
            self.assertIsNone(ld.detect_file(log))
            log.write_text("work\n" * 4000 + "You've hit your usage limit. Resets in 2h\n",
                           encoding="utf-8")
            self.assertIsNotNone(ld.detect_file(log, 0))
            self.assertIsNone(ld.detect_file(log.with_name("gone.log"), 1))


class CliTests(unittest.TestCase):
    """The exit-code contract run_task.py and conductor.ps1 rely on."""

    def run_cli(self, text, code):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "session.log"
            log.write_text(text, encoding="utf-8")
            r = subprocess.run([sys.executable, str(FLOW / "tools" / "limit_detection.py"),
                                str(log), "--exit-code", str(code)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r

    def test_cli_exit_codes(self):
        r = self.run_cli(DEVIN_SUCCESS_TAIL, 0)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        r = self.run_cli(AGY_STREAM_ERROR, 1)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(r.stdout.startswith("limit: "), r.stdout)


if __name__ == "__main__":
    unittest.main()
