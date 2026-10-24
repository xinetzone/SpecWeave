---
name: version-floor-contract-guard
version: 1.0.0
description: "把 manifest 声明的最低支持版本变成可执行契约：先用真实旧版本实测出真门槛，再枚举全部声明面（实例、模板、脚手架生成器、文档、conda/环境文件），把断言并入已有 CI 校验脚本，并用夹具做正负双向验证与扫描面审计。当用户提到『版本下限失真』『声明 0.10 但实测要求 0.11』『minimum-version 该写多少』『构建后端下限要上调』『守卫脚本漏扫目录』，或发现声明的最低版本从未被任何东西执行时，必须使用本技能；不用于依赖升级、版本选型或普通构建排错。"
argument-hint: "<仓库根> [依赖包名] [目标能力]"
user-invocable: true
disable-model-invocation: false
paths:
  - ".agents/skills/version-floor-contract-guard/**"
title: "版本下限契约守卫 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/version-floor-contract-guard/SKILL.toml"
---

# 版本下限契约守卫 (Version Floor Contract Guard)

## 1. Why

A minimum supported version in a manifest is three artifacts at once: a human-readable policy, a resolver constraint, and a CI assertion. When only the first two exist, the floor is never executed. `pip install -e .`, `npm install`, and container builds resolve the newest release, so a stale or wrong floor stays green until someone actually builds with the old version. Bumping the number does not fix that. The fix is to make the floor executable and to prove the guard can fail.

> **为什么门槛只能用旧版本实测？** changelog 是能力宣告，不是本仓组合下的行为证据。真实门槛取决于本仓实际用到的字段、后端版本与打包路径。只有装上一个具体版本并跑真实解析或构建，才知道它接不接受；照抄 changelog 只会把门槛写成"看起来合理"的数字，下一次变更照样失真。

> **为什么断言必须并入已有 CI 脚本？** 新写一个"建议运行"的脚本不会拦住任何人。只有落在 CI 已经调用、且失败即红的那个入口里，下限才从文档变成契约。

> **为什么模板要同批改？** 模板与脚手架是"下一次生成"的真源。只改当前实例，新项目仍会带着旧下限出生，几个月后同一个问题会再出现一次。

## 2. 适用与不适用

适用：

- manifest 声明了最低支持版本，例如构建后端、`requires-python`、`engines.node`、容器基础镜像、peerDependency
- 声明与实际所需不符（声明 0.10、实测要求 0.11）
- 为某个新能力（新元数据字段、新配置项、新平台）抬高下限
- 已有守卫脚本，但怀疑扫描面漏了目录

不适用：

- 普通依赖升级、锁文件刷新、只是想让版本变新
- 版本选型或支持周期决策，这是用户的产品决策
- 单次构建失败的排错，按普通调试处理
- 跨文件声明漂移的"哪一侧是真源"判定，用 `declared-consistency-fix`；本技能接在它之后，负责把"应该是哪个版本"变成可执行断言

## 3. 五步流程

### 3.1 第 1 步：实测真门槛

先确定驱动这次下限的能力。例如"声明 PEP 639 的 SPDX 字符串与 `license-files`"，而不是笼统的"要对齐版本"。然后用三个版本夹逼：一个明显低于怀疑值、一个怀疑值、一个高于它。

对每个候选版本：

1. 隔离安装该精确版本（独立 venv，或 `pip download` / `npm pack` 后本地安装）
2. 用仓库真实使用的消费路径跑最小夹具（真实元数据解析器、真实构建入口），不要用 `--version` 或模块里的版本号代替
3. 记录「能力 × 版本」矩阵；若能力涉及文件，同时覆盖"文件存在"与"文件缺失"两个分支

完成标准：矩阵中最低的全绿版本即门槛，且门槛之上再验一个版本仍为绿，证明边界确实在那里。

> **为什么还要验门槛之上一个版本？** 只测一个失败点和一个成功点，无法区分"门槛在此"与"较高版本恰好可用"。上界验证把单调性钉住，避免把偶发通过当成边界。

已知陷阱：

- 内部导入路径不是公开 API。`scikit_build_core.metadata.StandardMetadata` 不存在，真实入口是 vendored 的 `pyproject_metadata`
- 包自身的 `__version__` 可能过期。0.11.2 的轮子里该属性显示 `0.9.1`；有效版本用 `importlib.metadata.version` 或包管理器查询
- 只测 happy path 会漏掉"声明了但文件不存在"的失败形态

可复跑的实测记录见 `references/probe-matrix.md`。

### 3.2 第 2 步：枚举全部声明面

按需求串搜索，而不是按文件名搜索：

```bash
git grep -n -E 'scikit-build-core|minimum-version' -- ':!vendor' ':!.git'
```

把命中按类清点：

- 实例 manifest：`pyproject.toml`、`package.json`、`Cargo.toml`
- 再生产源：模板、脚手架生成器、`init` 命令、CI 默认值
- 文档：构建指南、架构页、README 示例
- 打包配方：`conda.recipe/meta.yaml`、`environment.yml`、Dockerfile 基础镜像
- 有意钉住旧版本的测试或夹具

按类报告计数。某一类为空也要写明"该类为空"，未登记的声明面正是下限漂回去的路径。

### 3.3 第 3 步：把断言并入已有 CI 校验脚本

先定位 CI 已经在跑的检查脚本：

```bash
grep -rn -E 'check_|lint|quality' .github/workflows/
grep -rn 'continue-on-error' .github/
```

若已有脚本，就在其中新增断言；若没有，先提出方案并把它接进一个失败即红的步骤，不要造一个没人调用的检查器。

断言至少覆盖：

