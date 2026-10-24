#!/usr/bin/env python3
"""Read-only license consistency checker for Python repositories."""

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("check_license_consistency.py requires Python 3.11+ (tomllib).", file=sys.stderr)
    raise SystemExit(2)

DEFAULT_EXCLUDES = {
    ".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "env",
    "node_modules", "build", "dist", ".tox", ".nox", ".mypy_cache",
    ".ruff_cache", ".pytest_cache", "site-packages", "_build", "htmlcov",
    "coverage", ".idea", ".vscode",
}

LICENSE_FILENAMES = {
    "LICENSE", "LICENCE", "COPYING", "COPYING.LIB",
    "LICENSE.TXT", "LICENSE.MD", "LICENCE.TXT", "LICENCE.MD",
}

CLASSIFIER_MAP = {
    "license :: osi approved :: apache software license": "Apache-2.0",
    "license :: osi approved :: mit license": "MIT",
    "license :: osi approved :: gnu general public license v2 (gplv2)": "GPL-2.0",
    "license :: osi approved :: gnu general public license v3 (gplv3)": "GPL-3.0",
    "license :: osi approved :: bsd license": "BSD-3-Clause",
    "license :: osi approved :: mozilla public license 2.0 (mpl 2.0)": "MPL-2.0",
}

ALIASES = {
    "apache-2.0": "Apache-2.0",
    "apache-2": "Apache-2.0",
    "apache": "Apache-2.0",
    "mit": "MIT",
    "gpl": "GPL",
    "gpl-2.0": "GPL-2.0",
    "gpl-2.0-only": "GPL-2.0",
    "gpl-2.0-or-later": "GPL-2.0",
    "gplv2": "GPL-2.0",
    "gnu-general-public-v2": "GPL-2.0",
    "gnu-gpl-v2": "GPL-2.0",
    "gpl-3.0": "GPL-3.0",
    "gpl-3.0-only": "GPL-3.0",
    "gpl-3.0-or-later": "GPL-3.0",
    "gplv3": "GPL-3.0",
    "gnu-general-public-v3": "GPL-3.0",
    "gnu-gpl-v3": "GPL-3.0",
    "bsd": "BSD",
    "bsd-3-clause": "BSD-3-Clause",
    "mpl-2.0": "MPL-2.0",
}

README_TOKEN_RE = re.compile(
    r"(?i)\b(apache(?:[- ]2\.0)?|mit|gpl(?:[- ]?[23]\.0(?:-only|-or-later)?)?|"
    r"bsd(?:[- ]3[- ]clause)?|mpl(?:[- ]2\.0)?)\b"
)
LICENSE_LINE_RE = re.compile(r"(?i)licen[cs]e|许可证|许可协议|版权")


def configure_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def normalize(value):
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    key = re.sub(r"[\s_]+", "-", text.lower())
    key = key.replace("license", "").strip("-")
    key = re.sub(r"-+", "-", key)
    return ALIASES.get(key, text)


def same_license(left, right):
    if not left or not right:
        return True
    if left == right:
        return True
    if "GPL" in {left, right}:
        return True
    if {left, right} == {"BSD", "BSD-3-Clause"}:
        return True
    return False


def detect_license(text):
    lowered = text.lower()
    head = lowered[:2000]
    if "apache license" in head and "version 2.0" in head:
        return "Apache-2.0"
    if "gnu general public license" in head:
        if "version 3" in head:
            return "GPL-3.0"
        if "version 2" in head:
            return "GPL-2.0"
    if "mozilla public license" in head and "2.0" in head:
        return "MPL-2.0"
    if "mit license" in head or "permission is hereby granted, free of charge" in head:
        return "MIT"
    if "redistribution and use in source and binary forms" in lowered:
        if "neither the name" in lowered:
            return "BSD-3-Clause"
        return "BSD"
    return None


def read_text(path, limit=8192):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def find_license_file(directory):
    try:
        entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
    except OSError:
        return None
    for entry in entries:
        if entry.is_file() and entry.name.upper() in LICENSE_FILENAMES:
            return entry
    for entry in entries:
        if entry.is_file():
            upper = entry.name.upper()
            if upper.startswith("LICENSE") or upper.startswith("COPYING"):
                return entry
    return None


def should_skip_dir(path, root, excludes, include_submodules):
    if path == root:
        return False
    name = path.name
    if name in DEFAULT_EXCLUDES:
        return True
    if name.startswith(".") and name not in {".github", ".gitlab"}:
        return True
    if not include_submodules and (path / ".git").exists():
        return True
    relative = path.relative_to(root).as_posix()
    for pattern in excludes:
        if fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False


def iter_pyprojects(root, excludes, include_submodules):
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not should_skip_dir(current / name, root, excludes, include_submodules)
        )
        if "pyproject.toml" in filenames:
            yield current / "pyproject.toml"


def parse_project(pyproject):
    try:
        data = tomllib.loads(pyproject.read_bytes().decode("utf-8"))
    except Exception as exc:
        return None, f"cannot parse: {exc}"
    project = data.get("project", {})
    if not isinstance(project, dict):
        return None, "project table is not a mapping"
    return project, None


