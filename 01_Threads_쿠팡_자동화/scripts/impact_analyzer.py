#!/usr/bin/env python3
"""
ANTIGRAVITY Impact Analyzer (PHASE 13)
Fast dependency impact analysis for modular updates.
Determines affected modules, templates, and targeted tests when modifying a single file.
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent

# Core foundational modules that inherently have a high blast radius
CORE_MODULES = {
    "database/models.py",
    "database/connection.py",
    "app/main.py",
    "app/templates/base.html",
    "app/static/js/core/apiClient.js",
    "app/static/js/core/state.js",
    "utils/cache.py",
    "config.py"
}

def get_relative_path(path_str: str) -> str:
    path = Path(path_str).resolve()
    try:
        return str(path.relative_to(ROOT_DIR)).replace("\\", "/")
    except ValueError:
        return path_str.replace("\\", "/")

def scan_file_references(target_rel_path: str) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Find all references to target file in Python files, HTML templates, and JS files.
    Returns: (python_dependents, template_dependents, test_files)
    """
    py_deps = set()
    tpl_deps = set()
    test_deps = set()

    stem = Path(target_rel_path).stem
    ext = Path(target_rel_path).suffix

    # Python module dot notation (e.g. services.account_service)
    py_mod = target_rel_path.replace("/", ".").replace(".py", "") if ext == ".py" else ""
    class_candidates = [
        "".join(part.capitalize() for part in stem.split("_")), # snake to PascalCase
        stem
    ]

    PROJECT_DIRS = {"agents", "app", "components", "database", "domain_types", "integrations", "prompts", "scripts", "services", "tests", "utils"}

    for p_dir in PROJECT_DIRS:
        sub_dir = ROOT_DIR / p_dir
        if not sub_dir.exists():
            continue
        for root, dirs, files in os.walk(sub_dir):
            dirs[:] = [d for d in dirs if d not in {".pytest_cache", "__pycache__"}]
            for f in files:
                file_path = Path(root) / f
                rel = str(file_path.relative_to(ROOT_DIR)).replace("\\", "/")
                if rel == target_rel_path:
                    continue

                if f.endswith(".py"):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        is_hit = False
                        if py_mod and (py_mod in content or f"from {py_mod}" in content):
                            is_hit = True
                        elif any(c in content for c in class_candidates if len(c) > 3):
                            for c in class_candidates:
                                if len(c) > 3 and re.search(rf"\b{c}\b", content):
                                    is_hit = True
                                    break
                        elif stem in content and ext in [".py", ".js"]:
                            if re.search(rf"\b{stem}\b", content):
                                is_hit = True

                        if is_hit:
                            if rel.startswith("tests/"):
                                test_deps.add(rel)
                            else:
                                py_deps.add(rel)
                    except Exception:
                        pass

                elif f.endswith(".html"):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if stem in content or target_rel_path in content or f"{stem}.js" in content:
                            tpl_deps.add(rel)
                    except Exception:
                        pass

                elif f.endswith(".js"):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if stem in content:
                            py_deps.add(rel)
                    except Exception:
                        pass

    return py_deps, tpl_deps, test_deps

def analyze_impact(file_path_str: str) -> Dict:
    rel_path = get_relative_path(file_path_str)
    full_path = ROOT_DIR / rel_path

    if not full_path.exists():
        return {"error": f"File not found: {rel_path}"}

    py_deps, tpl_deps, test_deps = scan_file_references(rel_path)

    total_dependents = len(py_deps) + len(tpl_deps)
    is_core = rel_path in CORE_MODULES

    if is_core or total_dependents >= 6:
        risk = "LARGE"
        color = "\033[91m" # Red
        desc = "High Impact: Foundational component. Full regression testing required."
    elif total_dependents >= 3:
        risk = "MEDIUM"
        color = "\033[93m" # Yellow
        desc = "Moderate Impact: Multiple modules affected. Targeted testing recommended."
    else:
        risk = "SMALL"
        color = "\033[92m" # Green
        desc = "Low Impact: Isolated module (Local Change Principle). Safe for rapid deployment."

    stem = Path(rel_path).stem
    all_tests = list((ROOT_DIR / "tests").glob("test_*.py"))
    recommended_tests = set(test_deps)
    for t in all_tests:
        t_rel = str(t.relative_to(ROOT_DIR)).replace("\\", "/")
        if stem in t_rel or stem.replace("_service", "") in t_rel or "modular" in t_rel:
            recommended_tests.add(t_rel)

    return {
        "target_file": rel_path,
        "risk": risk,
        "risk_color": color,
        "risk_desc": desc,
        "is_core": is_core,
        "dependent_count": total_dependents,
        "python_dependents": sorted(list(py_deps)),
        "template_dependents": sorted(list(tpl_deps)),
        "recommended_tests": sorted(list(recommended_tests))
    }

def print_report(res: Dict):
    if "error" in res:
        print(f"\n❌ {res['error']}\n")
        return

    reset = "\033[0m"
    bold = "\033[1m"
    cyan = "\033[96m"
    gray = "\033[90m"

    print("\n" + "=" * 70)
    print(f" 🚀 {bold}ANTIGRAVITY ARCHITECTURE IMPACT ANALYZER{reset}")
    print("=" * 70)
    print(f" Target File       : {cyan}{res['target_file']}{reset}")
    print(f" Impact Risk Level : {res['risk_color']}{bold}[{res['risk']}]{reset} ({res['risk_desc']})")
    print(f" Total Dependents  : {bold}{res['dependent_count']}{reset} direct components")
    if res['is_core']:
        print(f" Core Component    : {bold}\033[91mYES (Framework Foundation)\033[0m")
    print("-" * 70)

    print(f" 📦 {bold}Affected Backend/Scripts ({len(res['python_dependents'])}):{reset}")
    if res['python_dependents']:
        for dep in res['python_dependents']:
            print(f"   • {dep}")
    else:
        print(f"   {gray}(None - isolated module){reset}")

    print(f"\n 🎨 {bold}Affected UI Templates ({len(res['template_dependents'])}):{reset}")
    if res['template_dependents']:
        for tpl in res['template_dependents']:
            print(f"   • {tpl}")
    else:
        print(f"   {gray}(None - UI unaffected){reset}")

    print(f"\n 🧪 {bold}Recommended Targeted Tests ({len(res['recommended_tests'])}):{reset}")
    if res['recommended_tests']:
        test_cmd = f"pytest " + " ".join(res['recommended_tests'])
        print(f"   Run Command: {cyan}{test_cmd}{reset}")
        for t in res['recommended_tests']:
            print(f"   • {t}")
    else:
        print(f"   Run Command: {cyan}pytest tests/test_modular_architecture.py{reset}")

    print("=" * 70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Analyze blast radius and dependencies for any file modification.")
    parser.add_argument("file", nargs="?", help="Target file path to analyze (e.g. services/account_service.py)")
    args = parser.parse_args()

    if not args.file:
        print("Usage: python scripts/impact_analyzer.py <filepath>")
        print("Example: python scripts/impact_analyzer.py services/account_service.py")
        sys.exit(1)

    result = analyze_impact(args.file)
    print_report(result)

if __name__ == "__main__":
    main()
