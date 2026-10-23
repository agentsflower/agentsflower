"""Unit tests for AgentsFlower specialized skills ecosystem, including geo-seo-audit."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FLOW = Path(__file__).resolve().parents[1]
SKILLS = FLOW / "skills"
GEO_AUDIT_SCRIPT = SKILLS / "geo-seo-audit" / "scripts" / "geo_audit.py"


class SkillsEcosystemTests(unittest.TestCase):
    def test_skills_registry_files_exist(self):
        self.assertTrue((SKILLS / "README.md").is_file(), "skills/README.md must exist")
        self.assertTrue((SKILLS / "INDEX.md").is_file(), "skills/INDEX.md must exist")
        self.assertTrue((SKILLS / "ATTRIBUTION.md").is_file(), "skills/ATTRIBUTION.md must exist")

    def test_geo_seo_audit_skill_contract(self):
        skill_md = SKILLS / "geo-seo-audit" / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "geo-seo-audit/SKILL.md must exist")
        content = skill_md.read_text(encoding="utf-8")
        self.assertIn("name: geo-seo-audit", content)
        self.assertIn("description:", content)
        self.assertTrue(GEO_AUDIT_SCRIPT.is_file(), "geo_audit.py script must exist")

    def test_geo_audit_runs_cleanly_on_sample_html(self):
        sample = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>High Quality SEO & GEO Page Demonstration</title>
  <meta name="description" content="A comprehensive example of optimal SEO and AI citability markup.">
  <meta property="og:title" content="High Quality Page">
  <meta property="og:description" content="A comprehensive example.">
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "AgentsFlower Studio"
  }
  </script>
</head>
<body>
  <header><h1>AgentsFlower Studio is a multi-project cockpit</h1></header>
  <main>
    <h2>Core Features</h2>
    <p>Provides deterministic AI handoff and task enforcement.</p>
  </main>
</body>
</html>
"""
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "index.html"
            f.write_text(sample, encoding="utf-8")
            (Path(td) / "llms.txt").write_text("# AgentsFlower llms.txt\n", encoding="utf-8")
            (Path(td) / "llms-full.txt").write_text("# AgentsFlower Full Context\n", encoding="utf-8")

            res = subprocess.run(
                [sys.executable, str(GEO_AUDIT_SCRIPT), str(f), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            data = json.loads(res.stdout)
            self.assertGreaterEqual(data["score"], 80)
            self.assertEqual(data["verdict"], "OPTIMIZED")
            self.assertEqual(data["categories"]["structured_data"]["score"], 25)
            self.assertEqual(data["categories"]["semantic_structure"]["score"], 20)


if __name__ == "__main__":
    unittest.main()
