# Review：okw CLI 架构重构独立审查报告

- **审查日期**：2026-07-02
- **审查方式**：全新上下文独立代理只读审查（fresh-context adversarial review），审查者未参与实施；审查期间禁止写文件/提交 git，可运行 pytest 与只读 git 命令。
- **审查基线**：`git HEAD`（旧 `src/okw/cli.py` 等经 `git show HEAD:...` 取回）。
- **解释器**：`C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`（Python 3.14.7）。
- **总体结论**：✅ **PASS**（10/10 AC 全部 PASS；无 P0、无 P1；4 条 P2，已处置）。

## 一、验收标准核对（审查者独立复跑，非转述实施证据）

| AC | 判定 | 独立证据 |
|---|---|---|
| AC-1 CLI 表面逐字节不变 | PASS | 旧 `build_parser()` 序列化 == 新 `build_parser()` 序列化 == 入库快照，三者全等；17 个 parser 节点 `format_help()` 零 diff；13 个错误路径退出码与 stderr 全等；18 组 argv 命名空间仅多内部属性 `_group_help`，业务值全等。 |
| AC-2 现有测试零回归 | PASS | 审查者自跑 **349 passed**（基线 279）；12 个旧测试文件（含 test_cli.py、conftest.py）零修改。 |
| AC-3 私有 API 清零 | PASS | src 全树 `._subparsers`/`._group_actions`/`._name_parser_map` 0 命中；门禁测试随全量绿。 |
| AC-4 注册表交叉校验 | PASS | 注册表恰好 14 键且值皆 callable；parser 叶子集 == 注册表键集；两子组空命令 rc=2 且旧/新 stdout 字节一致。 |
| AC-5 异常体系与单点收口 | PASS（见 P2-1） | WslError/ScaffoldError 为 OkwError 子类、raise 文案零改动；main 单点捕获 → stderr 恰好一行 `错误：…\n` + rc=1；ValueError 不被吞。 |
| AC-6 版本守卫 | PASS | 守卫位于 docstring 后、业务导入前；无 PEP604/match；边界版本实测放行/拒绝正确；10 个守卫用例绿。 |
| AC-7 零副作用导入 | PASS | 干净子进程把 subprocess/os.system 全替换为 raise 后，import okw 全链、build_parser()、访问旧别名零触发。 |
| AC-8 工程红线 | PASS | pyproject 未改（`dependencies=[]`、`requires-python>=3.10`、`okw=okw.cli:main`、scikit-build 后端）；`from __future__` 0 命中；新文件无 GPL/SPDX 头；entry point 可 load，`python -m okw --version` → `okw 0.1.0`。 |
| AC-9 分层结构质量 | PASS（5/5） | parser 205 / main 43（≤300），命令分组 13–85（≤250）；parser 无 IO、main 无装配调用（AST 强制）；领域层 → commands 引用仅存在于两处 PEP 562 `__getattr__` 惰性函数内。 |
| AC-10 覆盖率 | PASS | TOTAL 1247 stmts / 36 miss / **97%**；cli/、commands/、errors 新模块 **100%**。 |

## 二、Findings 与处置

### P0（必须修）：无
### P1（应修）：无

### P2（建议）

| 编号 | 发现 | 处置 |
|---|---|---|
| P2-1 | **单点收口带来的一处缺陷路径改善（唯一观测到的行为差异）**：`wsl.exe` 缺失时 `okw export`/`okw unregister --yes` 旧版为未捕获 WslError 的 traceback 外泄，新版为 stderr 单行 `错误：…` + return 1；进程退出码两边均为 1。该变化是 AC-5 的明确要求，exec/podman/image 路径无此差异。 | **登记保留，不回退**；提交说明中显式标注此单点。 |
| P2-2 | argparse `set_defaults` 会把 `_group_help` 传播到叶子命令 Namespace；当前 main 先判子命令、handler 不读该属性，安全，但未来可能误用。 | **已采纳**：[parser.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/parser.py) 两处 set_defaults 上方补注释，声明叶子会继承且 handler 禁用。 |
| P2-3 | 包化后 `python -m okw.cli` 不可执行（旧单文件底部有 `__main__` 守卫）；README/FR-8 从未承诺该形态，承诺的 `python -m okw` 与 console script 均正常。 | **登记不改**：属未记载的内部形态；如未来有需求再补 `cli/__main__.py`。 |
| P2-4 | `main.py` 的 `COMMAND_HANDLERS[key]` 在 try 外，理论上可能 KeyError；实际键有效性由 argparse choices 解析期保证，不可达。 | **已采纳**：[main.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/main.py) 查表前补注释，固化「KeyError 不可达」的前提与交叉测试锁定。 |
| 附 | tasks.md Task 5 证据中 distro_cmds 行数「82 行」为笔误，Task 7 实测 85 行，数字不影响任何 AC。 | 已知悉，以 TR-7.4 的 85 行为准。 |

