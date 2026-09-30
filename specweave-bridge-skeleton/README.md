# specweave-bridge 插件

Hermes Agent 的 SpecWeave 工作区规范集成插件。本目录是该插件的**规范源码**（纳入版本控制），部署时将其内容拷贝到 Hermes 用户插件目录即可。

## 功能

| 组件 | 类型 | 作用 |
|---|---|---|
| `pre_llm_call` | hook | 处于 SpecWeave 工作区时向用户消息层注入「启动协议」brief（不污染 system prompt，保留 prompt cache）；按识别信号分流：主信号注入启动协议 brief，兼容信号注入兼容模式 brief |
| `specweave_route` | tool | 任务关键词 → 规范路径，支持 apps/projects/vendor 子区域路由；无匹配回退 `.agents/context-routing.md` |
| `specweave_check` | tool | 运行 `.agents/scripts/` 下验证脚本，服务门控（非工作区不派发）|
| `/specweave` | slash command | `status` / `route` / `help`（status 显示命中信号）|
| `hermes specweave` | CLI 子命令 | `status` / `route` |
| `specweave:protocol` | read-only skill | 启动协议 / 上下文路由 / 内容敏感度参考 |

## 工作区识别（双信号）

`detector.py` 对齐 SpecWeave [五步发现流程](../.agents/protocols/workspace-discovery.md) 的步骤 1/3/4，主动识别 `.agents` + `AGENTS.md` 双信号：

| 信号 | 判定条件 | 语义 |
|---|---|---|
| 主信号 `agents_md` | `AGENTS.md` 存在且含「启动协议」关键词 | Root Workspace，注入标准启动协议 brief |
| 兼容信号 `agents_dir` | `.agents/` 目录存在且 `roles/` 与 `skills/` 同时存在 | 兼容模式（旧版 SpecWeave 项目，无标准 AGENTS.md 也可识别），注入兼容模式 brief |

- 同一目录内主信号优先；层级上**就近命中即返回**（从 cwd 向上递归，命中即停止，嵌套子工作区按其自身上下文治理）
- 兼容信号较五步发现流程步骤 3 的文字描述更严格（要求 `roles/` 与 `skills/` 同时存在）：仅含单一 `skills/` 的通用技能管理器目录（如 `~/.agents/skills/`）不会误判，避免用户主目录被识别为兼容工作区、污染所有非 SpecWeave 会话
- 行为变化提示（v0.2.0 起）：含 `.agents/roles` + `.agents/skills` 的嵌套子工作区（如 `vendor/flexloop/apps/chaos`、`apps/docker-images/pytorch-base`）现在会被识别为独立兼容工作区，而非继续向上归属外层 SpecWeave 根——这是五步发现流程「命中即返回」的既定语义
- `detector.detect_workspace_signal()` 返回命中的信号名，供 `status` / `verify` 展示与诊断

> 使用者接入说明见 [ACCESS.md](ACCESS.md)。

## 一键安装（Python 自动化）

本目录提供零第三方依赖的安装脚本 [install.py](install.py)，自动化「部署 + 启用 + 验证」：

```powershell
$env:HERMES_HOME = "C:\Users\admin\.hermes"
python install.py install     # deploy + enable（幂等，自动备份 config.yaml）
python install.py verify      # 校验：插件加载 + 工作区检测 + 路由 + 协议注入
python install.py all         # install + verify
```

特性：幂等（重复执行无副作用）、enable 前自动备份 `config.yaml.bak-<ts>`、复用插件自身 `detector.py` 校验逻辑、`verify` 输出机器可读 JSON + 退出码。

## 目录结构

```
specweave-bridge-skeleton/
├── plugin.yaml            # 插件清单（Hermes 识别与加载）
├── _constants.py          # 常量 + ROUTES 路由表
├── detector.py            # 工作区检测 / 子区域检测
├── __init__.py            # register() 入口，注册全部组件
└── skills/
    └── protocol/
        └── SKILL.md       # 只读协议参考技能
```

## 部署

1. 确认 Hermes 用户目录（`HERMES_HOME`）。本环境为 `C:\Users\admin\.hermes`
2. 将本目录内容拷贝到 `<HERMES_HOME>/plugins/specweave-bridge/`

```powershell
Copy-Item -Path "specweave-bridge-skeleton\*" `
          -Destination "$env:HERMES_HOME\plugins\specweave-bridge\" -Recurse -Force
```

3. 在 `<HERMES_HOME>/config.yaml` 的 `plugins.enabled` 中加入 `specweave-bridge`：

```yaml
plugins:
  enabled:
  - specweave-bridge
```

4. 重启 Hermes 会话生效。

## 验证

```powershell
$env:HERMES_HOME = "C:\Users\admin\.hermes"
hermes plugins list --plain --no-bundled   # 应显示 specweave-bridge (enabled/user)
hermes specweave status                    # 显示当前工作区、识别信号与子区域
hermes specweave route 复盘                # 查询任务对应规范路径
```

## 测试

检测逻辑单元测试位于 [.agents/scripts/tests/test_specweave_bridge_detector.py](../.agents/scripts/tests/test_specweave_bridge_detector.py)（沿用仓库统一测试入口，覆盖双信号判定、就近命中递归、子区域检测、brief 分流与打包一致性）：

```powershell
python -m pytest .agents/scripts/tests/test_specweave_bridge_detector.py -v
```

## 设计原则

遵循 Hermes 的 Footprint Ladder：一切以插件/技能形式叠加在核心之上，不修改 Hermes 内部实现。
启动协议注入到**用户消息层**（而非 system prompt），保证系统提示词字节级不变，复用三层 prompt cache 前缀。

> AI生成