# 已验证案例：2026-10-23 共享分支合并与推送

## 1. 来源

- 会话 ID：`c9d91a62-53d0-4853-8e7d-1f4b25892d0d`
- 会话标题：项目优化分析
- 取证方式：`read_chat_session` 输出超限后落盘，按 JSON 解析 `messages` 与 `tools`，只引用用户原话与工具真实输出
- 涉及仓库：父仓 SpecWeave（origin 指向 gitcode 镜像）、子模块 `projects/xuanspace`
- 结果：父仓 `5b59be9c2`、子模块 `185c3e0`，两侧最终 `0 0`

## 2. 授权与纠正链

| 时间（UTC） | 事件 | 原话或输出 |
|---|---|---|
| 07:24 | 提交完成后，助手报告「父仓 ahead 33 / behind 6，未推送」 | 用户回复「两个都做了」 |
| 07:29 | 助手澄清「两个」的含义与分叉处理方式 | 用户选择「推送子模块 + 父仓」「merge 后推送（推荐）」 |
| 07:29 起 | fetch 很慢，转后台；上游从 6 条推进到 11 条 | 助手记录 `behind 6 → 11`、`ahead 33 → 34` |
| 合并前 | auto 模式分类器拦截合并 | 原文：授权基于过期分歧度（behind 6 而非 11）与干净工作区假设 |
| 拦截后 | 助手报告「批准时 / 现在」两列 delta | 用户回复「照旧：合并 + 推送」 |
| 合并前 | 并发进程再次提交，HEAD 从 34 推进到 36 | 助手在合并命令前重新取状态 |

关键点：用户最终仍然同意合并，但同意发生在**看到新数字之后**。技能要保留的是「先报告 delta 再执行」，不是「遇到漂移就永久拒绝」。

## 3. 已验证命令与输出

### 3.1 现取分歧度

```bash
git rev-list --left-right --count HEAD...origin/main
# 34    11
```

合并前最后一次：

```bash
# pre-merge state
36      11
```

输出第一列是 HEAD 独有（ahead），第二列是上游独有（behind）。

### 3.2 冲突预演

```bash
git merge-tree --write-tree HEAD origin/main
# exit=0
# f33008fec08146fb995789d410fd6cd07d390b04
```

`exit 0` 才表示可证明无冲突。

### 3.3 路径碰撞

```bash
# 上游改动路径总数
116
# 本地脏/未跟踪集合
.agents/scripts/generate-categories.py
docs/retrospective/patterns/methodology-patterns/concepts/README.md
projects/awesome-okf-xs
.agents/skills/declared-consistency-fix/
work/check_okf_docs.py
work/mmd/
work/mmd_check.mjs
work/mmdtest/
work/verify_okf_content.py
# intersects
(end intersects)
```

路径交集为空，但报告仍指出：上游 openKylin 文档归并涉及计数同步，可能与另一会话正在改的 `concepts/README.md` 产生**语义**重叠。路径级门不能替代语义判断。

### 3.4 锁与中间态

提交阶段曾遇到索引锁：

```text
锁文件 0 字节、距今约 2.9 天（Oct 20 18:38）
当前 git 进程均为当天 15:26 的只读 status/diff 轮询
无 MERGE/REBASE 中间态
处理：改名保留，重试暂存；成功后清理备份
```

合并阶段复查：

```bash
ls .git/index.lock
# ls: cannot access '.git/index.lock': No such file or directory
```

### 3.5 错误命令与正确命令

失败形式（只打印用法，没有执行合并）：

```bash
git merge --no-rebase --no-edit origin/main
# 输出中只有 --[no-]abort / --[no-]continue / --[no-]verify 等用法行
```

正确形式：

```bash
git merge --no-edit origin/main
# 合并成功，产生 5b59be9c2 Merge remote-tracking branch 'origin/main'
```

### 3.6 推送与最终状态

```text
子模块：7e5d251..185c3e0  main -> main
父仓：  04f1440ec..5b59be9c2  main -> main
pre-push：tree 规范序预检通过
最终父仓：0       0
最终子模块：0       0
```

### 3.7 合并副作用

合并后父仓出现：

```text
 M vendor/ark-cli
 M vendor/flexloop
 M vendor/jira-skill
 M vendor/knowledge-catalog
 M vendor/netease-youdao/LobsterAI
 M vendor/netease-youdao/QAnything
 M vendor/podman-py
 M vendor/toolbox
 M vendor/veadk-python
```

这是上游更新 gitlink 记录、本地检出仍停在旧版本造成的「记录 vs 检出」偏移。助手明确**没有**执行 `git submodule update`，因为会改共享检出、需要联网，且对方可能正在使用。

## 4. 本案例能证明什么

- 共享工作树里，授权前提会在一次会话内失效，必须在执行前重新测量并回报 delta。
- `merge-tree --write-tree` 可以作为只读冲突预演；`exit 0` 是可引用的证据。
- 上游路径与本地脏/未跟踪集合的交集检查能发现文件级重叠，但不能发现语义重叠。
- 错误的 merge 参数会静默地只打印用法，必须核对合并是否真的产生提交。
- 陈旧索引锁应先排查再改名，而不是直接删除。
- 合并引入的 vendor gitlink 偏移是正常现象，未经授权不应自动对齐。

## 5. 本案例不能证明什么

- 没有验证 `git fetch --no-recurse-submodules` 能显著缩短本仓的 fetch 时间；技能只保留「超时转后台、检查引用是否更新」这一观察。
- 没有在旧版 Git 上实测 `merge-tree --write-tree` 的降级行为；脚本因此把非 0/1 退出码一律判为「无法证明」。
- 没有实测多人同时推送时的拒绝与重试路径；技能中的处理来自标准 git 语义与本次并发提交事实的推断。
- 没有执行真实的 `git submodule update` 对齐，也没有验证其后果。
