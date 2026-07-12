"""spec_loader 生产环境集成测试。

覆盖真实生产场景：
1. CLI命令端到端测试（benchmark/cache-stats/cache-clear/audit/task）
2. 真实项目根目录下的冷启动→温启动→缓存命中全流程
3. 多任务类型连续加载（代码审查→提交→复盘→mermaid→链接检查）
4. 缓存mtime失效（文件修改后自动重新加载）
5. 跨实例一致性（多loader实例共享缓存）
6. 配置文件加载验证
7. 快速连续加载（模拟高频调用）
8. 所有TASK_ROUTING路由的L2文件存在性审计
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from lib.spec_loader import SpecLoader, TASK_ROUTING, CACHE_FILENAME

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
CLI = SCRIPTS_DIR / "spec-loader.py"
passed = 0
failed = 0
errors = []


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        errors.append(f"{name}: {detail}")
        print(f"  [FAIL] {name} -- {detail}")


def run_cli(*args) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


print("=" * 70)
print("spec_loader 生产环境集成测试")
print(f"项目根目录: {PROJECT_ROOT}")
print("=" * 70)

# ── PHASE 1: CLI 命令端到端测试 ──────────────────────────────────
print("\n--- PHASE 1: CLI 命令端到端测试 ---")

print("\n[1.1] cache-clear")
code, out = run_cli("cache-clear")
check("cache-clear 退出码为0", code == 0, f"code={code}")
check("cache-clear 输出确认", "已清除" in out or "清除" in out, out[:200])

print("\n[1.2] benchmark（生产配置）")
code, out = run_cli("benchmark")
check("benchmark 退出码为0", code == 0, f"code={code}")
check("benchmark 包含冷启动", "冷启动" in out)
check("benchmark 包含温启动", "温启动" in out)
check("benchmark 包含综合平均", "综合平均" in out)
check("benchmark 命中率100%", "100%" in out)
import re
warm_match = re.search(r"综合平均\s*\|([^|]+)\|([^|]+)", out)
if warm_match:
    cold = float(warm_match.group(1).strip())
    warm = float(warm_match.group(2).strip())
    check(f"冷启动 < 2ms ({cold:.2f}ms)", cold < 2.0, f"冷启动过慢")
    check(f"温启动 < 0.5ms ({warm:.2f}ms)", warm < 0.5, f"温启动过慢")
    check(f"加速比 > 2.5x ({cold/warm:.1f}x)", cold/warm > 2.5)

print("\n[1.3] cache-stats")
code, out = run_cli("cache-stats")
check("cache-stats 退出码为0", code == 0)
check("cache-stats 包含版本", "缓存版本" in out)
check("cache-stats 包含条目数", "条目数量" in out)
entry_match = re.search(r"条目数量:\s*(\d+)", out)
if entry_match:
    check(f"缓存条目 >= 5 ({entry_match.group(1)})", int(entry_match.group(1)) >= 5)

print("\n[1.4] audit（路由文件审计）")
code, out = run_cli("audit")
check("audit 退出码为0", code == 0, f"code={code}, out={out[:300]}")

print("\n[1.5] task execution")
code, out = run_cli("task", "代码审查")
check("task execution 退出码为0", code == 0, f"code={code}")

print("\n[1.6] task planning（含L1b）")
code, out = run_cli("task", "代码审查", "--stage", "planning")
check("task planning 退出码为0", code == 0, f"code={code}, err={out[:300]}")

# ── PHASE 2: 冷启动→温启动全流程（用临时目录隔离） ─────────────
print("\n--- PHASE 2: 冷启动→温启动全流程（隔离临时项目） ---")

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    agents = root / ".agents"
    agents.mkdir()
    config_dir = agents / "config"
    config_dir.mkdir(parents=True)
    for name, content in [
        ("ONBOARDING.md", "# L0\nEntry content"),
        ("global-core-rules.md", "# Core\nRules content"),
        ("capability-boundaries.md", "# Bound\nBoundaries content"),
        ("capability-registry.md", "# Reg\nRegistry content"),
        ("context-routing.md", "# Route\nRouting content"),
    ]:
        (agents / name).write_text(content, encoding="utf-8")
    (agents / "skills").mkdir()
    (agents / "skills" / "README.md").write_text("# Skills\nIndex", encoding="utf-8")
    wf_dir = agents / "workflows"
    wf_dir.mkdir()
    (wf_dir / "code-review.md").write_text("# CR\nReview workflow", encoding="utf-8")
    role_dir = agents / "roles"
    role_dir.mkdir()
    (role_dir / "reviewer.md").write_text("# Reviewer\nRole desc", encoding="utf-8")

    # 写生产配置
    config_toml = """
