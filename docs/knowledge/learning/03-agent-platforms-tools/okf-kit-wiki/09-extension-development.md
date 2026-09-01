---
type: Wiki Tutorial

id: "okf-kit-wiki-09"
title: "okf-kit 完全指南 — 扩展与开发"
source: "https://github.com/vinodborole/okf-kit"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/okf-kit-wiki/09-extension-development.toml"
---
# okf-kit 完全指南 — 扩展与开发

> 一句话摘要：okf-kit 采用模块化分层架构，核心模块（crawl/mapper/writer/okf）无 LLM 依赖，Fetcher 层可扩展新的抓取后端，Provider 层可扩展新的 LLM 服务，与 calknowledge 平台形成"轻量核心+增强平台"的生态关系。

---

## 1. 源码结构

```
okf-kit/
├── pyproject.toml              # 项目配置、依赖、extras
├── README.md                   # 项目说明
├── okf_kit/                    # 主包
│   ├── __init__.py             # 版本号 __version__
│   ├── cli.py                  # CLI 入口（argparse 命令定义）
│   ├── config.py               # ~/.okf/ 路径配置
│   ├── model.py                # Page/PageRecord 数据类
│   ├── crawl.py                # BFS 爬取控制
│   ├── mapper.py               # URL→路径映射
│   ├── writer.py               # Bundle 写入与索引生成
│   ├── okf.py                  # OKF 格式验证、frontmatter、zip
│   ├── sync.py                 # 增量同步
│   ├── registry.py             # Registry 下载/安装
│   ├── visualize.py            # 知识图谱生成
│   ├── bundle_nav.py           # 导航基元（list/read/search）
│   ├── bundle_reader.py        # 通用 bundle 读取工具
│   ├── enrich.py               # LLM 富化（calknowledge扩展）
│   ├── fetch/                  # Fetcher 抽象层
│   │   ├── __init__.py
│   │   ├── base.py             # Fetcher 抽象基类
│   │   ├── http.py             # HttpFetcher（httpx + trafilatura）
│   │   └── browser.py          # BrowserFetcher（crawl4ai）
│   ├── chat/                   # Chat 对话系统
│   │   ├── __init__.py
│   │   ├── agent.py            # Agent 导航循环
│   │   ├── providers.py        # LLM Provider 抽象与实现
│   │   ├── retrieval.py        # 零Key检索
│   │   ├── history.py          # 对话历史管理
│   │   └── repl.py             # REPL 交互模式
│   └── serve/                  # HTTP API 服务
│       ├── __init__.py
│       ├── app.py              # FastAPI 应用定义
│       ├── run.py              # 服务启动与端口管理
│       ├── settings.py         # Provider 设置与密钥存储
│       └── reader.py           # HTTP 层 bundle 读取工具
└── tests/                      # 测试目录
    ├── test_mapper.py          # URL映射测试
    ├── test_okf.py             # OKF格式验证测试
    ├── test_sync.py            # 增量同步测试
    ├── test_crawl.py           # 爬取测试
    └── ...
```

---

## 2. 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/vinodborole/okf-kit.git
cd okf-kit

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 以可编辑模式安装（含开发依赖）
pip install -e '.[dev,all]'

# 4. 验证安装
okf --version
```

---

## 3. 核心 API

### 3.1 以编程方式构建 Bundle

```python
import asyncio
from pathlib import Path
from okf_kit.crawl import crawl_site
from okf_kit.fetch.http import HttpFetcher
from okf_kit.writer import write_bundle
from okf_kit.okf import validate_bundle

async def build_docs():
    # 创建 Fetcher
    fetcher = HttpFetcher(
        sleep_ms=300,
        timeout=30,
        user_agent="okf-kit/dev"
    )

    try:
        # BFS 爬取
        pages, url_to_path, links = await crawl_site(
            seed="https://docs.example.com",
            fetcher=fetcher,
            max_depth=2,
            max_pages=50,
            path_prefix="/docs/",
        )

        # 写入 Bundle
        output = Path("./my-docs")
        write_bundle(
            bundle_dir=output,
            pages=pages,
            url_to_path=url_to_path,
            links=links,
            config={
                "root_url": "https://docs.example.com",
                "max_depth": 2,
                "max_pages": 50,
            }
        )

        # 验证
        is_valid = validate_bundle(output, quiet=True)
        print(f"Valid: {is_valid}")
    finally:
        await fetcher.close()

