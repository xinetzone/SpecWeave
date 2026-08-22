---
id: "okf-sources-path-normalization"
source: "../../../../../.trae/specs/jupyter-okf-wiki-group/progress.md + fix_jupyter_frontmatter.py 修复实践"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/okf-sources-path-normalization.toml"
---
# OKF sources 路径规范化：5级前缀 + 映射表 + 正则字符类陷阱

## 模式概述

批量生成 OKF（Open Knowledge Format）文档时，`sources` 字段必须指向真实存在的信源文件（`references/` 下的相对路径）。当 bundle 目录与源码目录不在同一层级时，规范化 `sources` 需要三步：**提取真实路径 → 拼接正确层级的 `../` 前缀 → 存在性过滤**。本模式沉淀了批量修复中的三条关键经验：5 级 `../` 前缀计算、bundle→源码目录命名差异映射表、正则字符类吞点陷阱。

## 问题现象

批量生成的 facts.md/insights.md 中 `sources` 字段普遍不可用，表现为五类缺失与两类路径错误：

**五类 frontmatter 缺失**：
1. 缺 `type`
2. 缺 `okf_version`
3. 缺 `title`
4. 缺 `generated`
5. 缺 `sources`

**两类路径错误**：
1. **前缀层级不足**：`sources` 用 `../` 回退层级不够，无法从 bundle 目录到达仓库根。
2. **含 bundle 子目录**：`sources` 路径误包含 bundle 目录名，指向不存在的路径。

## 解决方案

### 修复算法（三步骤）

```
提取：从正文 F- 行正则提取源码相对路径 ∪ 现有 sources 字段
规范化：按 bundle→源码目录映射表替换目录名差异
拼前缀：计算 bundle 目录到仓库根的 ../ 层级数，拼接正确前缀
过滤：存在性过滤（只保留真实存在的文件），重建 frontmatter
```

### 5 级 `../` 前缀计算

bundle 目录位于 `projects/awesome-okf-xs/bundles/jupyter/<bundle>/`，源码位于 `external/libs/jupyter/<src>/`：

```
<root>/projects/awesome-okf-xs/bundles/jupyter/<bundle>/  → 仓库根 = 5 级
../  → bundles/jupyter/<bundle>/
../../ → jupyter/<bundle>/
../../../ → <bundle>/
../../../../ → awesome-okf-xs/
../../../../../ → root/
```

因此正确 sources 形如：
```
../../../../../external/libs/jupyter/<src>/<file>.py
```

### bundle→源码目录映射表

部分 bundle 名与源码目录名不一致，无法靠同名推断，需 48 个异常项映射表：

| bundle 名 | 源码目录名 | 差异类型 |
|-----------|-----------|---------|
| jupyter-docker-stacks | docker-stacks | 前缀剥离 |
| jupyterlite-ai | ai | 前缀剥离 |
| jupyterlab-pygments | jupyterlab_pygments | 连字符→下划线 |
| jupyter-server-terminals | jupyter_server_terminals | 连字符→下划线 |
| …（48 项） | … | … |

### 正则字符类陷阱

路径提取正则的**字符类不能包含 `.`**：

```python
# ❌ 错误：字符类含 .，贪婪吞掉扩展名前的点
pattern = r"([A-Za-z0-9_/.\-]+)"   # app.py 会被截成 appp 或吃掉扩展名

# ✅ 正确：字符类不含 .，扩展名点留在类外
pattern = r"([A-Za-z0-9_/\-]+(?:\.[A-Za-z0-9]+)?)"
```

`.py` 等扩展名前的点若被吞进字符类，`app.py` 会因贪婪匹配把 `p.py` 之后的内容一并吞掉，造成路径截断。

### 无源码仓库豁免

无独立本地源码仓库的 bundle（如 xeus-lite-demo），`sources` 无法指向真实文件：在 log.md 标注「无源码仓库」豁免，作为可接受告警而非错误。

## 适用场景