def resolve_declared(project, directory):
    raw = project.get("license")
    declared = None
    license_file = None
    warnings = []
    if isinstance(raw, str):
        declared = normalize(raw)
    elif isinstance(raw, dict):
        if "file" in raw:
            license_file = directory / str(raw["file"])
            if not license_file.exists():
                warnings.append(f"license file {raw['file']!r} does not exist")
                license_file = None
        elif "text" in raw:
            warnings.append("license uses deprecated {text=...}; prefer an SPDX string")
            text = str(raw["text"])
            declared = normalize(text)
            if declared is None or len(text.strip()) > 100:
                declared = detect_license(text)
        else:
            warnings.append(f"unsupported license table: {raw!r}")
    elif raw is not None:
        warnings.append(f"unsupported license value: {raw!r}")
    return declared, license_file, warnings


def classifier_licenses(project):
    classifiers = project.get("classifiers", [])
    if not isinstance(classifiers, list):
        return []
    found = []
    for classifier in classifiers:
        mapped = CLASSIFIER_MAP.get(str(classifier).strip().lower())
        if mapped and mapped not in found:
            found.append(mapped)
    return found


def readme_mentions(readme, declared):
    warnings = []
    text = read_text(readme, limit=200000)
    for lineno, line in enumerate(text.splitlines(), 1):
        if not LICENSE_LINE_RE.search(line):
            continue
        tokens = {normalize(token) for token in README_TOKEN_RE.findall(line)}
        tokens.discard(None)
        if declared and tokens and not any(same_license(token, declared) for token in tokens):
            warnings.append(
                f"{readme.name}:{lineno} mentions {sorted(tokens)} "
                f"but project declares {declared}"
            )
    return warnings


def main(argv=None):
    configure_stdout()
    parser = argparse.ArgumentParser(
        description="Read-only license consistency checker for Python repositories."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when warnings are present, not only conflicts",
    )
    parser.add_argument(
        "--include-submodules",
        action="store_true",
        help="scan nested repositories and submodules as well",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help="additional path pattern to exclude; repeatable",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    files = []
    conflicts = []
    warnings = []
    errors = []

    for pyproject in iter_pyprojects(root, args.exclude, args.include_submodules):
        relative = pyproject.relative_to(root).as_posix()
        project, error = parse_project(pyproject)
        if error:
            errors.append({"path": relative, "message": error})
            continue

        declared, license_file, local_warnings = resolve_declared(project, pyproject.parent)
        for message in local_warnings:
            warnings.append({"path": relative, "message": message})

        file_license = None
        if license_file is None:
            license_file = find_license_file(pyproject.parent)
        if license_file is not None:
            text = read_text(license_file)
            file_license = detect_license(text)
            if file_license is None and len(text.strip()) < 200:
                file_license = normalize(text)
            if file_license is None:
                warnings.append(
                    {
                        "path": relative,
                        "message": f"could not detect a known license in {license_file.name}",
                    }
                )

        if declared is None and file_license is not None:
            declared = file_license

        label = license_file.name if license_file is not None else "LICENSE"
        if declared and file_license and not same_license(declared, file_license):
            conflicts.append(
                {
                    "path": relative,
                    "message": f"license declares {declared} but {label} is {file_license}",
                }
            )

        classifier_licenses_found = classifier_licenses(project)
        if declared and classifier_licenses_found:
            for classifier_license in classifier_licenses_found:
                if not same_license(declared, classifier_license):
                    conflicts.append(
                        {
                            "path": relative,
                            "message": (
                                f"license declares {declared} "
                                f"but classifier is {classifier_license}"
                            ),
                        }
                    )
        elif not declared and classifier_licenses_found and file_license:
            for classifier_license in classifier_licenses_found:
                if not same_license(classifier_license, file_license):
                    warnings.append(
                        {
                            "path": relative,
                            "message": (
                                f"classifier is {classifier_license} "
                                f"but {label} is {file_license}"
                            ),
                        }
                    )

        readme = None
        try:
            for entry in pyproject.parent.iterdir():
                if entry.is_file() and entry.name.lower() == "readme.md":
                    readme = entry
                    break
        except OSError:
            pass
        if readme is not None:
            readme_declared = declared
            if readme_declared is None and len(classifier_licenses_found) == 1:
                readme_declared = classifier_licenses_found[0]
            for message in readme_mentions(readme, readme_declared):
                warnings.append({"path": relative, "message": message})

        files.append(
            {
                "path": relative,
                "name": project.get("name"),
                "declared": declared,
                "license_file": (
                    license_file.relative_to(root).as_posix()
                    if license_file is not None and license_file.is_relative_to(root)
                    else (str(license_file) if license_file is not None else None)
                ),
                "file_license": file_license,
                "classifiers": classifier_licenses_found,
            }
        )

    summary = {
        "root": str(root),
        "scanned": len(files),
        "files": files,
        "conflicts": conflicts,
        "warnings": warnings,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Scanned {len(files)} pyproject.toml file(s) under {root}")
        for item in conflicts:
            print(f"[CONFLICT] {item['path']}: {item['message']}")
        for item in warnings:
            print(f"[WARNING] {item['path']}: {item['message']}")
        for item in errors:
            print(f"[ERROR] {item['path']}: {item['message']}")
        print(
            f"\nSummary: {len(conflicts)} conflict(s), "
            f"{len(warnings)} warning(s), {len(errors)} error(s)."
        )

    if conflicts or errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
