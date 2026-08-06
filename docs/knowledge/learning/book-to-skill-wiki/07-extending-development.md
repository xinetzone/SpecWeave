# 扩展开发

本章介绍如何扩展 book-to-skill 的功能，包括新增格式支持、修改生成行为、使用开发工具，以及理解优雅降级的设计原则。

## 7.1 新增格式支持

book-to-skill 的解析器采用模块化设计，每个格式对应一个独立的解析器模块。新增格式支持遵循四步标准化流程，参考 [ARCHITECTURE.md:99-103](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L99-L103)。

### 步骤 1：创建解析器模块

在 `book_to_skill/parsers/` 目录下创建 `<fmt>.py` 模块。解析器必须遵循统一的返回约定：

- **成功**：返回 `(text: str, parser_name: str)` 元组
- **失败**：返回 `None`（表示尝试下一个 fallback 解析器）或抛出异常

参考现有解析器的实现：
- [parsers/pdf.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/pdf.py)
- [parsers/epub.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/epub.py)
- [parsers/docx.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/docx.py)

**解析器设计原则**：
1. 优先使用第三方库获得最佳提取质量
2. 必须提供 stdlib fallback 以保证零依赖可用性
3. 提取的文本应通过 `sanitize.py` 进行 Unicode 清理
4. 异常应向上传播或返回 `None` 触发 fallback 链

### 步骤 2：注册扩展名

在 [config.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py) 中注册新格式的文件扩展名：

```python
# 在 config.py 中添加格式集合
NEW_FORMAT_EXTENSIONS = {".ext1", ".ext2"}

# 将扩展名加入 SUPPORTED_EXTENSIONS
SUPPORTED_EXTENSIONS = {
    ".pdf", ".epub", ".docx", ".rtf",
    *TEXT_EXTENSIONS,
    *HTML_EXTENSIONS,
    *CALIBRE_EBOOK_EXTENSIONS,
    *NEW_FORMAT_EXTENSIONS,  # 新增
}

# 如有 Python 依赖，添加到 PYTHON_DEPENDENCIES
PYTHON_DEPENDENCIES = {
    # ... 现有依赖
    "new_lib": "new-pip-package",
}
```

