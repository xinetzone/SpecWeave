# 来源会话取证与未验证项

来源会话：`c9d91a62-53d0-4853-8e7d-1f4b25892d0d`。本文件区分「本机可复核的仓库事实」「会话 dump 中读到的工具输出」「无法复核的推断」，避免把复述当成证据。

## 1. 可复核的仓库事实

截至 2026-10-24，父仓库 `D:/spaces/SpecWeave` 与嵌套仓库 `projects/xuanspace` 中可读到：

| 提交 | 仓库 | 主题 | 触及文件 |
|---|---|---|---|
| `88790e5` | xuanspace | `refactor(license): 许可元数据统一为 PEP 639 表达式形态` | 12 个文件，含根 `pyproject.toml` |
| `8bfa7fd` | xuanspace | `build(deps): 构建下限提升至 scikit-build-core>=0.11` | 14 个文件，含根 `pyproject.toml` |
| `92e2b55` | xuanspace | `docs(build): 同步构建下限声明并结合 PEP 639 说明原因` | 9 个文件 |
| `8db593d` | xuanspace | `feat(scripts): 校验 scikit-build-core 下限契约` | `scripts/check_pyproject_style.py` 等 |
| `5a2f001b7` | SpecWeave | `chore(submodule): 前移 xuanspace 指针至 4d393b3（PEP 639 许可元数据与 linkcheck 门禁）` | gitlink |
| `9fd137b6e` | SpecWeave | `chore(submodule): 前移 xuanspace 指针至 8db593d（构建下限契约化）` | gitlink |

关键检查：`git -C projects/xuanspace show 88790e5 -- pyproject.toml` 与 `git show 8bfa7fd -- pyproject.toml` 的 hunk 互不重叠——前者改 `license` / `license-files` 与 `License ::` classifier，后者只改 `scikit-build-core>=0.10` 与 `minimum-version`。这证明「同一文件里两类关注点被拆进两个提交」在最终历史中确实成立。

## 2. 会话中读到的失败与处置

| 现象 | 原因 | 处置 |
|---|---|---|
| `cd: projects/xuanspace: No such file or directory` | Bash 调用之间工作目录被重置，相对路径落到别处 | 全部改为 `git -C <绝对路径>` |
| `cp: cannot stat '/tmp/mystx-full.toml'` | Git Bash 的 `/tmp` 与 Windows Python 的临时目录不是同一命名空间 | 放弃跨运行时临时文件，改为同一命名空间内的备份 |

这两条失败是本技能第 1、2 条 Gotchas 的直接来源。

## 3. 推送证据

会话中按「嵌套仓提交 → 嵌套远端 → 父仓 gitlink → 父仓远端」顺序推进，并以 `ls-remote` 与 `ls-tree` 收尾。仓库历史中父仓的两次 gitlink 前移（`5a2f001b7`、`9fd137b6e`）与嵌套仓对应提交（`4d393b3`、`8db593d`）一一对应，可复核。

## 4. 未验证或不可复核项

1. **会话里构造中间态的确切脚本文本未保留在会话 dump 中**。dump 保留了命令输出与提交结果，但没有完整的脚本源码。因此本技能附带的 `scripts/split_state.py` 是按同一思路重写的可复现等价实现，不是对来源会话代码的转录。
2. **等价实现已在临时仓库实测**（见 [split-runbook.md](split-runbook.md) 第 3 节）：正例两次提交、四类负例退出码、本地裸仓的分层推送与 gitlink 校验均通过。它证明的是本技能流程与脚本可用，不证明与来源会话逐字一致。
3. **会话中 `cb8e280`、`c1d671b`、`8f1544b`、`103bea7` 等 SHA** 出现在 `8bfa7fd` 的提交说明里（指向 `libs/mystx`、`libs/tvm-book` 等嵌套子模块），在本机主仓库与 `projects/xuanspace` 中不可解析；这些子模块各自的远端状态本次未核验。
4. **来源会话是否使用过 `--dry-run` 与次数断言无从确认**。这两项是本技能为可复核性新增的门，不是对历史操作的复述。

## 5. 对技能内容的约束

- 不把来源会话的具体文件清单、业务路径写成通用规则；正文只用「一个文件、两类关注点」的抽象形态。
- 不宣称「每个中间提交都能通过完整 CI」；只宣称 diff 只含一类关注点。来源案例中许可提交先于下限提交，短暂存在元数据与下限不匹配的窗口，推送前才闭合。
- 所有推荐命令都来自本机实际执行过的序列，未执行项已在第 4 节单列。
