#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径迁移自动化脚本模板
五步法：常量先行→元数据迁移→引用批量修复→ID同步→分层验证

日志级别说明：
- INFO: 关键步骤、进度、汇总统计
- DEBUG: 每个文件的详细操作、匹配行详情、git命令输出
- WARNING: 非致命问题（跳过的文件、编码问题）
- ERROR: 致命错误（文件写入失败、git提交失败）
"""
import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# ============================================================================
# 配置区 - 根据实际迁移任务修改
# ============================================================================
OLD_PATH = ".agents/scripts/ci-check"
NEW_PATH = ".agents/scripts/ci"
MIGRATION_NAME = "ci-path-migration"
TOML_MIRROR_ROOT = Path(".meta/toml")
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

DRY_RUN = False
VERBOSE = False

SKIP_DIRS = {
    ".git", "__pycache__", ".pytest_cache", "node_modules", "vendor", ".venv",
    ".temp", ".gitcode", "external", "_build", "build", "dist", ".tox", ".mypy_cache",
    ".idea", ".vscode"
}
SCRIPT_EXTS = {".py", ".ps1", ".sh"}
DOC_EXTS = {".md"}
CONFIG_EXTS = {".toml", ".yaml", ".yml", ".json"}

TRACE = 5
logging.addLevelName(TRACE, "TRACE")
def trace(msg, *args, **kwargs):
    logger.log(TRACE, msg, *args, **kwargs)

# ============================================================================
# 日志设置
# ============================================================================
def setup_logging(verbose: bool = False, trace: bool = False):
    if trace:
        level = TRACE
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-7s] [%(funcName)-20s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
logger = logging.getLogger(__name__)

def log_section(title: str):
    logger.info("=" * 70)
    logger.info(f"  {title}")
    logger.info("=" * 70)

def log_subsection(title: str):
    logger.info("-" * 50)
    logger.info(f"  {title}")
    logger.info("-" * 50)

# ============================================================================
# 结果数据类
# ============================================================================
@dataclass
class Result:
    step: str
    modified: List[Path] = field(default_factory=list)
    moved: List[Tuple[Path, Path]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration: float = 0.0
    success: bool = True

    def summary(self) -> str:
        status = "OK" if self.success else "FAIL"
        return (f"[{self.step}] {status} "
                f"Modified:{len(self.modified)} Moved:{len(self.moved)} "
                f"Warn:{len(self.warnings)} Err:{len(self.errors)} "
                f"Time:{self.duration:.2f}s")

    def detail(self) -> str:
        lines = [self.summary()]
        if self.modified:
            lines.append("  修改的文件:")
            for f in self.modified[:10]:
                lines.append(f"    - {f.relative_to(PROJECT_ROOT)}")
            if len(self.modified) > 10:
                lines.append(f"    ... 还有{len(self.modified)-10}个文件")
        if self.moved:
            lines.append("  移动的文件/目录:")
            for old, new in self.moved:
                lines.append(f"    - {old} -> {new}")
        if self.warnings:
            lines.append("  警告:")
            for w in self.warnings[:5]:
                lines.append(f"    ! {w}")
        if self.errors:
            lines.append("  错误:")
            for e in self.errors:
                lines.append(f"    X {e}")
        return "\n".join(lines)

# ============================================================================
# 工具函数
# ============================================================================
def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False

def safe_relpath(p: Path) -> str:
    try:
        return str(p.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(p)

def run_git(args: List[str], check: bool = False) -> subprocess.CompletedProcess:
    cmd = ["git"] + args
    logger.debug(f"  GIT: {' '.join(cmd)}")
    start = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=PROJECT_ROOT,
            encoding="utf-8", errors="replace"
        )
        elapsed = time.time() - start
        if result.stdout.strip():
            logger.debug(f"  git-stdout ({elapsed:.2f}s):\n{result.stdout.strip()}")
        if result.stderr.strip():
            logger.debug(f"  git-stderr ({elapsed:.2f}s):\n{result.stderr.strip()}")
        if check and result.returncode != 0:
            logger.error(f"  git命令失败 (exit={result.returncode}): {' '.join(cmd)}")
        return result
    except FileNotFoundError:
        logger.error("  错误: 未找到git命令")
        raise
    except Exception as e:
        logger.error(f"  git命令异常: {type(e).__name__}: {e}")
        raise

# ============================================================================
# 四层扫描 - 详细日志版
# ============================================================================
def find_files(exts: Set[str], desc: str = "") -> List[Path]:
    log_subsection(f"扫描{desc}文件 (扩展名: {sorted(exts)})")
    start_time = time.time()
    result = []
    dirs_scanned = 0
    dirs_skipped = 0
    files_seen = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):
        root_path = Path(root)
        dirs_scanned += 1
        skip_dirs = [d for d in dirs if d in SKIP_DIRS]
        if skip_dirs:
            dirs_skipped += len(skip_dirs)
            logger.log(TRACE, f"  目录 {safe_relpath(root_path)}: 跳过 {skip_dirs}")
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for f in files:
            files_seen += 1
            p = root_path / f
            if p.suffix in exts and not should_skip(p):
                result.append(p)

    elapsed = time.time() - start_time
    logger.info(f"  完成: 遍历{dirs_scanned}目录(跳过{dirs_skipped}), 检查{files_seen}文件, 找到{len(result)}目标文件, 耗时{elapsed:.2f}s")
    return result

def scan_layer(name: str, exts: Set[str], patterns: List[re.Pattern]) -> Dict[Path, List[Tuple[int, str]]]:
    log_subsection(f"扫描层: {name}")
    start_time = time.time()
    results = {}
    files = find_files(exts, desc=name)
    total_matches = 0
    read_errors = 0

    for idx, f in enumerate(files, 1):
        rel = safe_relpath(f)
        if idx % 100 == 0 or idx == len(files):
            logger.debug(f"  进度: {idx}/{len(files)} ({idx*100//len(files)}%)")
        matches = []
        try:
            content = f.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                for pat in patterns:
                    if pat.search(line):
                        matches.append((i, line.strip()))
                        logger.debug(f"    MATCH @ {rel}:{i}: {line.strip()[:100]}")
                        break
        except UnicodeDecodeError:
            read_errors += 1
            logger.warning(f"  编码错误(尝试gbk): {rel}")
            try:
                content = f.read_text(encoding="gbk", errors="replace")
                for i, line in enumerate(content.splitlines(), 1):
                    for pat in patterns:
                        if pat.search(line):
                            matches.append((i, line.strip()))
                            logger.debug(f"    MATCH(gbk) @ {rel}:{i}: {line.strip()[:100]}")
                            break
            except Exception as e2:
                logger.error(f"  读取失败 {rel}: {e2}")
        except PermissionError:
            read_errors += 1
            logger.warning(f"  权限不足: {rel}")
        except Exception as e:
            read_errors += 1
            logger.warning(f"  读取异常 {rel}: {type(e).__name__}: {e}")
        if matches:
            results[f] = matches
            total_matches += len(matches)
            logger.info(f"  发现{len(matches)}处引用: {rel}")

    elapsed = time.time() - start_time
    logger.info(f"  {name}层完成: {len(results)}文件含旧路径, {total_matches}处匹配, 读错{read_errors}, 耗时{elapsed:.2f}s")

    if results and VERBOSE:
        logger.debug("  详细匹配列表:")
        for f, mlist in results.items():
            logger.debug(f"    {safe_relpath(f)}: {len(mlist)}处")
            for ln, line in mlist[:3]:
                logger.debug(f"      L{ln}: {line[:80]}")
            if len(mlist) > 3:
                logger.debug(f"      ... 还有{len(mlist)-3}处")
    return results

def scan_all() -> Dict[str, Dict]:
    log_section("开始四层路径依赖扫描")
    start_time = time.time()
    logger.info(f"  旧路径: {OLD_PATH}")
    logger.info(f"  新路径: {NEW_PATH}")
    logger.info(f"  项目根: {PROJECT_ROOT}")

    pat = re.compile(re.escape(OLD_PATH))
    wiki_pat = re.compile(r"\[\[.*?" + re.escape(OLD_PATH))
    link_pat = re.compile(r"\]\([^)]*?" + re.escape(OLD_PATH))
    xref_pat = re.compile(r"x-toml-ref:.*?" + re.escape(OLD_PATH))

    layers = [
        ("scripts", "脚本路径", SCRIPT_EXTS, [pat]),
        ("toml", "TOML元数据", CONFIG_EXTS, [pat]),
        ("markdown", "Markdown引用", DOC_EXTS, [wiki_pat, link_pat, xref_pat, pat]),
        ("tests", "测试路径", SCRIPT_EXTS | DOC_EXTS | CONFIG_EXTS, [pat]),
    ]
    results = {}
    total_files = 0
    total_matches = 0
    for key, name, exts, patterns in layers:
        layer_result = scan_layer(name, exts, patterns)
        results[key] = layer_result
        total_files += len(layer_result)
        total_matches += sum(len(v) for v in layer_result.values())

    elapsed = time.time() - start_time
    log_section("扫描汇总")
    logger.info(f"  总耗时: {elapsed:.2f}s")
    logger.info(f"  含旧路径文件: {total_files}")
    logger.info(f"  匹配引用总数: {total_matches}")
    for key, name, _, _ in layers:
        layer = results[key]
        mc = sum(len(v) for v in layer.values())
        logger.info(f"    - {name}: {len(layer)}文件, {mc}处匹配")
    all_files = set()
    for layer in results.values():
        all_files.update(layer.keys())
    logger.info(f"  去重后唯一文件: {len(all_files)}")
    return results

# ============================================================================
# 原子提交 - 详细日志版
# ============================================================================
def git_status() -> str:
    logger.debug("  获取git status...")
    result = run_git(["status", "--short"])
    status = result.stdout.strip()
    if status:
        lines = status.splitlines()
        logger.debug(f"  当前变更 ({len(lines)}个文件):")
        for line in lines[:20]:
            logger.debug(f"    {line}")
        if len(lines) > 20:
            logger.debug(f"    ... 还有{len(lines)-20}个")
    else:
        logger.debug("  工作区干净")
    return status

def git_diff_stat() -> str:
    logger.debug("  获取diff --stat...")
    result = run_git(["diff", "--stat", "HEAD"])
    if result.stdout.strip():
        logger.debug(f"  Diff统计:\n{result.stdout.strip()}")
    return result.stdout.strip()

def git_commit(msg: str, files: Optional[List[Path]] = None) -> bool:
    log_subsection(f"原子提交: {msg}")
    start_time = time.time()

    if DRY_RUN:
        logger.info(f"  [DRY-RUN] 将执行:")
        if files:
            logger.info(f"    git add ({len(files)}个文件)")
            for f in files[:10]:
                logger.info(f"      - {safe_relpath(f)}")
        else:
            logger.info(f"    git add -A")
        logger.info(f"    git commit -m \"{msg}\"")
        logger.info(f"  [DRY-RUN] 模拟完成")
        return True

    try:
        status_before = git_status()
        staged_before = len([l for l in status_before.splitlines() if l[:2] in ("A ", "M ", "R ", "D ", "AM")])
        logger.info(f"  提交前已暂存: {staged_before}个文件")

        logger.info("  执行git add...")
        if files:
            file_args = [str(f.relative_to(PROJECT_ROOT)) for f in files]
            run_git(["add"] + file_args, check=True)
            logger.info(f"  已add {len(files)}个指定文件")
        else:
            run_git(["add", "-A"], check=True)
            logger.info("  已执行git add -A")

        cached = run_git(["diff", "--cached", "--stat"])
        if cached.stdout.strip():
            logger.debug(f"  暂存区内容:\n{cached.stdout.strip()}")
        else:
            logger.warning("  警告: 暂存区无变更")

        logger.info(f"  执行git commit...")
        commit_result = run_git(["commit", "-m", msg])

        if commit_result.returncode == 0:
            elapsed = time.time() - start_time
            logger.info(f"  COMMIT OK! 耗时{elapsed:.2f}s")
            if commit_result.stdout.strip():
                for line in commit_result.stdout.strip().splitlines():
                    logger.info(f"    {line}")
            git_status()
            return True
        else:
            stderr = commit_result.stderr.strip()
            if "nothing to commit" in stderr or "nothing added to commit" in stderr:
                logger.warning("  无内容需要提交（可能已包含）")
                return True
            logger.error(f"  COMMIT FAILED!")
            logger.error(f"  stdout: {commit_result.stdout.strip()}")
            logger.error(f"  stderr: {stderr}")
            return False
    except Exception as e:
        logger.error(f"  提交异常: {type(e).__name__}: {e}", exc_info=VERBOSE)
        return False

# ============================================================================
# 文件操作 - 详细日志版
# ============================================================================
def replace_in_file(fpath: Path, old: str, new: str, dry_run: Optional[bool] = None) -> Tuple[bool, int]:
    if dry_run is None:
        dry_run = DRY_RUN
    rel = safe_relpath(fpath)
    try:
        content = fpath.read_text(encoding="utf-8")
        count = content.count(old)
        if count == 0:
            return False, 0
        logger.debug(f"  {rel}: 发现{count}处匹配")

        if VERBOSE and count <= 5:
            for i, line in enumerate(content.splitlines(), 1):
                if old in line:
                    logger.debug(f"    L{i}(-): {line.strip()[:80]}")
                    logger.debug(f"    L{i}(+): {line.replace(old, new).strip()[:80]}")

        if not dry_run:
            fpath.write_text(content.replace(old, new), encoding="utf-8")
            logger.debug(f"  已写入: {rel}")
        return True, count
    except UnicodeDecodeError:
        logger.warning(f"  编码错误(gbk重试): {rel}")
        try:
            content = fpath.read_text(encoding="gbk", errors="replace")
            count = content.count(old)
            if count == 0:
                return False, 0
            if not dry_run:
                fpath.write_text(content.replace(old, new), encoding="utf-8")
            logger.debug(f"  已写入(gbk): {rel}")
            return True, count
        except Exception as e2:
            logger.error(f"  写入失败 {rel}: {e2}")
            return False, 0
    except PermissionError:
        logger.error(f"  权限不足: {rel}")
        return False, 0
    except Exception as e:
        logger.error(f"  替换失败 {rel}: {type(e).__name__}: {e}")
        return False, 0

# ============================================================================
# 五步法执行 - 详细日志版
# ============================================================================
def step1_constants(scan: Dict) -> Result:
    log_section("STEP 1: 常量先行 - 更新脚本硬编码路径")
    start_time = time.time()
    r = Result(step="S1")
    logger.info("  策略: 先更新路径常量，避免移动后脚本失效")
    scripts_layer = scan.get("scripts", {})
    logger.info(f"  脚本层: {len(scripts_layer)}个文件待更新")

    const_file = PROJECT_ROOT / ".agents" / "scripts" / "constants.py"
    if const_file.exists():
        m, c = replace_in_file(const_file, OLD_PATH, NEW_PATH)
        if m:
            r.modified.append(const_file)
            logger.info(f"  已更新constants.py: {c}处")
    else:
        r.warnings.append(f"constants.py不存在")
        logger.warning(f"  常量文件不存在")

    total_c = 0
    for f in scripts_layer:
        m, c = replace_in_file(f, OLD_PATH, NEW_PATH)
        if m:
            r.modified.append(f)
            total_c += c
    logger.info(f"  共更新{len(r.modified)}个脚本, {total_c}处引用")
    r.duration = time.time() - start_time
    logger.info(f"\n{r.detail()}")
    return r

def step2_toml(scan: Dict) -> Result:
    log_section("STEP 2: 元数据迁移 - TOML镜像同步")
    start_time = time.time()
    r = Result(step="S2")
    logger.info("  策略: 保持TOML元数据与Markdown镜像结构一致")
    old_toml = TOML_MIRROR_ROOT / OLD_PATH
    new_toml = TOML_MIRROR_ROOT / NEW_PATH

    if old_toml.exists():
        logger.info(f"  发现旧TOML目录: {old_toml}")
        if not DRY_RUN:
            new_toml.parent.mkdir(parents=True, exist_ok=True)
            if new_toml.exists():
                logger.warning(f"  目标已存在，合并")
            shutil.move(str(old_toml), str(new_toml))
            logger.info(f"  已移动TOML: {old_toml} -> {new_toml}")
        else:
            logger.info(f"  [DRY-RUN] 将移动: {old_toml} -> {new_toml}")
        r.moved.append((old_toml, new_toml))
    else:
        r.warnings.append(f"旧TOML位置不存在: {old_toml}")
        logger.warning(f"  旧TOML不存在（可能已迁移）")

    logger.info("  更新TOML文件内容...")
    toml_layer = scan.get("toml", {})
    tc = 0
    for f in toml_layer:
        m, c = replace_in_file(f, OLD_PATH, NEW_PATH)
        if m:
            r.modified.append(f)
            tc += c
    logger.info(f"  更新{len(r.modified)}个TOML, {tc}处引用")
    r.duration = time.time() - start_time
    logger.info(f"\n{r.detail()}")
    return r

def step3_xref(scan: Dict) -> Result:
    log_section("STEP 3: 引用批量修复")
    start_time = time.time()
    r = Result(step="S3")
    logger.info("  策略: 批量修复所有引用（禁止手动sed替换）")
    all_files = set()
    for cat_name, cat_data in scan.items():
        logger.info(f"  {cat_name}层: {len(cat_data)}个文件")
        all_files.update(cat_data.keys())
    logger.info(f"  去重: {len(all_files)}个文件")
    tc = 0
    for f in all_files:
        m, c = replace_in_file(f, OLD_PATH, NEW_PATH)
        if m:
            r.modified.append(f)
            tc += c
    logger.info(f"  共修复{len(r.modified)}个文件, {tc}处引用")
    fix_script = PROJECT_ROOT / ".agents" / "scripts" / "fix-x-toml-ref.py"
    if fix_script.exists():
        logger.info(f"  建议运行fix-x-toml-ref.py验证相对路径深度")
    r.duration = time.time() - start_time
    logger.info(f"\n{r.detail()}")
    return r

def step4_files(scan: Dict) -> Result:
    log_section("STEP 4: 文件物理移动 + ID同步")
    start_time = time.time()
    r = Result(step="S4")
    logger.info("  策略: 物理移动目录，然后检查id一致性")
    old_base = PROJECT_ROOT / OLD_PATH
    new_base = PROJECT_ROOT / NEW_PATH
    logger.info(f"  源: {old_base}")
    logger.info(f"  目标: {new_base}")
    if old_base.exists():
        if not DRY_RUN:
            new_base.parent.mkdir(parents=True, exist_ok=True)
            if new_base.exists():
                logger.warning(f"  目标已存在，合并")
                for item in old_base.iterdir():
                    target = new_base / item.name
                    if target.exists():
                        if target.is_dir():
                            shutil.rmtree(target)
                        else:
                            target.unlink()
                    shutil.move(str(item), str(target))
                try:
                    old_base.rmdir()
                except OSError as e:
                    r.warnings.append(f"源目录非空未删除")
            else:
                shutil.move(str(old_base), str(new_base))
            logger.info(f"  已移动: {old_base} -> {new_base}")
        else:
            logger.info(f"  [DRY-RUN] 将移动: {old_base} -> {new_base}")
        r.moved.append((old_base, new_base))
    else:
        r.warnings.append(f"源位置不存在: {old_base}")
        logger.warning(f"  源位置不存在")
    logger.info("  ID同步原则: 以Markdown frontmatter为准更新TOML")
    r.duration = time.time() - start_time
    logger.info(f"\n{r.detail()}")
    return r

def step5_verify(scan: Dict) -> Result:
    log_section("STEP 5: 分层验证")
    start_time = time.time()
    r = Result(step="S5")
    new_p = PROJECT_ROOT / NEW_PATH
    logger.info("  检查1: 新路径是否存在")
    if new_p.exists():
        if new_p.is_dir():
            fc = sum(1 for _ in new_p.rglob("*") if _.is_file())
            logger.info(f"  OK: 新路径存在, {fc}个文件")
        else:
            logger.info(f"  OK: 新路径存在(文件)")
    else:
        r.errors.append(f"新路径不存在: {safe_relpath(new_p)}")
        r.success = False
        logger.error(f"  FAIL: 新路径不存在")

    old_p = PROJECT_ROOT / OLD_PATH
    logger.info("  检查2: 旧路径是否移除")
    if old_p.exists():
        r.warnings.append(f"旧路径仍存在: {safe_relpath(old_p)}")
        logger.warning(f"  WARN: 旧路径仍存在")
    else:
        logger.info(f"  OK: 旧路径已移除")

    logger.info("  检查3: 复扫旧路径引用")
    rescan = scan_all()
    total_rem = sum(len(v) for v in rescan.values())
    if total_rem > 0:
        r.errors.append(f"仍有{total_rem}个文件含旧路径")
        r.success = False
        for ln, ld in rescan.items():
            if ld:
                logger.warning(f"  WARN: {ln}层有{len(ld)}个残留")
                if VERBOSE:
                    for f, ml in ld.items():
                        logger.warning(f"    - {safe_relpath(f)}")
        logger.error(f"  FAIL: 仍有残留引用")
    else:
        logger.info(f"  OK: 无残留旧路径引用")

    logger.info("  建议验证命令:")
    logger.info(f"    python .agents/scripts/check-version-ripple.py --root .agents/docs --bootstrap")
    logger.info(f"    python -m pytest .agents/scripts/tests/ -v")
    logger.info(f"    python .agents/scripts/check-links.py")
    r.duration = time.time() - start_time
    logger.info(f"\n{r.detail()}")
    return r

# ============================================================================
# 主函数
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="路径迁移五步法自动化脚本（带详细日志）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="试运行不实际修改")
    parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG级别详细日志")
    parser.add_argument("--trace", action="store_true", help="TRACE级别（含每个跳过目录等最细粒度日志）")
    parser.add_argument("--scan-only", action="store_true", help="只扫描不执行")
    parser.add_argument("--no-commit", action="store_true", help="执行修改但不提交")
    args = parser.parse_args()

    global DRY_RUN, VERBOSE
    DRY_RUN = args.dry_run
    VERBOSE = args.verbose
    TRACE_ENABLED = args.trace
    setup_logging(VERBOSE, TRACE_ENABLED)

    log_section(f"路径迁移启动: {OLD_PATH} -> {NEW_PATH}")
    logger.info(f"  迁移名: {MIGRATION_NAME}")
    logger.info(f"  模式: {'DRY-RUN' if DRY_RUN else 'LIVE'}")
    if TRACE_ENABLED:
        log_level = "TRACE"
    elif VERBOSE:
        log_level = "DEBUG"
    else:
        log_level = "INFO"
    logger.info(f"  日志: {log_level}")
    logger.info(f"  跳过目录: {sorted(SKIP_DIRS)}")
    total_start = time.time()

    scan = scan_all()
    if args.scan_only:
        log_section("扫描完成，退出")
        return 0

    steps = [
        (step1_constants, f"refactor(path): {MIGRATION_NAME} step1 - constants"),
        (step2_toml, f"refactor(metadata): {MIGRATION_NAME} step2 - toml"),
        (step3_xref, f"fix(xref): {MIGRATION_NAME} step3 - xref"),
        (step4_files, f"refactor(files): {MIGRATION_NAME} step4 - move"),
        (step5_verify, None),
    ]

    results = []
    all_modified = set()
    for func, cmsg in steps:
        res = func(scan)
        results.append(res)
        all_modified.update(res.modified)
        if not res.success:
            logger.error(f"  {res.step}失败，终止")
            return 1
        if cmsg and (res.modified or res.moved) and not args.no_commit:
            files_to_commit = list(set(res.modified + [p[0] for p in res.moved] + [p[1] for p in res.moved]))
            ok = git_commit(cmsg, files=files_to_commit)
            if not ok:
                logger.error("  提交失败，终止")
                return 1

    total_elapsed = time.time() - total_start
    log_section("迁移完成汇总")
    logger.info(f"  总耗时: {total_elapsed:.2f}s")
    logger.info(f"  总修改: {len(all_modified)}文件")
    logger.info(f"  总移动: {sum(len(r.moved) for r in results)}项")
    logger.info(f"  警告: {sum(len(r.warnings) for r in results)}")
    logger.info(f"  错误: {sum(len(r.errors) for r in results)}")
    for r in results:
        logger.info(f"    {r.summary()}")

    if not args.no_commit and not DRY_RUN:
        git_status()
        logger.info("  最近提交:")
        lr = run_git(["log", "--oneline", "-5"])
        if lr.stdout.strip():
            for line in lr.stdout.strip().splitlines():
                logger.info(f"    {line}")
    logger.info("\n迁移流程执行完毕")
    return 0

if __name__ == "__main__":
    sys.exit(main())
