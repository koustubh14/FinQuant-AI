"""Conservative source credential scan; prints paths only, never matched values."""

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
skip = {
    ".git",
    ".venv",
    ".cache",
    "node_modules",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
patterns = [
    re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{30,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
findings = []
for path in root.rglob("*"):
    if (
        not path.is_file()
        or any(p in skip for p in path.relative_to(root).parts)
        or path.relative_to(root).parts[0] == "data"
    ):
        continue
    if path.name == ".env":
        continue  # Local credentials are intentionally not read or printed.
    if path.suffix.lower() not in {
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".json",
        ".toml",
        ".yml",
        ".yaml",
        ".md",
        ".txt",
        ".html",
    }:
        continue
    content = path.read_text(encoding="utf-8", errors="replace")
    if any(p.search(content) for p in patterns):
        findings.append(str(path.relative_to(root)))
print(
    json.dumps(
        {
            "status": "pass" if not findings else "review",
            "files_with_possible_secrets": findings,
            "scope": "Active text source, docs and manifests; excludes local env, dependencies, data and Git history.",
        }
    )
)
raise SystemExit(bool(findings))
