# 取证命令手册

> 配套 [SKILL.md](../SKILL.md) §6。目标：在**不读网页日志**的前提下，把「哪个 job 红、红在哪一行、本地能否复现」变成三条可复跑的命令。

## 一、定位失败 job

```bash
# 本 run 的总体结论 + 每个 job 的结论
gh run view <run_id> --repo <owner>/<repo> --json status,conclusion,jobs \
  --jq '{status,conclusion,jobs:[.jobs[]|{name,conclusion}]}'

# 只看最近几次 run（不知道 run_id 时）
gh run list --repo <owner>/<repo> --limit 5 \
  --json databaseId,headSha,status,conclusion,displayTitle
```

判读要点：

| 现象 | 含义 |
|---|---|
| `conclusion: failure` 且只有 1 个 job 红 | 其余 job 多为 `skipped`（被 `needs` 阻断），不要逐个排查 |
| job 名里列出多个门禁 | 该 job 是「一个 step 跑一个脚本」的串联结构，红项就是那一行 shell |
| 红 job 名与本仓库改动的领域不符 | 先怀疑存量红或环境问题，再怀疑本次改动 |

> 为什么先看 job 列表而不是先看日志？因为 `needs` 会把下游 job 全部置为 `skipped`，日志里会出现大量「没有输出」的假象。先确认只有一个 job 真正执行，能省掉大半噪声。

## 二、取失败日志并定点读取

```bash
gh run view --repo <owner>/<repo> --job <job_id> --log-failed
```

输出超过工具上限时会落盘，并给出 `<persisted-output>` 与 `Full output saved to: <path>`。此后：

```bash
# 用 Grep 工具在落盘文件上匹配，不要 Read 全文
# pattern: (FAIL|ERROR|::error|✗|Traceback|exit code)
# 命中后只 Read 命中行前后 20-40 行
```

若所在环境没有 Grep 工具，用脚本切片而不是 `Read` 全文：

```bash
python - <<'PY'
from pathlib import Path
p = Path(r"<落盘路径>")
lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
for i, ln in enumerate(lines):
    if "✗" in ln or "::error" in ln or "exit code" in ln:
        lo, hi = max(0, i - 20), min(len(lines), i + 20)
        print("\n".join(lines[lo:hi]))
        print("-" * 60)
PY
```

> 为什么必须切片？日志前缀会重复输出环境变量块（`pythonLocation`、`LD_LIBRARY_PATH` 等），有效信息占比可能不足 10%。全文读会同时消耗预算与注意力。

## 三、本地复现

```bash
# 在仓库根执行失败 job 中那一行原样命令
python scripts/<gate>.py
echo $LASTEXITCODE   # PowerShell
echo $?              # bash
```

复现判据：

1. 退出码相同（本例为 1）；
2. 报错条目文字相同（本例为两条 `[规模数字矛盾]`）；
3. 条目里引用的文件与数字相同。

三者有任一不符，说明不是同一个缺陷，回到第二节重新取日志。

## 四、确认「这个脚本真的在这个 job 里跑」

```bash
# 先看 job 的 steps
gh run view <run_id> --repo <owner>/<repo> --json jobs --jq '.jobs[]|{name,steps:[.steps[]|{name,conclusion}]}'

# 再看 workflow 定义：触发条件与 run 行
# .github/workflows/*.yml  →  on.paths / jobs.<id>.steps[].run
```

> 为什么单独一步？因为「本地红」与「CI 红」最常见的不一致来源就在这里：本地跑了全量测试，CI 只跑其中一个文件；或 workflow 因 `on.paths` 未匹配而根本没触发。不核对这两处，后面的分诊全是猜测。

## 五、推送后验收

```bash
# 推送
git push origin <branch>

# 取新 run（按时间倒序，第 1 条通常就是刚触发的）
gh run list --repo <owner>/<repo> --limit 2 \
  --json databaseId,headSha,status,conclusion,displayTitle

# 轮询新 run 的 job 结论
gh run view <new_run_id> --repo <owner>/<repo> --json status,conclusion,jobs \
  --jq '{status,conclusion,jobs:[.jobs[]|{name,conclusion}]}'
```

验收判据：原先失败的 job 的 `conclusion` 变为 `success`。

- 新 run 仍 `in_progress`：继续等待，不要宣称已修复；
- 新 run 换成另一个 job 红：回到第二节，用新 run 的日志重来；
- 排队过久：如实记录「已推送、待观察」，并给出 run id 方便下次接续。

## 六、平台差异速查

| 场景 | bash | PowerShell 7+ |
|---|---|---|
| 截断长输出 | `cmd \| head -c 3000` | 无等价原生 `head -c`；用 `Select-Object -First N` 或落盘后切片 |
| 取退出码 | `$?` | `$LASTEXITCODE` |
| 多行提交信息 | `-m "$(cat <<'EOF' ... EOF)"` | `$msg = @'` … `'@` 独占行，再 `-m $msg` |
| 路径分隔 | `/` | `\`（但 `git` 子命令两者皆可） |
