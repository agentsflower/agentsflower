import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import local_adapter
import failover


class TestLocalAdapter(unittest.TestCase):
    def test_select_best_coding_model_deepseek_priority(self):
        models = [
            {"id": "llama3.2:3b", "name": "llama3.2:3b"},
            {"id": "deepseek-r1:14b", "name": "deepseek-r1:14b"},
            {"id": "qwen2.5-coder:7b", "name": "qwen2.5-coder:7b"},
        ]
        best = local_adapter.select_best_coding_model(models)
        self.assertIsNotNone(best)
        self.assertEqual(best["id"], "deepseek-r1:14b")

    def test_select_best_coding_model_qwen_priority_when_no_deepseek(self):
        models = [
            {"id": "llama3.2:3b", "name": "llama3.2:3b"},
            {"id": "qwen2.5-coder:7b", "name": "qwen2.5-coder:7b"},
            {"id": "mistral-nemo", "name": "mistral-nemo"},
        ]
        best = local_adapter.select_best_coding_model(models)
        self.assertIsNotNone(best)
        self.assertEqual(best["id"], "qwen2.5-coder:7b")

    def test_select_best_coding_model_fallback_first(self):
        models = [
            {"id": "custom-special-model", "name": "custom-special-model"},
        ]
        best = local_adapter.select_best_coding_model(models)
        self.assertIsNotNone(best)
        self.assertEqual(best["id"], "custom-special-model")

    def test_select_best_coding_model_none_when_empty(self):
        best = local_adapter.select_best_coding_model([])
        self.assertIsNone(best)

    @patch("urllib.request.urlopen")
    def test_probe_ollama_runtime(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "models": [
                {
                    "name": "deepseek-r1:8b",
                    "details": {
                        "family": "deepseek",
                        "parameter_size": "8B",
                        "quantization_level": "Q4_K_M"
                    }
                }
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = local_adapter.probe_runtime({
            "id": "ollama",
            "name": "Ollama Test",
            "base_url": "http://127.0.0.1:11434",
            "probe_path": "/api/tags",
            "type": "ollama",
        })

        self.assertTrue(res["online"])
        self.assertEqual(len(res["models"]), 1)
        self.assertEqual(res["models"][0]["id"], "deepseek-r1:8b")
        self.assertEqual(res["models"][0]["parameter_size"], "8B")

    @patch("urllib.request.urlopen")
    def test_probe_lmstudio_openai_runtime(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({
            "data": [
                {"id": "qwen2.5-coder-32b-instruct"}
            ]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = local_adapter.probe_runtime({
            "id": "lmstudio",
            "name": "LM Studio Test",
            "base_url": "http://127.0.0.1:1234",
            "probe_path": "/v1/models",
            "type": "openai",
        })

        self.assertTrue(res["online"])
        self.assertEqual(len(res["models"]), 1)
        self.assertEqual(res["models"][0]["id"], "qwen2.5-coder-32b-instruct")


class TestFailoverProtocol(unittest.TestCase):
    def test_failover_tier_1_to_tier_2(self):
        candidate = failover.resolve_failover_candidate("devin", "swe-2-high", "token_limit")
        self.assertEqual(candidate["tier"], 2)
        self.assertEqual(candidate["tool"], "codex")
        self.assertEqual(candidate["type"], "cloud")

    @patch("local_adapter.select_best_coding_model")
    def test_failover_tier_2_to_tier_3_local(self, mock_best):
        mock_best.return_value = {
            "id": "deepseek-r1:32b",
            "runtime_id": "ollama",
            "runtime_type": "ollama",
        }
        candidate = failover.resolve_failover_candidate("codex", "gpt-6.1-sol", "rate_limit")
        self.assertEqual(candidate["tier"], 3)
        self.assertEqual(candidate["tool"], "local")
        self.assertEqual(candidate["model"], "deepseek-r1:32b")
        self.assertEqual(candidate["type"], "local_zero_cost")

    def test_transfer_session_context_preserves_and_annotates(self):
        original = [
            {"role": "user", "content": "Implement feature A"},
            {"role": "assistant", "content": "I have created the files."},
        ]
        candidate = {
            "tier": 2,
            "tool": "codex",
            "model": "gpt-6.1-sol",
        }
        migrated = failover.transfer_session_context(original, "devin", candidate)
        self.assertEqual(len(migrated), 3)
        self.assertEqual(migrated[0]["content"], "Implement feature A")
        self.assertEqual(migrated[1]["content"], "I have created the files.")
        self.assertEqual(migrated[2]["role"], "system")
        self.assertIn("AgentsFlower Failover Protocol", migrated[2]["content"])
        self.assertIn("devin", migrated[2]["content"])
        self.assertIn("codex", migrated[2]["content"])


if __name__ == "__main__":
    unittest.main()