- ✅ OKF/同类带 `sources` 溯源字段的批量文档生成后的批量修复
- ✅ bundle 目录与源码目录层级不同、存在命名差异的批量映射
- ✅ 正则提取路径/文件名的代码编写
- ✅ 批量 frontmatter 规范化的质量门（V 阶段）

**不适用场景**：
- ❌ 单个文档手动补 sources（脚本修复过度工程）
- ❌ sources 指向网络 URL 而非本地文件（无需层级计算）

## 实际案例

### 案例1：jupyter-okf-wiki-group 全量修复（本项目）

65 个 bundle 批量生成后，frontmatter 五类缺失与 sources 路径错误集中爆发。修复脚本按「正文 F- 行提取路径 ∪ 现有 sources → 规范化 → 拼正确前缀 → 存在性过滤」重建，全部修复；最终 frontmatter 校验 0 错误、2 可接受告警（xeus-lite-demo 无源码豁免）。

### 案例2：MDI 研究报告原子化（metadata-layering 源实践）

原子化拆分时 frontmatter 模板化 + 路径自动计算（配合 depth-reference-table 模式），证明"路径层级计算脚本化"在批量场景的高性价比。

## 反模式

### 反模式1：凭印象写 `../` 层级

不数目录深度，随手写 2-3 级 `../`。

**为什么错**：层级不足导致 sources 解析失败，且错误隐蔽（仅链接失效不报语法错误）。

**正确做法**：从文件目录逐级回退到仓库根，精确计数。

### 反模式2：用同名推断源码目录

认为 bundle 名一定等于源码目录名。

**为什么错**：48 项异常（前缀剥离/连字符→下划线）导致大量路径指向不存在文件。

**正确做法**：建立 bundle→源码目录映射表逐一映射。

### 反模式3：正则字符类含 `.`

路径提取正则字符类包含 `.` 导致贪婪吞点。

**为什么错**：`app.py` 被截成 `appp` 或吃掉扩展名，静默产生错误路径。

**正确做法**：字符类排除 `.`，扩展名作为可选分组放在类外。

### 反模式4：无源码仓库不豁免、硬造路径

对无源码仓库的 bundle 编造 sources 路径使其"看起来完整"。

**为什么错**：虚构路径违反零推测原则，读者引用即断链。

**正确做法**：标注「无源码仓库」豁免，记入 log.md，作为可接受告警。

### 反模式5：只修 sources 不修五类缺失

修复只处理路径，忽略 type/okf_version/title/generated 缺失。

**为什么错**：frontmatter 校验仍失败，质量门不通过。

**正确做法**：一次性重建完整 frontmatter（五类字段 + sources）。

### 反模式6：不做过滤直接写死路径

拼接路径后不验证存在性直接写入。

**为什么错**：映射表遗漏项或拼写错误会写入大量断链。

**正确做法**：存在性过滤只保留真实文件，暴露映射表缺口。

## 与其他模式的关系

| 相关模式 | 关系 | 说明 |
|---------|------|------|
| [metadata-layering.md](../architecture-patterns/metadata-layering.md) | 配套 | sources 规范化是元数据分层中"内联溯源字段"的落地修复 |
| [link-check-cmd](../../../skills/link-check-cmd/SKILL.md) | 配套 | sources 修复后需链接检查验证 |
| [source-code-to-okf-wiki-workflow.md](../methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md) | 上游 | 本模式是五阶段工作流 V 阶段（验证修复）的可复用代码经验 |
| [content-fingerprint-incremental-sync.md](../architecture-patterns/content-fingerprint-incremental-sync.md) | 类比 | 都强调"机器可验证"而非"看起来对" |

## 边界与选型

### 什么时候必须建映射表？

- bundle 名与源码目录名不一致的数量 > 个位数
- 差异类型多样（前缀剥离/连字符→下划线/完全无关）

### 什么时候可省略存在性过滤？

- 映射表已完全覆盖且经过全量验证
- 路径来源为单一可信目录遍历（无映射需求）

### 兼容与迁移

- 目录重命名后需同步更新映射表与前缀计算
- 新增 bundle 类型时先查映射表，禁止靠同名推断

<!-- changelog -->
