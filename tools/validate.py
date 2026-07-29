#!/usr/bin/env python3
"""Repository validator for Agent Memory Wiki."""
from __future__ import annotations

import re
import stat
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by setup, not CI
    raise SystemExit("PyYAML is required; run: python3 -m pip install -r requirements-dev.txt") from exc

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills" / "note-taking"
CANONICAL = SKILLS_ROOT / "obsidian-memory-wiki"
SKILL_NAMES = ("obsidian-memory-wiki", "obsidian", "prepforreset", "wikijanitor")
REQUIRED = (
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "VERSION",
    "requirements-dev.txt",
    "scripts/install-hermes.sh",
    "scripts/wiki-janitor-cron-wrapper.sh.example",
    ".github/workflows/validate.yml",
    "tests/test_integration.py",
    "examples/hermes-skill-config.yaml.example",
    "skills/note-taking/obsidian-memory-wiki/SKILL.md",
    "skills/note-taking/obsidian-memory-wiki/references/reset-multistore-handoff.md",
    "skills/note-taking/obsidian-memory-wiki/references/per-agent-vault-layout.md",
    "skills/note-taking/obsidian-memory-wiki/references/dedicated-vault-rollout.md",
    "skills/note-taking/obsidian-memory-wiki/templates/daily-log.md",
    "skills/note-taking/obsidian-memory-wiki/templates/session-log.md",
    "skills/note-taking/obsidian-memory-wiki/templates/janitor-report.md",
    "skills/note-taking/obsidian/SKILL.md",
    "skills/note-taking/prepforreset/SKILL.md",
    "skills/note-taking/wikijanitor/SKILL.md",
)

# Build high-risk prefixes in pieces so this source does not match its own scan.
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
    re.compile("gh" + r"[pousr]_[A-Za-z0-9]{30,}"),
    re.compile("github_" + r"pat_[A-Za-z0-9_]{20,}"),
    re.compile("sk" + r"-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile("A" + r"(?:KI|SI)A[0-9A-Z]{16}"),
    re.compile("xox" + r"[bcaprse]-[A-Za-z0-9-]{10,}"),
    re.compile("gl" + r"pat-[A-Za-z0-9_-]{20,}"),
    re.compile("hf" + r"_[A-Za-z0-9]{20,}"),
    re.compile(r"[0-9]{6,}" + r":[A-Za-z0-9_-]{30,}"),
    re.compile(r"Bearer\s+eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", re.I),
)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError("missing or malformed YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    body = text[match.end():].strip()
    if not body:
        raise ValueError("skill body is empty")
    return data, body


def scan_secret_text(text: str) -> list[str]:
    return [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]


def iter_public_text_files(root: Path):
    allowed = {".md", ".sh", ".py", ".txt", ".example", ".yaml", ".yml", ".json"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in {".git", ".venv", "__pycache__"} for part in relative.parts):
            continue
        if relative.parts[0] == "tools":
            continue
        if path.suffix in allowed or path.name in {"SECURITY.md", "CONTRIBUTING.md"}:
            yield path


def validate_repo(root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    version_path = root / "VERSION"
    bundle_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else ""
    if bundle_version != "2.0.0":
        errors.append("VERSION must contain exactly 2.0.0")

    for relative in REQUIRED:
        if not (root / relative).exists():
            errors.append(f"missing required path: {relative}")

    config_example = root / "examples/hermes-skill-config.yaml.example"
    if config_example.exists():
        try:
            example_data = yaml.safe_load(config_example.read_text(encoding="utf-8"))
            vault_value = example_data["skills"]["config"]["obsidian_memory_wiki"]["vault_path"]
            if not isinstance(vault_value, str) or not vault_value.startswith("/"):
                errors.append("examples/hermes-skill-config.yaml.example: vault_path must be an absolute placeholder")
        except (OSError, TypeError, KeyError, yaml.YAMLError) as exc:
            errors.append(f"examples/hermes-skill-config.yaml.example: invalid config shape ({exc})")

    skill_paths = sorted((root / "skills").glob("**/SKILL.md"))
    for skill_path in skill_paths:
        name = skill_path.parent.name
        try:
            frontmatter, body = parse_frontmatter(skill_path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f"{skill_path.relative_to(root)}: {exc}")
            continue
        if frontmatter.get("name") != name:
            errors.append(f"{skill_path.relative_to(root)}: name must equal directory name {name!r}")
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(f"{skill_path.relative_to(root)}: description must be a non-empty string <= 1024 chars")
        if frontmatter.get("version") != bundle_version:
            errors.append(f"{skill_path.relative_to(root)}: version must match VERSION ({bundle_version!r})")
        for field in ("author", "license"):
            value = frontmatter.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{skill_path.relative_to(root)}: {field} must be a non-empty string")
        if not body.strip():
            errors.append(f"{skill_path.relative_to(root)}: skill body must be non-empty")
        hermes = (frontmatter.get("metadata") or {}).get("hermes") if isinstance(frontmatter.get("metadata"), dict) else None
        if name == "obsidian-memory-wiki":
            config_entries = hermes.get("config") if isinstance(hermes, dict) else None
            if not isinstance(config_entries, list) or not any(
                isinstance(item, dict) and item.get("key") == "obsidian_memory_wiki.vault_path"
                for item in config_entries
            ):
                errors.append(f"{skill_path.relative_to(root)}: must declare obsidian_memory_wiki.vault_path config metadata")
        if not isinstance(hermes, dict) or not isinstance(hermes.get("tags"), list):
            errors.append(f"{skill_path.relative_to(root)}: metadata.hermes.tags must be a list")

    canonical_text = (root / "skills/note-taking/obsidian-memory-wiki/SKILL.md").read_text(encoding="utf-8") if (root / "skills/note-taking/obsidian-memory-wiki/SKILL.md").exists() else ""
    for required_phrase in (
        "[[WIKI_JANITOR_NOTIFY]]",
        "[[WIKI_JANITOR_END]]",
        "[[WIKI_JANITOR_SILENT]]",
        "references/per-agent-vault-layout.md",
        "references/dedicated-vault-rollout.md",
        "templates/daily-log.md",
        "templates/session-log.md",
        "templates/janitor-report.md",
    ):
        if required_phrase not in canonical_text:
            errors.append(f"canonical skill missing required contract/reference: {required_phrase}")

    session_template = root / "skills/note-taking/obsidian-memory-wiki/templates/session-log.md"
    if session_template.exists():
        session_text = session_template.read_text(encoding="utf-8")
        for heading in ("## Current status", "## Commands, tests, and outcomes", "## Verification", "## Blockers and cautions", "## Next actions"):
            if heading not in session_text:
                errors.append(f"session template missing required heading: {heading}")

    for script in (root / "scripts/install-hermes.sh", root / "scripts/wiki-janitor-cron-wrapper.sh.example"):
        if script.exists() and not (script.stat().st_mode & stat.S_IXUSR):
            errors.append(f"not executable: {script.relative_to(root)}")

    for path in root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(root)}: link escapes repository: {target}")
                continue
            if not candidate.exists():
                errors.append(f"{path.relative_to(root)}: broken relative link: {target}")

    for path in iter_public_text_files(root):
        matches = scan_secret_text(path.read_text(encoding="utf-8", errors="replace"))
        if matches:
            errors.append(f"possible secret pattern in {path.relative_to(root)}: {matches[0]}")

    return errors


def main() -> int:
    errors = validate_repo()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
