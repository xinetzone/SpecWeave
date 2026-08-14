#!/usr/bin/env python3
"""
DevContainer CI Build Failure Diagnostics Analyzer
===================================================
Parses the 10-dimension diagnostic artifacts produced by failed CI builds
or local-build.sh, and generates a visual HTML root-cause report.

Usage:
    python3 analyze-diagnostics.py <diagnostics_directory> [--output report.html]
    python3 analyze-diagnostics.py /tmp/diag-abc123/ -o report.html
    python3 analyze-diagnostics.py artifacts.zip   # auto-extract if zipfile available

Input: A directory containing files produced by the CI "Collect diagnostics on failure" step:
    00-summary.txt        - Build metadata (if from local-build.sh)
    01-system.txt         - System state (date, uptime, memory, disk, CPU)
    02-docker.txt         - Docker daemon state, images, containers
    03-dockerd.log        - Docker daemon logs (WSL2/Linux)
    04-build-cache.txt    - BuildKit cache usage
    05-errors.txt         - Extracted error patterns from build logs
    06-containers.txt     - Container states
    07-networks.txt       - Networks and volumes
    08-build-logs.txt     - Full build logs with errors
    09-env-git.txt        - Environment variables and Git context
    10-packages.txt       - Package manager state
    build-*.log           - Raw build logs (from local-build.sh)

Output: Single HTML file with:
    - Build failure summary card
    - 10-dimension health dashboard (color-coded)
    - Root-cause probability analysis
    - Error timeline with severity indicators
    - Recommended fix actions
    - Raw diagnostic data sections (collapsible)
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import zipfile
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DimensionResult:
    """Result of analyzing one diagnostic dimension."""
    name: str
    file: str
    status: str  # "ok", "warning", "error", "critical"
    summary: str
    findings: list[str] = field(default_factory=list)
    raw_content: str = ""


@dataclass
class RootCause:
    """Identified potential root cause."""
    category: str
    probability: float  # 0.0-1.0
    evidence: list[str]
    dimension: str
    suggested_fix: str
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class BuildDiagnostics:
    """Complete analysis of a build failure."""
    source_dir: Path
    build_time: str = ""
    commit_sha: str = ""
    variant: str = ""
    dimensions: OrderedDict[str, DimensionResult] = field(default_factory=OrderedDict)
    root_causes: list[RootCause] = field(default_factory=list)
    error_timeline: list[tuple[str, str, str]] = field(default_factory=list)  # (time, level, message)
    raw_files: dict[str, str] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Root Cause Patterns (10-dimension diagnosis system)
# ═══════════════════════════════════════════════════════════════════════════════

# Each pattern: (regex, category, severity, suggested_fix, dimension, weight)
ERROR_PATTERNS = [
    # ── Network/DNS ──
    (r"(?:could not resolve|name resolution failed|Temporary failure resolving|DNS_PROBE|network is unreachable|connection refused|connection timed out|Connection reset by peer|443.*timeout|SSL.*handshake.*fail|EOF.*before.*completion|503 Service Unavailable|502 Bad Gateway|429 Too Many Requests|apt.*404|pip.*connection|conda.*HTTPError)",
     "network", "critical",
     "检查网络连接/DNS配置；如在国内环境使用 --cn 镜像参数；配置代理或检查防火墙规则",
     "docker-daemon", 0.9),

    # ── Disk Space ──
    (r"(?:no space left on device|disk space|No space|ENOSPC|disk quota exceeded|out of disk space|cannot create.*no space)",
     "disk-space", "critical",
     "清理Docker缓存: docker system prune -a --volumes; 清理磁盘空间; 扩大CI runner磁盘配额",
     "system-state", 0.95),

    # ── Out of Memory ──
    (r"(?:out of memory|OOM|Killed process|cannot allocate memory|ENOMEM|memory limit|cgroup.*memory.*oom|exit code 137)",
     "memory", "critical",
     "增加Docker内存限制(WSL2: .wslconfig中配置memory=8GB+); 减少并行编译数; 减小Dockerfile中pip install并发数",
     "system-state", 0.9),

    # ── Permission Denied ──
    (r"(?:permission denied|Permission denied|EACCES|access denied|operation not permitted|must be root|chmod.*denied)",
     "permission", "high",
     "检查Docker socket权限: sudo chmod 666 /var/run/docker.sock; 检查文件/目录权限; 用户组配置",
     "containers", 0.8),

    # ── Docker Daemon Issues ──
    (r"(?:docker daemon|dockerd|Cannot connect to Docker|docker.sock|buildkit.*not.*running|daemon.*not.*running|docker:.*not found)",
     "docker-daemon", "critical",
     "启动Docker服务: sudo systemctl start docker (或 sudo dockerd); 检查Buildx插件安装",
     "docker-daemon", 0.85),

    # ── BuildKit/Buildx Issues ──
    (r"(?:buildx.*not.*found|buildkit.*missing|BUILDKIT.*error|frontend.*dockerfile.v0.*not.*found|syntax.*not found)",
     "buildkit", "high",
     "安装Buildx插件; 设置DOCKER_BUILDKIT=0回退传统构建; 更新Docker版本",
     "build-cache", 0.8),

    # ── Package Not Found (pip/conda/apt) ──
    (r"(?:package.*not found|No matching distribution|Could not find a version|ERROR:.*No such|Package.*does not exist|E: Unable to locate package|conda.*PackagesNotFoundError|pip.*ResolutionImpossible|UnsatisfiableError)",
     "package-missing", "high",
     "检查包名拼写和版本约束; 更新镜像源(--cn/--official); 检查Python/conda版本兼容性",
     "packages", 0.75),

    # ── Compilation/Build Errors ──
    (r"(?:error: command.*failed|gcc.*error|cmake.*error|make.*Error|nvcc.*error|fatal error:.*No such file|undefined reference|collect2: error|compilation terminated)",
     "compilation", "high",
     "检查编译依赖(llvm/gcc/cmake版本); 检查build-base依赖链; 安装缺失的-dev/-devel包",
     "build-logs", 0.7),

    # ── Hash Mismatch/Checksum ──
    (r"(?:hash mismatch|checksum|sha256.*mismatch|MD5.*mismatch|invalid hash|corrupt.*package|bad checksum)",
     "checksum", "medium",
     "清除包管理器缓存(pip cache purge/conda clean -a); 重新下载; 检查网络稳定性",
     "packages", 0.65),

    # ── Timeout ──
    (r"(?:timeout|timed out|deadline exceeded|context deadline)",
     "timeout", "medium",
     "增加超时时间; 检查网络; 简化Dockerfile RUN步骤; 考虑分层缓存策略",
     "build-logs", 0.6),

    # ── Git/Clone Issues ──
    (r"(?:git.*clone.*failed|fatal:.*repository|could not read from remote|git.*authentication|fatal:.*unable to access)",
     "git", "medium",
     "检查Git认证配置; 确认仓库可访问性; 检查SSH key/token配置",
     "env-git", 0.6),

    # ── Layer Caching Issues ──
    (r"(?:layer.*not found|blob.*unknown|manifest unknown|cache.*invalid|failed to export)",
     "cache", "low",
     "使用--no-cache重试; 清理buildx缓存: docker buildx prune -af",
     "build-cache", 0.5),

    # ── Python Version Issues ──
    (r"(?:requires-python|Python.*version.*not supported|SyntaxError|ImportError.*version|ModuleNotFoundError)",
     "python-version", "medium",
     "检查Python版本兼容性(3.10+); pyproject.toml中requires-python约束; Dockerfile中ARG PYTHON_VERSION",
     "build-logs", 0.55),

    # ── Conda Solver Issues ──
    (r"(?:conda.*conflict|conflict:|UnsatisfiableError|incompatible|Solving environment.*failed|libmamba.*error)",
     "conda-solver", "high",
     "使用libmamba solver加速解析; 固定包版本范围; 检查conda-forge channel优先级",
     "packages", 0.7),
]

DIMENSION_FILES = OrderedDict([
    ("system-state",  "01-system.txt"),
    ("docker-daemon", "02-docker.txt"),
    ("dockerd-logs",  "03-dockerd.log"),
    ("build-cache",   "04-build-cache.txt"),
    ("errors",        "05-errors.txt"),
    ("containers",    "06-containers.txt"),
    ("networks",      "07-networks.txt"),
    ("build-logs",    "08-build-logs.txt"),
    ("env-git",       "09-env-git.txt"),
    ("packages",      "10-packages.txt"),
])

DIMENSION_LABELS = {
    "system-state":  "🖥️ 系统状态",
    "docker-daemon": "🐳 Docker守护进程",
    "dockerd-logs":  "📋 Docker日志",
    "build-cache":   "📦 构建缓存",
    "errors":        "🚨 错误提取",
    "containers":    "📦 容器状态",
    "networks":      "🌐 网络/存储卷",
    "build-logs":    "📝 构建日志",
    "env-git":       "⚙️ 环境/Git",
    "packages":      "📦 包管理器",
}

CAT_LABELS = {
    "network": "🌐 网络/DNS问题",
    "disk-space": "💾 磁盘空间不足",
    "memory": "🧠 内存不足(OOM)",
    "permission": "🔒 权限问题",
    "docker-daemon": "🐳 Docker守护进程",
    "buildkit": "🔨 BuildKit/Buildx",
    "package-missing": "📦 包未找到",
    "compilation": "⚙️ 编译错误",
    "checksum": "🔐 校验和不匹配",
    "timeout": "⏱️ 超时",
    "git": "📂 Git操作失败",
    "cache": "💨 缓存失效",
    "python-version": "🐍 Python版本",
    "conda-solver": "🔬 Conda依赖解析",
    "unknown": "❓ 未知原因",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis Engine
# ═══════════════════════════════════════════════════════════════════════════════

class DiagnosticsAnalyzer:
    """Analyzes CI/local build diagnostic artifacts."""

    def __init__(self, source_path: Path):
        self.source = Path(source_path)
        self.result = BuildDiagnostics(source_dir=self.source)

    def load(self) -> bool:
        """Load all diagnostic files. Returns True if any files found."""
        if self.source.is_file() and self.source.suffix == '.zip':
            return self._extract_zip()
        if not self.source.is_dir():
            print(f"Error: {self.source} is not a directory or zip file", file=sys.stderr)
            return False

        files_found = False
        for dim_name, filename in DIMENSION_FILES.items():
            filepath = self.source / filename
            if filepath.is_file():
                content = filepath.read_text(errors='replace', encoding='utf-8')
                self.result.raw_files[dim_name] = content
                files_found = True
            else:
                # Try partial matches (local-build.sh may use different naming)
                for f in self.source.iterdir():
                    if f.is_file() and f.name.startswith(filename[:2]) and dim_name not in self.result.raw_files:
                        content = f.read_text(errors='replace', encoding='utf-8')
                        self.result.raw_files[dim_name] = content
                        files_found = True
                        break

        # Also load any build-*.log files from local-build.sh
        for f in sorted(self.source.glob("*.log")):
            content = f.read_text(errors='replace', encoding='utf-8')
            self.result.raw_files[f"log::{f.name}"] = content
            if "build-logs" not in self.result.raw_files:
                self.result.raw_files["build-logs"] = content
            else:
                self.result.raw_files["build-logs"] += f"\n\n=== {f.name} ===\n{content}"
            files_found = True

        # Load summary if present
        summary_file = self.source / "00-summary.txt"
        if summary_file.is_file():
            content = summary_file.read_text(errors='replace', encoding='utf-8')
            self.result.raw_files["summary"] = content
            self._parse_summary(content)

        if not files_found:
            # Try looking in subdirectories (zip extraction creates subdirs)
            for sub in self.source.iterdir():
                if sub.is_dir():
                    for filename in DIMENSION_FILES.values():
                        if (sub / filename).is_file():
                            return DiagnosticsAnalyzer(sub).load()

        return files_found

    def _extract_zip(self) -> bool:
        """Extract a zip file to a temp directory and analyze it."""
        import tempfile
        tmpdir = Path(tempfile.mkdtemp(prefix="diag-"))
        print(f"Extracting {self.source} to {tmpdir}...")
        with zipfile.ZipFile(self.source, 'r') as zf:
            zf.extractall(tmpdir)
        self.source = tmpdir
        self.result.source_dir = tmpdir
        return self.load()

    def _parse_summary(self, content: str):
        """Extract metadata from summary file."""
        for line in content.splitlines():
            if "Date:" in line or "date:" in line:
                self.result.build_time = line.split(":", 1)[-1].strip()
            if "Failure stage:" in line:
                self.result.variant = line.split(":", 1)[-1].strip()
            if "SHA" in line.lower() and ":" in line:
                self.result.commit_sha = line.split(":", 1)[-1].strip()

    def analyze(self) -> BuildDiagnostics:
        """Run full analysis on loaded diagnostics."""
        self._analyze_dimensions()
        self._identify_root_causes()
        self._extract_error_timeline()
        return self.result

    def _analyze_dimensions(self):
        """Analyze each diagnostic dimension individually."""
        for dim_name, filename in DIMENSION_FILES.items():
            content = self.result.raw_files.get(dim_name, "")
            result = DimensionResult(
                name=dim_name,
                file=filename,
                status="ok",
                summary="无异常",
                raw_content=content,
            )

            if not content:
                result.status = "warning"
                result.summary = "文件缺失"
                result.findings.append(f"未找到诊断文件: {filename}")
                self.result.dimensions[dim_name] = result
                continue

            # Dimension-specific analysis
            if dim_name == "system-state":
                self._analyze_system_state(content, result)
            elif dim_name == "docker-daemon":
                self._analyze_docker(content, result)
            elif dim_name == "dockerd-logs":
                self._analyze_dockerd_logs(content, result)
            elif dim_name == "build-cache":
                self._analyze_build_cache(content, result)
            elif dim_name == "errors":
                self._analyze_error_extract(content, result)
            elif dim_name == "containers":
                self._analyze_containers(content, result)
            elif dim_name == "networks":
                self._analyze_networks(content, result)
            elif dim_name == "build-logs":
                self._analyze_build_logs(content, result)
            elif dim_name == "env-git":
                self._analyze_env_git(content, result)
            elif dim_name == "packages":
                self._analyze_packages(content, result)

            self.result.dimensions[dim_name] = result

    def _check_patterns(self, content: str) -> list[tuple[str, str, str, str, float]]:
        """Check content against all error patterns. Returns matches."""
        matches = []
        for pattern, category, severity, fix, dimension, weight in ERROR_PATTERNS:
            found = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if found:
                # Get context around the match
                for m in found[:3]:  # Limit to first 3 occurrences per pattern
                    line_match = re.search(rf".{{0,80}}{re.escape(str(m)[:50])}.{{0,80}}", content, re.IGNORECASE)
                    context = line_match.group(0).strip() if line_match else str(m)[:160]
                    matches.append((category, severity, fix, dimension, weight, context))
        return matches

    def _analyze_system_state(self, content: str, result: DimensionResult):
        issues = []
        # Check memory
        mem_match = re.search(r"Mem:\s+(\S+)\s+(\S+)\s+(\S+)", content)
        if mem_match:
            total_str = mem_match.group(1)
            try:
                # Parse Gi/Mi values
                val = float(re.sub(r'[A-Za-z]', '', total_str))
                if 'Gi' in total_str and val < 4:
                    issues.append(f"内存不足: 总计 {total_str} (建议 >= 8GB)")
                    result.status = "critical"
            except (ValueError, IndexError):
                pass

        # Check disk
        disk_matches = re.findall(r"/dev/\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)%", content)
        for total, used, avail, pct in disk_matches:
            if int(pct) > 95:
                issues.append(f"磁盘空间不足: 使用率 {pct}%")
                result.status = "critical"
            elif int(pct) > 85:
                issues.append(f"磁盘空间警告: 使用率 {pct}%")
                if result.status != "critical":
                    result.status = "warning"

        # Check load
        load_match = re.search(r"load average:\s+([\d.]+)", content)
        if load_match:
            try:
                load1 = float(load_match.group(1))
                nproc = re.search(r"(\d+)", content)
                if nproc and load1 > float(nproc.group(1)) * 2:
                    issues.append(f"系统负载过高: {load1}")
                    if result.status == "ok":
                        result.status = "warning"
            except ValueError:
                pass

        # Check for OOM/killed
        if re.search(r"(Killed process|out of memory|OOM)", content, re.I):
            issues.append("检测到OOM Kill事件")
            result.status = "critical"

        # Pattern matching
        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev == "critical":
                result.status = "critical"
            elif sev == "high" and result.status in ("ok", "warning"):
                result.status = "error"
            elif sev == "medium" and result.status == "ok":
                result.status = "warning"

        if issues:
            result.findings = issues
            result.summary = f"发现 {len(issues)} 个问题"
        else:
            result.summary = "系统资源正常"

    def _analyze_docker(self, content: str, result: DimensionResult):
        issues = []
        if re.search(r"(Cannot connect|ERROR.*error during connect|not found)", content, re.I):
            issues.append("Docker守护进程无法连接")
            result.status = "critical"
        if re.search(r"ERROR:", content):
            errors = re.findall(r"ERROR:.*", content)
            issues.extend([e[:120] for e in errors[:3]])
            result.status = "critical"
        if "Server Version" not in content and "Server:" not in content:
            issues.append("Docker服务端信息缺失")
            if result.status == "ok":
                result.status = "warning"

        # Check storage driver
        if re.search(r"vfs", content) and not re.search(r"overlay2", content):
            issues.append("存储驱动为vfs(性能差)，建议使用overlay2")
            if result.status == "ok":
                result.status = "warning"

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev == "critical":
                result.status = "critical"
            elif sev in ("high", "medium") and result.status == "ok":
                result.status = "error" if sev == "high" else "warning"

        if issues:
            result.findings = issues
            result.summary = f"发现 {len(issues)} 个问题"
        else:
            # Extract version for summary
            ver_match = re.search(r"Server version:\s*(\S+)", content, re.I)
            ver = ver_match.group(1) if ver_match else "可用"
            result.summary = f"Docker正常 (v{ver})"

    def _analyze_dockerd_logs(self, content: str, result: DimensionResult):
        issues = []
        if not content.strip():
            result.status = "warning"
            result.summary = "日志为空或未收集"
            return

        errors = re.findall(r"(?:level=error|ERRO\[).*", content)
        warns = re.findall(r"(?:level=warn|WARN\[).*", content)
        if errors:
            issues.extend([e[:120] for e in errors[:5]])
            result.status = "error"
        if warns and not errors:
            issues.extend([w[:120] for w in warns[:3]])
            result.status = "warning"

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev in ("critical", "high"):
                result.status = "critical"

        if issues:
            result.findings = issues
            result.summary = f"发现 {len(errors)} 个错误, {len(warns)} 个警告"
        else:
            result.summary = "守护进程日志正常"

    def _analyze_build_cache(self, content: str, result: DimensionResult):
        issues = []
        if not content.strip():
            result.status = "warning"
            result.summary = "缓存信息不可用"
            return

        if re.search(r"(Reclaimable|cache is empty)", content, re.I):
            reclaim_match = re.search(r"Reclaimable:\s*(\S+)", content)
            if reclaim_match:
                result.summary = f"缓存可回收: {reclaim_match.group(1)}"

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev in ("critical", "high"):
                result.status = "error"

        if issues:
            result.findings = issues
            result.summary = f"发现 {len(issues)} 个问题"
        else:
            # Get cache stats
            usage_match = re.search(r"Build Cache usage:\s*(\d+)", content)
            result.summary = "构建缓存正常"

    def _analyze_error_extract(self, content: str, result: DimensionResult):
        issues = []
        if not content.strip() or "no error patterns" in content.lower():
            result.summary = "未提取到明确错误模式"
            return

        error_lines = [l for l in content.splitlines() if re.search(r"(error|fatal|failed|denied|not found)", l, re.I)]
        if error_lines:
            result.status = "critical"
            issues.extend([l.strip()[:150] for l in error_lines[:10]])

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            result.status = "critical"

        result.findings = issues
        result.summary = f"提取到 {len(issues)} 个错误模式"

    def _analyze_containers(self, content: str, result: DimensionResult):
        issues = []
        exited = re.findall(r"Exited\s*\((\d+)\)", content, re.I)
        if exited:
            non_zero = [c for c in exited if c != "0"]
            if non_zero:
                issues.append(f"{len(non_zero)} 个容器以非零状态退出: {', '.join(non_zero[:5])}")
                result.status = "warning"

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev == "critical":
                result.status = "critical"

        if issues:
            result.findings = issues
            result.summary = f"{len(issues)} 个容器异常"
        else:
            result.summary = "容器状态正常"

    def _analyze_networks(self, content: str, result: DimensionResult):
        issues = []
        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev in ("critical", "high"):
                result.status = "warning"

        if issues:
            result.findings = issues
            result.summary = f"{len(issues)} 个网络/卷问题"
        else:
            result.summary = "网络/存储卷正常"

    def _analyze_build_logs(self, content: str, result: DimensionResult):
        issues = []
        if not content.strip():
            result.status = "warning"
            result.summary = "构建日志为空"
            return

        # Extract fatal errors
        fatals = re.findall(r"(?:FATA\[|FATAL|fatal error:|#\d+ ERROR:|error:.*failed|failed to solve|process.*did not complete)", content, re.I)
        errors = re.findall(r"(?:error[:\s]|ERROR:|E: )[^\n]{10,150}", content, re.I)
        if fatals:
            result.status = "critical"
            issues.extend([f[:150] for f in fatals[:5]])
        if errors and not fatals:
            result.status = "error"
            issues.extend([e.strip()[:150] for e in errors[:8]])

        pattern_matches = self._check_patterns(content)
        seen_cats = set()
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            if cat not in seen_cats:
                issues.append(f"[{cat}] {ctx[:120]}")
                seen_cats.add(cat)
            if sev == "critical":
                result.status = "critical"

        result.findings = issues
        if fatals or errors:
            result.summary = f"{len(fatals)} 个致命错误, {len(errors)} 个一般错误"
        elif issues:
            result.summary = f"发现 {len(issues)} 个问题"
        else:
            result.status = "ok"
            result.summary = "构建日志无明显错误(需结合错误提取分析)"

    def _analyze_env_git(self, content: str, result: DimensionResult):
        issues = []
        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            issues.append(f"[{cat}] {ctx[:120]}")
            if sev in ("critical", "high"):
                result.status = "error"

        if issues:
            result.findings = issues
            result.summary = f"{len(issues)} 个环境/Git问题"
        else:
            result.summary = "环境/Git配置正常"

    def _analyze_packages(self, content: str, result: DimensionResult):
        issues = []
        # Check for apt errors
        apt_errors = re.findall(r"E: [^\n]{10,}", content)
        pip_errors = re.findall(r"ERROR: (?:Could not find|No matching|ResolutionImpossible)[^\n]{0,200}", content)
        conda_errors = re.findall(r"(?:PackagesNotFoundError|UnsatisfiableError|LibMamba.*error)[^\n]{0,200}", content)

        if apt_errors:
            result.status = "error"
            issues.extend([e[:150] for e in apt_errors[:3]])
        if pip_errors:
            result.status = "error"
            issues.extend([e[:150] for e in pip_errors[:3]])
        if conda_errors:
            result.status = "error"
            issues.extend([e[:150] for e in conda_errors[:3]])

        pattern_matches = self._check_patterns(content)
        for cat, sev, fix, dim, weight, ctx in pattern_matches:
            if not any(cat in i for i in issues):
                issues.append(f"[{cat}] {ctx[:120]}")
            if sev == "critical":
                result.status = "critical"

        if issues:
            result.findings = issues
            result.summary = f"{len(apt_errors)+len(pip_errors)+len(conda_errors)} 个包管理错误"
        else:
            result.summary = "包管理器状态正常"

    def _identify_root_causes(self):
        """Aggregate dimension findings to identify root causes with probability scores."""
        cat_scores: dict[str, dict] = {}

        for dim_name, dim_result in self.result.dimensions.items():
            for finding in dim_result.findings:
                for pattern, cat, severity, fix, pdim, weight in ERROR_PATTERNS:
                    if re.search(pattern, finding, re.IGNORECASE):
                        if cat not in cat_scores:
                            cat_scores[cat] = {
                                "score": 0.0,
                                "evidence": [],
                                "dimension": dim_name,
                                "severity": severity,
                                "fix": fix,
                                "hits": 0,
                            }
                        cat_scores[cat]["score"] += weight
                        cat_scores[cat]["hits"] += 1
                        if len(cat_scores[cat]["evidence"]) < 5:
                            cat_scores[cat]["evidence"].append(finding[:180])
                        # Upgrade severity if worse
                        sev_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
                        if sev_order.get(severity, 0) > sev_order.get(cat_scores[cat]["severity"], 0):
                            cat_scores[cat]["severity"] = severity
                            cat_scores[cat]["fix"] = fix

        # Normalize scores and create RootCause objects
        max_score = max((v["score"] for v in cat_scores.values()), default=1.0)
        for cat, data in sorted(cat_scores.items(), key=lambda x: -x[1]["score"]):
            probability = min(data["score"] / max(max_score, 0.1), 1.0)
            rc = RootCause(
                category=cat,
                probability=round(probability, 2),
                evidence=data["evidence"],
                dimension=data["dimension"],
                suggested_fix=data["fix"],
                severity=data["severity"],
            )
            self.result.root_causes.append(rc)

        # If no root causes found but there are errors, add a generic one
        if not self.result.root_causes:
            errors_dim = self.result.dimensions.get("errors")
            if errors_dim and errors_dim.status in ("error", "critical"):
                self.result.root_causes.append(RootCause(
                    category="unknown",
                    probability=0.5,
                    evidence=errors_dim.findings[:3] or ["未能自动识别根因，需人工分析"],
                    dimension="errors",
                    suggested_fix="查看构建日志中的详细错误信息，结合上下文分析具体原因",
                    severity="high",
                ))

    def _extract_error_timeline(self):
        """Extract timestamped errors from build logs for timeline view."""
        build_logs = self.result.raw_files.get("build-logs", "")
        if not build_logs:
            return

        # Match common log formats with timestamps
        ts_patterns = [
            r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})",  # ISO 8601
            r"(\d{2}:\d{2}:\d{2})",  # HH:MM:SS
        ]

        for line in build_logs.splitlines():
            level = "info"
            if re.search(r"(?i)(fatal|FATAL|FATA\[)", line):
                level = "critical"
            elif re.search(r"(?i)(error|ERROR|ERRO\[)", line):
                level = "error"
            elif re.search(r"(?i)(warn|WARN|⚠️)", line):
                level = "warning"
            elif re.search(r"(?i)(success|SUCCESS|✅|PASS)", line):
                level = "success"
            else:
                continue

            ts = ""
            for pat in ts_patterns:
                m = re.search(pat, line)
                if m:
                    ts = m.group(1)
                    break

            msg = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()[:200]  # Strip ANSI codes
            if msg and level in ("critical", "error", "warning"):
                self.result.error_timeline.append((ts, level, msg))


# ═══════════════════════════════════════════════════════════════════════════════
# HTML Report Renderer
# ═══════════════════════════════════════════════════════════════════════════════

def generate_html_report(diag: BuildDiagnostics, output_path: Path):
    """Generate a visual HTML report from analysis results."""

    # Severity colors
    sev_colors = {
        "critical": {"bg": "#dc2626", "text": "#fff", "badge": "🔴"},
        "high":     {"bg": "#ea580c", "text": "#fff", "badge": "🟠"},
        "medium":   {"bg": "#ca8a04", "text": "#fff", "badge": "🟡"},
        "low":      {"bg": "#16a34a", "text": "#fff", "badge": "🟢"},
    }

    status_colors = {
        "critical": {"bg": "#fef2f2", "border": "#dc2626", "text": "#991b1b", "icon": "💀"},
        "error":    {"bg": "#fff7ed", "border": "#ea580c", "text": "#9a3412", "icon": "❌"},
        "warning":  {"bg": "#fefce8", "border": "#ca8a04", "text": "#854d0e", "icon": "⚠️"},
        "ok":       {"bg": "#f0fdf4", "border": "#16a34a", "text": "#166534", "icon": "✅"},
    }

    # Build dimension cards HTML
    dim_cards = []
    error_count = 0
    warn_count = 0
    ok_count = 0

    for dim_name, dim in diag.dimensions.items():
        sc = status_colors.get(dim.status, status_colors["warning"])
        label = DIMENSION_LABELS.get(dim_name, dim_name)
        findings_html = ""
        if dim.findings:
            findings_items = "".join(f"<li>{html.escape(f)}</li>" for f in dim.findings[:8])
            findings_html = f'<ul class="findings">{findings_items}</ul>'
        dim_cards.append(f"""
        <div class="dim-card" style="border-left: 4px solid {sc['border']}; background: {sc['bg']};">
            <div class="dim-header">
                <span class="dim-icon">{sc['icon']}</span>
                <span class="dim-name">{html.escape(label)}</span>
                <span class="dim-status" style="background: {sc['border']}; color: white;">{dim.status.upper()}</span>
            </div>
            <div class="dim-summary" style="color: {sc['text']};">{html.escape(dim.summary)}</div>
            {findings_html}
        </div>""")
        if dim.status == "critical":
            error_count += 1
        elif dim.status in ("error", "warning"):
            warn_count += 1
        else:
            ok_count += 1

    # Root cause cards
    rc_cards = []
    for i, rc in enumerate(diag.root_causes[:10]):
        sc = sev_colors.get(rc.severity, sev_colors["medium"])
        cat_label = CAT_LABELS.get(rc.category, rc.category)
        prob_pct = int(rc.probability * 100)
        evidence_items = "".join(f"<li>{html.escape(e)}</li>" for e in rc.evidence)
        dim_label = DIMENSION_LABELS.get(rc.dimension, rc.dimension)

        rc_cards.append(f"""
        <div class="rc-card">
            <div class="rc-header" style="background: linear-gradient(135deg, {sc['bg']}, {sc['bg']}dd);">
                <div class="rc-rank">#{i+1}</div>
                <div class="rc-title">
                    <span class="rc-cat">{html.escape(cat_label)}</span>
                    <span class="rc-severity" style="background: rgba(255,255,255,0.25);">{sc['badge']} {rc.severity.upper()}</span>
                </div>
                <div class="rc-prob">
                    <div class="prob-bar">
                        <div class="prob-fill" style="width: {prob_pct}%; background: white;"></div>
                    </div>
                    <span class="prob-text">{prob_pct}% 概率</span>
                </div>
            </div>
            <div class="rc-body">
                <div class="rc-section">
                    <div class="rc-label">🔍 关键证据 (来自{html.escape(dim_label)}):</div>
                    <ul class="rc-evidence">{evidence_items}</ul>
                </div>
                <div class="rc-section fix-section">
                    <div class="rc-label">💡 修复建议:</div>
                    <div class="rc-fix">{html.escape(rc.suggested_fix)}</div>
                </div>
            </div>
        </div>""")

    # Timeline
    timeline_html = ""
    if diag.error_timeline:
        timeline_items = []
        for ts, level, msg in diag.error_timeline[-30:]:  # Last 30 events
            level_icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "success": "🟢"}.get(level, "⚪")
            timeline_items.append(f"""
            <div class="tl-item tl-{level}">
                <span class="tl-icon">{level_icon}</span>
                <span class="tl-time">{html.escape(ts) if ts else '—'}</span>
                <span class="tl-msg">{html.escape(msg)}</span>
            </div>""")
        timeline_html = f"""
        <div class="timeline">
            <h3>错误时间线 (最近{min(len(diag.error_timeline), 30)}条)</h3>
            {''.join(timeline_items)}
        </div>"""

    # Raw data sections (collapsible)
    raw_sections = []
    for dim_name, dim in diag.dimensions.items():
        if dim.raw_content:
            label = DIMENSION_LABELS.get(dim_name, dim_name)
            content_id = f"raw-{dim_name}"
            raw_sections.append(f"""
            <details class="raw-section">
                <summary>{html.escape(label)} ({dim.file})</summary>
                <pre class="raw-content">{html.escape(dim.raw_content[:5000])}</pre>
            </details>""")

    # Summary stats
    total_dims = len(diag.dimensions)
    health_pct = int(((ok_count) / max(total_dims, 1)) * 100)
    health_color = "#16a34a" if error_count == 0 else ("#ea580c" if warn_count > 0 else "#dc2626")

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevContainer 构建故障诊断报告</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
    background: #f8fafc;
    color: #1e293b;
    line-height: 1.6;
    padding: 20px;
}}
.container {{ max-width: 1200px; margin: 0 auto; }}

.header {{
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 32px;
    border-radius: 16px;
    margin-bottom: 24px;
}}
.header h1 {{ font-size: 24px; margin-bottom: 8px; }}
.header .subtitle {{ opacity: 0.8; font-size: 14px; }}
.meta-row {{ display: flex; gap: 24px; margin-top: 16px; flex-wrap: wrap; }}
.meta-item {{ font-size: 13px; opacity: 0.9; }}
.meta-item strong {{ margin-right: 6px; }}

.health-overview {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}}
.stat-card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.stat-value {{ font-size: 36px; font-weight: 700; margin-bottom: 4px; }}
.stat-label {{ font-size: 13px; color: #64748b; }}
.stat-critical .stat-value {{ color: #dc2626; }}
.stat-error .stat-value {{ color: #ea580c; }}
.stat-warning .stat-value {{ color: #ca8a04; }}
.stat-ok .stat-value {{ color: #16a34a; }}

.section {{
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.section h2 {{
    font-size: 18px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f1f5f9;
}}

.dim-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 12px;
}}
.dim-card {{
    border-radius: 8px;
    padding: 14px;
    transition: transform 0.15s;
}}
.dim-card:hover {{ transform: translateY(-2px); }}
.dim-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
.dim-icon {{ font-size: 18px; }}
.dim-name {{ font-weight: 600; flex: 1; font-size: 14px; }}
.dim-status {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
}}
.dim-summary {{ font-size: 13px; margin-bottom: 6px; }}
.findings {{ margin: 0; padding-left: 18px; font-size: 12px; }}
.findings li {{ margin-bottom: 3px; line-height: 1.4; color: #475569; }}

.rc-list {{ display: flex; flex-direction: column; gap: 16px; }}
.rc-card {{
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
}}
.rc-header {{
    padding: 14px 18px;
    color: white;
    display: flex;
    align-items: center;
    gap: 14px;
}}
.rc-rank {{
    font-size: 20px;
    font-weight: 800;
    opacity: 0.9;
    min-width: 32px;
}}
.rc-title {{ flex: 1; }}
.rc-cat {{ font-size: 15px; font-weight: 600; display: block; }}
.rc-severity {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-top: 4px; display: inline-block; }}
.rc-prob {{ min-width: 120px; text-align: right; }}
.prob-bar {{
    height: 6px;
    background: rgba(255,255,255,0.3);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 4px;
}}
.prob-fill {{ height: 100%; border-radius: 3px; transition: width 0.5s; }}
.prob-text {{ font-size: 12px; opacity: 0.9; }}
.rc-body {{ padding: 14px 18px; }}
.rc-section {{ margin-bottom: 12px; }}
.rc-section:last-child {{ margin-bottom: 0; }}
.rc-label {{ font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px; }}
.rc-evidence {{ padding-left: 18px; font-size: 12px; color: #64748b; }}
.rc-evidence li {{ margin-bottom: 3px; }}
.fix-section {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 12px;
}}
.rc-fix {{ font-size: 13px; color: #166534; line-height: 1.5; }}

.timeline {{ }}
.tl-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 13px;
}}
.tl-icon {{ min-width: 22px; }}
.tl-time {{ min-width: 80px; color: #94a3b8; font-family: monospace; font-size: 12px; }}
.tl-msg {{ flex: 1; color: #475569; }}
.tl-critical .tl-msg {{ color: #dc2626; font-weight: 500; }}
.tl-error .tl-msg {{ color: #ea580c; }}
.tl-warning .tl-msg {{ color: #ca8a04; }}

.raw-section {{
    margin-bottom: 8px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
}}
.raw-section summary {{
    padding: 10px 14px;
    background: #f8fafc;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
}}
.raw-section summary:hover {{ background: #f1f5f9; }}
.raw-content {{
    padding: 14px;
    background: #1e293b;
    color: #94a3b8;
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    font-size: 11px;
    line-height: 1.5;
    overflow-x: auto;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}}

.footer {{
    text-align: center;
    padding: 20px;
    font-size: 12px;
    color: #94a3b8;
}}

@media (max-width: 768px) {{
    .health-overview {{ grid-template-columns: repeat(2, 1fr); }}
    .dim-grid {{ grid-template-columns: 1fr; }}
    .rc-header {{ flex-wrap: wrap; }}
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🔬 DevContainer 构建故障诊断报告</h1>
        <div class="subtitle">基于10维诊断体系的自动化根因分析</div>
        <div class="meta-row">
            <div class="meta-item"><strong>📂 诊断目录:</strong> {html.escape(str(diag.source_dir))}</div>
            <div class="meta-item"><strong>🕐 生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            {f'<div class="meta-item"><strong>🔨 失败阶段:</strong> {html.escape(diag.variant)}</div>' if diag.variant else ''}
            {f'<div class="meta-item"><strong>📝 构建时间:</strong> {html.escape(diag.build_time)}</div>' if diag.build_time else ''}
        </div>
    </div>

    <div class="health-overview">
        <div class="stat-card stat-critical">
            <div class="stat-value">{sum(1 for d in diag.dimensions.values() if d.status == 'critical')}</div>
            <div class="stat-label">💀 严重问题</div>
        </div>
        <div class="stat-card stat-error">
            <div class="stat-value">{sum(1 for d in diag.dimensions.values() if d.status == 'error')}</div>
            <div class="stat-label">❌ 错误</div>
        </div>
        <div class="stat-card stat-warning">
            <div class="stat-value">{sum(1 for d in diag.dimensions.values() if d.status == 'warning')}</div>
            <div class="stat-label">⚠️ 警告</div>
        </div>
        <div class="stat-card stat-ok">
            <div class="stat-value">{ok_count}</div>
            <div class="stat-label">✅ 正常</div>
        </div>
    </div>

    <div class="section">
        <h2>🎯 根因分析 (按概率排序)</h2>
        <div class="rc-list">
            {''.join(rc_cards) if rc_cards else '<p style="color:#64748b;">未识别到明确根因，请查看下方原始诊断数据</p>'}
        </div>
    </div>

    <div class="section">
        <h2>📊 10维健康仪表盘</h2>
        <div class="dim-grid">
            {''.join(dim_cards)}
        </div>
    </div>

    {f'''<div class="section">
        <h2>⏱️ 错误时间线</h2>
        {timeline_html}
    </div>''' if timeline_html else ''}

    <div class="section">
        <h2>📄 原始诊断数据</h2>
        {''.join(raw_sections)}
    </div>

    <div class="footer">
        Generated by DevContainer Diagnostics Analyzer | 10-Dimension Diagnosis System
    </div>
</div>
</body>
</html>"""

    output_path.write_text(html_content, encoding='utf-8')
    return output_path


