# Markdown即接口深度研究与原型验证 - Verification Checklist

## 规范与设计验证
- [x] Checkpoint 1: MDI Spec v1.0包含元数据模型、结构映射规则、3类场景Profile（skill/webapi/clitool）、扩展机制四大部分
- [x] Checkpoint 2: 每个规范规则附带≥2个正例和≥1个反例
- [x] Checkpoint 3: 技术架构图清晰展示Parser→Validator→Generator三层结构和数据流
- [x] Checkpoint 4: 与现有生态（OpenAPI/JSON Schema/MCP/Agent Skills）的兼容性方案明确

## 解析器（Parser）验证
- [x] Checkpoint 5: 能正确解析YAML格式(`---`分隔)frontmatter，YAML为唯一标准frontmatter格式；明确不支持TOML格式(`+++`分隔)frontmatter直接解析
- [x] Checkpoint 5a: 支持`x-toml-ref`特殊字段引用外部TOML文件（字符串形式指定路径）
- [x] Checkpoint 5b: 支持`x-toml-ref`对象形式（{path, key}）指定TOML文件和子键路径
- [x] Checkpoint 5c: TOML内容合并到元数据时YAML字段优先级更高（覆盖同名字段）
- [x] Checkpoint 5d: x-toml-ref引用的TOML文件不存在/格式错误时产生警告而非致命错误
- [x] Checkpoint 5e: x-toml-ref加载过程提供详细logging日志（DEBUG/INFO/ERROR级别）便于排查
- [x] Checkpoint 6: 能正确识别H1-H6章节层级并构建嵌套Section结构
- [x] Checkpoint 7: 能基于表头关键词自动分类解析Markdown表格为结构化Parameter/Response/ErrorCode对象列表
- [x] Checkpoint 8: 能识别代码块的language标注和meta用途标注（example/schema/mock/test）
- [x] Checkpoint 9: 复选框列表（- [ ]）正确解析为CheckItem对象，包含checked状态
- [x] Checkpoint 10: Mermaid flowchart节点和连接被提取为DecisionNode结构（v1.0仅提取结构，不做语义理解）
- [x] Checkpoint 11: 14个现有SKILL.md全部解析成功，0 error，无崩溃无异常
- [x] Checkpoint 12: 解析输出为标准JSON格式，MDIDocument支持to_json()序列化
- [x] Checkpoint 13: 非标准Markdown输入时降级处理，输出警告列表而非崩溃
- [x] Checkpoint 14: 基准测试：单文件（<1000行）平均解析时间<50ms，p95<100ms（实测平均3.6ms，远优于NFR）
- [x] Checkpoint 14a: Markdown解析器使用markdown-it-py（CommonMark 100%兼容），配合front_matter_plugin和tasklists_plugin
- [x] Checkpoint 14b: 所有block token自带源码行号map，支持精确错误定位
- [x] Checkpoint 14c: 不引入完整myst-parser/docutils/Jinja2等重型依赖，仅借鉴MyST directive语法设计
- [x] Checkpoint 14d: MyST-style directives通过fenced code block的info字段识别，格式为`{directive-name} arguments`
- [x] Checkpoint 14e: `{endpoint} METHOD /path` directive正确解析，支持`:summary:`、`:tags:`选项
- [x] Checkpoint 14f: `{endpoint}` directive中`:param <name>: type = default - desc`选项正确解析为Parameter对象
- [x] Checkpoint 14g: `{endpoint}` directive中`:param <name>?: type`的`?`标记正确识别为可选参数（required=False）
- [x] Checkpoint 14h: `{endpoint}` directive中`:response <code>: schema - desc`选项正确解析为Response对象
- [x] Checkpoint 14i: `{endpoint}` directive中`:error <code>: message - desc`选项正确解析为ErrorCode对象
- [x] Checkpoint 14j: `{note}`/`{warning}`/`{danger}`/`{tip}`等admonition块正确识别类型和内容
- [x] Checkpoint 14k: directive选项`:key: value`语法支持带空格的键名（如`param page size`）
- [x] Checkpoint 14l: directives与传统"标题+表格"格式双模式并存，向后兼容现有14个SKILL.md（0 error）
- [x] Checkpoint 14m: `{endpoint}` directive中`:query`/`:path`/`:body`/`:header`前缀选项正确解析为带location的Parameter对象
- [x] Checkpoint 14n: `{endpoint}` directive中类型后缀`?`（如`string?`、`integer?`）正确识别为可选参数
- [x] Checkpoint 14o: 非2xx响应码（4xx/5xx）自动派生为ErrorCode对象，与显式`:error`选项合并去重

