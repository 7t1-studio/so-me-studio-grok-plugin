"""Regression checks for the package's portable manifest and MCP trust boundary."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_plugin.py"
SPEC = importlib.util.spec_from_file_location("validate_plugin", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.manifest = {"name": "test-plugin", "description": "A test plugin.", "version": "1.0.0",
                         "logo": "assets/logo.svg", "skills": "skills", "mcpServers": "mcp.json"}
        self.mcp = {"mcpServers": {"so-me-studio": {"url": validator.ENDPOINT, "headers": {"X-MCP-Auth-Mode": "oauth"}}}}
        self.write(".cursor-plugin/plugin.json", json.dumps(self.manifest))
        self.write("mcp.json", json.dumps(self.mcp))
        self.write("assets/logo.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.write("README.md", "Test package")
        self.write("LICENSE", "Test fixture only")
        self.write("scripts/helper.py", "pass\n")
        self.write("skills/posting/SKILL.md", "---\nname: posting\ndescription: Help with posting.\n---\n"
                   "See [helper](../../scripts/helper.py) and [reference](reference.md).\n")
        self.write("skills/posting/reference.md", "See [docs](https://example.test/docs).\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_valid_package_and_internal_parent_links(self):
        self.assertEqual(validator.validate(self.root), {"name": "test-plugin", "skills": 1, "mcpServers": 1})

    def test_unknown_manifest_fields_and_bad_types_fail(self):
        for field, value in (("displayName", "Unsupported"), ("version", 1), ("author", "Person"),
                             ("skills", [123]), ("name", "Bad_Name")):
            with self.subTest(field=field):
                self.write(".cursor-plugin/plugin.json", json.dumps(dict(self.manifest, **{field: value})))
                with self.assertRaises(validator.ValidationError):
                    validator.validate(self.root)

    def test_manifest_paths_cannot_escape_on_either_os(self):
        for value in ("../logo.svg", "/tmp/logo.svg", "C:\\private\\logo.svg", "\\\\host\\share\\logo.svg",
                      "assets/../assets/logo.svg"):
            with self.subTest(value=value):
                self.write(".cursor-plugin/plugin.json", json.dumps(dict(self.manifest, logo=value)))
                with self.assertRaises(validator.ValidationError):
                    validator.validate(self.root)

    def test_missing_skill_links_and_nested_reference_links_fail(self):
        self.write("skills/posting/reference.md", "Missing [guide][guide].\n\n[guide]: missing.md\n")
        with self.assertRaisesRegex(validator.ValidationError, "does not exist"):
            validator.validate(self.root)

    def test_skill_links_cannot_leave_repository(self):
        self.write("skills/posting/reference.md", "[outside](../../../private.txt)\n")
        with self.assertRaisesRegex(validator.ValidationError, "leaves the plugin"):
            validator.validate(self.root)

    def test_skill_frontmatter_requires_named_string_fields(self):
        for frontmatter in ("name: posting", "name: Wrong_Name\ndescription: A task", "name: other\ndescription: A task",
                            "name: posting\ndescription: []", "name: posting\ndescription: true"):
            with self.subTest(frontmatter=frontmatter):
                self.write("skills/posting/SKILL.md", f"---\n{frontmatter}\n---\nHelp.\n")
                with self.assertRaises(validator.ValidationError):
                    validator.validate(self.root)

    def test_skill_block_description_is_valid(self):
        self.write("skills/posting/SKILL.md", "---\nname: posting\ndescription: >-\n  Help publish posts.\n"
                   "  Use when posting content.\n---\nHelp.\n")
        self.assertEqual(validator.validate(self.root)["skills"], 1)

    def test_mcp_rejects_different_endpoints_commands_and_secrets(self):
        variants = [
            {"url": "http://api.so-me.studio/mcp/posting"},
            {"url": validator.ENDPOINT + "?token=private"},
            {"url": "https://other.example.test/mcp"},
            {"url": validator.ENDPOINT, "headers": {"Authorization": "Bearer private"}},
            {"url": validator.ENDPOINT, "command": "python"},
            {"url": validator.ENDPOINT, "env": {"TOKEN": "private"}},
            {"url": validator.ENDPOINT, "type": "stdio"},
        ]
        for server in variants:
            with self.subTest(keys=list(server)):
                self.write("mcp.json", json.dumps({"mcpServers": {"so-me-studio": server}}))
                with self.assertRaises(validator.ValidationError):
                    validator.validate(self.root)

    def test_mcp_rejects_an_additional_server(self):
        self.mcp["mcpServers"]["unexpected"] = {"url": "https://other.example.test/mcp"}
        self.write("mcp.json", json.dumps(self.mcp))
        with self.assertRaisesRegex(validator.ValidationError, "exactly one MCP server"):
            validator.validate(self.root)

    def test_mcp_requires_only_the_public_oauth_mode_header(self):
        for headers in (None, {}, {"X-MCP-Auth-Mode": "anonymous"},
                        {"X-MCP-Auth-Mode": "oauth", "Authorization": "Bearer private"},
                        {"X-MCP-Auth-Mode": "oauth", "X-API-Key": "private"}):
            with self.subTest(headers=headers):
                self.write("mcp.json", json.dumps({"mcpServers": {"so-me-studio": {
                    "url": validator.ENDPOINT, "headers": headers,
                }}}))
                with self.assertRaisesRegex(validator.ValidationError, "non-secret OAuth"):
                    validator.validate(self.root)

    def test_symlink_escape_is_rejected_where_supported(self):
        with tempfile.TemporaryDirectory() as outside:
            destination = Path(outside) / "outside.svg"
            destination.write_text("private", encoding="utf-8")
            link = self.root / "assets" / "outside.svg"
            try:
                link.symlink_to(destination)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable for this user/OS")
            self.write(".cursor-plugin/plugin.json", json.dumps(dict(self.manifest, logo="assets/outside.svg")))
            with self.assertRaisesRegex(validator.ValidationError, "leaves the plugin"):
                validator.validate(self.root)


if __name__ == "__main__":
    unittest.main()