P2-2/P2-4 采纳后已重跑全量：**349 passed / 97%**，行为零变化（仅注释）。

## 三、法律清洁专项（审查者独立结论）

- 逐份比对 xuan-compose 对应文件（cli/main.py、cli/parser.py、cli/__init__.py、commands/__init__.py、errors.py、版本守卫、快照相关测试与生成器）+ 归一化行集机械重合度检测：除 `import sys`/`import argparse`/`if __name__ == "__main__"`/`write_text(..., encoding="utf-8")` 等通用样板行外**无非平凡代码或注释重合**；errors/commands 注册表/cli __init__/注册表测试重合为 0。
- 借鉴范围仅限架构模式（cli 分层、显式注册表、异常收口、版本守卫、快照测试）；okw 序列化器为独立递归两层设计，字段集与 xc 版不同。
- xc 参考文件全部携带 `SPDX-License-Identifier: GPL-2.0-only`；okw 全部新增文件无任何许可证头（延续 MIT 仓本体）。
- 循环导入：三种极端导入顺序在干净子进程实测 rc=0；`__getattr__` 未知属性正确抛 AttributeError。

## 四、未覆盖与残留风险

1. 审查者未独立复跑真实 WSL/editable console 冒烟（其环境无 wsl）；entry point 可 load 已验证，实施侧的真实冒烟（`okw --version`/`okw list` rc=0、中文输出完好）记录于 tasks.md TR-7.4。
2. P2-1 为 monkeypatch 进程内实证（代码路径明确，结论可靠），未在真实缺失 wsl.exe 的机器上复现。
3. 相似度检测为归一化整行集合比对（非 token/AST 级），已辅以逐文件人工通读，未发现改名换序的大段移植。

## 五、收尾判定

- 七项任务全部 completed 且证据回填完整；本审查 PASS，规格 AC-1~AC-10 关闭。
- 工作区变更**未做 Git 提交**；提交时遵循原子提交规范，并在提交说明中：①标注 P2-1 故障路径改善；②注明 CLI 快照由生成器一次性生成（Task 2）。

## 六、审查后优化跟进（2026-10-12）

审查 PASS 并完成两次原子提交（`9e40dc21b` docs、`03aa3457c` refactor）后，按用户决策继续处理 P2 项与内部债务，新增两次本地提交（未推送）：

1. **P2 兼容层清理（提交 `e86c6411b`）**：全包走查证实五个迁移期别名（`podman.cmd_preflight/cmd_install/cmd_verify`、`image.cmd_build/cmd_verify`）已无真实消费者——旧测试均经 `cli.main` 走注册表，别名仅被 Task 5 专为兼容期写的断言引用。删除两领域模块的 PEP 562 `__getattr__` 与迁移注释（−90/+7），注册表测试删除 8 条别名断言（保留键集/可调用性/零副作用探针），过时注释同步更正；341 项测试全绿，CLI 表面零变化。注册表自此成为 handler 的唯一分发路径。
2. **P2-3 关闭**：新增 [cli/\_\_main\_\_.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/__main__.py)，`python -m okw.cli` 与 `python -m okw`、console script 三形态等价（真实冒烟 `okw 0.1.0`）。
3. **类型注解**：14 个 handler 统一签名 `(args: argparse.Namespace) -> int`，注册表新增 `Handler = Callable[[argparse.Namespace], int]` 别名并标注 `dict[str, Handler]`；全部 3.10 兼容（无 PEP 604/PEP 563），AST 守护参数化自动覆盖。
4. **入口测试**：新增 test_entry_points.py（4 用例，runpy 覆盖两个 __main__ 的 --version/无参数路径），`__main__.py` 与 `cli/__main__.py` 覆盖率均达 100%；全量 **347 passed / 97%**。
5. **P2-1** 维持登记保留（故障路径改善，退出码不变）；**P2-2/P2-4** 注释已于审查当日采纳。领域层故障防御分支（podman/image/distro/verify 共 33 miss 行）经评估补测成本与回归风险偏高且 AC-10 早已达标，明确不补。