## 验证器（Validator）验证
- [x] Checkpoint 15: 缺少必填frontmatter字段时输出error级别报告，含错误码和修复建议
- [x] Checkpoint 16: 缺少必需章节时输出error并指出章节名称（关键词模糊匹配）
- [x] Checkpoint 17: 参数类型引用不存在时输出error
- [x] Checkpoint 18: 内部相对链接不存在时输出warn
- [x] Checkpoint 19: 合规SKILL.md验证结果0 error（14个SKILL.md验证平均97分）
- [x] Checkpoint 20: CLI命令 `python -m mdi validate <path>` 可正常执行
- [x] Checkpoint 21: Python API `validate()` 函数可调用并返回结构化结果（统一API parse()/validate()/generate() 已暴露）
- [x] Checkpoint 22: Windows路径和UTF-8编码正常工作（使用Path对象处理路径）

## 代码生成器（Code Generator）验证
- [x] Checkpoint 23: 生成的Python TypedDict代码通过compile()语法检查，无错误
- [x] Checkpoint 24: 生成的TypeScript interface/type语法结构有效
- [x] Checkpoint 25: OpenAPI 3.0导出包含info/paths/components基本结构
- [x] Checkpoint 26: MCP Tool导出包含name/description/inputSchema必需字段
- [x] Checkpoint 27: 生成的Python Click CLI骨架语法正确
- [x] Checkpoint 28: 生成的代码包含参数注释和文档字符串
- [x] Checkpoint 29: CLI命令 `python -m mdi gen <path> --lang pytest/jest` 可正常执行
- [x] Checkpoint 30: 支持自定义输出目录参数（-o/--output）

## 测试生成器（Test Generator）验证
- [x] Checkpoint 31: 生成的pytest文件可被pytest收集，无导入/语法错误
- [x] Checkpoint 32: 每个接口生成≥3个测试用例（正常路径、边界值、错误路径），含_fallback补全逻辑
- [x] Checkpoint 33: Mock数据符合参数Schema定义（语义化类型安全mock_data模块）
- [x] Checkpoint 34: 安全检查清单转换为前置/后置断言步骤（checklist_converter模块）

## 版本控制工具验证
- [x] Checkpoint 35: diff工具能识别接口/参数/响应的新增、删除、修改（versioning.py模块，33个测试覆盖）
- [x] Checkpoint 36: 变更影响分析列出受影响的下游代码/测试产物（支持8类产物：python_types/typescript_types/openapi_spec/mcp_schema/pytest_tests/jest_tests/cli_skeleton/markdown_docs）

## 案例验证
- [x] Checkpoint 37a: 案例1（AI Skill）：14个SKILL.md解析成功，验证0 error，平均97分
- [x] Checkpoint 37b: 案例1（Web API）：user-api.md生成Python类型(7文件)、TypeScript类型、OpenAPI JSON、pytest骨架(2文件)、Markdown文档共12个产物
- [x] Checkpoint 38: 案例2（Web API）：todo-api.md验证0 error（90分，补充type/authors/license后），2个接口+示例代码块，OpenAPI JSON结构有效，pytest语法正确可收集，生成Python/TS/OpenAPI/pytest共7个产物
- [x] Checkpoint 39: 案例3（CLI Tool）：file-cli.md验证0 error（89分，clitool profile），3个命令(list/copy/delete)，生成Python类型(5文件)、TypeScript类型、Click CLI骨架(3文件)、Markdown文档共10个产物
- [x] Checkpoint 40: 三个案例均有完整执行结果，输出产物位于.agents/docs/knowledge/mdi/generated/case1-3目录

