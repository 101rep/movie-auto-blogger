import os
import ast
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from adapters.base import BaseProgramAdapter, ProgramStatus

# Root directory of the entire Antigravity project
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent

EXCLUDE_DIRS = {
    ".venv", "__pycache__", ".git", "node_modules", "browser_sessions",
    ".user_uploaded", ".system_generated", "GPUPersistentCache", "logs"
}

ALLOWED_EXTENSIONS = {
    ".py", ".html", ".css", ".js", ".json", ".md", ".txt", ".env", ".yaml", ".yml", ".bat", ".sh"
}

class CodeModifierAdapter(BaseProgramAdapter):
    """Safe remote code inspection and modification engine for Telegram AI Commander."""

    def __init__(self) -> None:
        self.backup_dir = WORKSPACE_ROOT / "00_Central_AI_Manager" / "data" / "code_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, file_path_str: str) -> Optional[Path]:
        """Resolve file path and ensure it stays within the workspace boundary."""
        clean_path = file_path_str.strip().replace("\\", "/")
        if clean_path.startswith("/"):
            clean_path = clean_path.lstrip("/")
        
        target = (WORKSPACE_ROOT / clean_path).resolve()
        try:
            target.relative_to(WORKSPACE_ROOT.resolve())
            return target
        except ValueError:
            return None

    @property
    def name(self) -> str:
        return "code_modifier"

    @property
    def description(self) -> str:
        return "원격 코드 AI 수정 및 안전 검증 엔진"

    async def get_status(self) -> ProgramStatus:
        from adapters.base import ProgramStatus
        return ProgramStatus(
            name=self.name,
            is_running=True,
            details={
                "workspace_root": str(WORKSPACE_ROOT),
                "backup_dir": str(self.backup_dir)
            }
        )

    async def health_check(self) -> bool:
        return True

    async def get_recent_logs(self, lines: int = 40) -> str:
        return "CodeModifier is running and ready."

    async def restart(self) -> Dict[str, Any]:
        return {"status": "success", "message": "CodeModifier reloaded."}

    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        if action_name == "search_files":
            return self.search_files(params.get("keyword", ""), params.get("extension"))
        elif action_name == "read_file":
            return self.read_file(
                params.get("file_path", ""),
                int(params.get("start_line", 1)),
                int(params.get("end_line", 100))
            )
        elif action_name == "modify_code":
            return self.modify_code(
                params.get("file_path", ""),
                params.get("target_snippet", ""),
                params.get("replacement_snippet", ""),
                params.get("description", "")
            )
        elif action_name == "rollback":
            return self.rollback(params.get("file_path", ""))
        return {"status": "error", "message": f"Unknown action: {action_name}"}

    def search_files(self, keyword: str, extension: Optional[str] = None) -> Dict[str, Any]:
        """Search for keyword occurrences across workspace files."""
        if not keyword or len(keyword.strip()) < 2:
            return {"status": "error", "message": "검색어는 최소 2글자 이상이어야 합니다."}

        keyword_lower = keyword.lower()
        matches = []

        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if extension and ext != extension.lower():
                    continue
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(WORKSPACE_ROOT).as_posix()

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_idx, line in enumerate(f, start=1):
                            if keyword_lower in line.lower():
                                matches.append({
                                    "file": rel_path,
                                    "line": line_idx,
                                    "content": line.strip()[:100]
                                })
                                if len(matches) >= 30:
                                    break
                except Exception:
                    continue
            if len(matches) >= 30:
                break

        return {
            "status": "success",
            "keyword": keyword,
            "total_matches": len(matches),
            "results": matches
        }

    def read_file(self, file_path_str: str, start_line: int = 1, end_line: int = 100) -> Dict[str, Any]:
        """Read lines from a specified file."""
        target_path = self._resolve_safe_path(file_path_str)
        if not target_path or not target_path.is_file():
            return {"status": "error", "message": f"파일을 찾을 수 없습니다: {file_path_str}"}

        try:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()

            total_lines = len(all_lines)
            start_idx = max(1, start_line)
            end_idx = min(total_lines, end_line)

            selected_lines = [
                f"{i:4d} | {all_lines[i-1]}"
                for i in range(start_idx, end_idx + 1)
            ]

            return {
                "status": "success",
                "file": target_path.relative_to(WORKSPACE_ROOT).as_posix(),
                "total_lines": total_lines,
                "range": f"{start_idx}-{end_idx}",
                "content": "".join(selected_lines)
            }
        except Exception as e:
            return {"status": "error", "message": f"파일 읽기 실패: {str(e)}"}

    def modify_code(
        self,
        file_path_str: str,
        target_snippet: str,
        replacement_snippet: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Safely modify code snippet with automatic backup and AST syntax validation."""
        target_path = self._resolve_safe_path(file_path_str)
        if not target_path or not target_path.is_file():
            return {"status": "error", "message": f"대상 파일이 존재하지 않습니다: {file_path_str}"}

        if not target_snippet:
            return {"status": "error", "message": "수정할 기존 코드(target_snippet)가 비어 있습니다."}

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            if target_snippet not in original_content:
                return {
                    "status": "error",
                    "message": "수정하려는 코드 조각이 파일 내용과 일치하지 않습니다. 파일 내용을 먼저 조회해 주세요."
                }

            match_count = original_content.count(target_snippet)
            if match_count > 1:
                return {
                    "status": "error",
                    "message": f"수정 대상 코드가 파일 내에 {match_count}개 중복 존재합니다. 더 고유한 전후 코드를 포함해 주세요."
                }

            # 1. Create Timestamped Backup
            ts = int(time.time())
            safe_name = target_path.name + f"_{ts}.bak"
            backup_path = self.backup_dir / safe_name
            shutil.copy2(target_path, backup_path)

            # 2. Perform Replacement
            new_content = original_content.replace(target_snippet, replacement_snippet, 1)

            # 3. Syntax Verification for Python files
            if target_path.suffix == ".py":
                try:
                    ast.parse(new_content)
                except SyntaxError as se:
                    # Rollback immediately
                    return {
                        "status": "syntax_error",
                        "message": f"❌ 파이썬 문법 오류(SyntaxError) 감지로 수정을 취소했습니다: {se.msg} (Line {se.lineno})"
                    }

            # 4. Write back new content
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "status": "success",
                "file": target_path.relative_to(WORKSPACE_ROOT).as_posix(),
                "description": description or "코드 수정 완료",
                "backup_created": backup_path.name,
                "message": f"✅ <code>{target_path.name}</code> 파일 코드가 성공적으로 수정되었습니다."
            }

        except Exception as e:
            return {"status": "error", "message": f"코드 수정 중 예외 발생: {str(e)}"}

    def rollback(self, file_path_str: str) -> Dict[str, Any]:
        """Rollback to the most recent backup of the file."""
        target_path = self._resolve_safe_path(file_path_str)
        if not target_path:
            return {"status": "error", "message": "유효하지 않은 파일 경로입니다."}

        prefix = target_path.name + "_"
        matching_backups = sorted(
            [f for f in self.backup_dir.glob(f"{prefix}*.bak")],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not matching_backups:
            return {"status": "error", "message": f"복원 가능한 백업본이 없습니다: {target_path.name}"}

        latest_backup = matching_backups[0]
        try:
            shutil.copy2(latest_backup, target_path)
            return {
                "status": "success",
                "file": target_path.relative_to(WORKSPACE_ROOT).as_posix(),
                "restored_from": latest_backup.name,
                "message": f"🔄 <code>{target_path.name}</code> 파일이 백업본({latest_backup.name})으로 안전하게 롤백되었습니다."
            }
        except Exception as e:
            return {"status": "error", "message": f"롤백 복원 실패: {str(e)}"}

code_modifier = CodeModifierAdapter()