asyncio.run(build_docs())
```

### 3.2 使用 BrowserFetcher

```python
from okf_kit.fetch.browser import BrowserFetcher

fetcher = BrowserFetcher()
# 使用方式与 HttpFetcher 完全相同
pages, url_to_path, links = await crawl_site(
    seed="https://spa-docs.example.com",
    fetcher=fetcher,
    max_depth=2,
    max_pages=50,
)
await fetcher.close()
```

### 3.3 增量同步

```python
from okf_kit.sync import sync_bundle

result = sync_bundle(
    bundle_dir=Path("./my-docs"),
    # max_pages=100,  # 可选覆盖
    # browser=False,  # 使用浏览器
)
print(f"Added: {result.added}, Updated: {result.changed}, Removed: {result.removed}")
```

### 3.4 读取 Bundle

```python
from okf_kit.bundle_nav import list_directory, read_concept, search_bundle

bundle = Path.home() / ".okf" / "bundles" / "react-docs"

# 列目录
print(list_directory(bundle, "/"))

# 读概念
content = read_concept(bundle, "/pages/hooks/use-state.md")
print(content)

# 搜索
results = search_bundle(bundle, "useState", limit=5)
for r in results:
    print(f"- {r['title']}: {r['path']}")
```

### 3.5 零 Key 检索

```python
from okf_kit.chat.retrieval import answer
from okf_kit.config import bundles_dir

result = answer(bundles_dir() / "react-docs", "How to use useState?")
print(result["answer"])
for source in result["sources"]:
    print(f"  [{source['title']}]({source['path']})")
```

---

## 4. 自定义 Fetcher

Fetcher 是最常见的扩展点。可以通过继承 `Fetcher` 基类实现新的页面获取方式。

### 4.1 Fetcher 基类接口

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class FetchResult:
    url: str
    status_code: int
    markdown: str
    title: str
    description: str
    content_links: list[str]
    headers: dict

class Fetcher(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> FetchResult:
        """获取页面并返回 FetchResult"""
        ...

    @abstractmethod
    async def close(self):
        """释放资源（关闭连接池、浏览器等）"""
        ...
```

### 4.2 示例：GitHub API Fetcher

爬取 GitHub 仓库的 Markdown 文件：

```python
import httpx

class GitHubFetcher(Fetcher):
    """从 GitHub API 获取仓库 Markdown 文件"""

    def __init__(self, token: str | None = None):
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.AsyncClient(headers=headers, timeout=30)

    async def fetch(self, url: str) -> FetchResult:
        # 将 GitHub HTML URL 转换为 raw 内容 URL
        raw_url = url.replace("github.com", "raw.githubusercontent.com")
        raw_url = raw_url.replace("/blob/", "/")

        resp = await self.client.get(raw_url)
        if resp.status_code != 200:
            return FetchResult(
                url=url, status_code=resp.status_code,
                markdown="", title="", description="",
                content_links=[], headers=dict(resp.headers)
            )

        markdown = resp.text
        # 简单提取标题（第一个 # 行）
        title = url.split("/")[-1].replace(".md", "")
        for line in markdown.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # 提取 Markdown 链接
        import re
        links = re.findall(r'\[.*?\]\(([^)]+)\)', markdown)
        # 转换相对链接为绝对 URL
        content_links = []
        for link in links:
            if link.startswith("http"):
                content_links.append(link)
            elif link.endswith(".md"):
                # 相对 Markdown 链接 → GitHub URL
                base = "/".join(url.split("/")[:-1])
                content_links.append(f"{base}/{link}")

        return FetchResult(
            url=url,
            status_code=200,
            markdown=markdown,
            title=title,
            description=markdown[:200],
            content_links=content_links,
            headers=dict(resp.headers)
        )

    async def close(self):
        await self.client.aclose()
```

使用自定义 Fetcher：

```python
fetcher = GitHubFetcher(token="ghp_...")
pages, url_to_path, links = await crawl_site(
    seed="https://github.com/user/repo/blob/main/README.md",
    fetcher=fetcher,
    max_depth=3,
    max_pages=100,
    # 注意：GitHub 路径前缀需要特殊处理
    path_prefix="/user/repo/blob/main/",
)
```

