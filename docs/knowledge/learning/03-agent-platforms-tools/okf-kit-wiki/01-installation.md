---
id: "okf-kit-wiki-01"
title: "okf-kit 完全指南 — 安装与配置"
source: "https://github.com/vinodborole/okf-kit"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/01-installation.toml"
---

# okf-kit 完全指南 — 安装与配置

> 一句话摘要：okf-kit 支持 pip/uvx 多种安装方式，最小安装无浏览器无 LLM SDK 可秒级完成，通过 7 个可选 extras 按需启用 JS 渲染/LLM 对话/LLM富化/MCP 服务/HTTP API 功能，所有用户数据存储在 `~/.okf/` 目录下。

---

## 1. 前置条件

| 条件 | 要求 | 说明 |
|------|------|------|
| **Python 版本** | ≥ 3.10 | 使用了 `X \| Y` 类型联合语法（PEP 604）和 match/case（PEP 634） |
| **pip 版本** | ≥ 23.0 | 建议使用最新版 pip 以支持可选 extras 解析 |
| **网络环境** | 可访问 PyPI | 安装包约数 MB（核心依赖），JS/serve extras 较大 |
| **操作系统** | Windows/macOS/Linux | 全平台支持，部分路径处理代码专门兼容 Windows |
| **Git** | 可选 | 仅在需要从源码安装时需要 |

检查 Python 版本：

```bash
python --version    # 应 ≥ 3.10
pip --version       # 应 ≥ 23.0
```

---

## 2. 安装方式

### 2.1 pip 安装（推荐）

**最小安装（核心功能，无浏览器无 LLM SDK）：**

```bash
pip install okf-kit
```

核心安装仅包含：httpx（HTTP 客户端）、trafilatura（正文提取）、selectolax（HTML 解析）、pyyaml、lxml-html-clean 等基础依赖，CLI 使用 Python 标准库 argparse。安装体积小，数秒内完成。

**带所有可选功能的完整安装：**

```bash
pip install 'okf-kit[all]'
```

### 2.2 uvx 运行（无需安装）