- 需求项存在，且带有下限
- 下限不低于实测门槛；解析时归一化 `0.11`、`0.11.0`、`v0.11`
- 第二声明面（如 `minimum-version`）存在且达标；工具支持派生语义时允许明确哨兵（如 `"build-system.requires"`）
- 违规时输出文件名、当前值、门槛值，退出码 1

然后验证门是活的：CI 确实调用这个脚本、该步骤没有 `continue-on-error`、故意破坏的夹具能让作业变红。

### 3.4 第 4 步：夹具正负双向验证

用临时目录搭一个与仓库同形的夹具，最少包含：

- 正向：恰好等于门槛（如 `>=0.11`）；门槛带补丁位并配合哨兵（如 `>=0.11.0` + `"build-system.requires"`）
- 负向：低于门槛（如 `>=0.10`）、无下限、缺第二声明面
- 语义：位于 `.gitmodules` 之外、但目录内残留 `.git` 的路径仍应被扫描

断言精确退出码（0 / 1）与报错条数，而不是只看"它失败了"。用仓库里真实的检查器跑夹具，不要为测试重写一套判定逻辑。

### 3.5 第 5 步：扫描面审计

守卫的排除逻辑是最薄弱的环节。把"应扫描集合"与"实际扫描集合"对账：

- 打印实际扫描到的文件数与路径
- 子模块只按 `.gitmodules` 声明的路径判定，不要用"目录内有没有 `.git`"
- 主仓直接追踪、但目录内残留 `.git` 的目录不是子模块；排除它就是一个静默盲区
- 修完后复跑并对比计数（源案例 10 → 12），确认新纳入的文件全部通过

实现骨架与夹具的期望输出见 `references/guard-and-fixtures.md`。

## 4. 完成判据

报告"已完成"之前，以下证据必须齐全：

| # | 证据 |
|---|---|
| 1 | 能力 × 版本矩阵，含最低全绿版本与门槛之上一个版本 |
| 2 | 声明面按类计数，模板与生成器已包含 |
| 3 | 真实仓库跑检查器 → 退出码 0，并打印扫描计数 |
| 4 | 每个负向夹具 → 退出码 1；正向夹具 → 退出码 0 |
| 5 | 扫描面前后计数，新纳入的路径全部通过 |
| 6 | CI 中调用该检查器的文件与行号，且无 `continue-on-error` |

## 5. 安全检查清单（逐项确认）

- [ ] 写操作前已展示变更面与 diff 预览并获得确认（本技能本身不提交）
- [ ] 重复执行同一守卫是幂等的：结果一致，不产生新改动
- [ ] 门槛来自实测矩阵，不是 changelog 或经验
- [ ] 每个候选版本的安装来源与有效版本号已记录
- [ ] 声明面已按类枚举，模板与脚手架生成器已更新
- [ ] 断言位于 CI 已调用的脚本内，且该步骤失败即红
- [ ] 正向夹具退出码 0、负向夹具退出码 1，报错文案与条数已核对
- [ ] 扫描面覆盖所有第一方 manifest，排除项已逐一目检
- [ ] 子模块判定基于 `.gitmodules`，不基于目录内 `.git`
- [ ] 改动范围与 `git diff --stat` 一致，未触碰无关脏文件
- [ ] 未提交、未推送；提交需要单独授权

## 6. Gotchas（陷阱与反直觉行为）

1. **两处声明面互不背书。** `build-system.requires` 的下限与 `[tool.scikit-build].minimum-version` 是独立字段；只改一处，另一处仍会在构建时生效或报错。
2. **包内 `__version__` 会过期。** 已实测 0.11.2 轮子内该值为 `0.9.1`；判断有效版本要用 `importlib.metadata.version`。
3. **内部导入路径不是稳定 API。** 探测脚本引用 `scikit_build_core.metadata` 会直接 `ImportError`，真实入口是 vendored 的 `pyproject_metadata`。
4. **安装到最新版会掩盖失真。** CI 用 `pip install -e .` 时解析到最新发布版，旧下限永远不会被执行。
5. **用 `.git` 判定子模块会静默漏扫。** 主仓直接追踪但残留 `.git` 的目录会被当成子模块排除；源案例因此漏掉两个目录。
6. **只测正向等于没测门。** 守卫必须能红也能绿；负向夹具要断言精确退出码与报错条数。
7. **夹具放在仓库外时根目录推导会变。** 检查器通常用 `__file__` 的父目录推仓库根；在临时目录跑要么复制脚本，要么显式传根路径。
8. **`>=0.11` 与 `>=0.11.0` 语义等价。** 比较前补齐位数，否则会把达标值误判为低版本。
9. **哨兵值是合法配置，不是遗漏。** 如 `minimum-version = "build-system.requires"` 表示从需求派生；守卫应放行而不是报"缺失"。
10. **只改 `pyproject.toml` 会漏掉配方。** conda `meta.yaml`、`environment.yml`、构建指南里的 `pip install` 示例同样是声明面。
11. **文档示例会被复制。** 构建指南里的旧下限是下一次手写的来源，和模板同等优先级。
12. **格式化会打断验证链。** 新增断言后先跑仓库的 formatter/linter，再复跑守卫，避免"脚本能过但 ruff 不过"的假完成。

## 7. References

- `references/probe-matrix.md`：scikit-build-core 0.9.10 / 0.10.0 / 0.11.0 / 0.11.x 的实测矩阵、探测方法与两个导入/版本陷阱
- `references/guard-and-fixtures.md`：断言规则、`.gitmodules` 扫描面骨架、六组夹具的期望报错与退出码、CI 接线核查

## 8. Changelog

- 2026-10-24: 初始版本，萃取自会话 c9d91a62（xuanspace scikit-build-core 下限 0.10 → 0.11 的失真修复）。
