---
id: "okf-kit-wiki-10"
title: "okf-kit 完全指南 — FAQ 与排错"
source: "https://github.com/vinodborole/okf-kit/issues"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/10-faq-troubleshooting.toml"
---
# okf-kit 完全指南 — FAQ 与排错

> 一句话摘要：本章汇总安装、爬取、同步、Chat/MCP 各环节的常见问题与解决方案，包括 Playwright 依赖缺失、Python 版本要求、爬取结果为空、同步阈值拒绝、端口被占用等典型问题。

---

## 1. 安装相关问题

### Q1: 安装时报错 "Python 版本不兼容"

**原因**：okf-kit 要求 Python ≥ 3.10。

**解决**：

```bash
# 检查 Python 版本
python --version

# 如版本过低，升级 Python 后重新安装
# 推荐使用 pyenv 管理多版本
pyenv install 3.11.9
pyenv local 3.11.9
```

### Q2: `pip install 'okf-kit[browser]'` 后运行报错 "Playwright not found"

**原因**：Playwright 除了 pip 包，还需要安装浏览器二进制文件。

**解决**：

```bash
pip install 'okf-kit[browser]'
playwright install chromium
```

### Q3: Linux 上 Playwright 安装后仍缺少系统库

**原因**：Playwright 浏览器依赖一些系统库。

**解决**：

```bash
playwright install-deps chromium
```

### Q4: `[chat]` extra 安装后 Ollama 连接失败

**原因**：Ollama 服务未运行或未拉取模型。

**解决**：

```bash
# 安装 Ollama（如未安装）
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 启动服务
ollama serve

# 拉取模型
ollama pull llama3.1
```

---

## 2. 爬取相关问题

### Q5: 爬取结果为空（0 pages）

**可能原因与排查**：

1. **网站是纯 SPA（单页应用），HttpFetcher 无法获取内容**

   使用 `--browser` 标志：
   ```bash
   okf build https://spa-site.com --browser
   ```

2. **URL 规范化后与 seed URL 不匹配**

   检查是否有重定向。如果 `https://example.com` 被重定向到 `https://www.example.com`，使用最终 URL 作为 seed。

3. **path_prefix 设置错误**

   如果指定了 `--path-prefix /docs/`，确保该前缀确实存在于目标 URL 中。

4. **robots.txt 限制**

   okf-kit 默认遵守 robots.txt（通过 trafilatura）。可以使用浏览器模式尝试，但应尊重网站的爬虫政策。

5. **网站需要登录**

   okf-kit 不支持认证爬取。对于需要登录的网站，可以：
   - 使用浏览器模式手动登录后导出 cookie（高级用法）
   - 爬取公开可访问的文档部分

### Q6: 爬取速度太慢

**建议**：

- HttpFetcher 比 BrowserFetcher 快 5-10 倍，非 SPA 站点优先使用 HttpFetcher
- 调整并发数和延迟（注意：okf-kit 使用单线程 BFS + 礼貌延迟）
- 限制 `--max-pages` 和 `--max-depth` 先做小范围测试

```bash
# 先爬前两层，最多 20 页验证
okf build https://docs.example.com --max-depth 2 --max-pages 20 -o test

# 确认效果后再全量爬取
okf build https://docs.example.com -o full-docs
```

### Q7: 某些页面被遗漏

**排查步骤**：

1. 检查 `--path-prefix` 是否过窄
2. 检查页面是否通过 JavaScript 动态加载链接（需要 `--browser`）
3. 查看 bundle 中的 `log.md` 文件，了解哪些 URL 被跳过及原因
4. 检查页面链接是否在其他域名下（okf-kit 只爬同域）

### Q8: 生成的 Markdown 质量差（包含导航、广告等）

okf-kit 使用 trafilatura 进行正文提取，对大多数文档网站效果良好。如果提取效果差：

- 尝试 `--browser` 模式（crawl4ai 有自己的内容清理逻辑）
- 检查网站是否使用非标准 HTML 结构
- 可以在爬取后手动编辑生成的 Markdown 文件（sync 不会覆盖手动修改，因为 content_hash 会变化）

---

## 3. 同步相关问题

### Q9: sync 报错 "URL count changed by XX%, exceeding safety threshold"

**原因**：安全阈值保护机制。sync 检测到 URL 数量变化超过 30%（默认），拒绝执行以防误操作。

**解决**：

- 如果确认网站确实有大幅更新（如版本迁移），使用 `--force` 跳过阈值检查：
  ```bash
  okf sync my-docs --force
  ```

- 先检查原因：
  ```bash
  okf sync my-docs --dry-run
  ```

### Q10: sync 后有些文件没有更新

**原因**：内容哈希未变化。sync 只更新内容实际发生变化的页面。

**排查**：

- 如果确认远程页面已更新但哈希未变，可能是页面内容与缓存版本一致（只有非内容元素变化）
- 可以删除 `.okf-kit/state.json` 后重新 build（全量重建）

### Q11: sync 没有发现新增页面

