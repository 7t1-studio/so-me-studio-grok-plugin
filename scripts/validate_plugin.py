#!/usr/bin/env python3
"""Validate this repository's Cursor plugin package without network access.

Manifest field types follow https://cursor.com/docs/reference/plugins (2026-09-11).
The MCP checks intentionally enforce this package's OAuth-only remote-server
profile; they are narrower than Cursor's general MCP format. This is a local
packaging check, not a substitute for loading the plugin in Cursor/Grok Bot.
"""

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys
from urllib.parse import unquote, urlsplit


ENDPOINT = "https://api.so-me.studio/mcp/posting"
FIELD_TYPES = {
    "name": (str,), "description": (str,), "version": (str,),
    "author": (dict,), "homepage": (str,), "repository": (str,),
    "license": (str,), "keywords": (list,), "logo": (str,),
    "rules": (str, list), "agents": (str, list), "skills": (str, list),
    "commands": (str, list), "hooks": (str, dict),
    "mcpServers": (str, dict, list), "variables": (dict,),
}
PLUGIN_NAME = re.compile(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\Z")
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SEMVER = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z"
)


class ValidationError(ValueError):
    """An actionable package validation failure."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise ValidationError(f"Cannot read valid JSON: {path.name}") from error


def local_path(root, value, *, base=None, manifest=True):
    """Reject absolute paths on either OS and resolve symlinks before containment."""
    require(isinstance(value, str) and bool(value.strip()), "Expected a nonempty local path")
    normalized = value.replace("\\", "/")
    windows_path = PureWindowsPath(value)
    posix_path = PurePosixPath(normalized)
    require(not windows_path.drive and not windows_path.root and not posix_path.is_absolute(),
            f"Path must be relative: {value}")
    require(not urlsplit(normalized).scheme, f"Expected a local path: {value}")
    if manifest:
        require(".." not in posix_path.parts, f"Manifest path cannot contain '..': {value}")
    resolved = ((base or root) / normalized).resolve()
    require(resolved.is_relative_to(root), f"Path leaves the plugin repository: {value}")
    require(resolved.exists(), f"Referenced path does not exist: {value}")
    return resolved


def scalar_frontmatter(text, field):
    """Read required string fields, supporting plain, quoted and block scalars.

    No YAML is executed. Complex YAML values are rejected for these string fields.
    Other frontmatter fields are left to the host's complete YAML parser.
    """
    lines = text.splitlines()
    require(bool(lines) and lines[0] == "---", "SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValidationError("SKILL.md has unclosed YAML frontmatter") from error
    matches = [(index, line.split(":", 1)[1].strip()) for index, line in enumerate(lines[1:end], 1)
               if re.match(rf"^{re.escape(field)}\s*:", line)]
    require(len(matches) == 1, f"SKILL.md requires one {field} field")
    index, value = matches[0]
    if value in {">", ">-", ">+", "|", "|-", "|+"}:
        continuation = []
        for line in lines[index + 1:end]:
            if line and not line[0].isspace():
                break
            continuation.append(line.strip())
        value = " ".join(continuation).strip()
    elif value.startswith('"'):
        try:
            value = json.loads(value)
        except ValueError as error:
            raise ValidationError(f"Invalid quoted {field} string") from error
    elif value.startswith("'"):
        require(value.endswith("'") and len(value) >= 2, f"Invalid quoted {field} string")
        value = value[1:-1].replace("''", "'")
    else:
        require(not value.startswith(("[", "{", "&", "*", "!")) and
                value.lower() not in {"null", "~", "true", "false"} and
                not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value),
                f"SKILL.md {field} must be a string")
        value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    require(isinstance(value, str) and bool(value.strip()), f"SKILL.md {field} must be a nonempty string")
    return value


def validate_markdown_links(root, path, seen=None):
    """Check inline and reference-style local links, including linked Markdown."""
    seen = set() if seen is None else seen
    if path in seen:
        return
    seen.add(path)
    text = path.read_text(encoding="utf-8-sig")
    # Fenced examples are not document links.
    text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", "", text)
    targets = re.findall(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)", text)
    targets += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text)
    for target in targets:
        target = target.removeprefix("<").removesuffix(">")
        if target.startswith("#"):
            continue
        parsed = urlsplit(target)
        if parsed.scheme in {"https", "http", "mailto"}:
            continue
        require(not parsed.scheme and not parsed.netloc, f"Unsupported link scheme in {path.name}")
        linked = local_path(root, unquote(parsed.path), base=path.parent, manifest=False)
        if linked.is_file() and linked.suffix.lower() in {".md", ".markdown"}:
            validate_markdown_links(root, linked, seen)


def validate_mcp(config):
    require(isinstance(config, dict) and set(config) == {"mcpServers"},
            "MCP config must contain only mcpServers")
    servers = config["mcpServers"]
    require(isinstance(servers, dict) and len(servers) == 1,
            "This plugin must declare exactly one MCP server")
    name, server = next(iter(servers.items()))
    require(isinstance(name, str) and bool(name), "MCP server name must be nonempty")
    require(isinstance(server, dict), "MCP server config must be an object")
    require(set(server) <= {"url", "type"},
            "MCP server must not bundle headers, credentials, environment variables or commands")
    require(server.get("url") == ENDPOINT, "MCP server must use the approved So-me Studio posting endpoint")
    require(server.get("type", "http") == "http", "MCP server transport must be HTTP")


def validate(root):
    root = Path(root).resolve()
    manifest_path = local_path(root, ".cursor-plugin/plugin.json")
    manifest = read_json(manifest_path)
    require(isinstance(manifest, dict), "Plugin manifest must be a JSON object")
    require(set(manifest) <= set(FIELD_TYPES),
            "Undocumented Cursor manifest fields: " + ", ".join(sorted(set(manifest) - set(FIELD_TYPES))))
    for field, value in manifest.items():
        require(isinstance(value, FIELD_TYPES[field]), f"Wrong type for manifest field: {field}")
    require(bool(PLUGIN_NAME.fullmatch(manifest.get("name", ""))), "Plugin name must be lowercase kebab-case")
    require(bool(manifest.get("description", "").strip()), "Submission requires a nonempty description")
    if "version" in manifest:
        require(bool(SEMVER.fullmatch(manifest["version"])), "Plugin version must be semantic versioning")
    if "author" in manifest:
        author = manifest["author"]
        require(set(author) <= {"name", "email"} and isinstance(author.get("name"), str)
                and bool(author["name"].strip()), "Author requires name and may include email")
        require(all(isinstance(value, str) for value in author.values()), "Author values must be strings")
    if "keywords" in manifest:
        require(all(isinstance(value, str) and value for value in manifest["keywords"]),
                "Keywords must be nonempty strings")
    for field in ("homepage", "repository"):
        if field in manifest:
            url = urlsplit(manifest[field])
            require(url.scheme == "https" and bool(url.hostname) and not url.username and not url.password,
                    f"{field} must be a public HTTPS URL without credentials")
    if "logo" in manifest:
        require(local_path(root, manifest["logo"]).is_file(), "Logo must be a committed local file")
    for field in ("rules", "agents", "skills", "commands"):
        if field in manifest:
            values = manifest[field] if isinstance(manifest[field], list) else [manifest[field]]
            require(bool(values), f"{field} cannot be an empty path array")
            for value in values:
                local_path(root, value)
    if "hooks" in manifest:
        require(isinstance(manifest["hooks"], str), "This package does not permit inline executable hooks")
        local_path(root, manifest["hooks"])
    require("variables" not in manifest, "This OAuth-only package must not bundle token configuration")

    mcp_source = manifest.get("mcpServers", "mcp.json")
    sources = mcp_source if isinstance(mcp_source, list) else [mcp_source]
    require(len(sources) == 1, "This plugin must have exactly one MCP configuration")
    source = sources[0]
    if isinstance(source, str):
        validate_mcp(read_json(local_path(root, source)))
    else:
        validate_mcp(source)
    # Keep default discovery safe even if a manifest explicitly overrides it.
    if (root / "mcp.json").exists():
        validate_mcp(read_json(local_path(root, "mcp.json")))

    skill_sources = manifest.get("skills", "skills")
    skill_sources = skill_sources if isinstance(skill_sources, list) else [skill_sources]
    skills = set()
    for source in skill_sources:
        directory = local_path(root, source)
        require(directory.is_dir(), "Skill paths must point to directories")
        for path in directory.rglob("SKILL.md"):
            skills.add(local_path(root, str(path.relative_to(root))))
    require(bool(skills), "Plugin must include at least one SKILL.md")
    for path in sorted(skills):
        text = path.read_text(encoding="utf-8-sig")
        name = scalar_frontmatter(text, "name")
        require(bool(SKILL_NAME.fullmatch(name)), "Skill name must be lowercase kebab-case")
        require(name == path.parent.name, "Skill name must match its directory")
        scalar_frontmatter(text, "description")
        validate_markdown_links(root, path)
    for required in ("README.md", "LICENSE"):
        require(local_path(root, required).is_file(), f"Submission requires {required}")
    return {"name": manifest["name"], "skills": len(skills), "mcpServers": 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except (ValidationError, OSError, ValueError) as error:
        print(f"Plugin validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Plugin valid: {result['name']} ({result['skills']} skill(s), {result['mcpServers']} remote MCP server)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
