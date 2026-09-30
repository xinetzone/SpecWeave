# inurl BYOK Token Hub（Python 3.14+ 复刻）

BYOK 统一令牌枢纽复刻：E2EE 密钥保险库 + 逻辑别名路由 + 本地三协议代理 + 用量计费。

依据 OKF 知识包 `projects/awesome-okf-xs/doc/bundles/jishu/ai/products/inurl-byok-token-hub/`（13 份文档、F-001~F-122 事实台账）的规格，用 Python 3.14 复刻 `token.inurl.link` 的 **BYOK（Bring Your Own Key）统一令牌枢纽**：

- 云控制台侧：E2EE 密钥托管库、双 escrow、套餐与人工核销、用量台账、八模块后台；
- 本机侧：OpenAI 兼容本地代理（`http://127.0.0.1:3003/v1`）、逻辑别名路由、19 种策略 + Combo 回退链、5 档提示词压缩、三协议厂商适配、429/5xx 故障切换。

> **这不是原产品的源码移植**。原产品的本地代理是闭源二进制，知识包全程「未注册、未下载、未运行」，本复刻依据文档已描述的能力与边界条件重建，缺失与歧义处按合理默认实现（见 [doc/08-assumptions-and-differences.md](doc/08-assumptions-and-differences.md)）。

## 快速开始

```bash
# 本机默认 python 为 3.13.12，不满足 requires-python >= 3.14，须显式走 py314
conda activate py314
cd apps/inurl-byok-token-hub

# 安装（scikit-build-core 后端，纯 Python）
pip install -e ".[dev]"

# 端到端冒烟：全 mock、零真实密钥
PYTHONPATH=src python -m inurl_byok_token_hub smoke

# 启动本地代理 + 控制台
python -m inurl_byok_token_hub serve
# → http://127.0.0.1:3003/v1   控制台 http://127.0.0.1:3003/console/login
```

## 文档

完整文档已原子化至 [doc/](doc/README.md)（索引 + 10 篇，按主题单一职责拆分）：

| 文档 | 主题 |
|---|---|
| [doc/00-overview.md](doc/00-overview.md) | 项目定位、复刻边界声明、源知识包与勘误落地 |
| [doc/01-quickstart.md](doc/01-quickstart.md) | 安装、冒烟、启动与全部 CLI 子命令 |
| [doc/02-architecture.md](doc/02-architecture.md) | 分层架构、目录职责与分层约束 |
| [doc/03-configuration.md](doc/03-configuration.md) | 环境变量与配置覆盖链 |
| [doc/04-api-reference.md](doc/04-api-reference.md) | 五组 HTTP 接口清单 |
| [doc/05-auth-and-errors.md](doc/05-auth-and-errors.md) | 鉴权与错误语义（401/403） |
| [doc/06-data-model.md](doc/06-data-model.md) | 核心数据模型要点 |
| [doc/07-testing-and-build.md](doc/07-testing-and-build.md) | 测试命令、覆盖率与构建后端 |
| [doc/08-assumptions-and-differences.md](doc/08-assumptions-and-differences.md) | A1–A24 假设与差异说明 |
| [doc/09-security-boundaries.md](doc/09-security-boundaries.md) | 安全边界六条（必读） |