**原因**：BFS 从已有 URL 出发，如果新页面没有被任何已收录页面链接到，就不会被发现。

**解决**：使用 `okf build` 重新全量爬取，或使用 `--sync-url` 指定新的 seed URL。

---

## 4. Chat 相关问题

### Q12: `okf chat` 直接返回关键词匹配结果，没有使用 LLM

**原因**：默认不启用 LLM（`--provider none`），使用零 Key 检索模式。

**解决**：指定 Provider：

```bash
# 本地 Ollama（推荐先试这个）
okf chat my-docs --provider ollama --model llama3.1

# OpenAI
export OPENAI_API_KEY=sk-xxx
okf chat my-docs --provider openai --model gpt-4o-mini
```

### Q13: Agent 模式下回答说"找不到相关内容"

**排查**：

1. 使用 `--trace` 观察 Agent 的导航路径
2. 确认 Agent 确实在通过 list_directory 逐层浏览，而非猜测路径
3. 如果 Agent 一直走弯路，可能是模型 tool use 能力不足，换用更强的模型
4. 检查 bundle 目录结构是否合理（目录名应能反映内容主题）

```bash
okf chat my-docs --provider ollama --model llama3.1 --trace
```

### Q14: Ollama 模型回答质量差

**建议**：

- `llama3.1:8b` 工具调用能力有限，复杂导航场景推荐使用更大模型（70B）或云端模型
- `qwen2.5:7b` 在中文场景下通常表现更好
- OpenAI gpt-4o-mini 和 Anthropic claude-sonnet 的 tool use 能力最稳定

### Q15: Chat 历史存储在哪里？

对话历史存储在 `~/.okf/chats/<bundle-name>/` 目录下，JSONL 格式。每个会话一个文件。

---

## 5. MCP 相关问题

### Q16: Claude Code/Cursor 连接 MCP server 失败

**排查步骤**：

1. 确认 okf-kit 已安装且在 PATH 中：
   ```bash
   which okf
   okf --version
   ```

2. 确认 bundle 存在：
   ```bash
   ls ~/.okf/bundles/
   ```

3. 确认安装了 `[mcp]` extra：
   ```bash
   pip install 'okf-kit[mcp]'
   ```

4. 尝试手动运行 MCP server 检查是否有错误：
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | okf serve-mcp my-docs
   ```

5. 检查 MCP 配置文件中的路径是否正确（使用绝对路径）

### Q17: MCP 工具没有出现在 AI 助手中

- 重启 Claude Code/Cursor 以加载新的 MCP server 配置
- 检查配置文件 JSON 格式是否正确（没有多余逗号）
- 确认配置文件位置正确

---

## 6. HTTP 服务相关问题

### Q18: `okf serve` 端口被占用

okf serve 默认自动选择可用端口。如果需要指定端口：

```bash
okf serve --port 8080
```

如果指定端口仍被占用，检查是否有其他 okf serve 实例在运行：

```bash
# 查看运行中的 okf serve 进程
# Linux/macOS:
ps aux | grep "okf serve"
# Windows:
tasklist | findstr okf
```

### Q19: 忘记 serve token

token 在服务启动时打印到 stdout。如果丢失，重启服务即可获取新 token。

### Q20: API Key 存储在哪里？

- macOS: Keychain
- Windows: Windows Credential Locker
- Linux: Secret Service（GNOME Keyring/KWallet）
- 无头 Linux（无 keyring）：`~/.okf/.secrets.json`（权限 0600）

API Key 永远不通过 API 返回明文。

---

## 7. 通用问题

### Q21: 如何完全卸载 okf-kit？

```bash
# 卸载 pip 包
pip uninstall okf-kit

# 删除数据目录（包含 bundles、聊天历史、设置）
rm -rf ~/.okf
```

### Q22: 可以在没有网络的环境使用吗？

可以。以下功能完全离线可用：

- `okf chat`（零 Key 检索模式）
- `okf validate`
- `okf visualize`
- `okf serve-mcp`
- 读取和搜索已有 bundle
- Ollama 本地 LLM 对话（需 Ollama 运行中）

需要网络的功能：

- `okf build`（需要访问目标网站）
- `okf sync`（需要访问目标网站）
- `okf get`（需要从 Registry 下载）
- 云端 LLM Provider（OpenAI/Anthropic/OpenRouter）

### Q23: okf-kit 支持 Windows 吗？

支持。所有核心功能在 Windows 上均可使用。注意：

- 路径使用正斜杠（`/`）或反斜杠（`\`）均可
- Playwright 浏览器模式在 Windows 上正常工作
- keyring 使用 Windows Credential Locker

---

## 8. 获取帮助

- **GitHub Issues**: https://github.com/vinodborole/okf-kit/issues
- **GitHub Discussions**: https://github.com/vinodborole/okf-kit/discussions
- **文档**: https://github.com/vinodborole/okf-kit#readme

---

- [← 上一章：扩展与开发](09-extension-development.md) | [下一章：总结与资源](11-summary-resources.md) →
