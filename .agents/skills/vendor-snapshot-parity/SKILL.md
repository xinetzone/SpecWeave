---
name: vendor-snapshot-parity
version: 1.0.0
description: "把第三方单体（装饰器/单例构造的 CLI parser、配置结构等）迁出又要证明与上游逐字段对等时使用。用 vendor 无关序列化器一次性生成 JSON 快照入库，新构造器读快照对拍，日常测试不依赖 vendor 检出。触发：fork/vendor 库分层重构、argparse/CLI 参数表对等、上游结构对拍、'证明和上游一致'。"
argument-hint: "[<待对拍对象：argparse parser / 配置树 / ...>]"
user-invocable: true
title: "Vendor-Snapshot Parity 快照对拍迁移 Skill"
---

# Vendor-Snapshot Parity 快照对拍迁移 Skill

把"逐行翻译第三方单体"时的**对等性证明**从人肉断言变成机器可执行的快照对拍。
核心是让**生成快照**（需要 vendor）与**消费快照**（日常测试，不需要 vendor）解耦。

## 何时使用

- 把第三方单文件库（vendor/fork）的 argparse/CLI、配置 schema、序列化结构等
  迁入自有分层包，且要求"与上游 pinned 版本逐字段对等"；
- 需要在 CI 里长期守护对等性，但 CI 环境**不一定检出 vendor 子模块/源码**；
- 想在升级上游基线时，用一次脚本得到字段级 diff，而不是重新人肉通读。

不适用：纯行为重写（不追求对等）、只需少量函数输入输出对比（直接用上游单测即可）。

## 四件套结构（缺一不可）

在目标库 `tests/`（或等价测试目录）放置：

| 文件 | 角色 | 是否接触 vendor |
|---|---|---|
| `<lib>_parity_lib.py` | **vendor 无关序列化器**：把待测对象树（如 argparse parser）转成 JSON 安全的纯数据 | 否 |
| `generate_parity_snapshots.py` | **一次性生成脚本**：importlib 加载上游、复刻其构造顺序、调用序列化器产出快照 | 是 |
| `snapshots/<name>.json` | 入库的快照，含 `meta`（source/上游 commit/python/生成说明） | 产物 |
| `test_<name>_parity.py` | 对拍测试：读快照 → 构造新库对象树 → 用同一序列化器 → 逐节点深度对比 | 否 |

关键：**序列化器是新旧两侧共用的同一份代码**，保证对比口径一致；
测试运行只读仓库内 JSON，不 import、不路径依赖 vendor。

## 标准步骤

### 1. 冻结上游基线
记录 pinned commit（写进快照 meta 与 README/署名），确认 vendor 工作树洁净
（只读子模块：`git -C <vendor> status --porcelain` 应为空；注意 CRLF 翻转会造成整树假 M，
用 `git diff --ignore-cr-at-eol` 判定零语义差异）。

### 2. 写序列化器（先于看新库）
- 只采集**行为相关字段**，逐个显式列出，不用 `vars()`/`__dict__` 全量倾倒；
- argparse 建议维度：`option_strings / dest / action / nargs / const / default /
  choices / required / metavar / type / help`，外加命令的注册顺序与 help/description；
- 把不可 JSON 化的值归一化：`type` → `__name__`；callable → 类名；
  set/tuple → list；argparse 特有哨兵（如 argparse.SUPPRESS）→ 标记字符串；
- **明确记录豁免字段及理由**（典型：`prog` 随 `sys.argv[0]` 变化，重命名入口必然不同，
  须在 AC/文档中事先允许）——豁免是白名单显式声明，不是偷偷漏采。

### 3. 写生成脚本（复刻上游构造序，而非"等价重写"）
- 用 importlib/sys.path 指向上游源码，支持 `*_SRC` 环境变量覆盖路径；
- 严格按上游真实装配顺序构造对象（以上游 argparse 为例：先建全局 parser 与
  全局参数/subparsers，先 add 伪命令，再遍历注册表逐个 append parser），
  否则共享 parser 的挂载顺序差异不会暴露；
- 顶层结构稳定：`{"meta": {...}, "global": {...}, "commands": {...}}`。

### 4. 生成并人工审一眼快照
运行脚本产出 JSON，核对 `meta.commit` 是冻结的基线、命令数/顺序与上游一致后入库。

### 5. 写对拍测试（用同一序列化器）
- 新库提供纯函数构造器（无副作用、不读 argv），测试调用它得到对象树；
- 逐节点对比并在失败时输出**字段级 diff 报告**（命令名→action→字段→上游值 vs 当前值），
  便于一眼定位漂移；
- 同时对拍"命令表面"：命令集合、注册顺序、每命令 help 与多行 description；
- 用 subtest 参数化每个命令，使全命令都有独立证据。

### 6. 设重新生成纪律（写进生成脚本 docstring）
- 快照**仅在主动升级上游基线时**由维护者重新生成，生成后必须人工研判差异；
- 禁止"为了让测试变绿而刷新快照"——快照是被对拍的基准，不是可随手更新的产物；
- 日常 CI/门禁只跑对拍测试，不跑生成脚本（vendor 可不检出）。

## 反模式（踩过的坑）

1. **每个对拍测试都 import vendor**：CI 强依赖子模块检出，路径/版本漂移即红，
   快照方案的全部价值丧失。
2. **为变绿把关键维度排除在序列化器外**：default/nargs/required/choices 任何一个漏采，
   "零差异"结论都不可信。豁免必须显式、有 AC 依据、写进文档。
3. **生成脚本里"等价重写"上游构造逻辑**：若不严格复刻上游的注册/append 顺序，
   共享 parser 的挂载顺序错误不会被快照发现——生成侧必须忠实，对拍侧才谈得上严格。
4. **用 `vars(parser_action)` 全量倾倒**：会混入 prog 等易变字段与内部状态，
   噪音淹没真实差异，也无法做字段级豁免。
5. **快照无 meta 溯源**：三个月后无人知道快照对应哪个上游 commit，对等声明失去锚点。
6. **测试失败就改快照不改代码**：顺序必须是"测试红 → 回代码核对是漂移还是有意变更 →
   有意变更先登记差异+更新 AC，再谈基线"，不能反向。

## 参考实现（本仓库真实样板）

xuan-compose（libs/xuan-compose，对拍 podman-compose 1.6.0 / commit e3df104）：

- 序列化器：`libs/xuan-compose/tests/parity_lib.py`
- 生成脚本：`libs/xuan-compose/tests/generate_parity_snapshots.py`
- 快照：`libs/xuan-compose/tests/snapshots/cli_parity.json`（25 个 subparser 含 help 伪命令）
- 对拍测试：`libs/xuan-compose/tests/test_cli_parity.py`、
  `test_command_surface.py`（50 个 subtest）
- 结论：首跑即零差异（11 维，prog 豁免）；方法与总账见
  `libs/xuan-compose/docs/parity.md`、
  `libs/xuan-compose/docs/2026-09-16-xuan-compose-delivery-summary.md` §6 模式 1。

## 完成判据

- [ ] 四件套齐备，序列化器被新旧两侧共用
- [ ] 快照含 pinned commit 等 meta，命令/节点数与上游核对一致
- [ ] 对拍测试在**不检出 vendor** 的环境也能通过
- [ ] 豁免字段显式列入文档且有 AC 依据
- [ ] 生成脚本 docstring 写明"仅升级基线时重生成 + 禁止为变绿刷新"
- [ ] 对拍失败能输出字段级 diff
