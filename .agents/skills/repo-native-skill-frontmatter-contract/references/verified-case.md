# 实测证据

本文件记录本技能全部结论的出处：来源会话、本次创建会话的对照实验、源码定位与未验证项。命令均在 `D:\spaces\SpecWeave` 下执行，日期 2026-10-24。

## 1. 来源会话（48f79e3f-4485-4274-86c5-bf77dd7ddb31）

该会话创建了 `git-sandbox-rehearsal`，过程记录：

| 环节 | 结果 | 出处 |
|---|---|---|
| 首次质量门 | 80 分，缺 `version`、`user-invocable`、`argument-hint`、`paths` 四个推荐字段 | 会话内助手自述 |
| 补齐后复跑 | 100 分 | 会话内助手自述 |
| `quick_validate.py` | 退出 1，报 `Unexpected key(s): argument-hint, paths, title, user-invocable, version` | 会话内助手自述 |
| 报告口径 | 把退出 1 解释为契约差异，未删除字段迎合 | 会话内助手自述 |

会话转储只保留了摘要层，不含每条命令的原始 stdout；因此本轮重新做了可复现的实测，见下节。

## 2. 本次创建会话的对照实验

### 2.1 正样本：本技能自身

```text
python .agents/scripts/check-skill-quality.py --path .agents/skills/repo-native-skill-frontmatter-contract --score --threshold 100
repo-native-skill-frontmatter-contract: 100
平均: 100
exit=0
```

`--verbose` 中无 `[WARN]` / `[FAIL]` 行。

### 2.2 负样本：仅把四个推荐字段嵌套到 metadata

构造方法：复制本技能 `SKILL.md` 到临时目录，正文与其余字段完全不变，只把 `version`、`argument-hint`、`user-invocable`、`paths` 移入 `metadata`。输入键集合：

```yaml
name: repo-native-skill-frontmatter-contract
description: <原文>
disable-model-invocation: false
title: <原文>
source: <原文>
metadata:
  version: 1.0.0
  argument-hint: "<skill-dir>"
  user-invocable: true
  paths:
  - ".agents/skills/**/SKILL.md"
  - ...
```

结果：

```text
repo-native-skill-frontmatter-contract: 80
平均: 80
exit=1

[WARN] frontmatter.argument-hint: 建议字段 'argument-hint' 缺失
[WARN] frontmatter.user-invocable: 建议字段 'user-invocable' 缺失
[WARN] frontmatter.version: 建议字段 'version' 缺失
[WARN] frontmatter.paths: 建议字段 'paths' 缺失
```

四条 warn × 5 分 = −20，正好 80。正文一字未改，说明失分只来自键位。`yaml.safe_load` 能正常解析该文件，即文件本身是合法 YAML——错误不会以解析失败的形式暴露。

### 2.3 第一次夹具失败：目录名必须与 name 一致

首版夹具放在 `rnsfc-fixture-nested/`，分数为 **70**，额外出现：

```text
[WARN] open_standard.name.dir_match: name应与父目录名一致（name: repo-native-skill-frontmatter-contract，目录: rnsfc-fixture-nested）
[WARN] open_standard.compliance: 存在开放标准规范警告（建议修复name格式）
```

把夹具目录改名为 `repo-native-skill-frontmatter-contract` 后回到 80。教训：对照实验必须只改变一个变量，目录名也是变量。

### 2.4 通用门：本技能与同根满分兄弟

```text
python .agents/skills/skill-creator/scripts/quick_validate.py .agents/skills/repo-native-skill-frontmatter-contract
Unexpected key(s) in SKILL.md frontmatter: argument-hint, disable-model-invocation, paths, source, title, user-invocable, version.
exit=1

python .agents/skills/skill-creator/scripts/quick_validate.py .agents/skills/atomic-commit-mixed-file-split
Unexpected key(s) in SKILL.md frontmatter: argument-hint, paths, source, title, user-invocable, version.
exit=1
```

另测两个既有原生技能，均退出 1：

| 技能 | 质量门 | 通用门 | unexpected keys |
|---|---|---|---|
| `git-sandbox-rehearsal` | 100，退出 0 | 退出 1 | argument-hint, paths, title, user-invocable, version |
| `registered-skill-frontmatter-completion` | 未在本轮复测 | 退出 1 | argument-hint, disable-model-invocation, paths, source, user-invocable, version, x-toml-ref |

