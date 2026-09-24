# -*- coding: utf-8 -*-
"""
GitHub Development Agent
- 승인된 저장소만 접근 (허용 목록 화이트리스트)
- 격리된 작업 디렉터리 (/tmp/ag_workdir/)에서 작업
- 운영 서버 소스 직접 덮어쓰기 금지
- 테스트 미통과 시 배포 차단
- GITHUB_TOKEN은 서버 측 .env에만 저장
"""

import os
import json
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("github_agent")

WORKDIR_BASE = Path(tempfile.gettempdir()) / "ag_workdir"


class GitHubAgent:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        # Allowed repos from env (JSON array string) or empty list
        allowed_raw = os.getenv("GITHUB_ALLOWED_REPOS", "[]")
        try:
            self.allowed_repos: List[str] = json.loads(allowed_raw)
        except Exception:
            self.allowed_repos = []

    def _is_available(self) -> Tuple[bool, str]:
        if not self.token:
            return False, "GITHUB_TOKEN이 .env에 설정되지 않았습니다. 사용자가 토큰을 제공해야 합니다."
        if not self.allowed_repos:
            return False, "GITHUB_ALLOWED_REPOS가 설정되지 않았습니다. 허용 저장소를 .env에 추가하세요."
        return True, "OK"

    def _check_repo_allowed(self, repo: str) -> bool:
        """Check if repo is in whitelist. repo format: 'owner/reponame'"""
        return any(allowed.strip("/").endswith(repo.strip("/")) for allowed in self.allowed_repos)

    def _get_workdir(self, repo: str, branch: str) -> Path:
        safe_name = repo.replace("/", "_").replace(".", "_")
        return WORKDIR_BASE / f"{safe_name}_{branch}"

    async def checkout(self, repo: str, branch: str = "main") -> Dict[str, Any]:
        ok, msg = self._is_available()
        if not ok:
            return {"status": "ERROR", "message": msg}

        if not self._check_repo_allowed(repo):
            return {"status": "ERROR", "message": f"저장소 '{repo}'는 허용 목록에 없습니다."}

        workdir = self._get_workdir(repo, branch)

        try:
            if workdir.exists():
                shutil.rmtree(workdir)
            workdir.mkdir(parents=True, exist_ok=True)

            repo_url = f"https://{self.token}@github.com/{repo}.git"
            result = subprocess.run(
                ["git", "clone", "--depth=1", "--branch", branch, repo_url, str(workdir)],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                err = result.stderr.replace(self.token, "***")  # 토큰 비노출
                return {"status": "ERROR", "message": f"Clone 실패: {err[:300]}"}

            # Get latest commit info
            commit = subprocess.run(
                ["git", "log", "-1", "--format=%H %s"],
                capture_output=True, text=True, cwd=workdir
            ).stdout.strip()

            return {
                "status": "SUCCESS",
                "repo": repo,
                "branch": branch,
                "workdir": str(workdir),
                "latest_commit": commit
            }
        except subprocess.TimeoutExpired:
            return {"status": "ERROR", "message": "Git clone 시간 초과 (60초)"}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def search_files(self, repo: str, branch: str, pattern: str) -> Dict[str, Any]:
        workdir = self._get_workdir(repo, branch)
        if not workdir.exists():
            return {"status": "ERROR", "message": "먼저 checkout이 필요합니다."}

        matches = []
        for p in workdir.rglob(pattern):
            if ".git" not in str(p):
                matches.append(str(p.relative_to(workdir)))

        return {"status": "SUCCESS", "matches": matches[:50]}

    def read_file(self, repo: str, branch: str, filepath: str) -> Dict[str, Any]:
        workdir = self._get_workdir(repo, branch)
        target = workdir / filepath

        # Security: must stay within workdir
        try:
            target.resolve().relative_to(workdir.resolve())
        except ValueError:
            return {"status": "ERROR", "message": "디렉터리 경로 탈출 시도 감지됨."}

        if not target.exists():
            return {"status": "ERROR", "message": f"파일 없음: {filepath}"}

        try:
            content = target.read_text(encoding="utf-8", errors="replace")
            return {"status": "SUCCESS", "filepath": filepath, "content": content, "lines": len(content.splitlines())}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def apply_patch(self, repo: str, branch: str, filepath: str, original: str, replacement: str) -> Dict[str, Any]:
        workdir = self._get_workdir(repo, branch)
        target = workdir / filepath

        try:
            target.resolve().relative_to(workdir.resolve())
        except ValueError:
            return {"status": "ERROR", "message": "경로 탈출 시도 감지됨."}

        if not target.exists():
            return {"status": "ERROR", "message": f"파일 없음: {filepath}"}

        content = target.read_text(encoding="utf-8", errors="replace")
        if original not in content:
            return {"status": "ERROR", "message": "원본 코드를 파일에서 찾을 수 없습니다."}

        new_content = content.replace(original, replacement, 1)
        target.write_text(new_content, encoding="utf-8")

        # Static check (Python only)
        if filepath.endswith(".py"):
            check = subprocess.run(
                ["python3", "-m", "py_compile", str(target)],
                capture_output=True, text=True
            )
            if check.returncode != 0:
                target.write_text(content, encoding="utf-8")  # rollback
                return {"status": "ERROR", "message": f"문법 오류로 롤백됨: {check.stderr[:300]}"}

        # Generate diff
        diff = subprocess.run(
            ["git", "diff", filepath],
            capture_output=True, text=True, cwd=workdir
        ).stdout

        return {"status": "SUCCESS", "filepath": filepath, "diff": diff[:2000]}

    def run_tests(self, repo: str, branch: str) -> Dict[str, Any]:
        workdir = self._get_workdir(repo, branch)
        if not workdir.exists():
            return {"status": "ERROR", "message": "checkout 먼저 필요"}

        result = subprocess.run(
            ["python3", "-m", "pytest", "--tb=short", "-q"],
            capture_output=True, text=True, cwd=workdir, timeout=120
        )

        passed = result.returncode == 0
        return {
            "status": "SUCCESS" if passed else "FAILED",
            "passed": passed,
            "output": result.stdout[-2000:] + result.stderr[-500:],
            "message": "테스트 통과" if passed else "테스트 실패 — 배포 차단됨"
        }

    async def create_pr(self, repo: str, branch: str, pr_branch: str, title: str, body: str) -> Dict[str, Any]:
        ok, msg = self._is_available()
        if not ok:
            return {"status": "ERROR", "message": msg}

        if not self._check_repo_allowed(repo):
            return {"status": "ERROR", "message": "허용되지 않은 저장소"}

        workdir = self._get_workdir(repo, branch)

        try:
            # Create new branch
            subprocess.run(["git", "checkout", "-b", pr_branch], cwd=workdir, capture_output=True)
            subprocess.run(["git", "add", "-A"], cwd=workdir, capture_output=True)
            subprocess.run(["git", "commit", "-m", title], cwd=workdir, capture_output=True)

            # Push
            push = subprocess.run(
                ["git", "push", "origin", pr_branch],
                cwd=workdir, capture_output=True, text=True, timeout=30
            )
            if push.returncode != 0:
                return {"status": "ERROR", "message": push.stderr.replace(self.token, "***")[:300]}

            # Create PR via GitHub API
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(
                    f"https://api.github.com/repos/{repo}/pulls",
                    headers={"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"},
                    json={"title": title, "body": body, "head": pr_branch, "base": branch}
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    return {"status": "SUCCESS", "pr_url": data.get("html_url"), "pr_number": data.get("number")}
                return {"status": "ERROR", "message": resp.text[:300]}

        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    def cleanup_workdir(self, repo: str, branch: str):
        workdir = self._get_workdir(repo, branch)
        if workdir.exists():
            shutil.rmtree(workdir)

    def get_status(self) -> Dict[str, Any]:
        ok, msg = self._is_available()
        return {
            "available": ok,
            "message": msg if not ok else "GitHub 에이전트 준비됨",
            "allowed_repos": self.allowed_repos,
            "token_configured": bool(self.token)
        }


github_agent = GitHubAgent()
