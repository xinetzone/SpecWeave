# specweave-bridge 插件

Hermes Agent 的 SpecWeave 工作区规范集成插件。本目录是该插件的**规范源码**（纳入版本控制），部署时将其内容拷贝到 Hermes 用户插件目录即可。

## 功能

| 组件 | 类型 | 作用 |
|---|---|---|
| `pre_llm_call` | hook | 处于 SpecWeave 工作区时向用户消息层注入「启动协议」brief（不污染 system prompt，保留 prompt cache）|
| `specweave_route` | tool | 任务关键词 → 规范路径，支持 apps/projects/vendor 子区域路由；无匹配回退 `.agents/context-routing.md` |
| `specweave_check` | tool | 运行 `.agents/scripts/` 下验证脚本，服务门控（非工作区不派发）|
| `/specweave` | slash command | `status` / `route` / `help` |
| `hermes specweave` | CLI 子命令 | `status` / `route` |
| `specweave:protocol` | read-only skill | 启动协议 / 上下文路由 / 内容敏感度参考 |

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
hermes specweave status                    # 显示当前工作区与子区域
hermes specweave route 复盘                # 查询任务对应规范路径
```

## 设计原则

遵循 Hermes 的 Footprint Ladder：一切以插件/技能形式叠加在核心之上，不修改 Hermes 内部实现。
启动协议注入到**用户消息层**（而非 system prompt），保证系统提示词字节级不变，复用三层 prompt cache 前缀。