如果你安装了 [uv](https://docs.astral.sh/uv/)，可以直接运行无需预安装：

```bash
# 核心功能
uvx okf-kit build https://docs.example.com -o my-docs

# 带LLM对话
uvx --from 'okf-kit[chat]' okf chat my-docs --provider ollama
```

### 2.3 从源码安装

```bash
git clone https://github.com/vinodborole/okf-kit.git
cd okf-kit
pip install -e '.[dev]'
```

---

## 3. 可选依赖（Extras）

okf-kit 使用 extras 实现按需安装，避免强制安装大体积依赖（如 Playwright 浏览器）。

| Extra | 安装命令 | 启用的功能 | 额外依赖 | 安装体积 |
|-------|---------|-----------|---------|---------|
| **核心（默认）** | `pip install okf-kit` | build / sync / validate / zip / list / get / chat(零Key检索) / visualize | httpx, trafilatura, selectolax, pyyaml, lxml-html-clean | ~5 MB |
| `[js]` | `pip install 'okf-kit[js]'` | JS 渲染站点抓取（`--js` 标志，BrowserFetcher + crawl4ai） | crawl4ai（含 Playwright） | ~200+ MB（含浏览器） |
| `[chat]` | `pip install 'okf-kit[chat]'` | LLM 对话（OpenAI 兼容协议：OpenAI/Ollama/OpenRouter/Custom） | openai ≥ 1.60 | ~10 MB |
| `[anthropic]` | `pip install 'okf-kit[anthropic]'` | Anthropic Claude 原生支持 | anthropic ≥ 0.40 | ~15 MB |
| `[enrich]` | `pip install 'okf-kit[enrich]'` | build 时 LLM 富化 frontmatter（`--enrich` 标志） | openai ≥ 1.60 | ~10 MB |
| `[mcp]` | `pip install 'okf-kit[mcp]'` | stdio MCP 服务器（Claude Code/Cursor） | mcp ≥ 1.2.0 | ~5 MB |
| `[serve]` | `pip install 'okf-kit[serve]'` | 本地 HTTP API（FastAPI + SSE + keyring） | fastapi, uvicorn, keyring | ~20 MB |
| `[all]` | `pip install 'okf-kit[all]'` | 以上全部功能（js+chat+anthropic+enrich+mcp+serve） | 所有 extras 依赖 | ~250+ MB |
| `[dev]` | `pip install -e '.[dev]'` | 开发环境（测试+lint+构建） | pytest, pytest-asyncio, ruff, build | ~10 MB |

### 3.1 功能与 Extra 对照

| CLI 命令/标志 | 所需 Extra | 无 Extra 时行为 |
|----------|-----------|----------------|
| `okf build` | 无（核心已包含） | 可用，仅支持 HttpFetcher |
| `okf build --js` | `[js]` | 错误提示：需要安装 `[js]` extra |
| `okf build --enrich` | `[enrich]` | 需要 OPENAI_API_KEY，缺少 extra 时报错 |
| `okf sync` | 无（核心已包含） | 可用 |
| `okf validate` | 无（核心已包含） | 可用 |
| `okf zip` | 无（核心已包含） | 可用 |
| `okf list` | 无（核心已包含） | 可用 |
| `okf get` | 无（核心已包含） | 可用 |
| `okf visualize` | 无（核心已包含） | 可用（生成静态 HTML 知识图谱） |
| `okf chat`（零Key检索） | 无（核心已包含） | 可用（关键词检索模式） |
| `okf chat --provider <llm>` | `[chat]` 或 `[anthropic]` | 错误提示：需要安装对应 extra |
| `okf serve-mcp` | `[mcp]` | 错误提示：需要安装 `[mcp]` extra |
| `okf serve` | `[serve]` | 错误提示：需要安装 `[serve]` extra |

### 3.2 首次使用 BrowserFetcher 的额外步骤

使用 `--js` 抓取 JS 渲染站点时，首次运行需要安装 Playwright 浏览器：

```bash
pip install 'okf-kit[js]'
crawl4ai-setup        # 安装 Playwright 浏览器（首次运行 crawl4ai 时也会自动提示）
```

---

## 4. 验证安装

```bash
# 验证 CLI 可用
okf --version
# 输出：okf, version 0.3.3

# 查看帮助
okf --help
```

预期输出包含 11 个子命令：build, sync, validate, zip, list, get, chat, visualize, serve-mcp, serve, enrich（enrich 是 calknowledge 增强命令）。

---

## 5. 用户目录结构

okf-kit 将所有用户数据存储在用户主目录下的 `~/.okf/` 文件夹中：

```
~/.okf/
├── bundles/              # 所有 bundle 的存储位置
│   ├── react-docs/       # 一个 bundle（通过 build/get 安装）
│   └── ros2-docs/
├── chats/                # 对话历史（按 bundle 分子目录）
│   ├── react-docs/
│   │   └── 20260818-143022.jsonl  # 一个对话会话（JSONL 格式）
│   └── ros2-docs/
├── settings.json         # serve 功能的 Provider 设置
└── .secrets.json         # API Key 备份（0600权限，keyring 不可用时使用）
```

### 5.1 目录路径

| 目录 | 函数 | Windows 路径 | macOS/Linux 路径 |
|------|------|-------------|-----------------|
| Home | `config.home_dir()` | `%USERPROFILE%\.okf\` | `~/.okf/` |
| Bundles | `config.bundles_dir()` | `%USERPROFILE%\.okf\bundles\` | `~/.okf/bundles/` |
| Chats | `config.chats_dir()` | `%USERPROFILE%\.okf\chats\` | `~/.okf/chats/` |

### 5.2 Bundle 存储位置

bundle 默认存储在 `~/.okf/bundles/` 下。`okf build` 使用 `-o/--output` 参数指定输出路径，支持：

- **绝对路径**：`-o /data/my-bundle` → 直接使用该路径
- **相对路径**：`-o my-bundle` → 相对于当前工作目录
- **仅名称**：`-o my-bundle`（非路径）→ 存储到 `~/.okf/bundles/my-bundle/`

`okf get` 从 Registry 安装的 bundle 始终存储在 `~/.okf/bundles/` 下。

---

## 6. 虚拟环境建议

### 6.1 使用 venv

```bash
# 创建虚拟环境
python -m venv okf-env

# 激活（Windows PowerShell）
okf-env\Scripts\Activate.ps1

# 激活（macOS/Linux）
source okf-env/bin/activate

# 安装
pip install okf-kit

# 使用
okf --version
```

### 6.2 使用 uv（推荐）

```bash
# 创建项目并安装
uv init my-okf-project
cd my-okf-project
uv add okf-kit

# 运行
uv run okf --version
```

---

## 7. 升级与卸载

### 升级

```bash
pip install --upgrade okf-kit
```

### 卸载

```bash
pip uninstall okf-kit
```

卸载后 `~/.okf/` 目录中的 bundle 和聊天历史不会被自动删除，如需清理请手动删除：

```bash
# Windows
rmdir /s /q %USERPROFILE%\.okf

# macOS/Linux
rm -rf ~/.okf
```

---

## 8. 环境变量

okf-kit 目前不使用专用环境变量，但 LLM Provider 的 API Key 可以通过标准方式设置：

| Provider | 环境变量 | 说明 |
|---------|---------|------|
| OpenAI | `OPENAI_API_KEY` | 当 `--provider openai` 且未通过 serve 界面设置 key 时可用 |
| Anthropic | `ANTHROPIC_API_KEY` | 当 `--provider anthropic` 时可用 |
| OpenRouter | `OPENROUTER_API_KEY` | 当 `--provider openrouter` 时可用 |

使用 `okf serve` 启动 HTTP API 后，Key 会存储在 OS keychain 中，无需环境变量。

---

## 9. 常见安装问题

### Q: 安装 crawl4ai 时失败？

A: crawl4ai 需要 Playwright 浏览器，在某些网络环境下可能下载失败。可以尝试：
```bash
# 设置 Playwright 镜像（中国大陆用户）
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
pip install 'okf-kit[js]'
```

### Q: keyring 在 Linux 无头服务器上报错？

A: serve 功能检测到 keyring 后端不可用时，会自动降级到 `~/.okf/.secrets.json` 文件存储（0600 权限）。可以忽略 keyring 警告。

### Q: Python 版本不够？

A: okf-kit 要求 Python ≥ 3.10。如果系统 Python 版本过低，可以：
- 使用 pyenv/conda 安装 Python 3.10+
- 使用 uv 自动管理 Python 版本

### Q: Windows 上 PowerShell 执行策略限制？

A: 如果虚拟环境激活脚本被阻止，以管理员身份运行 PowerShell 执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 10. 安装验证清单

完成安装后，执行以下命令验证环境：

```bash
# 1. CLI 版本
okf --version
# 期望：okf, version 0.3.3

# 2. 核心命令可用
okf build --help | head -5
# 期望：显示 build 命令帮助

# 3. 零Key chat 可用（无需任何 API Key）
echo "test" | okf list
# 期望：列出 ~/.okf/bundles/ 下的 bundle（可能为空）

# 4. （可选）验证 chat extra
pip install 'okf-kit[chat]'
# 期望：安装成功
```

---

- [← 上一章：概述](00-overview.md) | [下一章：CLI 命令参考](02-cli-reference.md) →
