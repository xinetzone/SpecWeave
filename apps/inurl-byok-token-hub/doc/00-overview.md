---
id: "inurl-byok-overview"
title: "项目定位与源文档边界"
source: "../README.md"
---
# 项目定位与源文档边界

> 内容迁移自根 README 文首介绍与 §10。

inurl BYOK Token Hub（Python 3.14+ 复刻）是 BYOK 统一令牌枢纽复刻：E2EE 密钥保险库 + 逻辑别名路由 + 本地三协议代理 + 用量计费。

依据 OKF 知识包 [inurl-byok-token-hub（index.md）](../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/products/inurl-byok-token-hub/index.md)（13 份文档、F-001~F-122 事实台账）的规格，用 Python 3.14 复刻 `token.inurl.link` 的 **BYOK（Bring Your Own Key）统一令牌枢纽**：

- 云控制台侧：E2EE 密钥托管库、双 escrow、套餐与人工核销、用量台账、八模块后台；
- 本机侧：OpenAI 兼容本地代理（`http://127.0.0.1:3003/v1`）、逻辑别名路由、19 种策略 + Combo 回退链、5 档提示词压缩、三协议厂商适配、429/5xx 故障切换。

> **这不是原产品的源码移植**。原产品的本地代理是闭源二进制，知识包全程「未注册、未下载、未运行」，本复刻依据文档已描述的能力与边界条件重建，缺失与歧义处按合理默认实现（见 [08-assumptions-and-differences.md](08-assumptions-and-differences.md)「假设与差异说明」）。

## 源文档边界

源知识包 `status: flagged`，核心勘误 E1（免费档仅 3 个厂商密钥，「17 家 Key + 0 元」不成立）、E2（DeepSeek 官方收费）、E5（Agnes 免费档 512K）、E4（百度千帆每模型 100 万 / 3 个月）均已体现在实现中：

- `deepseek` 的 `tier = paid`；
- `agnes` 免费模型 `context_window = 524288`；
- 免费档密钥上限硬校验 3（超限返回 `key_limit_exceeded` 与升级提示）。
