# 来源会话验证案例

本文件记录 `skill-guidance-correction-propagation` 的证据来源。案例来自 2026-10-24 的会话 `a3d000e0-c33a-4ee7-9c39-8d055e687b13`，对象是既有 Skill `license-scope-unification` 的技术口径纠错。

以下命令与数字均为来源会话中实际执行或产出的结果。本次创建新 Skill 时只回读了当前文件状态，没有重跑许可证审计脚本。

## 1. 起点

会话最初创建了 `pep639-license-metadata-migration`。创建完成后，报告了一处遗留：

```text
C:/Users/xinzo/.qoder/skills/license-scope-unification/SKILL.md:128
```

原文要求：

```text
Python manifests: prefer the PEP 639 string form license = "Apache-2.0"
plus the matching License :: classifier.
```

而实测结论相反：SPDX 字符串与任意 `License ::` classifier 互斥，即使 classifier 与 SPDX 一致，也会在元数据解析阶段被拒绝。

## 2. 第一轮：只改用户指出的那一处

用户指令：

```text
是的，把那一处也顺手改了吧
```

实际改动落在两处，因为正文第 128 行指向引用文件：

| 文件 | 位置 | 改动 |
|---|---|---|
| `SKILL.md` | 第 128 行 | 改为 SPDX 字符串 + `license-files`，删除全部 `License ::`；写明二者互斥 |
| `references/evidence-and-exceptions.md` | 第 67 行章节标题 | 从 `SPDX and classifier mapping` 改为 `SPDX expressions and legacy license classifiers` |
| 同上 | 第 69 行引言 | 写明互斥与精确报错，说明外层会包裹为 `Failed to parse pyproject.toml (1 sub-exception)` |
| 同上 | 第 73 行表格用途 | 降级为“仅用于审计时读懂历史 manifest”，不是目标态 |
| 同上 | 第 85 / 89 行结论 | 删除 “classifier is supplementary” 旧结论 |

第一轮后的门禁：

```text
Unexpected key(s) in SKILL.md frontmatter: source. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
VALIDATE_EXIT=1
```

归因：`source` 是该 Skill **改动前就已存在的顶层字段**，不在用户级 `quick_validate.py` 的允许键集内。这不是本次改动引入的回归，因此没有擅自修改，只单独报告。后来新建的 `pep639-license-metadata-migration` 把溯源放进 `metadata.source`，才通过同一校验器。

第一轮仍未处理：

- 审计脚本只检查“classifier 与期望许可证不一致”，不检查“SPDX 字符串 + 任意 `License ::` 共存”。
- 测试夹具 `apache_pyproject()` 默认同时写 SPDX 与匹配的 Apache classifier，把非法组合当成健康基线。

## 3. 第二轮：修复测试数据

用户指令：

```text
顺便修复 audit 脚本的测试数据
```

改动全部在 `scripts/test_license_audit.py`，脚本行为未改：

| 夹具 | 原状态 | 现状态 |
|---|---|---|
| `apache_pyproject()` 默认值 | `license = "Apache-2.0"` + 匹配的 Apache classifier | 默认不含 classifier，改为声明 `license-files = ["LICENSE"]` |
| 模板漂移用例 | 模板同时写 `license = "MIT"` + MIT classifier | 只保留 `license = "MIT"`，形态正确、标识符错误 |
| GPL 有意例外用例 | SPDX + 匹配的 GPL classifier | SPDX + `license-files`，删除 classifier |
| classifier 不匹配用例 | 隐含“SPDX 与 classifier 并用合法” | 保留，但注明这是迁移中状态 |

删除模板里的 classifier 会让“模板 classifier 分支”失去覆盖，因此新增：

```text
test_legacy_template_classifier_mismatch_is_an_error
```

它构造旧式模板：只有 `License ::`、没有 SPDX 字段，断言仍产出 `TEMPLATE_CONFLICT`。

验证：

