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

## 验证器（Validator）验证
- [x] Checkpoint 15: 缺少必填frontmatter字段时输出error级别报告，含错误码和修复建议
- [x] Checkpoint 16: 缺少必需章节时输出error并指出章节名称（关键词模糊匹配）
- [x] Checkpoint 17: 参数类型引用不存在时输出error
- [x] Checkpoint 18: 内部相对链接不存在时输出warn
- [x] Checkpoint 19: 合规SKILL.md验证结果0 error（14个SKILL.md验证平均97分）
- [ ] Checkpoint 20: CLI命令 `python -m mdi validate <path>` 可正常执行（待实现CLI入口）
- [ ] Checkpoint 21: Python API `validate()` 函数可调用并返回结构化结果（待暴露统一API）
- [x] Checkpoint 22: Windows路径和UTF-8编码正常工作（使用Path对象处理路径）

## 代码生成器（Code Generator）验证
- [x] Checkpoint 23: 生成的Python TypedDict代码通过compile()语法检查，无错误
- [x] Checkpoint 24: 生成的TypeScript interface/type语法结构有效
- [x] Checkpoint 25: OpenAPI 3.0导出包含info/paths/components基本结构
- [x] Checkpoint 26: MCP Tool导出包含name/description/inputSchema必需字段
- [x] Checkpoint 27: 生成的Python Click CLI骨架语法正确
- [x] Checkpoint 28: 生成的代码包含参数注释和文档字符串
- [ ] Checkpoint 29: CLI命令 `python -m mdi gen <path> --lang python` 可正常执行（待实现CLI入口）
- [ ] Checkpoint 30: 支持自定义输出目录参数（CLI层待实现）

## 测试生成器（Test Generator）验证
- [ ] Checkpoint 31: 生成的pytest文件可被pytest收集，无导入/语法错误（待实现）
- [ ] Checkpoint 32: 每个接口生成≥3个测试用例（正常路径、边界值、错误路径）（待实现）
- [ ] Checkpoint 33: Mock数据符合参数Schema定义（待实现）
- [ ] Checkpoint 34: 安全检查清单转换为前置/后置断言步骤（待实现）

## 版本控制工具验证
- [ ] Checkpoint 35: diff工具能识别接口/参数/响应的新增、删除、修改（待实现）
- [ ] Checkpoint 36: 变更影响分析列出受影响的下游代码/测试产物（待实现）

## 案例验证
- [x] Checkpoint 37a: 案例1（AI Skill）：14个SKILL.md解析成功，验证0 error，平均97分
- [ ] Checkpoint 37b: 案例1（AI Skill）：生成TS类型文件（待生成）
- [ ] Checkpoint 38: 案例2（Web API）：user-api.md验证0 error，OpenAPI JSON结构有效，pytest可收集（待实现examples/和案例执行）
- [ ] Checkpoint 39: 案例3（CLI Tool）：file-cli.md生成Python Click骨架语法正确（待实现examples/和案例执行）
- [ ] Checkpoint 40: 三个案例均有完整的执行记录文档（步骤、预期、实际、问题记录）（待完成）

## 研究报告与质量验证
- [ ] Checkpoint 41: 研究报告包含可行性分析、架构设计、优劣势对比、场景矩阵、版本控制、生态分析6章（待撰写）
- [ ] Checkpoint 42: 研究报告≥5000字，包含≥5张Mermaid图表（待撰写）
- [ ] Checkpoint 43: 优劣势对比客观中立，明确标注不适用场景（待撰写）
- [ ] Checkpoint 44: 使用指南包含可复现的快速开始步骤（待撰写）
- [ ] Checkpoint 45: 核心模块（parser/validator/generator）单元测试覆盖率≥85%（待测量，目前108个测试用例）
- [x] Checkpoint 46: 全量单元测试通过，无回归失败（108个测试全部通过）
- [ ] Checkpoint 47: 所有内部文档链接有效（运行link-check验证）
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
