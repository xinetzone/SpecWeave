---
id: "doocs-md-py-rule-uploaders-dual-path"
title: "图床双路径辨识与签名纪律"
source: "../../AGENTS.md#P0 约束速览"
---

# 图床双路径辨识与签名纪律

> **适用范围**：修改任何"上传"相关代码（**先读本节 §1 辨识路径**）、改图床清单、改签名算法、改凭证来源。
> **权威事实源**：[../../src/doocs_md_py/uploaders/base.py](../../src/doocs_md_py/uploaders/base.py)（provider 注册表与公共基础设施，**图床数量以本文件为准**）、`server/upload_*.py`（服务端上传后端）、`tests/golden/*`（签名测试向量）。

## §1 两套上传路径辨识（**极易踩坑**）

本应用存在**两套相互独立**的上传实现，名字近似但职责完全不同：

| 维度 | 服务端上传后端 | Web 客户端图床 |
|------|--------------|---------------|
| 落点 | `server/upload_config.py`、`server/upload_filename.py`、`server/upload_github.py`、`server/upload_r2.py`、`server/upload_rate.py`、`server/routers/upload.py` | `uploaders/*.py` |
| 上游对应 | `apps/api/src/upload-*.ts` 与 `/upload` 端点 | 上游 Web 端 `apps/web` 的图床清单 |
| 调用方 | **HTTP 客户端**调服务端 `/upload` 接口 | **浏览器端**上传通道（由前端调用其逻辑等价物） |
| 关注点 | 门控、MIME/大小校验、限流、对象键、S3/GitHub 后端 | provider 协议、签名算法、凭证来源层级 |
| 规则文件 | [server-api-and-security.md](server-api-and-security.md) §6 | **本文 §2–§6** |

**判定口诀**：改动前先问"这段代码是被 HTTP 客户端经 `/upload` 调用，还是被 Web 端调用？"。**禁止**把两套路径混用、互相调用或合并 —— 上游本就是两套，合并即契约破坏。

## §2 Web 图床契约与 provider 注册表

- Web 图床的上游契约来自前端 `providers.ts` 的 provider 协议；本仓以 `uploaders/*.py` 复刻。
- **provider 注册表为唯一权威**：provider 名称、数量、启用条件一律以 [../../src/doocs_md_py/uploaders/base.py](../../src/doocs_md_py/uploaders/base.py) 的注册表为准。**禁止**在文档或代码中硬编码图床数量 —— 数量口径不一致时必须回到注册表裁决。
- 公共基础设施（HTTP 请求构造、公共字段拼装、错误归一）集中在 `base.py`；**各 provider 模块只实现差异部分**，不得重复实现公共逻辑（参见 SpecWeave 共享库纪律）。

## §3 签名算法手写纪律

- 所有图床签名（S3 SigV4、七牛、又拍云等）**一律使用标准库手写**（`hmac` / `hashlib` / `base64` / `urllib`）；**禁止**引入 `boto3`、`cryptography` 或各家 SDK。
- **必须配套已知答案测试向量**：向量以 JSON 落在 `tests/golden/`（如 `uploader_signature_vectors.json`、`s3_presign_vectors.json`、`sigv4_vectors.json`），由 `scripts/uploader_sig_regen.py` / `s3_presign_regen.py` / `sigv4_vectors_regen.py` 再生成。
- **再生成纪律**：向量由脚本从**已对拍上游的算法**生成；**禁止**手工改向量来迁就实现。实现与向量不符时，判定"实现错"还是"上游口径变更"，前者改实现，后者走差异登记。
- 签名算法**不得"顺手重构"**：任何等价改写都必须保持向量全绿；无向量的签名路径视为未验证。

## §4 凭证来源层级与零内置

- 凭证来源按优先级：**显式参数 → 环境变量 → 用户配置文件**。**零内置**：代码中不得出现任何官方/示例凭证（token、secret、accessKey、bucket 名）。
- 未提供凭证时，对应 provider **优雅降级**（标记为未启用 / 返回可读错误），**不得**崩溃或回退到内置值。
- 凭证**不得写入日志**；错误消息里涉及凭证的字段需脱敏。
- 用户级配置文件由 `src/doocs_md_py/user_config.py` 读取（见 `tests/test_user_config.py`）。

## §5 图床数量口径与差异登记

- 已知口径分歧（**历史事实，必须按本节处置而非择一**）：spec 侧曾记"13 个上传器 / 12 种非 `formCustom`"，而应用 README 与 [../../docs/architecture.md](../../docs/architecture.md) 记"14 家图床"。
- **裁决规则**：数量与清单**一律以 `uploaders/base.py` 注册表为准**。若注册表与任一处文档不一致，则：
  1. 以注册表修正文档；
  2. 若差异属于"复刻口径"问题（如某 provider 是否有上游对应），在 [../../docs/contract-differences.md](../../docs/contract-differences.md) 登记 `CD-` 编号并说明裁决；
  3. **禁止**在文档里保留两套互相矛盾的数字。

## §6 `formCustom` 边界

- `formCustom` provider 允许用户自定义上传表单（URL / 字段 / 请求方式），但**不执行用户提供的 JS**——该能力属于 NG2（浏览器运行时能力），**已冻结**。
- 实现上须以**声明式数据**驱动（配置字段 + 固定请求模板），**禁止**引入 `eval` / `exec` 或任意代码执行路径。
- 若上游 `formCustom` 语义超出声明式边界，按"规格裁剪"处理并登记 `CD-`。

## §7 反模式（出现即打回）

| # | 反模式 | 后果 |
|---|--------|------|
| A1 | 把服务端 `/upload` 后端与 `uploaders/*` 混用或互相调用 | 两套契约污染，上游对齐失效 |
| A2 | 引入 `boto3` / 各家 SDK / `cryptography` 做签名 | 违反依赖白名单 |
| A3 | 签名改写后未跑测试向量，或手改向量迁就实现 | 未验证的签名 = 隐患 |
| A4 | 代码中内置凭证或示例 bucket/token | 凭证泄露 |
| A5 | 文档硬编码图床数量，与注册表不一致 | 事实源分裂 |
| A6 | 为 `formCustom` 引入 `eval`/`exec` | 违反 NG2，安全风险 |
| A7 | useful in 各 provider 重复实现公共 HTTP/错误逻辑 | 违反共享库纪律 |

## 变更纪律

- 本文档只增不删；provider 清单、签名算法、凭证层级三者变更须同步 [../../docs/architecture.md](../../docs/architecture.md) §五、[../../README.md](../../README.md) 图床章节与测试向量，最后记 [../CHANGELOG.md](../CHANGELOG.md)。
