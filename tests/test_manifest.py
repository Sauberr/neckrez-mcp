"""Offline checks of the registry manifest and the docs: no network needed."""

import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class Manifest(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(read("server.json"))

    def test_required_fields(self):
        for key in ("$schema", "name", "description", "version", "repository", "remotes"):
            self.assertIn(key, self.doc)
        self.assertRegex(self.doc["name"], r"^io\.github\.[A-Za-z0-9-]+/[a-z0-9._-]+$")
        self.assertLessEqual(len(self.doc["description"]), 100)
        self.assertRegex(self.doc["version"], r"^\d+\.\d+\.\d+$")

    def test_remote_endpoints(self):
        """Two remotes: the OAuth sign-in endpoint (no header, the client signs in) and the API-key one."""
        remotes = {r["url"]: r for r in self.doc["remotes"]}
        self.assertEqual(set(remotes), {"https://neckrez.tech/mcp", "https://neckrez.tech/api/mcp"})
        for r in remotes.values():
            self.assertEqual(r["type"], "streamable-http")
        self.assertFalse(remotes["https://neckrez.tech/mcp"].get("headers"))
        auth = [h for h in remotes["https://neckrez.tech/api/mcp"].get("headers", []) if h["name"] == "Authorization"]
        self.assertTrue(auth and auth[0]["isSecret"] and auth[0]["isRequired"])

    def test_repository_matches_name(self):
        owner = self.doc["name"].split("/")[0].removeprefix("io.github.")
        self.assertEqual(self.doc["repository"]["url"].lower(), f"https://github.com/{owner}/neckrez-mcp".lower())

    def test_schema(self):
        """Validate against the official schema when jsonschema and the schema file are available (CI installs them)."""
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        path = os.environ.get("MCP_SERVER_SCHEMA")
        if not path or not os.path.exists(path):
            self.skipTest("MCP_SERVER_SCHEMA not set")
        with open(path, encoding="utf-8") as f:
            jsonschema.validate(self.doc, json.load(f))


class Docs(unittest.TestCase):
    def test_readme_uses_the_manifest_endpoint(self):
        readme = read("README.md")
        for r in json.loads(read("server.json"))["remotes"]:
            self.assertIn(r["url"], readme)
        url = "https://neckrez.tech/api/mcp"
        # every config snippet in the README points at the same endpoint
        for found in re.findall(r"https://[\w.-]+/api/mcp\b", readme):
            self.assertEqual(found, url)

    def test_readme_json_snippets_parse(self):
        blocks = re.findall(r"```json\n(.*?)```", read("README.md"), re.S)
        self.assertGreaterEqual(len(blocks), 3)
        for b in blocks:
            json.loads(b)

    def test_glama_maintainer(self):
        self.assertIn("Sauberr", json.loads(read("glama.json"))["maintainers"])


if __name__ == "__main__":
    unittest.main()