```text
Ran 11 tests
OK
TESTS_EXIT=0

Scanned 3 files: 0 error(s), 0 warning(s), 0 info.
Result: PASS
EXIT= 0
```

第二轮仍未处理：脚本的检测缺口。用户随后明确授权补检测逻辑。

## 4. 第三轮：补检测逻辑

用户指令：

```text
把检测逻辑也补上吧
```

改动：

| 文件 | 改动 |
|---|---|
| `scripts/license_audit.py` | `parse_pyproject` 在 `project.license` 为非空字符串且存在 `License ::` classifier 时，额外产出一条 `classifier-coexistence` 声明 |
| 同上 | `_check_declaration` 新增分支，产出 `LICENSE_CLASSIFIER_COEXISTENCE`（ERROR，带行号与原始 classifier 值） |
| `references/evidence-and-exceptions.md` §8 | 能力清单新增该检查；限制清单说明 `setup.cfg` / `setup.py` 不查 |

判定规则：只要 `[project] license` 是 SPDX 字符串，**任何** `License ::` classifier 都报错，与二者是否一致无关；模板同样适用；例外登记无法压制，因为这是元数据非法，不是有意许可证分歧。

验证：

```text
Ran 12 tests
OK
TESTS_EXIT=0

Scanned 917 files: 0 error(s), 0 warning(s), 8 info.
Result: PASS
AUDIT_EXIT=0
```

正样本（SPDX + 一致的 Apache classifier）：

```text
[ERROR] LICENSE_CLASSIFIER_COEXISTENCE pyproject.toml:6 - project.classifiers 声明 'License :: OSI Approved :: Apache Software License'，与 project.license 的 SPDX 字符串互斥；构建元数据会被拒绝
Scanned 2 files: 1 error(s), 0 warning(s), 0 info.
Result: FAIL
EXIT= 1
```

未覆盖：`tool.poetry.license` 与 `setup.cfg` / `setup.py` 的同形态组合，原因是 Poetry 历史行为允许并用、后两者的字符串语义模糊，误报风险高。

## 5. 当前状态回读

本次创建新 Skill 时回读了被改对象：

- `SKILL.md:128` 已是互斥表述。
- `references/evidence-and-exceptions.md` §3 标题与引言已改为互斥表述，表格标明仅供读取旧 manifest。
- `scripts/license_audit.py` 中存在 `classifier-coexistence` 与 `LICENSE_CLASSIFIER_COEXISTENCE`。
- `scripts/test_license_audit.py` 当前有 12 个 `test_` 方法。

## 6. 可复用的教训

| 教训 | 对应流程 |
|---|---|
| 正文与引用章节必须同批修改；引用文件的标题本身也可能是旧口径 | 第 3 步依赖顺序 |
| 测试夹具是“可执行的口径”，非法组合当基线会让测试绿、构建红 | 第 4 步覆盖守恒 |
| 删除某分支唯一夹具前，先补新非法形态测试 | 第 4 步覆盖守恒 |
| 文档与夹具改完不等于脚本能发现缺陷；检测行为变更单独授权 | 铁律 5、第 3 步 |
| 既有门禁失败要归因，不能算作本次回归，也不能顺手改无关字段 | 第 6 步 baseline / delta |
| 初始范围说“一处”时，仍应先枚举直接耦合面，否则会用两轮追加来收敛 | 第 1、2 步 |

## 7. 复现命令模板

```bash
SKILL="C:/Users/<user>/.qoder/skills/license-scope-unification"

python "$SKILL/scripts/test_license_audit.py"
echo "TESTS_EXIT=$?"

python "$SKILL/scripts/license_audit.py" "<repo>" \
  --expected Apache-2.0 --allow GPL-2.0-only
echo "AUDIT_EXIT=$?"
```

预期：测试全部通过；已迁移仓库 0 error、0 warning；正样本夹具出现 `LICENSE_CLASSIFIER_COEXISTENCE` 且退出 1。实际运行前先确认目标仓库与依赖环境，未运行时在报告中写“未验证”。
