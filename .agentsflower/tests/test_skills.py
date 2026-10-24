"""Unit tests for AgentsFlower specialized skills ecosystem, including geo-seo-audit."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FLOW = Path(__file__).resolve().parents[1]
SKILLS = FLOW / "skills"
GEO_AUDIT_SCRIPT = SKILLS / "geo-seo-audit" / "scripts" / "geo_audit.py"
ART_DIRECTION = SKILLS / "frontend-art-direction"
CHROME_MV3 = SKILLS / "chrome-extension-mv3"
MV3_LINT_SCRIPT = CHROME_MV3 / "scripts" / "mv3_lint.py"


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


class FrontendArtDirectionSkillTests(unittest.TestCase):
    def test_skill_package_structure(self):
        self.assertTrue(ART_DIRECTION.is_dir(), "frontend-art-direction/ must exist")
        skill_md = ART_DIRECTION / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "frontend-art-direction/SKILL.md must exist")
        self.assertTrue((ART_DIRECTION / "references").is_dir(), "references/ must exist")
        for name in ("anti-slop-guidelines.md", "micro-motion-easing.md", "design-tokens-wcag.md"):
            self.assertTrue((ART_DIRECTION / "references" / name).is_file(), f"references/{name} must exist")
        self.assertLessEqual(len(skill_md.read_text(encoding="utf-8").splitlines()), 500,
                             "SKILL.md must stay a <= 500-line router")

    def test_skill_frontmatter_conforms_to_spec(self):
        content = (ART_DIRECTION / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "SKILL.md must open with YAML frontmatter")
        end = content.find("\n---", 3)
        self.assertGreater(end, 0, "frontmatter block must be closed")
        fm = content[3:end]
        self.assertIn("name: frontend-art-direction", fm, "name must equal directory name")
        self.assertRegex(fm, r"description:\s*\S", "description must be present and non-empty")
        self.assertIn("domain: 1", fm, "metadata.domain must be 1")
        self.assertIn("Leonxlnx/taste-skill@main", fm)
        self.assertIn("emilkowalski/design-eng@main", fm)
        self.assertIn("license: MIT", fm, "metadata.license must be MIT")

    def test_skill_routes_to_existing_references(self):
        content = (ART_DIRECTION / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((references/[^)\s]+)\)", content)
        self.assertTrue(links, "router SKILL.md must link its references/ files")
        for link in links:
            self.assertTrue((ART_DIRECTION / link).is_file(), f"broken reference link: {link}")

    def test_references_provide_concrete_rules(self):
        refs = ART_DIRECTION / "references"
        anti = (refs / "anti-slop-guidelines.md").read_text(encoding="utf-8").lower()
        self.assertIn("icon card", anti, "anti-slop rules must ban the icon-card pattern")
        self.assertIn("shadow", anti, "anti-slop rules must cover translucent shadows")
        self.assertIn("typograph", anti, "anti-slop rules must cover typography hierarchy")
        motion = (refs / "micro-motion-easing.md").read_text(encoding="utf-8").lower()
        self.assertIn("ease-out", motion, "motion rules must mandate ease-out on enter")
        self.assertIn("ease-in", motion, "motion rules must address the ease-in mistake")
        self.assertIn("prefers-reduced-motion", motion, "motion rules must require reduced-motion compliance")
        tokens = (refs / "design-tokens-wcag.md").read_text(encoding="utf-8").lower()
        self.assertIn("4.5:1", tokens, "WCAG normal-text contrast ratio must be stated")
        self.assertIn("3:1", tokens, "WCAG large-text/UI-component ratio must be stated")
        self.assertIn("dark", tokens, "token rules must cover dark mode palettes")

    def test_registered_in_index_and_attribution(self):
        index = (SKILLS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("frontend-art-direction", index, "INDEX.md must register the skill")
        self.assertIn("frontend-art-direction/SKILL.md", index, "INDEX.md must link the SKILL.md")
        attr = (SKILLS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("frontend-art-direction", attr, "ATTRIBUTION.md must name the skill")
        self.assertIn("Leonxlnx/taste-skill", attr, "ATTRIBUTION.md must pin taste-skill")
        self.assertIn("emilkowalski", attr, "ATTRIBUTION.md must credit emilkowalski")
        self.assertIn("MIT", attr, "ATTRIBUTION.md must record the MIT license")


class ChromeExtensionMv3SkillTests(unittest.TestCase):
    def _write_extension(self, root: Path, manifest: dict, files: dict = None):
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        for name, body in (files or {}).items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")

    def _run_linter(self, target: Path):
        return subprocess.run(
            [sys.executable, str(MV3_LINT_SCRIPT), str(target), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_skill_package_structure(self):
        self.assertTrue(CHROME_MV3.is_dir(), "chrome-extension-mv3/ must exist")
        skill_md = CHROME_MV3 / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "chrome-extension-mv3/SKILL.md must exist")
        self.assertTrue((CHROME_MV3 / "references").is_dir(), "references/ must exist")
        for name in ("manifest-v3-rules.md", "service-worker-lifecycle.md"):
            self.assertTrue((CHROME_MV3 / "references" / name).is_file(), f"references/{name} must exist")
        self.assertTrue(MV3_LINT_SCRIPT.is_file(), "scripts/mv3_lint.py must exist")
        self.assertLessEqual(len(skill_md.read_text(encoding="utf-8").splitlines()), 500,
                             "SKILL.md must stay a <= 500-line router")

    def test_skill_frontmatter_conforms_to_spec(self):
        content = (CHROME_MV3 / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---"), "SKILL.md must open with YAML frontmatter")
        end = content.find("\n---", 3)
        self.assertGreater(end, 0, "frontmatter block must be closed")
        fm = content[3:end]
        self.assertIn("name: chrome-extension-mv3", fm, "name must equal directory name")
        self.assertRegex(fm, r"description:\s*\S", "description must be present and non-empty")
        self.assertIn("domain: 4", fm, "metadata.domain must be 4")
        self.assertIn("google/chrome-extensions-samples@main", fm, "metadata.source must pin chrome-extensions-samples")
        self.assertIn("GoogleChrome/modern-web-guidance@main", fm, "metadata.source must pin modern-web-guidance")
        self.assertIn("license: Apache-2.0", fm, "metadata.license must be Apache-2.0")

    def test_skill_routes_to_existing_references(self):
        content = (CHROME_MV3 / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((references/[^)\s]+)\)", content)
        self.assertTrue(links, "router SKILL.md must link its references/ files")
        for link in links:
            self.assertTrue((CHROME_MV3 / link).is_file(), f"broken reference link: {link}")

    def test_references_provide_concrete_rules(self):
        refs = CHROME_MV3 / "references"
        rules = (refs / "manifest-v3-rules.md").read_text(encoding="utf-8").lower()
        self.assertIn("manifest_version", rules, "rules must require manifest_version: 3")
        self.assertIn("service_worker", rules, "rules must cover background.service_worker")
        self.assertIn("chrome.action", rules, "rules must cover chrome.action")
        self.assertIn("host_permissions", rules, "rules must require separate host_permissions")
        self.assertIn("inline", rules, "rules must ban inline scripts/handlers")
        lifecycle = (refs / "service-worker-lifecycle.md").read_text(encoding="utf-8").lower()
        self.assertIn("chrome.storage.session", lifecycle, "lifecycle doc must cover chrome.storage.session")
        self.assertIn("alarms", lifecycle, "lifecycle doc must mandate chrome.alarms over setInterval")
        self.assertIn("onmessage", lifecycle, "lifecycle doc must cover message passing")

    def test_mv3_lint_accepts_valid_mv3_manifest(self):
        manifest = {
            "manifest_version": 3,
            "name": "Valid MV3 Extension",
            "version": "1.0.0",
            "action": {"default_popup": "popup.html"},
            "background": {"service_worker": "sw.js"},
            "permissions": ["storage", "alarms"],
            "host_permissions": ["https://api.example.com/*"],
            "content_security_policy": {"extension_pages": "script-src 'self'; object-src 'self'"},
            "web_accessible_resources": [{"resources": ["icon.png"], "matches": ["https://example.com/*"]}],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_extension(root, manifest, {
                "sw.js": "chrome.runtime.onInstalled.addListener(() => {});",
                "popup.html": "<!DOCTYPE html><html><body><script src=\"popup.js\"></script></body></html>",
                "popup.js": "console.log('ok');",
                "icon.png": "x",
            })
            res = self._run_linter(root)
            self.assertEqual(res.returncode, 0, f"valid MV3 manifest must pass, stderr: {res.stderr}")
            data = json.loads(res.stdout)
            self.assertEqual(data["verdict"], "MV3_COMPLIANT")
            self.assertEqual(data["errors"], 0)

    def test_mv3_lint_flags_mv2_antipatterns(self):
        manifest = {
            "manifest_version": 2,
            "name": "Legacy MV2 Extension",
            "version": "1.0.0",
            "browser_action": {"default_popup": "popup.html"},
            "background": {"scripts": ["bg.js"], "persistent": True},
            "permissions": ["<all_urls>", "tabs", "webRequestBlocking"],
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_extension(root, manifest, {
                "bg.js": "eval('alert(1)'); setInterval(() => {}, 1000);",
                "popup.html": "<!DOCTYPE html><html><body><button onclick=\"go()\">x</button>"
                              "<script>var x = 1;</script></body></html>",
            })
            res = self._run_linter(root)
            self.assertNotEqual(res.returncode, 0, "MV2 manifest must fail the linter")
            data = json.loads(res.stdout)
            self.assertEqual(data["verdict"], "NON_COMPLIANT")
            self.assertGreater(data["errors"], 0)
            report = json.dumps(data).lower()
            for marker in ("manifest_version", "browser_action", "service_worker",
                           "host_permissions", "eval", "content_security_policy"):
                self.assertIn(marker, report, f"lint report must flag {marker}")

    def test_registered_in_index_and_attribution(self):
        index = (SKILLS / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("chrome-extension-mv3", index, "INDEX.md must register the skill")
        self.assertIn("chrome-extension-mv3/SKILL.md", index, "INDEX.md must link the SKILL.md")
        attr = (SKILLS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("chrome-extension-mv3", attr, "ATTRIBUTION.md must name the skill")
        self.assertIn("chrome-extensions-samples", attr, "ATTRIBUTION.md must pin chrome-extensions-samples")
        self.assertIn("modern-web-guidance", attr, "ATTRIBUTION.md must pin modern-web-guidance")
        self.assertIn("Apache-2.0", attr, "ATTRIBUTION.md must record the Apache-2.0 license")


if __name__ == "__main__":
    unittest.main()