质量门满分 + 通用门拒绝同时成立，构成契约差异的证据。

### 2.5 链接门真实暴露的 `source` 坑

首次运行：

```text
python .agents/scripts/check-links.py --path .agents/skills/repo-native-skill-frontmatter-contract --check-frontmatter-paths
失败: 1 个 frontmatter 路径问题
  source: 来源会话 ...；本技能创建会话的 100/80 对照实测见 references/verified-case.md (文件不存在: ...)
exit=1
```

原因在 `.agents/scripts/check-links.py` 的 `_extract_paths_from_value`：先按 `+ | , ;` 切分，若片段含中文但**同时**含 `.md`/`.toml`/`.py` 则不跳过，再因含 `/` 判定为路径。`source` 里的「见 references/verified-case.md」因此被整段当成路径。

处置：`source` 只保留来源标识，路径说明移到正文。修改后复跑：

```text
通过: 所有本地引用均存在
通过: 所有 frontmatter 路径字段均有效
exit=0
```

### 2.6 经用户级联接复跑：跨目录相对链接断链

本技能按仓库约定以目录联接暴露到 `~/.qoder/skills/`。第一次经联接路径跑链接门：

```text
python .agents/scripts/check-links.py --path C:/Users/xinzo/.qoder/skills/repo-native-skill-frontmatter-contract --check-frontmatter-paths
校验失败: 发现 5 个断链（本地 5, 外部 0, frontmatter 0）
```

5 个断链全部来自 `references/verified-case.md` 里指向仓库脚本的 `../../../scripts/...`：在主权区该深度指向 `.agents/scripts/`，在用户级根同一相对路径会越出 Skill 目录。把这类链接降级为行内代码后，主权区与联接路径均通过。

> 这说明「主权区通过」不等于「联接后通过」：凡是链接目标在 Skill 目录之外的，都要按两个根各跑一次。

### 2.7 回读顶层键

```text
python -c "import yaml,pathlib; ... print(sorted(yaml.safe_load(fm).keys()))"
['argument-hint', 'description', 'disable-model-invocation', 'name', 'paths', 'source', 'title', 'user-invocable', 'version']
```

四个推荐字段全部出现在顶层集合中；`metadata` 未出现，因为没有使用它。

## 3. 源码定位

| 结论 | 源码 |
|---|---|
| 推荐字段集合与评分权重 | `.agents/scripts/lib/check_skill_quality/constants.py` 的 `FRONTMATTER_RECOMMENDED_FIELDS` |
| 每个未通过 warn 减 5 | `.agents/scripts/lib/check_skill_quality/scoring.py` |
| 行首锚点读取字段 | `.agents/scripts/lib/frontmatter.py` 的 `extract_yaml_field` |
| 通用门允许的 6 个键 | `.agents/skills/skill-creator/scripts/quick_validate.py` 的 `ALLOWED_PROPERTIES` |

## 4. 未验证项

- 未在 PyYAML 之外的解析器上验证嵌套字段行为；本结论只覆盖仓库当前检查器。
- 未验证其他客户端是否真的「安全忽略」自定义字段；只验证了仓库质量门与随包 `quick_validate` 的脚本行为。
- 本轮按约定不做四处登记（README、capability-registry、CHANGELOG、SKILL.toml 镜像），因此本技能尚未出现在仓库登记面。
- 未做 skill-creator 的 eval 自动评测；`evals/evals.json` 只有场景定义，未跑 grader。

## 5. 复现命令清单

```bash
REPO="$(git -C D:/spaces/SpecWeave rev-parse --show-toplevel)"
SKILL_DIR="$REPO/.agents/skills/repo-native-skill-frontmatter-contract"

python "$REPO/.agents/scripts/check-skill-quality.py" --path "$SKILL_DIR" --score --threshold 100
python "$REPO/.agents/scripts/check-skill-quality.py" --path "$SKILL_DIR" --verbose
python "$REPO/.agents/scripts/check-links.py" --path "$SKILL_DIR" --check-frontmatter-paths
python "$REPO/.agents/skills/skill-creator/scripts/quick_validate.py" "$SKILL_DIR"
python "$REPO/.agents/skills/skill-creator/scripts/quick_validate.py" "$REPO/.agents/skills/atomic-commit-mixed-file-split"
```
