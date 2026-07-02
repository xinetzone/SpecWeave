---
id: "insight-temp-file-discipline-20260701"
source: "defuddle-web-content-extraction"
x-toml-ref: "../../../.meta/toml/docs/retrospective/insights/insight-temp-file-discipline-20260701.toml"
---
# 临时文件路径规范执行卡点洞察

## 1. 事实数据采集

**事件经过**：
- 任务：使用 defuddle 提取两个网页内容进行分析
- 错误操作：执行 `defuddle parse <url> --md -o article1.md` 时，将输出文件直接写到项目根目录
- 正确做法：应该输出到 `.temp/article1.md`
- 发现与纠正：用户指出问题后，立即将文件移动到 `.temp/` 目录，并清理根目录

**违反的规范**：
- [.agents/protocols/dependency-management.md](../../../.agents/protocols/dependency-management.md#L16) 明确规定任务中间产物存放在 `.temp/`
- 项目根目录不应随意创建临时散文件

## 2. 根因分析

### 直接原因
执行命令行输出操作时，未在写入前检查路径合规性，专注于任务内容（网页分析）而忽略了文件存放位置这个"细节"。

### 深层原因（5 Whys）
1. **为什么放错了？** → 因为 `-o` 参数直接写了文件名没带路径前缀
2. **为什么没加路径前缀？** → 因为写命令时没停下来想"这个文件应该放哪"
3. **为什么没想？** → 因为没有把"路径合规性检查"作为文件写入操作的强制前置步骤
4. **为什么没有强制步骤？** → 虽然读过 dependency-management.md，但规范知识没有转化为操作卡点
5. **为什么知识没转化为卡点？** → 缺乏"高风险触发点"意识——命令行 `-o/--output/>` 是容易出错的地方，但没有建立停顿检查机制

**核心根因**：**知道规范 ≠ 执行规范**。阅读过规范文件只是建立了认知，但没有在具体操作点设置强制检查流程，导致执行时"凭直觉"而非"按规范"。

## 3. 关键洞察

### 洞察1：流程卡点比记忆更可靠
依赖"记住"规范是不可靠的，人（和 AI）在专注任务内容时会忽略路径这类"上下文细节"。必须在高风险操作点设置**强制检查卡点**，就像编译器强制类型检查、高铁发车前强制安全检查一样——不靠自觉，靠流程。

### 洞察2：识别高风险触发点
不是所有操作都需要同等强度的检查。以下操作是临时文件乱放的高风险触发点，遇到时**必须停顿检查**：
- 命令行工具的 `-o`/`--output` 参数
- Shell 重定向 `>` / `>>`
- PowerShell 的 `Out-File` / `Set-Content`
- Write 工具创建新文件（非编辑已有文件）
- defuddle/curl/wget 等下载/抓取工具保存文件

### 洞察3：三层防错闭环
单一防线不够，需要三层：
1. **事前**：操作前强制三问自检（流程卡点）
2. **事中**：高风险触发点自动触发警觉（记忆提醒）
3. **事后**：任务结束前工具检查兜底（自动化验证）

### 洞察4：错误即资产
犯错误不是坏事，但同样的错误犯第二次就是坏事。每一次错误都应该：
- 分析根因而不是只纠正表面
- 将教训转化为可执行的检查清单
- 写入项目记忆供后续会话参考
- 更新相关模式/规范文档

## 4. 可行动建议

| 建议 | 优先级 | 验收标准 |
|---|---|---|
| 所有智能体启动 quick memory pass 时必须读取 project_memory.md | 🔴 高 | project_memory.md 在内存快速扫描路径中 |
| 文件写入前强制执行"三问检查" | 🔴 高 | 无临时散文件出现在根目录 |
| 更新 file-creation-precheck-pattern 增加临时文件路径检查 | 🟡 中 | 模式文档包含 .temp/ 路径判断 |
| 任务结束前运行 repo-check.py gitignore 做兜底 | 🟡 中 | 每次任务交付前验证无违规文件 |

## 5. 关联资源

- 项目记忆：[project_memory.md](file:///c:/Users/admin/.trae-cn/memory/projects/-c-Users-admin-Desktop-Dao-flows-SpecWeave/project_memory.md)
- 临时依赖管理规范：[dependency-management.md](../../../.agents/protocols/dependency-management.md)
- 文件创建前置检查模式：[file-creation-precheck-pattern.md](../patterns/methodology-patterns/governance-strategy/file-creation-precheck-pattern.md)
