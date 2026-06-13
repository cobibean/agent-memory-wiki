#!/usr/bin/env python3
"""Lightweight repository validator for Agent Memory Wiki."""
from __future__ import annotations

import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "LICENSE",
    "skills/note-taking/obsidian/SKILL.md",
    "skills/note-taking/prepforreset/SKILL.md",
    "skills/note-taking/wikijanitor/SKILL.md",
    "templates/daily-log.md",
    "templates/session-log.md",
    "templates/janitor-report.md",
    "docs/installation.md",
    "docs/slash-command-setup.md",
    "docs/agent-copy-paste-prompt.md",
    "docs/security-and-secret-hygiene.md",
    "scripts/install-hermes.sh",
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*=\s*['\"]?(?!<|/absolute|value intentionally omitted|your-|example)[A-Za-z0-9_./+=:-]{16,}"),
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path} missing opening frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail(f"{path} missing closing frontmatter")
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith(" "):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
    return data


def main() -> int:
    for rel in REQUIRED:
        p = ROOT / rel
        if not p.exists():
            fail(f"missing required file: {rel}")

    for skill in (ROOT / "skills").glob("**/SKILL.md"):
        fm = parse_frontmatter(skill)
        for key in ["name", "description", "version", "author", "license"]:
            if not fm.get(key):
                fail(f"{skill} missing frontmatter key {key}")
        if len(fm["description"]) > 1024:
            fail(f"{skill} description too long")
        body = skill.read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()
        if not body:
            fail(f"{skill} has empty body")

    install = ROOT / "scripts/install-hermes.sh"
    mode = install.stat().st_mode
    if not (mode & stat.S_IXUSR):
        fail("scripts/install-hermes.sh must be executable")

    for p in ROOT.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                fail(f"possible secret-like value in {p.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in ["/prepforreset", "@cobi_bean", "Copy-paste prompt", "OBSIDIAN_VAULT_PATH"]:
        if needle not in readme:
            fail(f"README missing {needle}")

    print("OK: validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
