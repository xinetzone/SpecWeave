#!/usr/bin/env python3
"""check-submodule-pointer.py: 子模块指针一致性健康检查。

S1 行动项（vendor 子模块漂移治理）的 CI 落地点：
检查所有已初始化子模块的 HEAD 是否与主仓库 gitlink 记录一致，
检出「指针新、内容旧/无」的幻觉一致性风险。

与 check-vendor.py --deep 的区别：
- --deep 将「未初始化」记为 FAIL（适合本地完整校验）
- 本脚本将「未初始化」记为 SKIP（适合 CI——vendors 按需拉取是设计使然），
  仅对已初始化子模块做指针一致性硬校验

用法:
    python check-submodule-pointer.py              # 文本输出
    python check-submodule-pointer.py --json       # JSON 输出（CI 友好）
    python check-submodule-pointer.py --fix        # 打印修复命令（不执行）
    退出码: 0=通过, 1=存在指针漂移
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import subprocess
import sys
from pathlib import Path

# 复用 vendor 检查库的辅助函数（单一实现，避免双份逻辑漂移）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.checks.vendor import _get_gitlink_commit


def _run_git(cwd: Path, *args: str) -> str:
    """运行 git 命令并返回 stdout（去空白）。

    submodule status 首次扫描可能较慢（13s+），超时放宽至 60s。
    """
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        capture_output=True, text=True, cwd=str(cwd),
        timeout=60,
    )
    return result.stdout.strip()


def check_submodule_pointer(project_root: Path) -> dict:
    """检查所有已初始化子模块的指针一致性。

    Returns:
        {"total": N, "pass": N, "skip": N, "drift": N, "issues": [...]}
    """
    # 通过 git submodule status 获取权威子模块清单与状态
    status_out = _run_git(project_root, "submodule", "status")
    issues = []
    total = passed = skipped = drifted = 0

    for line in status_out.splitlines():
        if not line.strip():
            continue
        # 格式: [ -|+| ] <sha> <path> [(ref)]
        flag = line[0]
        parts = line[1:].split()
        if len(parts) < 2:
            continue
        sha = parts[0]
        sm_path = parts[1]
        total += 1

        sm_dir = project_root / sm_path
        if flag == "-" or not (sm_dir / ".git").exists():
            # 未初始化：设计使然，跳过
            skipped += 1
            issues.append({"path": sm_path, "status": "skip", "msg": "未初始化（按需拉取，跳过）"})
            continue

        expected = _get_gitlink_commit(project_root, sm_path)
        if not expected:
            skipped += 1
            issues.append({"path": sm_path, "status": "skip", "msg": "gitlink 记录缺失，跳过"})
            continue

        # 已初始化：硬校验 HEAD == gitlink
        actual = _run_git(sm_dir, "rev-parse", "HEAD")
        if actual != expected:
            drifted += 1
            issues.append({
                "path": sm_path,
                "status": "error",
                "msg": f"指针漂移: HEAD {actual[:12]} ≠ gitlink {expected[:12]}",
                "expected": expected,
                "actual": actual,
                "fix": f"git submodule update --init {sm_path}",
            })
        else:
            passed += 1
            issues.append({"path": sm_path, "status": "pass", "msg": f"指针一致 ({expected[:12]})"})

    return {
        "total": total,
        "pass": passed,
        "skip": skipped,
        "drift": drifted,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="子模块指针一致性健康检查")
    parser.add_argument("--path", type=str, default=None, help="项目根目录（默认自动探测）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--fix", action="store_true", help="输出修复命令（不执行）")
    args = parser.parse_args()

    project_root = Path(args.path).resolve() if args.path else Path(__file__).resolve().parent.parent.parent

    result = check_submodule_pointer(project_root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"子模块指针一致性检查: 共 {result['total']} 个，"
              f"通过 {result['pass']}，跳过 {result['skip']}，漂移 {result['drift']}")
        for issue in result["issues"]:
            status = {"pass": "[PASS]", "skip": "[SKIP]", "error": "[FAIL]"}[issue["status"]]
            print(f"  {status} {issue['path']}: {issue['msg']}")
            if args.fix and issue.get("fix"):
                print(f"      修复: {issue['fix']}")

    return 1 if result["drift"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