[cache]
enabled = true
dir_name = ".cache"
filename = "spec-loader.json"
max_entries = 200
version = 2
atomic_write = true
mtime_precision = 0.001
[performance]
auto_save_cache = true
"""
    (config_dir / "spec-loader.toml").write_text(config_toml, encoding="utf-8")

    # 冷启动
    loader_cold = SpecLoader(root, use_disk_cache=True)
    check("冷启动: 初始磁盘条目=0", loader_cold.get_cache_stats()["disk_entries"] == 0)
    t0 = time.perf_counter()
    r_cold = loader_cold.load_for_task("代码审查", stage="execution")
    t_cold = (time.perf_counter() - t0) * 1000
    check(f"冷启动耗时<200ms ({t_cold:.2f}ms)", t_cold < 200.0)
    check("冷启动: L0=1", r_cold.layer_summary.get("L0", 0) == 1)
    check("冷启动: L1a=2", r_cold.layer_summary.get("L1a", 0) == 2)
    check("冷启动: L1b=0(execution)", r_cold.layer_summary.get("L1b", 0) == 0)
    check("冷启动: L2=2(代码审查路由)", r_cold.layer_summary.get("L2", 0) == 2)
    loader_cold.save_cache()

    # 温启动（新实例）
    loader_warm = SpecLoader(root, use_disk_cache=True)
    stats_warm = loader_warm.get_cache_stats()
    check(f"温启动: 磁盘缓存预加载条目>=5 ({stats_warm['disk_entries']})",
          stats_warm["disk_entries"] >= 5)
    t0 = time.perf_counter()
    r_warm = loader_warm.load_for_task("代码审查", stage="execution")
    t_warm = (time.perf_counter() - t0) * 1000
    check(f"温启动耗时<1ms ({t_warm:.2f}ms)", t_warm < 1.0, f"warm={t_warm}ms")
    check(f"温启动加速比 > 2x ({t_cold/t_warm:.1f}x)", t_cold/t_warm > 2.0)
    check("温启动: 磁盘缓存命中>0", loader_warm.get_cache_stats()["disk_cache_hits"] > 0)

# ── PHASE 3: 多任务类型（各自独立loader） ────────────────────────
print("\n--- PHASE 3: 多任务类型加载验证 ---")

task_keywords = {
    "代码审查": "code_review",
    "帮我提交代码": "commit",
    "复盘一下这个项目": "retrospective",
    "画个mermaid流程图": "mermaid",
    "链接检查修复": "link_check",
}
for desc, expected_type in task_keywords.items():
    loader = SpecLoader(PROJECT_ROOT, use_disk_cache=False)
    r = loader.load_for_task(desc, stage="execution")
    matched = loader.match_task_type(desc)
    ok_layers = (r.layer_summary.get("L0", 0) == 1 and
                 r.layer_summary.get("L1a", 0) == 2 and
                 r.layer_summary.get("L1b", 0) == 0)
    check(f"任务'{desc[:8]}' L0=1,L1a=2,L1b=0", ok_layers,
          f"L0={r.layer_summary.get('L0')} L1a={r.layer_summary.get('L1a')} L1b={r.layer_summary.get('L1b')}")
    check(f"任务'{desc[:8]}' 匹配类型包含'{expected_type}'",
          expected_type in matched, f"matched={matched}")
    check(f"任务'{desc[:8]}' L2>=1", r.layer_summary.get("L2", 0) >= 1,
          f"L2={r.layer_summary.get('L2')}")

# ── PHASE 4: L1b延迟加载完整流程 ────────────────────────────────
print("\n--- PHASE 4: L1b延迟加载完整流程 ---")

loader_l1b = SpecLoader(PROJECT_ROOT, use_disk_cache=False)
r_exec = loader_l1b.load_for_task("代码审查", stage="execution")
check("execution: L1b=0", r_exec.layer_summary.get("L1b", 0) == 0)
paths_exec = loader_l1b.get_loaded_paths()
l1b_in_exec = [p for p in SpecLoader.L1B_INDEX_SPECS if p in paths_exec]
check(f"execution后L1b文件未加载({len(l1b_in_exec)})", len(l1b_in_exec) == 0, str(l1b_in_exec))

r_l1b = loader_l1b.ensure_l1b()
check(f"ensure_l1b()加载3个L1b文件({r_l1b.layer_summary.get('L1b',0)})",
      r_l1b.layer_summary.get("L1b", 0) == 3)
paths_all = loader_l1b.get_loaded_paths()
l1b_now = [p for p in SpecLoader.L1B_INDEX_SPECS if p in paths_all]
check("ensure_l1b后所有L1b已加载", len(l1b_now) == 3, str(l1b_now))

r_again = loader_l1b.ensure_l1b()
check("ensure_l1b()幂等: 无新文件", len(r_again.loaded_specs) == 0)
check("ensure_l1b()幂等: already_loaded=3", len(r_again.already_loaded) == 3)

# planning阶段include_l1b=False覆盖
loader_override = SpecLoader(PROJECT_ROOT, use_disk_cache=False)
r_no_l1b = loader_override.load_for_task("代码审查", stage="planning", include_l1b=False)
check("planning+include_l1b=False: L1b=0", r_no_l1b.layer_summary.get("L1b", 0) == 0)

# ── PHASE 5: 生产配置文件验证 ───────────────────────────────────
print("\n--- PHASE 5: 生产配置验证 ---")

loader_cfg = SpecLoader(PROJECT_ROOT)
cfg = loader_cfg.get_cache_stats()["config"]
check("cfg: cache_enabled=True", cfg["cache_enabled"] is True)
check("cfg: cache_version=2", cfg["cache_version"] == 2)
check("cfg: max_entries=200", cfg["max_entries"] == 200)
check("cfg: mtime_precision=0.001", abs(cfg["mtime_precision"] - 0.001) < 0.0001)
check("cfg: atomic_write=True", cfg["atomic_write"] is True)
check("cfg: auto_save=True", cfg["auto_save"] is True)
config_file = PROJECT_ROOT / ".agents" / "config" / "spec-loader.toml"
check(f"配置文件存在: {config_file.name}", config_file.exists())

# ── PHASE 6: 高频连续加载（内存缓存命中） ──────────────────────
print("\n--- PHASE 6: 高频连续加载（20次调用） ---")

loader_fast = SpecLoader(PROJECT_ROOT, use_disk_cache=True)
# 首次加载（冷）
loader_fast.load_for_task("代码审查", stage="execution")
times_fast = []
for i in range(20):
    t0 = time.perf_counter()
    loader_fast.load_for_task("代码审查", stage="execution")
    times_fast.append((time.perf_counter() - t0) * 1000)
avg_fast = sum(times_fast) / len(times_fast)
max_fast = max(times_fast)
check(f"20次连续调用平均<0.1ms ({avg_fast:.4f}ms)", avg_fast < 0.1, f"avg={avg_fast}")
check(f"20次连续调用最大<1ms ({max_fast:.4f}ms)", max_fast < 1.0, f"max={max_fast}")

# ── PHASE 7: mtime缓存失效 ─────────────────────────────────────
print("\n--- PHASE 7: mtime缓存失效 ---")

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    agents = root / ".agents"
    agents.mkdir()
    for name in ["ONBOARDING.md", "global-core-rules.md", "capability-boundaries.md",
                  "capability-registry.md", "context-routing.md"]:
        (agents / name).write_text(f"# {name}\nv1", encoding="utf-8")
    (agents / "skills").mkdir()
    (agents / "skills" / "README.md").write_text("# Skills\nv1", encoding="utf-8")

    l1 = SpecLoader(root, use_disk_cache=True)
    l1.load_for_task("test", stage="execution")
    l1.save_cache()

    l2 = SpecLoader(root, use_disk_cache=True)
    r2 = l2.load_for_task("test", stage="execution")
    ob = [s for s in r2.loaded_specs if s.path == "ONBOARDING.md"]
    check("mtime: v1缓存命中", len(ob) == 1 and "v1" in ob[0].content)

    time.sleep(0.05)
    (agents / "ONBOARDING.md").write_text("# ONBOARDING.md\nv2_MODIFIED", encoding="utf-8")

    l3 = SpecLoader(root, use_disk_cache=True)
    r3 = l3.load_for_task("test", stage="execution")
    ob2 = [s for s in r3.loaded_specs if s.path == "ONBOARDING.md"]
    check("mtime: 修改后加载v2", len(ob2) == 1 and "MODIFIED" in ob2[0].content,
          ob2[0].content if ob2 else "NOT FOUND")

# ── PHASE 8: TASK_ROUTING完整性 ────────────────────────────────
print("\n--- PHASE 8: 路由文件完整性 ---")

agents_dir = PROJECT_ROOT / ".agents"
missing = []
for tt, cfg in TASK_ROUTING.items():
    for sp in cfg.get("l2_specs", []):
        if not (agents_dir / sp).exists():
            missing.append(f"{tt}:{sp}")
check(f"所有路由L2文件存在(缺失{len(missing)})", len(missing) == 0, str(missing))

# ── PHASE 9: 缓存健壮性 ────────────────────────────────────────
print("\n--- PHASE 9: 缓存健壮性（损坏/空/版本不匹配） ---")

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    agents = root / ".agents"
    agents.mkdir()
    for n in ["ONBOARDING.md", "global-core-rules.md", "capability-boundaries.md",
               "capability-registry.md", "context-routing.md"]:
        (agents / n).write_text(f"# {n}\nx", encoding="utf-8")
    (agents / "skills").mkdir()
    (agents / "skills" / "README.md").write_text("# Skills\nx", encoding="utf-8")
    cdir = agents / ".cache"
    cdir.mkdir()
    cfile = cdir / CACHE_FILENAME

    for label, content in [
        ("损坏JSON", "INVALID{{{"),
        ("空文件", ""),
        ("版本不匹配", json.dumps({"version": 999, "entries": {}})),
    ]:
        cfile.write_text(content, encoding="utf-8")
        lx = SpecLoader(root, use_disk_cache=True)
        rx = lx.load_for_task("test", stage="execution")
        check(f"{label}: 不崩溃", rx is not None)
        check(f"{label}: L0=1,L1a=2",
              rx.layer_summary.get("L0", 0) == 1 and rx.layer_summary.get("L1a", 0) == 2,
              f"L0={rx.layer_summary.get('L0')} L1a={rx.layer_summary.get('L1a')}")

# ── PHASE 10: include_l1b强制加载 + format输出验证 ──────────────
print("\n--- PHASE 10: include_l1b强制加载 & format输出 ---")

loader_fmt = SpecLoader(PROJECT_ROOT, use_disk_cache=False)
r_exec_fmt = loader_fmt.load_for_task("代码审查", stage="execution")
out_exec = loader_fmt.format_for_prompt(r_exec_fmt, include_content=False)
l1b_listed_exec = sum(1 for f in SpecLoader.L1B_INDEX_SPECS if f in out_exec)
check(f"execution format: L1b文件不出现在清单中(出现{l1b_listed_exec}个)", l1b_listed_exec == 0)

loader_fmt2 = SpecLoader(PROJECT_ROOT, use_disk_cache=False)
r_plan_fmt = loader_fmt2.load_for_task("代码审查", stage="planning")
out_plan = loader_fmt2.format_for_prompt(r_plan_fmt, include_content=False)
l1b_listed_plan = sum(1 for f in SpecLoader.L1B_INDEX_SPECS if f in out_plan)
check(f"planning format: L1b文件全部出现在清单中({l1b_listed_plan}/3)", l1b_listed_plan == 3)

# ── 总结 ────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"集成测试结果: {passed} PASSED, {failed} FAILED")
if errors:
    print("\n失败项:")
    for e in errors:
        print(f"  ✗ {e}")
else:
    print("\n所有集成测试通过！生产环境无回归问题。")
print("=" * 70)

sys.exit(0 if failed == 0 else 1)
