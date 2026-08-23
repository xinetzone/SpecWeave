---
id: "open-code-review-wiki-14"
title: "审查规则系统技术参考"
source: "https://open-codereview.ai/docs/review-rules"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/14-review-rules.toml"
---
# 审查规则系统技术参考

> 本章深入解析 OCR 规则系统的技术实现细节。四层规则优先级的基本概念和基础配置已在[关键技术优化](04-optimizations.md#用户主观性问题四层规则穿透机制)、[集成与高级用法](05-integrations.md#三自定义评审规则)和[常见问题](09-faq.md#q5-如何自定义评审规则四层规则如何生效)中介绍，本章补充 ProjectRule 结构、Glob 语法、默认排除、系统规则映射、文件过滤算法与安全限制等技术参考内容。

---

## 1. ProjectRule 结构

项目级与全局级配置共享同一个 `ProjectRule` 结构：

```go
// internal/rules/types.go
type ProjectRule struct {
    Include          []string   `json:"include,omitempty"`
    Exclude          []string   `json:"exclude,omitempty"`
    Rules            []PathRule `json:"rules,omitempty"`
    MergeSystemRule  *bool      `json:"merge_system_rule,omitempty"`
}

type PathRule struct {
    Path string `json:"path"` // glob 模式
    Rule string `json:"rule"` // 规则文件名（如 go.md）
}
```

### 1.1 字段语义详解

#### include —— 绕过默认排除，而非白名单

这是最容易误解的字段。`include` 的作用不是"只审查这些文件"，而是"把被默认排除的文件重新放行"。

例如，默认排除会跳过 `**/*_test.go`（测试文件）。如果团队希望审查测试文件：

```json
{
  "include": ["**/*_test.go"]
}
```

此时 `**/*_test.go` 不再被默认排除命中，进入审查范围。但 `include` **无法穿透扩展名白名单**——即便放行了一个 `.bin` 文件，仍会因扩展名不在白名单而被排除。

#### exclude —— 最高优先级排除

`exclude` 是绝对的排除，优先级高于一切。即便文件被 `include` 放行、被系统规则覆盖，只要命中 `exclude`，就被排除：

```json
{
  "exclude": ["**/generated/**", "**/*.pb.go", "vendor/**"]
}
```

#### rules —— 声明顺序评估

`rules` 是有序数组，按声明顺序逐条评估，首个匹配的 `path` 决定使用哪个 `rule` 文件：

```json
{
  "rules": [
    { "path": "**/proto/**/*.go", "rule": "go_proto.md" },
    { "path": "**/*.go", "rule": "go.md" }
  ]
}
```

更具体的模式应放在前面。

#### merge_system_rule —— 合并系统规则

设为 `true` 时，对命中 `rules` 的文件，OCR 把系统默认规则与项目指定规则**合并**（而非替换）。合并格式为项目规则在前、系统规则在后，Agent 同时看到两份指引。

- 不开启：项目 `rules` 命中后**替换**系统规则
- 开启：项目规则与系统规则**并存**，适合"在系统规则基础上增量补充"

---

## 2. Glob 匹配语法

OCR 的 Glob 匹配由 [`bmatcuk/doublestar`](https://github.com/bmatcuk/doublestar) v4 实现。

### 2.1 语法速查表

| 通配符 | 含义 | 示例 | 匹配 | 不匹配 |
|--------|------|------|------|--------|
| `*` | 匹配除 `/` 外的任意字符 | `*.go` | `a.go` | `a/b.go` |
| `**` | 跨目录边界（含零层） | `**/*.go` | `a.go`、`a/b.go` | — |
| `?` | 匹配单个字符 | `a?c.go` | `abc.go` | `ac.go` |
| `[abc]` | 字符类，匹配其一 | `[abc].go` | `a.go` | `d.go` |
| `{a,b,c}` | 大括号扩展 | `*.{go,js}` | `a.go`、`b.js` | `a.ts` |

### 2.2 关键细节

- **大小写不敏感**：路径与模式在匹配前统一小写化，`*.GO` 与 `*.go` 等价
- **`*` 不跨越目录分隔符**：`*.go` 只匹配当前目录下的 Go 文件
- **`**` 跨越目录边界**：`**/*.go` 匹配任意层级的 Go 文件
- **大括号展开**：`**/*.{js,jsx,ts,tsx}` 等价于四个独立模式

---

## 3. 内置默认排除模式

OCR 内置一份默认排除清单（`default_exclude_patterns.json`），跳过测试文件、生成代码、构建产物等：

```json
[
  "**/*_test.go",
  "**/*.test.{js,jsx,ts,tsx}",
  "**/*.spec.{js,jsx,ts,tsx}",
  "**/__tests__/**",
  "**/*_test.py",
  "**/*_spec.rb",
  "**/*.test.ets",
  "**/*.spec.ets"
]
```

绕过方式：使用项目配置的 `include` 字段重新放行，而非修改内置清单。

---

## 4. 系统规则 system_rules.json

系统规则是优先级最低的兜底层，包含 **36 条 glob → 规则文件映射**，覆盖 **30+ 种语言/文件类型**。

### 4.1 default_rule 兜底

当没有任何 glob 匹配到目标文件时，使用 `default_rule` 指定的 `default.md`，保证任何文件都不会"无规则可循"。

### 4.2 配置文件的单独映射

OCR 为常见配置文件单独映射规则文件：

| 文件 | 规则文件 | 理由 |
|------|----------|------|
| `**/mapper_*.xml`（MyBatis） | `mapper_dao_xml.md` | SQL 注入风险审查 |
| `**/pom.xml` | `pom_xml.md` | Maven 依赖审查 |
| `**/build.gradle` | `build_gradle.md` | Gradle 依赖审查 |
| `**/package.json` | `package_json.md` | npm 依赖与脚本审查 |
| `**/Cargo.toml` | `cargo_toml.md` | Rust 依赖审查 |
| `**/composer.json` | `composer_json.md` | PHP 依赖审查 |

### 4.3 GitHub Workflows YAML 特殊处理

- `**/.github/workflows/*.yml` 与 `*.yaml` → `github_workflow_yaml.md`（审查 secrets 泄露、权限过大、注入风险）
- 其余 `.yml` / `.yaml` → `yaml.md`（通用 YAML 审查）

---

## 5. 文件过滤五门算法

文件是否进入审查，由 `whyExcluded` 函数决定，采用**五道关卡顺序检查**：

```
文件输入
  │
  ├─ 门 1: binary? ──是──→ 排除: binary
  │（否）
  ├─ 门 2: user_exclude? ──是──→ 排除: user_exclude
  │（否）
  ├─ 门 3: user_include? ──命中──→ 放行（绕过默认排除，仍受门 4 约束）
  │（未命中）
  ├─ 门 4: unsupported_ext? ──是──→ 排除: unsupported_ext
  │（否）
  └─ 门 5: default_path? ──是──→ 排除: default_path
       （否）
       ↓
   通过，进入审查
```

| 门 | 检查内容 | 命中结果 |
|----|----------|----------|
| 1 | 二进制文件 | 排除 |
| 2 | 命中 `exclude` | 排除（最高优先级） |
| 3 | 命中 `include` | 放行并跳过门 5 |
| 4 | 扩展名不在白名单 | 排除 |
| 5 | 命中默认排除模式 | 排除 |

`deleted`（文件被删除）状态不在五门之内，在更早阶段单独计算。

### 5.1 文件类型白名单

`supported_file_types.json` 列出受支持扩展名：

```
.go, .py, .java, .kt, .scala,
.js, .jsx, .ts, .tsx, .vue,
.c, .cpp, .h, .hpp, .rs,
.rb, .php, .swift, .cs,
.yml, .yaml, .json, .xml, .toml, .md
```

白名单比黑名单更安全——新增未知类型默认被排除。

---

## 6. 规则文件安全限制

规则文件来自外部（项目配置、用户目录），OCR 施加四项安全限制：

| 限制 | 值 | 防御目标 |
|------|----|----------|
| 扩展名白名单 | `.md` / `.txt` / `.markdown` | 防止加载可执行/二进制规则文件 |
| 大小上限 | 512 KB | 防止超大文件耗尽内存 |
| symlink 解析 | `EvalSymlinks` 后校验 | 防止符号链接指向仓库外 |
| 路径逃逸校验 | resolved 必须以 `repoDir + Separator` 为前缀 | 防止 `../` 逃逸 |

路径逃逸校验杜绝了 `../../etc/passwd` 逃逸、symlink 指向 `/etc/shadow`、`..%2f..%2f` 编码绕过等攻击。

---

## 7. 规则调试：ocr rules check

`ocr rules check` 输出指定文件命中了哪一层、哪个模式、哪个规则文件：

```bash
$ ocr rules check internal/handler/user_test.go
File:    internal/handler/user_test.go
Source:  default-exclude
Pattern: **/*_test.go
Rule:    (excluded)
```

```bash
$ ocr rules check src/main.go
File:    src/main.go
Source:  system
Pattern: **/*.go
Rule:    go.md
```

| 输出项 | 含义 |
|--------|------|
| File | 被检查的文件 |
| Source | 命中的规则来源层（`project` / `global` / `system` / `flag` / `default-exclude`） |
| Pattern | 命中的 glob 模式 |
| Rule | 使用的规则文件或 `(excluded)` |

---

## 8. 配置示例

### 8.1 项目级 rule.json 完整示例

```json
{
  "include": ["**/*_test.go"],
  "exclude": ["vendor/**", "**/generated/**", "**/*.pb.go"],
  "rules": [
    { "path": "**/proto/**/*.go", "rule": "go_proto.md" },
    { "path": "**/*.go", "rule": "go.md" },
    { "path": "**/*.py", "rule": "python_strict.md" }
  ],
  "merge_system_rule": true
}
```

规则文件放在 `.opencodereview/rules/` 目录下。

### 8.2 --exclude flag 临时排除

```bash
ocr review --from "HEAD~1" --to "HEAD" --exclude "docs/**,**/*.md"
```

`--exclude` 接受逗号分隔的 glob 模式，临时排除指定路径，不修改配置文件。