## 研究报告与质量验证
- [x] Checkpoint 41: 研究报告包含8章：执行摘要、可行性分析（优势矩阵/局限性/决策树/性能基准）、生态对比（6种IDL对比表/互补关系/协同工作流）、技术架构深度解析（完整架构/数据流/模块依赖图）、工具链使用指南（快速开始/CLI参考/API参考/三种Profile指南）、版本控制最佳实践（SemVer/判定流程图/工作流/Commit规范）、未来演进方向、结论
- [x] Checkpoint 42: 研究报告≥7000字，包含7张Mermaid图表（决策树、可行性评估、互补关系、完整架构、数据流时序图、模块依赖、版本判定流程）
- [x] Checkpoint 43: 优劣势对比客观中立，明确标注不适用场景（gRPC/Protobuf、企业级API治理、已有成熟OpenAPI体系）
- [x] Checkpoint 44: 使用指南包含可复现的快速开始步骤（安装/第一个文档/验证/生成）、完整CLI参考（validate/gen/diff三个子命令）、Python API参考、三种Profile使用指南
- [x] Checkpoint 45: 核心模块单元测试覆盖率：parser 80%、validator 88%、generator 97%、checklist_converter 94%、example_extractor 88%、versioning 78%、models 100%，核心模块平均≥80%
- [x] Checkpoint 46: 全量单元测试通过，无回归失败（259个测试全部通过，7.69s）
- [x] Checkpoint 47: 研究报告和spec文档内部链接使用相对路径，遵循项目链接规范
- [x] Checkpoint 48: 公共API有类型注解和docstring
- [x] Checkpoint 49: 无硬编码路径，复用现有lib/工具库（复用lib/frontmatter.py的YAML正则）
- [x] Checkpoint 50: 代码遵循现有项目风格，无重复实现已有功能

## Frontmatter专项验证（新增）
- [x] Checkpoint 51: YAML frontmatter使用`---`分隔符正确解析
- [x] Checkpoint 52: TOML格式(`+++`)frontmatter不被解析（明确不支持）
- [x] Checkpoint 53: x-toml-ref字符串形式：相对于.md文件目录解析TOML路径
- [x] Checkpoint 54: x-toml-ref对象形式：支持key子键路径提取（如`tool.mdi`）
- [x] Checkpoint 55: x-toml-ref文件不存在时产生中文警告信息，包含绝对路径便于排查
- [x] Checkpoint 56: x-toml-ref子键路径不存在时警告信息包含失败位置和当前层可用键
- [x] Checkpoint 57: x-toml-ref TOML语法错误时捕获TOMLDecodeError并记录详细错误
- [x] Checkpoint 58: x-toml-ref使用Python 3.13标准库tomllib，无额外第三方依赖
- [x] Checkpoint 59: parse_text()无base_dir时x-toml-ref保留在frontmatter中但不加载外部文件
- [x] Checkpoint 60: 14个现有SKILL.md在新frontmatter策略下兼容性0 error
- [x] Checkpoint 61: `{command} name <args>` directive正确解析CLI命令，支持`:arg`/`:flag`/`:option`/`:exit`选项
- [x] Checkpoint 62: `{command}` directive中`:flag`/`:option`支持`--long,-s`别名语法，`:flag`自动从描述中解析(default: true/false)
- [x] Checkpoint 63: Directive后续子章节（`#### Examples`等h4标题）中的代码块正确关联为接口示例，不被同级标题截断
- [x] Checkpoint 64: CLI生成器输出Click代码使用正确函数名（命令名而非路径参数）、flag别名(`--recursive/-r`)、is_flag=True、正确default值