# ═══════════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="DevContainer CI Build Failure Diagnostics Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 analyze-diagnostics.py /tmp/diag-abc123/
  python3 analyze-diagnostics.py /tmp/diag-abc123/ -o my-report.html
  python3 analyze-diagnostics.py artifacts.zip
  python3 analyze-diagnostics.py /tmp/diag-abc123/ --open
        """
    )
    parser.add_argument("diagnostics_dir", help="Path to diagnostics directory or zip file")
    parser.add_argument("-o", "--output", default=None, help="Output HTML file path (default: <dir>/diagnostic-report.html)")
    parser.add_argument("--text", action="store_true", help="Also print text summary to stdout")
    parser.add_argument("--open", action="store_true", help="Open report in browser after generation")

    args = parser.parse_args()
    source = Path(args.diagnostics_dir)

    if not source.exists():
        print(f"Error: {source} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"🔬 Analyzing diagnostics from: {source}")
    analyzer = DiagnosticsAnalyzer(source)

    if not analyzer.load():
        print(f"Error: No diagnostic files found in {source}", file=sys.stderr)
        print("Expected files: " + ", ".join(DIMENSION_FILES.values()), file=sys.stderr)
        sys.exit(1)

    result = analyzer.analyze()

    # Determine output path
    if args.output:
        output = Path(args.output)
    else:
        out_dir = source if source.is_dir() else Path.cwd()
        if source.is_file() and source.suffix == '.zip':
            out_dir = result.source_dir
        output = out_dir / "diagnostic-report.html"

    generate_html_report(result, output)
    print(f"✅ Report generated: {output}")

    # Print text summary
    if args.text or True:  # Always print summary
        print(f"\n{'='*60}")
        print("📊 诊断摘要")
        print(f"{'='*60}")
        crit = sum(1 for d in result.dimensions.values() if d.status == 'critical')
        err = sum(1 for d in result.dimensions.values() if d.status == 'error')
        warn = sum(1 for d in result.dimensions.values() if d.status == 'warning')
        ok = sum(1 for d in result.dimensions.values() if d.status == 'ok')
        print(f"  💀 严重: {crit}  ❌ 错误: {err}  ⚠️ 警告: {warn}  ✅ 正常: {ok}")
        print()

        if result.root_causes:
            print("🎯 根因排名:")
            for i, rc in enumerate(result.root_causes[:5]):
                prob = int(rc.probability * 100)
                label = CAT_LABELS.get(rc.category, rc.category)
                print(f"  #{i+1} [{prob:3d}%] {label} ({rc.severity})")
                print(f"      💡 {rc.suggested_fix}")
        else:
            print("  未识别到明确根因")

        print(f"\n📄 HTML报告: {output}")

    if args.open:
        import webbrowser
        webbrowser.open(f"file://{output.resolve()}")


if __name__ == "__main__":
    main()
