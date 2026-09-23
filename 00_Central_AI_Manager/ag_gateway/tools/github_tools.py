import os
from pathlib import Path
from typing import List, Dict, Any

# Placeholder for GitHub interactions. In a real system, you'd use PyGitHub or GitHub REST API.
# For now we simulate basic operations using the local filesystem assuming the repository
# is checked out under the project root.

REPO_ROOT = Path(__file__).resolve().parents[2] / "repository"

def _ensure_repo_root():
    if not REPO_ROOT.is_dir():
        raise FileNotFoundError(f"Repository root not found at {REPO_ROOT}. Please clone the repo here.")

def list_files(path: str = "") -> List[str]:
    """List files under the repository (relative to REPO_ROOT)."""
    _ensure_repo_root()
    target = REPO_ROOT / path
    if not target.exists():
        raise FileNotFoundError(f"Path {path} does not exist in repository.")
    return [str(p.relative_to(REPO_ROOT)) for p in target.rglob("*") if p.is_file()]

def read_file(file_path: str) -> str:
    """Read content of a file in the repository."""
    _ensure_repo_root()
    target = REPO_ROOT / file_path
    if not target.is_file():
        raise FileNotFoundError(f"File {file_path} not found in repository.")
    return target.read_text(encoding="utf-8")

def analyze_code(file_path: str) -> Dict[str, Any]:
    """Very lightweight code analysis.

    Returns line count, size, and a mock list of "issues" (e.g., TODO comments).
    """
    content = read_file(file_path)
    lines = content.splitlines()
    issues = [
        {"line": i + 1, "type": "TODO", "text": line.strip()}
        for i, line in enumerate(lines)
        if "TODO" in line
    ]
    return {
        "file": file_path,
        "line_count": len(lines),
        "size_bytes": len(content.encode("utf-8")),
        "issues": issues,
    }

def generate_patch(file_path: str, new_content: str) -> Dict[str, str]:
    """Generate a diff between the current file and the provided new content.

    For simplicity we use the built‑in difflib to produce a unified diff string.
    """
    import difflib

    old_content = read_file(file_path)
    diff = "\n".join(
        difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )
    return {"file": file_path, "diff": diff}
