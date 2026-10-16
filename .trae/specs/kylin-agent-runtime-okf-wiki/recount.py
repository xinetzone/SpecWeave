#!/usr/bin/env python3
"""V 阶段计数断言独立复核：用 Python（pathlib+re，异于 R 阶段 PowerShell）重数关键数量。"""
import re, pathlib

S = pathlib.Path(r"d:\spaces\SpecWeave\external\dao\action\openkylin\agent-runtime")

def grep(path_glob, pattern):
    rx = re.compile(pattern, re.M)
    n = 0
    for p in S.glob(path_glob):
        n += len(rx.findall(p.read_text(encoding="utf-8", errors="replace")))
    return n

def count_py(path):
    return len(list((S / path).rglob("*.py")))

checks = {
    "agent py (=120)": count_py("agent"),
    "tools py (=93)": count_py("tools"),
    "cli pkg py (=94)": count_py("kylin_agent_runtime_cli"),
    "gateway py (=64)": count_py("gateway"),
    "platforms files (=32)": len([p for p in (S/"gateway/platforms").glob("*.py") if p.name != "__init__.py"]),
    "adapter subclasses (=21)": grep("gateway/platforms/*.py", r"^class \w+\(BasePlatformAdapter\)")
                              + grep("gateway/platforms/qqbot/*.py", r"^class \w+\(BasePlatformAdapter\)"),
    "TOOLSETS keys (=31)": grep("toolsets.py", r'^    "[a-z_]+":\s*\{'),
    "register_transport (=4)": grep("agent/transports/*.py", r"^register_transport\("),
    "FailoverReason (=18)": 0,  # enum 成员多行，单独数
    "LSP ServerDef (=26)": grep("agent/lsp/servers.py", r"^    ServerDef\("),
    "mcp.tool (=10)": grep("mcp_serve.py", r"@mcp\.tool\(\)"),
    "VALID_HOOKS (=17)": grep("kylin_agent_runtime_cli/plugins.py", r'^    "[a-z_]+"[,:]\s*$'),
    "SKILL.md (=77)": len(list((S/"skills").rglob("SKILL.md"))),
    "plugins dirs (=17)": len([p for p in (S/"plugins").iterdir() if p.is_dir()]),
    "memory backends (=8)": len([p for p in (S/"plugins/memory").iterdir() if p.is_dir()]),
    "web backends (=8)": len([p for p in (S/"plugins/web").iterdir() if p.is_dir()]),
    "locales yaml (=16)": len(list((S/"locales").glob("*.yaml"))),
    "env class tree (=9: 8 leaves+1 mid-base)": grep("tools/environments/*.py", r"^class \w+\(BaseEnvironment\)")
                        + grep("tools/environments/*.py", r"^class \w+\(BaseModalExecutionEnvironment\)"),
}
# FailoverReason 成员：error_classifier.py 24-61 行内 '    xxx = "' 计数
ec = (S/"agent/error_classifier.py").read_text(encoding="utf-8", errors="replace").splitlines()
checks["FailoverReason (=18)"] = sum(1 for ln in ec[23:62] if re.match(r'^    [a-z_]+ = "', ln))
# _BUILTIN_SUBCOMMANDS：main.py 10405-10421 区间引号条目
mm = (S/"kylin_agent_runtime_cli/main.py").read_text(encoding="utf-8", errors="replace").splitlines()
block = "\n".join(mm[10405:10421])
checks["builtin subcommands (=48)"] = len(re.findall(r'"[a-z-]+"', block))

bad = 0
for k, v in checks.items():
    print(f"{k:32} -> {v}")
    m = re.search(r"=(\d+)\)", k)
    if m and int(m.group(1)) != v:
        bad += 1
        print("    !!! MISMATCH")
print("RESULT:", "ALL MATCH" if bad == 0 else f"{bad} MISMATCH")
