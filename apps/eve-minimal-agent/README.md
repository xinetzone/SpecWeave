# minimal-agent

一个最小可运行的 **Vercel Eve** Agent 示例。它演示了 Eve 的核心设计哲学——**"文件系统即接口"**：你只需把文件放在约定位置，框架自动发现并组合，零胶水代码。它也是 `IMP-001`（实际运行 Eve 框架）的最小落地版本。

## 目录结构

```
minimal-agent/
├── package.json              # 依赖与 npm scripts
├── tsconfig.json             # TypeScript 编译配置
├── .env.example              # 模型凭证示例（复制为 .env 使用）
├── agent/
│   ├── agent.ts              # 模型与运行时配置（defineAgent）
│   ├── instructions.md       # 始终生效的系统指令
│   ├── tools/
│   │   └── get_weather.ts    # 工具（文件名即工具名）
│   └── channels/
│       └── eve.ts            # 内置 HTTP 通道（可选，默认已启用）
└── evals/                    # 评测（可选，本示例未启用）
```

## 快速开始

需要 **Node.js ≥ 24** 和一个模型凭证。

```sh
# 1. 安装依赖
npm install

# 2. 配置模型凭证（复制 .env.example 为 .env 并填入）
cp .env.example .env
#   默认走 Vercel AI Gateway：AI_GATEWAY_API_KEY=...

# 3. 启动开发服务器（打开交互式终端 UI）
npm run dev
```

在 TUI 中直接提问，例如：

```text
What's the weather in Brooklyn?
```

Agent 会调用 `get_weather` 工具返回数据（演示用 mock 数据）。

### 用 HTTP 接口调用

```sh
curl -X POST http://localhost:2000/eve/v1/session \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the weather in Paris?"}'
# → {"continuationToken":"eve:7f3c...","ok":true,"sessionId":"ses_01h..."}
```

## 各文件关键逻辑

### `agent/agent.ts` — 模型与运行时契约

```ts
import { defineAgent } from "eve";

export default defineAgent({
  model: "anthropic/claude-sonnet-5",
});
```

- `model` 为模型 ID，走 Vercel AI Gateway 路由，天然支持 provider fallback。
- 可选配置：`reasoning`（推理强度）、`compaction`（上下文压缩阈值）、`limits`（会话 token 预算）等。
- 文件存在时 `model` 必填；省略整个 `agent.ts` 则用默认模型。

### `agent/instructions.md` — 身份与常驻规则

始终注入提示词，负责"我是谁、长期行为准则"。按需的操作手册放 `skills/`，具体动作放 `tools/`——三者职责分离。

### `agent/tools/get_weather.ts` — 类型化动作

```ts
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Return mock weather data for a city.",
  inputSchema: z.object({ city: z.string().min(1) }),
  async execute({ city }) {
    return { city, condition: "Sunny", temperatureF: 72 };
  },
});
```

- `description`：写给模型看的说明，模型据此决定何时调用。
- `inputSchema`：Zod schema，**必填**（无输入用 `z.object({})`），同时作为 `execute` 的参数类型推断。
- `execute(input, ctx)`：实现，可同步/异步，返回 JSON 可序列化对象。
- 文件名即工具名（`get_weather.ts` → 工具 `get_weather`），运行时在**应用运行时**（可信侧，可读 `process.env`）执行。

### `agent/channels/eve.ts` — 前端入口

```ts
import { eveChannel } from "eve/channels/eve";
import { localDev, vercelOidc } from "eve/channels/auth";

export default eveChannel({
  auth: [vercelOidc(), localDev()],
});
```

- 挂载 `/eve/v1/session*` 系列路由（启会话、续聊、取消、流式）。
- 默认已启用，只有要覆盖默认认证策略时才写该文件。本地开发用 `localDev()` 放行，生产需替换为真实 `AuthFn`。

## 模型凭证（两种方式）

默认走 Vercel AI Gateway，`agent.ts` 中模型为 Gateway ID 时使用 `AI_GATEWAY_API_KEY`。

如需 BYOK 直连某供应商，可改为：

```ts
import { defineAgent } from "eve";
import { anthropic } from "@ai-sdk/anthropic";

export default defineAgent({
  model: anthropic("claude-opus-4-8"),
});
```

此时需安装 `@ai-sdk/anthropic` 并设置 `ANTHROPIC_API_KEY`。

## 验证

```sh
npm run typecheck   # 类型检查
npm run build       # 构建（eve build）
```

## 延伸阅读

- 官方文档：<https://eve.dev/docs>
- 本仓库内 Eve 源码文档：`d:\AI\external\tools\eve\docs\`（vendor 子模块，只读参考）
- 首个完整教程：`d:\AI\external\tools\eve\docs\tutorial\first-agent.mdx`
- 项目结构：`d:\AI\external\tools\eve\docs\project-structure.mdx`