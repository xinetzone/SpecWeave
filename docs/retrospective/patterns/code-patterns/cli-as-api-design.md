---
id: "cli-as-api-design"
source: "../../reports/competitive-analysis/retrospective-sunlogin-cli-wiki-20260706/insight-extraction.md#洞察1"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/cli-as-api-design.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "script-json-output-contract"
---
> **来源**：从向日葵企业CLI（awesun-cli）复盘萃取，经向日葵CLI产品验证

# CLI即API设计模式（CLI as API Design Pattern）

## 模式类型

代码模式（CLI工具接口设计）

## 成熟度

L1 首次萃取（向日葵CLI产品验证）

## 适用场景

设计命令行工具时，预期会被以下场景调用：
- Shell/Python脚本自动化编排
- CI/CD流水线集成
- AI Agent通过shell命令调用
- 无头环境（headless server）批量运维
- DevOps工具链集成

## 问题背景

传统CLI工具主要面向人类交互设计，存在以下问题：
1. **输出不可解析**：彩色表格、进度条、人类友好的提示信息混杂在stdout中，脚本无法可靠提取数据
2. **错误处理不一致**：错误信息混入stdout，退出码约定模糊，脚本无法判断成功/失败
3. **无会话持久化**：每次调用建立新连接，长时操作无法中断续接
4. **单格式输出**：只有人类可读格式，没有为程序消费设计结构化输出

script-json-output-contract模式解决了最基本的`--json`输出问题，但CLI即API模式是更完整的设计哲学——不仅是加个参数，而是从底层数据模型出发，让命令行工具天然同时服务人类和机器两类消费者。

## 核心规则

CLI即API设计的核心是：**人类可读格式只是结构化数据的一种渲染方式**，所有命令输出天然结构化，通过输出格式参数控制渲染为不同形态。

**核心公式**：
```
CLI即API = 多格式输出（table/json/yaml/wide）⊕ 结构化错误（错误码+JSON错误对象）⊕ 明确退出码约定 ⊕ 会话持久化机制
```

### 四大核心要素

| 要素 | 实现方式 | 解决的问题 |
|------|---------|-----------|
| 多格式输出 | `--output`/`-o`参数支持table/json/yaml/wide四种格式 | 人类用户获得友好表格，程序获得可解析JSON |
| 结构化错误 | 错误时输出JSON错误对象（含error_code、error_message），退出码明确区分错误类型 | 脚本/AI可程序化处理错误（重试/放弃/上报），不用解析自然语言错误字符串 |
| 退出码约定 | 0=成功，1-6（或更多）=不同错误类型，退出码语义稳定 | 上层调用者通过`$?`快速判断结果类别 |
| 会话持久化 | 连接建立后返回session_id，后续命令通过session_id操作，支持断开重连 | 长时操作（批量部署、大文件传输、渲染任务）可中断续接，类似HTTP session |

### 反模式（应避免）

- ❌ 仅面向人类的彩色表格输出，无JSON/YAML选项
- ❌ 错误信息混入stdout（应走stderr，JSON模式下stdout只有JSON）
- ❌ 没有明确的退出码约定（所有错误都exit 1）
- ❌ 输出格式随版本随意变更（字段重命名、层级调整破坏解析器）
- ❌ 连接信息无法持久化（每次调用都要重新建立连接）

## 与script-json-output-contract的关系

script-json-output-contract是本模式的子集，解决最基础的`--json`输出契约问题；CLI即API模式在此基础上增加了：
- 多格式支持（不仅是json，还有yaml/table/wide）
- 会话持久化机制
- 错误码体系设计
- 完整的"双消费者"设计哲学

两者是互补关系，script-json-output-contract适合简单脚本，CLI即API适合需要被AI Agent/自动化系统深度集成的命令行工具。

## 验证清单

- [ ] `--output json`输出可被`json.loads()`解析
- [ ] 错误场景退出码非0，且错误类型可通过退出码区分
- [ ] JSON模式下stdout只有JSON，人类可读日志走stderr
- [ ] 输出字段向后兼容（新增字段不破坏旧解析器）
- [ ] 会话ID机制支持断开重连
- [ ] 默认输出（无--output参数）为人类友好的table格式
