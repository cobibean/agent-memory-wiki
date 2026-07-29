from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-hermes.sh"
WRAPPER = ROOT / "scripts" / "wiki-janitor-cron-wrapper.sh.example"


def run(command: list[str], *, env: dict[str, str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout, check=False)


class InstallerTests(unittest.TestCase):
    def base_env(self, home: Path) -> dict[str, str]:
        fake = home / "fake-hermes"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "if args[:2] != ['config', 'set']:\n"
            "    raise SystemExit(2)\n"
            "key, value = args[-2], args[-1]\n"
            "path = pathlib.Path(os.environ['HERMES_HOME']) / 'config.yaml'\n"
            "data = json.loads(path.read_text()) if path.exists() else {}\n"
            "data = data or {}\n"
            "node = data\n"
            "parts = key.split('.')\n"
            "for part in parts[:-1]:\n"
            "    node = node.setdefault(part, {})\n"
            "node[parts[-1]] = value\n"
            "path.parent.mkdir(parents=True, exist_ok=True)\n"
            "path.write_text(json.dumps(data, indent=2) + '\\n')\n"
        )
        fake.chmod(0o755)
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["HERMES_BIN"] = str(fake)
        env.pop("HERMES_HOME", None)
        return env

    def test_clean_install_init_spaces_and_idempotent_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amw installer ") as raw:
            scratch = Path(raw)
            home = scratch / "user home"
            hermes_home = scratch / "Hermes Home"
            vault = scratch / "Vault With Spaces"
            home.mkdir()
            env = self.base_env(home)
            command = ["bash", str(INSTALLER), "--hermes-home", str(hermes_home), "--vault", str(vault), "--init-vault"]

            first = run(command, env=env)
            self.assertEqual(first.returncode, 0, first.stderr)
            for skill in ("obsidian-memory-wiki", "obsidian", "prepforreset", "wikijanitor"):
                self.assertTrue((hermes_home / "skills/note-taking" / skill / "SKILL.md").is_file())
            for expected in (
                "Home.md",
                "Vault Guide.md",
                "Daily Logs",
                "Session Logs",
                "Janitor Reports",
                "Templates/daily-log.md",
                ".obsidian/templates.json",
                ".obsidian/daily-notes.json",
            ):
                self.assertTrue((vault / expected).exists(), expected)
            config = yaml.safe_load((hermes_home / "config.yaml").read_text())
            self.assertEqual(config["skills"]["config"]["obsidian_memory_wiki"]["vault_path"], str(vault.resolve()))
            self.assertEqual((hermes_home / "config.yaml").stat().st_mode & 0o777, 0o600)

            stale = hermes_home / "skills/note-taking/obsidian-memory-wiki/stale.txt"
            stale.write_text("remove me")
            second = run(command, env=env)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertFalse(stale.exists())
            config = yaml.safe_load((hermes_home / "config.yaml").read_text())
            self.assertEqual(config["skills"]["config"]["obsidian_memory_wiki"]["vault_path"], str(vault.resolve()))
            backups = list(hermes_home.glob("agent-memory-wiki.backup.*"))
            self.assertGreaterEqual(len(backups), 2)
            self.assertEqual(len(backups), len({path.name for path in backups}))

    def test_profile_overrides_inherited_hermes_home(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amw-profile-") as raw:
            scratch = Path(raw)
            home = scratch / "home"
            home.mkdir()
            ambient = scratch / "wrong-home"
            vault = scratch / "vault"
            vault.mkdir()
            env = self.base_env(home)
            env["HERMES_HOME"] = str(ambient)
            result = run(["bash", str(INSTALLER), "--profile", "alpha", "--vault", str(vault)], env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            intended = home / ".hermes/profiles/alpha/skills/note-taking/obsidian-memory-wiki/SKILL.md"
            self.assertTrue(intended.is_file())
            self.assertFalse(ambient.exists())

    def test_config_update_preserves_values_backslashes_and_hardens_modes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amw-config-") as raw:
            scratch = Path(raw)
            home = scratch / "home"
            home.mkdir()
            target = scratch / "target"
            target.mkdir()
            vault = scratch / "vault\\segment#1"
            vault.mkdir()
            (target / "config.yaml").write_text('{"keep": 1, "skills": {"config": {"obsidian_memory_wiki": {"vault_path": "/old"}}}}\n')
            (target / "config.yaml").chmod(0o644)
            env = self.base_env(home)
            result = run(["bash", str(INSTALLER), "--hermes-home", str(target), "--vault", str(vault)], env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            config = yaml.safe_load((target / "config.yaml").read_text())
            self.assertEqual(config["keep"], 1)
            self.assertEqual(config["skills"]["config"]["obsidian_memory_wiki"]["vault_path"], str(vault.resolve()))
            self.assertEqual((target / "config.yaml").stat().st_mode & 0o777, 0o600)
            backup = next(target.glob("agent-memory-wiki.backup.*/profile-config.yaml"))
            self.assertEqual(backup.stat().st_mode & 0o777, 0o600)

    def test_invalid_profile_and_missing_vault_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amw-invalid-") as raw:
            scratch = Path(raw)
            home = scratch / "home"
            home.mkdir()
            env = self.base_env(home)
            bad = run(["bash", str(INSTALLER), "--profile", "../../escape", "--vault", str(scratch / "vault"), "--init-vault"], env=env)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("Invalid profile name", bad.stderr)
            missing = run(["bash", str(INSTALLER), "--vault", str(scratch / "missing")], env=env)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("Vault does not exist", missing.stderr)
            unsafe = run(["bash", str(INSTALLER), "--hermes-home", "/", "--vault", str(scratch), "--dry-run"], env=env)
            self.assertNotEqual(unsafe.returncode, 0)
            self.assertIn("unsafe Hermes home", unsafe.stderr)
            expanded = run(["bash", str(INSTALLER), "--hermes-home", str(scratch / "target"), "--vault", str(scratch / 'literal-${HOME}'), "--init-vault"], env=env)
            self.assertNotEqual(expanded.returncode, 0)
            self.assertIn("literal ${...}", expanded.stderr)

    def test_no_aliases_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="amw-options-") as raw:
            scratch = Path(raw)
            home = scratch / "home"
            home.mkdir()
            vault = scratch / "vault"
            vault.mkdir()
            target = scratch / "target"
            env = self.base_env(home)
            dry = run(["bash", str(INSTALLER), "--hermes-home", str(target), "--vault", str(vault), "--dry-run"], env=env)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertFalse(target.exists())
            installed = run(["bash", str(INSTALLER), "--hermes-home", str(target), "--vault", str(vault), "--no-aliases"], env=env)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertTrue((target / "skills/note-taking/obsidian-memory-wiki/SKILL.md").is_file())
            self.assertFalse((target / "skills/note-taking/prepforreset").exists())
            with_aliases = run(["bash", str(INSTALLER), "--hermes-home", str(target), "--vault", str(vault)], env=env)
            self.assertEqual(with_aliases.returncode, 0, with_aliases.stderr)
            self.assertTrue((target / "skills/note-taking/prepforreset").exists())
            removed = run(["bash", str(INSTALLER), "--hermes-home", str(target), "--vault", str(vault), "--no-aliases"], env=env)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse((target / "skills/note-taking/prepforreset").exists())


class WrapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="amw-wrapper-")
        self.scratch = Path(self.temp.name)
        self.vault = self.scratch / "vault"
        self.vault.mkdir()
        self.fake = self.scratch / "fake-hermes"
        self.args_file = self.scratch / "args.txt"
        self.fake.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$@\" > \"$FAKE_ARGS_FILE\"\n"
            "if [[ \" $* \" == *' config get '* ]]; then\n"
            "  for last; do :; done\n"
            "  case \"$last\" in\n"
            "    *.vault_path) printf '%s\\n' \"$FAKE_CONFIG_VAULT\" ;;\n"
            "    *.janitor_timeout_seconds) printf '%s\\n' '5' ;;\n"
            "    *.janitor_max_turns) printf '%s\\n' '100' ;;\n"
            "  esac\n"
            "  exit 0\n"
            "fi\n"
            "case \"${FAKE_MODE:-notify}\" in\n"
            "  notify) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' 'Updated Daily Logs safely.' '[[WIKI_JANITOR_END]]'; exit 7 ;;\n"
            "  silent) printf '%s\\n' '[[WIKI_JANITOR_SILENT]]'; exit 0 ;;\n"
            "  routine) printf '%s\\n' '[[WIKI_JANITOR_SILENT]]'; exit 0 ;;\n"
            "  unmarked) printf '%s\\n' 'TOP_SECRET_SHOULD_NOT_LEAK'; exit 0 ;;\n"
            "  malformed) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' 'unsafe partial'; exit 0 ;;\n"
            "  reversed) printf '%s\\n' '[[WIKI_JANITOR_END]]' '[[WIKI_JANITOR_NOTIFY]]' 'unsafe reversed'; exit 0 ;;\n"
            "  mixed) printf '%s\\n' '[[WIKI_JANITOR_SILENT]]' '[[WIKI_JANITOR_NOTIFY]]' 'unsafe mixed' '[[WIKI_JANITOR_END]]'; exit 0 ;;\n"
            "  secret) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' \"ghp_$(printf 'A%.0s' {1..36})\" '[[WIKI_JANITOR_END]]'; exit 0 ;;\n"
            "  slack) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' \"$(printf 'xox%s' 'b-1234567890-abcdefghijklmnop')\" '[[WIKI_JANITOR_END]]'; exit 0 ;;\n"
            "  telegram) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' \"$(printf '%s:%s' '123456789' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghi')\" '[[WIKI_JANITOR_END]]'; exit 0 ;;\n"
            "  modern) printf '%s\\n' '[[WIKI_JANITOR_NOTIFY]]' \"$(printf 'github_%s_%s' 'pat' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')\" \"$(printf 'xox%s' 'c-1234567890-abcdefghijklmnop')\" \"$(printf 'AS%s' 'IAABCDEFGHIJKLMNOP')\" '[[WIKI_JANITOR_END]]'; exit 0 ;;\n"
            "  sleep) sleep 30 & child=$!; printf '%s' \"$child\" > \"$FAKE_CHILD_PID_FILE\"; wait ;;\n"
            "esac\n"
        )
        self.fake.chmod(0o755)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def env(self, mode: str) -> dict[str, str]:
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(self.scratch / "home"),
                "HERMES_BIN": str(self.fake),
                "HERMES_PROFILE": "test-profile",
                "OBSIDIAN_VAULT_PATH": str(self.vault),
                "WIKI_JANITOR_LOCK_ROOT": str(self.scratch / "locks"),
                "WIKI_JANITOR_TIMEOUT_SECONDS": "5",
                "WIKI_JANITOR_MAX_TURNS": "100",
                "FAKE_MODE": mode,
                "FAKE_ARGS_FILE": str(self.args_file),
                "FAKE_CONFIG_VAULT": str(self.vault),
            }
        )
        return env

    def test_marked_digest_wins_even_when_hermes_exits_nonzero(self) -> None:
        result = run(["bash", str(WRAPPER)], env=self.env("notify"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Memory-wiki janitor completed with review-worthy findings. Open the newest Janitor Report in the configured vault.")
        args = self.args_file.read_text().splitlines()
        self.assertIn("-p", args)
        self.assertIn("test-profile", args)
        self.assertIn("--skills", args)
        self.assertIn("obsidian-memory-wiki", args)
        self.assertLess(args.index("chat"), args.index("--max-turns"))

    def test_silent_output_is_suppressed(self) -> None:
        for mode in ("silent", "routine"):
            with self.subTest(mode=mode):
                result = run(["bash", str(WRAPPER)], env=self.env(mode))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_profile_skill_config_is_used_without_environment_overrides(self) -> None:
        env = self.env("notify")
        env.pop("OBSIDIAN_VAULT_PATH")
        env.pop("WIKI_JANITOR_TIMEOUT_SECONDS")
        env.pop("WIKI_JANITOR_MAX_TURNS")
        result = run(["bash", str(WRAPPER)], env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Memory-wiki janitor completed with review-worthy findings. Open the newest Janitor Report in the configured vault.")

    def test_profile_is_derived_from_named_hermes_home(self) -> None:
        env = self.env("notify")
        env.pop("HERMES_PROFILE")
        env["HERMES_HOME"] = str(self.scratch / "profiles/derived-profile")
        result = run(["bash", str(WRAPPER)], env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.args_file.read_text().splitlines()
        self.assertIn("derived-profile", args)

    def test_unmarked_and_partial_output_never_leak(self) -> None:
        for mode in ("unmarked", "malformed", "reversed", "mixed"):
            with self.subTest(mode=mode):
                result = run(["bash", str(WRAPPER)], env=self.env(mode))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("suppressed", result.stdout)
                combined = result.stdout + result.stderr
                for forbidden in ("TOP_SECRET", "unsafe partial", "unsafe reversed", "unsafe mixed"):
                    self.assertNotIn(forbidden, combined)

    def test_valid_notify_envelopes_never_forward_model_text(self) -> None:
        expected = "Memory-wiki janitor completed with review-worthy findings. Open the newest Janitor Report in the configured vault."
        for mode in ("notify", "secret", "slack", "telegram", "modern"):
            with self.subTest(mode=mode):
                result = run(["bash", str(WRAPPER)], env=self.env(mode))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), expected)
                for forbidden in ("Updated Daily Logs", "ghp_", "xox" + "b-", "xox" + "c-", "github_" + "pat_", "123456789" + ":", "AS" + "IA"):
                    self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_installed_hermes_parser_supports_chat_max_turns(self) -> None:
        hermes = shutil.which("hermes")
        if not hermes:
            self.skipTest("Hermes CLI is not installed in this test environment")
        result = run([hermes, "-p", "default", "chat", "--max-turns", "1", "--skills", "obsidian-memory-wiki", "--help"], env=os.environ.copy())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--max-turns", result.stdout)

    def test_timeout_and_lock_contention(self) -> None:
        env = self.env("sleep")
        env["WIKI_JANITOR_TIMEOUT_SECONDS"] = "1"
        child_pid_file = self.scratch / "child.pid"
        env["FAKE_CHILD_PID_FILE"] = str(child_pid_file)
        timed = run(["bash", str(WRAPPER)], env=env, timeout=10)
        self.assertNotEqual(timed.returncode, 0)
        self.assertIn("exceeded 1 seconds", timed.stdout)
        child_pid = int(child_pid_file.read_text())
        for _ in range(20):
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail(f"timeout left descendant process {child_pid} alive")

        lock = self.scratch / "locks/agent-memory-wiki-test-profile.lock"
        lock.mkdir(parents=True, exist_ok=True)
        locked = run(["bash", str(WRAPPER)], env=self.env("notify"))
        self.assertEqual(locked.returncode, 0)
        self.assertIn("already active", locked.stdout)


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("amw_validate", ROOT / "tools/validate.py")
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def fixture_repo(self, root: Path) -> Path:
        repo = root / "repo"
        shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        return repo

    def test_common_secret_shapes_are_detected(self) -> None:
        samples = (
            "gh" + "p_" + "A" * 36,
            "sk" + "-proj-" + "A" * 30,
            "AK" + "IA" + "A" * 16,
            "AS" + "IA" + "A" * 16,
            "xox" + "b-1234567890-abcdefghijklmnop",
            "xox" + "c-1234567890-abcdefghijklmnop",
            "github_" + "pat_" + "A" * 30,
            "gl" + "pat-" + "A" * 30,
            "hf" + "_" + "A" * 30,
            "123456789" + ":ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghi",
            "Bearer " + "eyJabc.def.ghi",
            "-----BEGIN OPENSSH " + "PRIVATE KEY-----",
        )
        for sample in samples:
            with self.subTest(sample=sample[:12]):
                self.assertTrue(self.module.scan_secret_text(sample))

    def test_repository_validation(self) -> None:
        self.assertEqual(self.module.validate_repo(ROOT), [])

    def test_validator_rejects_missing_package_file(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            repo = self.fixture_repo(Path(scratch))
            (repo / "VERSION").unlink()
            self.assertTrue(any("missing required path: VERSION" in item for item in self.module.validate_repo(repo)))

    def test_validator_rejects_extra_malformed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            repo = self.fixture_repo(Path(scratch))
            skill = repo / "skills/extra/broken/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("not frontmatter\n")
            self.assertTrue(any("missing or malformed YAML frontmatter" in item for item in self.module.validate_repo(repo)))

    def test_validator_rejects_missing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            repo = self.fixture_repo(Path(scratch))
            skill = repo / "skills/note-taking/obsidian/SKILL.md"
            skill.write_text(skill.read_text().replace("author: Jacobi Lange (@cobi_bean)\n", ""))
            self.assertTrue(any("author must be a non-empty string" in item for item in self.module.validate_repo(repo)))

    def test_validator_rejects_broken_markdown_link(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            repo = self.fixture_repo(Path(scratch))
            readme = repo / "README.md"
            readme.write_text(readme.read_text() + "\n[broken](missing-local-file.md)\n")
            self.assertTrue(any("broken relative link" in item for item in self.module.validate_repo(repo)))


if __name__ == "__main__":
    unittest.main()
