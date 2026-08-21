---
id: 03-dependencies
title: pyproject.toml 依赖清单
source: veadk-python codebase analysis
---

## [project.dependencies]（核心依赖）

```
pydantic-settings==2.10.1
a2a-sdk==0.3.7
deprecated==1.2.18
google-adk>=1.34.0
litellm>=1.83.7
sqlalchemy>=2,<3
python-dotenv>=1.1.0
opentelemetry-exporter-otlp==1.37.0
opentelemetry-instrumentation-logging>=0.56b0
wrapt==1.17.2
volcengine-python-sdk>=5.0.36
volcengine>=1.0.193
agent-pilot-sdk==0.1.2
fastmcp>=2.12.3
trustedmcp==0.0.5
mcp==1.26.0
cookiecutter==2.6.0
jinja2==3.1.6
omegaconf==2.3.0
psycopg2-binary>=2.9.10
asyncpg>=0.29.0
pymysql==1.1.1
aiomysql==0.3.2
filetype==1.2.0
pypdfium2>=4.30.0
pillow>=10.0.0
vikingdb-python-sdk>=0.1.3
agentkit-sdk-python>=0.8.0
websockets>=15,<16
openviking-sdk>=0.1.3
python-frontmatter==1.1.0
tos>=2.8.4
```

## [project.optional-dependencies]（可选依赖分组）

### codex
```
openai-codex==0.1.0b3
openai-codex-cli-bin==0.137.0a4
```

### extensions
```
redis>=5.0
cozeloop>=0.1.21
llama-index>=0.14.0
llama-index-embeddings-openai-like>=0.2.2
llama-index-llms-openai-like>=0.5.1
llama-index-vector-stores-redis>=0.6.1
llama-index-vector-stores-opensearch>=0.6.1
llama-index-vector-stores-milvus>=0.4
pymilvus>=2.4
opensearch-py>=2.8.0
lark-channel-sdk
lark-oapi
```

### database
```
redis>=5.0
pymysql>=1.1.1
volcengine>=1.0.193
mem0ai>=1.0.0,<2
```

### speech
```
（空列表）
```

### a2ui
```
a2ui-agent-sdk>=0.2.1
```

### pdf
```
（空列表，向后兼容别名）
```

### eval
```
prometheus-client>=0.22.1
deepeval>=3.2.6
google-adk[eval]>=1.34.0
```

### harness
```
headroom
```

### cli
```
（空列表）
```

### dev
```
pre-commit>=4.2.0
pytest>=8.4.1
pytest-asyncio>=1.0.0
pytest-xdist>=3.8.0
```

---

本文件列出了 pyproject.toml 中定义的所有核心依赖和可选依赖分组。核心依赖包含34个直接依赖项，覆盖配置管理、代理架构、模型调用、数据库连接、云服务集成等模块。可选依赖包含10个分组，分别对应 codex、extensions、database、speech、a2ui、pdf、eval、harness、cli、dev 等不同功能场景。所有依赖项及其版本约束均直接从 pyproject.toml 中提取，未进行主观修改。
