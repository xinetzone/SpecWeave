---
id: "edge-case-adaptation-interface"
title: "特殊场景适配策略与模块接口规范"
source: "trae-edge-case-handler.md#03-adaptation-interface"
x-toml-ref: "../../../.meta/toml/.agents/teams/trae-edge-case-handler/03-adaptation-interface.toml"
---
# 特殊场景适配策略与模块接口规范

## 特殊场景适配策略

针对已知的典型边界场景，提供预定义适配策略，避免每次遇到时重新探索。策略按优先级递减排列，前一优先级不可用时回退至下一级。

### 沙箱限制适配

**触发场景**：智能体在 Trae IDE 沙箱中无法访问用户目录或安装依赖。

| 优先级 | 适配方案 | 适用条件 | 注意事项 |
|---|---|---|---|
| 1 | 优先使用 Trae 集成浏览器 | 操作目标为浏览器自动化且集成浏览器已登录 | 集成浏览器不受沙箱文件系统限制 |
| 2 | 使用 `dangerouslyDisableSandbox` 绕过 | 操作必须在沙箱外执行（如安装依赖、访问用户目录） | 须用户显式确认；遵循 AGENTS.md 中 sandbox 禁用规则，识别具体受限资源 |
| 3 | 回退到手动操作指引 | 前两优先级均不可用 | 输出详细的手动操作步骤与预期结果 |

### PowerShell 编码适配

**触发场景**：智能体在 Windows PowerShell 环境下执行命令遇到编码或引号问题。

| 优先级 | 适配方案 | 适用条件 | 注意事项 |
|---|---|---|---|
| 1 | 多行文本使用 `-F` 文件参数而非 `-m` 内联参数 | 命令需传入多行或含特殊字符的文本 | 避免引号转义地狱；临时文件须清理 |
| 2 | 中文输出乱码不影响实际内容时忽略 | 乱码仅出现在日志/输出，不影响命令执行结果 | 须验证实际写入内容正确（如文件内容校验） |
| 3 | 编码冲突时显式设置 `chcp 65001` | 命令输出含乱码且影响结果判断 | 在命令前缀 `chcp 65001 >nul &&` 切换至 UTF-8 |

### 论坛登录状态过期适配

**触发场景**：智能体检测到论坛登录状态过期（Cookie 失效）。

| 步骤 | 操作 | 说明 |
|---|---|---|
| 1 | 多信号确认过期 | 使用 [multi-signal-detection](../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)，至少 2 个信号命中（URL 跳转、登录表单、API 401） |
| 2 | 提示用户重新执行 login 命令 | 输出明确的重新登录指令与命令 |
| 3 | 重新登录后恢复操作 | 恢复前须验证登录态（多信号检测） |
| 4 | 记录过期频率用于优化 | 统计单次任务内过期次数，≥ 3 次须提请优化登录持久化策略 |

### DOM 结构变化适配

**触发场景**：智能体检测到论坛 DOM 结构变化导致选择器失效。

| 优先级 | 适配方案 | 适用条件 | 注意事项 |
|---|---|---|---|
| 1 | 优先使用语义定位 | 目标元素有稳定的文本/role/label | 如 `getByRole`、`getByText`、`getByLabel` |
| 2 | 使用多选择器备选链 | 已预定义 ≥ 2 个备选选择器 | 按可靠性顺序尝试，遵循 [multi-signal-detection](../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md) 排序原则 |
| 3 | 使用 JavaScript DOM 查询兜底 | 选择器全部失效但页面结构可编程访问 | 通过 `page.evaluate` 执行 JS 查询 |
| 4 | 记录新 DOM 结构用于更新选择器常量 | 适配成功后 | 输出新结构特征，提请更新选择器常量配置 |


## 模块接口规范

### 与团队管理模块的接口

trae-edge-case-handler 与团队管理模块（team-admin、permission-system、admin-verification 等）协作时，遵循以下接口规范。

| 接口类型 | 方向 | 规范 |
|---|---|---|
| 输入接口 | orchestrator → 本模块 | 接收 orchestrator 提交的边界情况报告，含场景类别、检测信号、上下文 |
| 输出接口 | 本模块 → 调用方 | 返回处理决策（继续 continue / 降级 degrade / 退出 exit）与诊断信息 JSON |
| 日志接口 | 本模块 → 日志系统 | 所有边界判断结果写入结构化日志，遵循 SG-LOG 格式（见 [.agents/rules/stage-guardrails.md](../../rules/stage-guardrails.md)） |
| 验证接口 | 本模块 → admin-verification | 边界处理若涉及特权操作（如禁用沙箱、大规模回退），须遵循 [admin-verification.md](.././admin-verification.md) 的 V2/V3 验证分级 |

**输出决策 JSON 示例**：

```yaml
decision:
  boundary_type: "trae-forum-login-expired"
  level: "warning"
  action: "degrade"
  rationale: "Cookie 失效，多信号确认过期，执行重新登录降级"
  signals_hit:
    - "url_redirect_to_login"
    - "api_401"
  fallback_used: "relogin"
  recovered: true
  diagnostic_log: ".agents/logs/boundary-20260629T100000Z.log"
```

### 与脚本模块的接口

`.agents/scripts/` 下的脚本调用边界处理规范时，遵循以下接口约定。

| 约定 | 规范 |
|---|---|
| 调用位置 | 脚本须在核心分支（写操作、外部调用、状态变更前）调用边界检查函数 |
| 检查函数语义 | 边界检查函数遵循 [check-and-restore](../../docs/retrospective/patterns/code-patterns/check-and-restore.md) 模式——检查不改变状态，必要时保存-检测-恢复 |
| 结果传递 | 边界处理结果通过返回值传递，不通过副作用（全局变量、文件写入） |
| 日志输出 | 边界检查结果写入结构化日志，与脚本主日志分离（遵循双通道分层日志） |
| 退出码 | 致命级边界导致脚本退出时，退出码非零（建议 130） |

**脚本调用示例**：

```python
def post_reply(topic_id, content):
    # 核心分支前调用边界检查
    status = check_boundary("trae-forum-login")
    if status.level == "fatal":
        log_boundary(status)
        sys.exit(130)
    if status.level == "warning":
        recover_login()  # 降级操作
        if not verify_recovered():
            sys.exit(130)

    # 边界检查通过后执行主操作
    return do_post_reply(topic_id, content)
```


---

## 相关模式

- - [forum-posting Skill](../../skills/forum-posting/SKILL.md)
- - [trae_edge_case_handler/包](../../scripts/trae_edge_case_handler/README.md)
- - [任务交接协议](../../protocols/handoff.md)

← 上一章: [边界条件判断标准与异常处理流程](02-criteria-process.md) | **[返回索引](../trae-edge-case-handler.md)** | 下一章 → [验证清单与使用约束](04-checklist-constraints.md)
