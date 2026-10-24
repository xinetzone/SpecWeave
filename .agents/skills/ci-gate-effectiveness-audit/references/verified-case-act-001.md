# 实测案例：xuanspace ACT-001（移除 linkcheck 的 continue-on-error）

- **时间**：2026-10-24
- **对象**：`projects/xuanspace`（SpecWeave 的 git submodule，`gitdir: ../../.git/modules/projects/xuanspace`）
- **来源**：会话 `c9d91a62-53d0-4853-8e7d-1f4b25892d0d` 第 13 轮（用户指令「先执行 ACT-001」）+ 2026-10-24 本地复核
- **行动项出处**：`docs/retrospective/reports/concepts/milestone/xuanspace-license-unification-dual-repo-milestone-20261024.md` 第七节 ACT-001（验收标准原文：`grep -c 'continue-on-error: true'` = 0；一次 CI 运行的 linkcheck 步骤状态反映真实结果）

## 一、抑制点（改动前）

`.github/workflows/ci.yml:152`

```yaml
      # --- 链接检查 ---
      - name: Check documentation links
        run: xs docs linkcheck
        continue-on-error: true
```

同文件另有 2 处步骤体内 `|| true`（合法尽力而为，未动）：

| 位置 | 内容 |
|---|---|
| `ci.yml:76` | pdm venv `ensurepip --upgrade` 兜底后接 `|| true` |
| `ci.yml:308` | `python -m pip install -e ".[dev]" 2>&1 || true` |

这 2 处就是「验收计数必须限定到被删模式」的直接证据：对抑制族整体计 0 永不达标，且会诱导越界删除。

## 二、退出码链（证明该命令本可以失败）

`projects/xuanspace/tools/xs/src/xs/commands/docs_cmd.py`

| 环节 | 行 | 内容 |
|---|---|---|
| CLI 入口 | 126–128 | `def docs_linkcheck() -> None:` → `docs_build(builder="linkcheck")` |
| 子进程 | 44 | `result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=workspace_root)` |
| 非零传播 | 63 | `raise typer.Exit(1)` |

结论：linkcheck 失败会以非零退出码回到 shell；`continue-on-error: true` 是唯一让作业仍然变绿的成因。

## 三、基线（改动前）

环境：py314（3.14.3）+ sphinx 9.1.0。默认 shell 环境是 anaconda 3.13.9 + sphinx 8.2.3，结论不可比。

```bash
python -m sphinx -b linkcheck doc doc/_build/linkcheck
# 退出码 1
```

`output.txt` 共 4 行，全为 `[timeout]`：

| 位置 | 链接 |
|---|---|
| index.md:167 | xinetzone/xuanspace/issues |
| intro.md:62 | xinetzone/xuanspace |
| index.md:109 | apache/tvm-ffi |
| index.md:110 | daoflows/caffe |

状态列统计：`awk '{print $2}' output.txt | sort | uniq -c` → `4 [timeout]`。

同一次运行的产物语义对照（2026-10-24 本地复核）：

| 文件 | 行数 | 内容 |
|---|---|---|
| `output.txt` | 4 | 仅非 working 项 |
| `output.json` | 12 | `unchecked` 1 / `working` 7 / `timeout` 4，JSONL |

`json.load(output.json)` → `json.JSONDecodeError: Extra data: line 2 column 1 (char 172)`。

## 四、伪失败判定

```bash
curl -o /dev/null -w '%{http_code}' --max-time 15 https://github.com/
# 000   15.010658s
```

⇒ 4 条失败**全部**源自本机出站受限；本次基线**未发现真实断链**。若省略探针，就会把 4 条环境伪失败登记为「4 条断链」。

## 五、改动

删除 `ci.yml:152` 一行，`1 file changed, 1 deletion(-)`。

```diff
@@ -149,7 +149,6 @@ jobs:
       # --- 链接检查 ---
       - name: Check documentation links
         run: xs docs linkcheck
-        continue-on-error: true
```

## 六、机械验收（实测值）

| 项 | 命令 | 实测结果 |
|---|---|---|
| 模式限定计数 | `scan_gate_suppressions.py projects/xuanspace --expect-zero 'continue-on-error: true'` | 命中 0，退出码 0 |
| YAML 重解析 | `yaml.safe_load(ci.yml)` | `jobs: ['test','quality','template-validation','py-compat']`；`test` 23 个步骤；末步 keys `['name','run']` |
| 改动作用域 | `git diff --stat` | 1 文件、1 删除行 |
| 子模块分叉 | `git rev-list --left-right --count HEAD...origin/main` | `0  0` |

同一轮里全仓 `grep` 复核被显式取值（输出 `grep_exit=1`），即可复现「零命中时 grep 退出码为 1」这一 `&&` 链截断成因。

## 七、终态

已提交：`4d393b3 chore(ci): 移除 linkcheck 的 continue-on-error 以暴露真实断链`（`1 file changed, 1 deletion(-)`）。

该子模块工作流现已无 `continue-on-error`；`xs docs linkcheck` 的真实结果直接决定作业结论。2026-10-24 复核：`.github/workflows/` 下 `continue-on-error` 命中 0，`|| true` 命中 2（`ci.yml:76`、`ci.yml:308`，均为步骤体内合法尽力而为）。

## 八、残余风险（当时上报，未扩大改动范围）

- Sphinx 默认 `linkcheck_timeout=30` + `linkcheck_retries=1`；runner 上一次瞬时网络抖动会让矩阵里 9 个组合同时变红。
- 同一检查在 matrix 的每个组合里重复执行（3 OS × 3 包管理器 = 9 次），单点失败被放大。
- `actionlint` 未安装 ⇒ 未做工作流静态 lint。YAML 解析不等于 lint，不得混为「已完成校验」。

## 九、两条判据修正

本技能相对最初建议的两处刻意偏差，理由如下：

1. **`if: always()` 不计入抑制族**。它只改变运行顺序（先前失败后仍运行），不阻断失败传播——失败的步骤照样让作业红。计入抑制族会产假阳性，故归 `needs-review` 供人工判读。
2. **验收计数限定到被删模式，不对抑制族整体计 0**。本仓 `ci.yml:76` / `ci.yml:308` 的 `|| true` 在尽力而为步骤里合法存在；按族计 0 会诱导越界删除，正是本技能要防的 scope creep。