参考：[config.py:16-34](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/config.py#L16-L34)

### 步骤 3：添加依赖探测

在 [dependencies.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py) 的 `DEPENDENCY_GROUPS` 列表中添加新格式的依赖探测配置：

```python
DEPENDENCY_GROUPS = [
    # ... 现有格式组
    {
        "label": "New Format Name",
        "modules": ["new_lib"],           # Python 模块名列表
        "any_of_modules": True,           # 是否任一模块即可
        "any_tool_suffices": False,       # 是否任一工具（module+system）即可
        "system": [                       # 系统命令依赖
            ("cmd-name", "Pretty Name", "install hint"),
        ],
        "note": "falls back to a stdlib parser if missing",  # 用户提示
    },
]
```

同时需要在 `prepare_dependencies()` 函数中添加对应的依赖安装提示逻辑，参考 [dependencies.py:166-213](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L166-L213)。

### 步骤 4：集成到提取流程

在 [utils.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py) 的 `extract_single_file()` 函数中添加新格式的分支逻辑：

1. 在文件顶部导入解析器函数
2. 在 `extract_single_file()` 中添加格式判断分支
3. 按照「最佳工具优先 → fallback 链」的顺序尝试解析器
4. 处理失败情况并给出明确的错误提示

参考现有 PDF 格式的 fallback 链实现：[utils.py:484-530](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L484-L530)

## 7.2 修改生成行为

生成行为由 [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md) 定义，这是 agent 遵循的规范文档。修改生成行为需遵循以下原则：

### 核心原则

1. **保持精简（lean）**：SKILL.md 是每次运行都会加载的核心文档，避免不必要的膨胀
2. **证据支持变更**：根据 [CONTRIBUTING.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/CONTRIBUTING.md)，所有修改必须有可测量的证据支持
3. **优先修改现有步骤**：优先编辑现有 Step 而非新增 Step
4. **网络新增内容**：净新增内容必须有充分理由，并用 benchmark 数据证明收益

### 证据类型

修改 SKILL.md 前需要提供以下类型之一的证据：

- **测试结果**：新增或更新的测试用例证明行为正确
- **Benchmark 数据**：使用 `tools/discovery_tax.py` 测量的 token 成本变化
- **Before/After 对比**：在真实书籍上运行的效果对比
- **问题复现**：清晰的 bug 复现场景和修复验证

参考：[CONTRIBUTING.md:9-14](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/CONTRIBUTING.md#L9-L14)

### 修改流程

1. 确定需要修改的具体 Step 编号
2. 在本地修改 SKILL.md
3. 使用 `tools/validate_skill.py` 验证格式
4. 在真实书籍上测试效果
5. 运行完整测试套件（ruff + pytest）
6. 提交 PR 并附上证据

## 7.3 工具脚本详解

book-to-skill 提供了一系列开发和验证工具，位于 `tools/` 和 `scripts/` 目录下。

### 7.3.1 tools/discovery_tax.py — Discovery Loop Tax 测量

**功能**：量化三种策略在回答定向问题时的 token 成本：
1. **context-dump**：整本书常驻上下文，每轮重复计费
2. **discovery-loop**：实时 PDF 阅读 agent 导航（读 ToC → 拉取章节 → 回溯缺失定义）
3. **book-to-skill**：小型常驻 SKILL.md 核心 + 按需加载的预编译章节

**核心功能**：
- 使用真实提取的书籍进行测量
- 支持 tiktoken（cl100k_base）精确计数，或 `words/0.75` 启发式估算
- 报告 best case（ToC + 目标章节）和 loop case（+ 前置章节查定义）
- 复用提取器的章节检测逻辑，保证计数一致性

**用法**：
```bash
python3 tools/discovery_tax.py --full-text <full_text.txt> \
    [--skill-dir <skill_folder>] [--target-chapter N] [--core-tokens 4000]
```

参考：[tools/discovery_tax.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/discovery_tax.py)

### 7.3.2 tools/validate_skill.py — SKILL.md 宿主规则校验

**功能**：检查生成的 SKILL.md 是否符合目标宿主（host）的规则。

**支持的 lens（宿主）**：
- `claude`：Claude Code 规则（默认）
- `copilot`：GitHub Copilot CLI 规则
- `amp`：Sourcegraph Amp 规则

**校验内容**：
- YAML frontmatter 有效性
- `name` 字段：必填、≤64字符、小写字母/数字/连字符
- `description` 字段：必填、≤1024字符
- `allowed-tools`：识别宿主内置工具，检测缺失的 Bash 权限
- 未识别的 frontmatter key（警告）
- 正文行数 >500 行（软警告）

**严重级别**：
- **ERROR**：会破坏/降低技能在该宿主上的功能（CI 失败）
- **WARN**：宿主忽略或为软指南（不中断 CI）

**用法**：
```bash
python3 tools/validate_skill.py [--lens claude|copilot|amp] [path/to/SKILL.md]
```

参考：[tools/validate_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/validate_skill.py)

### 7.3.3 tools/scan_generated_skill.py — 提示注入扫描（Step 9.5）

**功能**：对生成的 Skill 进行提示注入和权限越权的安全扫描，这是生成流程中的 Step 9.5。

**扫描范围**：
- `SKILL.md`（主文件）
- `chapters/*.md`（章节文件）
- `glossary.md`、`patterns.md`、`cheatsheet.md`（辅助文件）

**检测规则**：

| 规则 ID | 检测内容 |
|---------|---------|
| `unicode.invisible` | 不可见 Unicode 码点（零宽字符、标签块等） |
| `prompt.ignore_previous` | "ignore previous instructions" 类指令覆盖短语 |
| `prompt.disregard_system` | "disregard the system" 类系统指令覆盖 |
| `prompt.role_reassignment` | "you are now" 角色重分配短语 |
| `prompt.fake_system_prefix` | 伪造的 system/developer 消息前缀 |
| `prompt.system_tag` | `<system>` 标签 |
| `prompt.chat_template_tag` | 模型聊天模板分隔符（`<|im_start|>`、`[INST]`） |
| `prompt.tool_call_tag` | tool-call 控制 token |
| `tool.exfiltration_shape` | 数据渗出形态（curl/wget/send + 敏感词） |
| `frontmatter.allowed_tools` | frontmatter 声明或扩大工具权限 |
| `frontmatter.model_invocation_enabled` | 显式启用模型调用 |

**安全特性**：
- 结果只报告规则 ID 和文件位置，**永远不报告匹配的文本**
- 扫描为建议性质（advisory），规则 intentionally broad 可能误报合法内容
- 不修改任何文件

**用法**：
```bash
python3 tools/scan_generated_skill.py <generated-skill-dir-or-SKILL.md>
```

参考：[tools/scan_generated_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/scan_generated_skill.py)

### 7.3.4 scripts/extract.py — 薄入口垫片

**功能**：向后兼容的入口点包装器，将调用转发到 `book_to_skill.cli`。

**设计目的**：
- 保持旧调用方式继续工作
- 处理 Windows 控制台 UTF-8 编码问题（✓/✗ 等符号）
- 确保项目根目录在 `sys.path` 中，保证模块化包可靠导入

**代码结构**：
```python
from book_to_skill.cli import main

if __name__ == "__main__":
    main()
```

参考：[scripts/extract.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/scripts/extract.py)

## 7.4 优雅降级设计原则

优雅降级（Graceful degradation）是 book-to-skill 的核心设计原则之一，参考 [ARCHITECTURE.md:57-58](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/docs/ARCHITECTURE.md#L57-L58)。

### 核心原则

**每个格式都有 stdlib fallback**：
- PDF：pdftotext → pypdf → pdfminer（多级 fallback）
- EPUB：ebooklib + bs4 → stdlib zipfile 解析器
- DOCX：python-docx → stdlib ZIP/XML 解析器
- HTML：beautifulsoup4 → stdlib html.parser
- RTF：striprtf → 基础正则清理 fallback
- **例外**：MOBI/AZW/AZW3 必须依赖 Calibre（无 stdlib fallback）

**一个坏源被跳过而非致命错误**：
- 在多源提取时，单个文件失败不会导致整个流程崩溃
- 失败的源被记录到 warnings 列表，继续处理其他文件
- 只有当所有源都失败时才返回错误退出码

参考：[utils.py:642-659](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L642-L659)

### 降级策略示例

以 PDF 提取为例，fallback 链的设计：

1. **Technical 模式**：优先使用 Docling（布局感知，支持表格/代码/公式）
2. **Text 模式**：
   - 第一选择：pdftotext（poppler-utils，系统工具，质量最佳）
   - 第二选择：pypdf（纯 Python）
   - 第三选择：pdfminer.six（纯 Python）
3. **所有失败**：抛出 `ExtractionError`，给出安装提示

每一级 fallback 失败时都会打印明确的状态信息，用户可以清楚地知道使用了哪个提取器。

参考：[utils.py:484-526](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/utils.py#L484-L526)

### 依赖检查与提示

`--check` 命令提供完整的依赖状态报告：
- 哪些可选依赖已安装（✓）
- 哪些缺失（✗）
- 每个格式的满意度状态（ready / fallback available / MISSING）
- 精确的安装命令

参考：[dependencies.py:216-289](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L216-L289)

---

**事实来源**：本章节基于以下事实编号 F-039, F-040, F-041