### 4.3 注册自定义 CLI 命令

okf-kit 使用标准库 argparse 构建 CLI，目前不支持通过 entry point 扩展命令。如需自定义命令，建议直接导入 okf-kit 的核心函数编写自己的脚本。

---

## 5. 自定义 LLM Provider

```python
from okf_kit.chat.providers import BaseProvider, ProviderResponse, ToolCall

class MyCustomProvider(BaseProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or "https://api.my-llm.com/v1"
        # 初始化 HTTP 客户端
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"}
        )

    async def chat(self, messages, tools=None, **kwargs):
        # 调用你的 LLM API
        resp = await self.client.post("/chat/completions", json={
            "model": self.model,
            "messages": messages,
            "tools": tools,
        })
        data = resp.json()

        # 解析响应为统一的 ProviderResponse 格式
        return ProviderResponse(
            content=data["choices"][0]["message"].get("content", ""),
            tool_calls=self._parse_tool_calls(data),
            usage=data.get("usage"),
        )

    def _parse_tool_calls(self, data):
        # 将 API 返回的 tool_calls 转换为统一格式
        calls = []
        msg = data["choices"][0]["message"]
        for tc in msg.get("tool_calls", []):
            calls.append(ToolCall(
                id=tc["id"],
                name=tc["function"]["name"],
                arguments=json.loads(tc["function"]["arguments"])
            ))
        return calls

    async def close(self):
        await self.client.aclose()
```

---

## 6. 测试

okf-kit 使用 pytest 进行测试。

### 6.1 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_mapper.py -v

# 运行并显示覆盖率
pytest --cov=okf_kit --cov-report=term-missing
```

### 6.2 测试结构

| 测试文件 | 覆盖模块 | 测试重点 |
|---------|---------|---------|
| `test_mapper.py` | mapper.py | URL→路径映射的确定性、保留名避让、query hash |
| `test_okf.py` | okf.py | frontmatter 解析、validate 规则 |
| `test_sync.py` | sync.py | delta 计算、安全阈值、unchanged 文件保持 |
| `test_crawl.py` | crawl.py | URL 规范化、同域检查、BFS 顺序 |
| `test_bundle_nav.py` | bundle_nav.py | list/read/search 功能 |
| `test_retrieval.py` | retrieval.py | 零Key检索相关性 |

### 6.3 测试原则

- mapper 的测试用例最多，因为映射逻辑确定性强且边界情况多
- 网络请求使用 mock，不依赖外部网站
- sync 测试使用临时目录构建 fixture bundle

---

## 7. calknowledge 生态关系

okf-kit 是 [calknowledge](https://github.com/vinodborole/calknowledge) 生态的轻量开源核心。两者的关系：

| 维度 | okf-kit（本项目） | calknowledge（平台） |
|------|------------------|---------------------|
| **定位** | CLI 工具 + 核心库 | 完整平台（Web UI + 高级功能） |
| **许可证** | Apache-2.0（开源） | 开源核心 + 商业功能 |
| **LLM 富化** | ❌ 不包含 | ✅ 自动标注 type/description/标签 |
| **RAG 导出** | ❌ | ✅ 导出向量索引 |
| **检索评估** | ❌ | ✅ RAG 质量评估 |
| **Web GUI** | ❌（serve 是 API 层） | ✅ 完整 Web 界面 |
| **用户管理** | ❌ | ✅ 多用户/权限 |
| **云同步** | ❌ | ✅ 云端同步 |
| **bundle 构建** | ✅ | ✅（使用 okf-kit 核心） |
| **增量同步** | ✅ | ✅ |
| **MCP 服务** | ✅ | ✅ |

简单来说：okf-kit 专注"把网站变成可移植的 Markdown bundle"这一件事；calknowledge 在 okf-kit 之上构建完整的知识管理平台。

---

## 8. 代码风格与贡献

- **Python 版本**：≥ 3.10，使用类型注解
- **格式化**：使用 ruff 格式化
- **类型检查**：mypy --strict
- **测试要求**：新功能必须包含测试
- **提交规范**：Conventional Commits（feat:/fix:/docs:/test: 等）

---

- [← 上一章：Registry 与可视化](08-registry-visualize.md) | [下一章：FAQ 与排错](10-faq-troubleshooting.md) →
