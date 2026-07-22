---
id: "template-placeholder-granularity-design"
domain: "methodology"
layer: "methodology"
maturity: "L2"
validation_count: 2
reuse_count: 0
documentation_level: "standard"
source: "sc-20260722-docker-template 方法论编排复盘"

[bindings]
rules = []
references = ["../../templates/docker-snippets/skeleton/Dockerfile", "../../templates/docker-snippets/skeleton/CONFIG.md"]
skills = []
---

# 模板占位符的粒度设计原则

## 触发场景

- 设计可跨项目复用的模板（Dockerfile/配置文件/脚本），需要定义 `{{PLACEHOLDER}}` 变量体系
- 模板中存在"可选配置块"（某些项目需要，某些项目不需要）
- 模板中存在"需要语法感知的值"（如 Python 列表字面量、Shell 命令片段）
- 需要平衡模板的通用性和易用性

**识别信号**：
- 模板使用者反馈"某配置项在我的项目中不需要，但模板强制要求填写"
- 占位符名模糊（如 `{{EXTRA}}`），使用者不知道应该填什么
- 占位符值有语法要求（如必须加引号），但文档未说明

**不适用场景**：
- 一次性模板（不需要复用，直接硬编码即可）
- 所有配置项对所有使用者都必填的模板

## 问题背景

### 占位符设计的三个常见错误

| 错误 | 表现 | 后果 |
|------|------|------|
| **可选配置硬编码** | 时区强制设为 `Asia/Shanghai` | 非亚洲用户需要手动修改模板本身 |
| **语法感知值无说明** | `{{VERIFY_PIP_DEPS}}` 要求填 `'numpy','scipy'`（带引号） | 使用者填 `numpy,scipy` 导致 Python 语法错误 |
| **模糊占位符名** | 用 `{{EXTRA}}` 代替 `{{BUILTIN_VERIFY_EXTRA}}` | 使用者不知道这个占位符控制什么行为 |

**实际案例**：Docker 模板升级（2026-07-22），在 skeleton 模板中新增三个占位符：
- `{{TIMEZONE_SETUP}}`：将硬编码的时区设置改为可配置
- `{{VERIFY_PIP_DEPS}}`：将 pip 安装后的验证包名独立为占位符
- `{{BUILTIN_VERIFY_EXTRA}}`：将构建时的额外验证步骤独立为占位符

## 解决方案

### 原则：三类占位符，分别处理

**类型一：可空配置块**

```dockerfile
# 好：独立占位符，可留空
RUN set -eux; \
    apt-get install -y tzdata ...; \
    {{TIMEZONE_SETUP}} \
    rm -rf /var/lib/apt/lists/*
```

```markdown
<!-- CONFIG.md 中的说明 -->
| `{{TIMEZONE_SETUP}}` | 时区设置命令（可为空） |
`ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; echo "Asia/Shanghai" > /etc/timezone;`
```

**类型二：语法感知值**

```dockerfile
# 好：占位符名暗示语法要求，CONFIG.md 显式说明
python -c "from importlib.metadata import version; \
deps=[{{VERIFY_PIP_DEPS}}]; \
[print(f'  {d}: {version(d)}') for d in deps if True]"
```

```markdown
<!-- CONFIG.md 中的说明 -->
| `{{VERIFY_PIP_DEPS}}` | pip安装后验证的包名（逗号分隔，每个必须加引号） |
`'numpy','scipy','pandas'`
```

**类型三：可选代码片段**

```dockerfile
# 好：占位符名明确表达用途，在关键步骤之间插入
    python -c "import {{CORE_MODULE_COMMA_SEPARATED}}; ..."; \
    {{BUILTIN_VERIFY_EXTRA}} \
    chown -R ai:ai "$SITE_PKGS" ...
```

```markdown
<!-- CONFIG.md 中的说明 -->
| `{{BUILTIN_VERIFY_EXTRA}}` | 构建时额外验证步骤（可为空） |
见下方"功能验证示例"章节
```

### 占位符命名规范

| 特征 | 命名规范 | 示例 |
|------|---------|------|
| 可空 | 以 `_SETUP` 或 `_EXTRA` 结尾 | `TIMEZONE_SETUP`, `BUILTIN_VERIFY_EXTRA` |
| 语法感知 | 以 `_DEPS`/`_LIST`/`_PATTERN` 结尾 | `VERIFY_PIP_DEPS`, `WHEEL_NAME_PATTERN` |
| 必填核心 | 用明确的名词 | `BUILD_IMAGE_NAME`, `CONDA_ENV_NAME` |
| 路径类 | 以 `_PATH`/`_DIR` 结尾 | `WHEEL_RELATIVE_PATH`, `LIB_DIR` |

### 文档规范

每个占位符在 CONFIG.md 中必须包含：
1. **说明**：一句话描述用途
2. **示例值**：真实的项目示例
3. **可空说明**：如果可为空，明确标注"可为空"及留空后的行为

## 反模式

1. **把可选配置硬编码在模板中**——使用者需要修改模板而非配置，违背模板复用原则
2. **用模糊名称（`{{EXTRA}}`）代替具体名称（`{{BUILTIN_VERIFY_EXTRA}}`）**——名称即文档，模糊名称导致误用
3. **语法感知值不在文档中说明语法要求**——使用者填错值类型导致运行时错误
4. **新增占位符不同步更新 CONFIG.md**——文档与模板不一致，增加使用成本

## 迁移验证

| 场景 | 验证方式 |
|------|---------|
| Dockerfile 模板 | 三个新占位符已通过 XMNN 项目验证 |
| 配置文件模板（YAML/TOML/JSON） | 同样适用：可空段用独立占位符、语法感知值在文档标注 |
| 脚本模板 | 可空段用 `{{OPTIONAL_BLOCK}}`，必填段用具体名称 |

## 相关模式

- [file-creation-precheck-pattern](../methodology-patterns/governance-strategy/file-creation-precheck-pattern.md) — 文件创建前的预检查模式
- [immutable-constraint-documentation](../methodology-patterns/governance-strategy/immutable-constraint-documentation.md) — 不可变约束的文档化