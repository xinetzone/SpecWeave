---
id: "tuyaopen-pattern-4-config-driven"
title: "模式 4：编译时配置 + 运行时配置（配置驱动）"
source: "insight-extraction.md#模式-4编译时配置-运行时配置配置驱动"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-analysis-20260630/patterns/pattern-4-compile-runtime-config-driver.toml"
---
# 模式 4：编译时配置 + 运行时配置（配置驱动）

**模式名称**：编译时配置 + 运行时配置

**核心理念**：
> 通过编译时配置（Kconfig）裁剪功能，运行时配置（CLI）调整参数，实现灵活的功能组合。

**适用场景**：
- 嵌入式系统功能裁剪
- 需要支持多种硬件配置
- 需要用户自定义参数

**实现步骤**：

```markdown
1. **编译时配置 (Kconfig)**
   - 定义配置项：平台选择、功能模块开关
   - 菜单配置：tos.py config menu
   - 默认配置：app_default.config

2. **运行时配置 (CLI)**
   - 定义 CLI 命令：set_model_provider, set_wifi, set_channel_mode
   - 配置持久化：KV 存储（tal_kv）
   - 配置优先级：CLI > 编译配置 > 错误

3. **配置验证**
   - 参数校验：类型检查、范围检查
   - 必需参数检查：缺失时报错
   - 配置回退：无效配置使用默认值

4. **配置更新**
   - 动态更新：部分参数支持热更新
   - 重启生效：核心参数需要重启
   - OTA 更新：远程配置推送
```

**关键文件示例**：
- `boards/<platform>/Kconfig`：平台配置
- `src/<module>/Kconfig`：模块配置
- `cli/serial_cli.c`：运行时 CLI
- `tal_kv/`：配置存储

**效果验证**：
- 功能裁剪精确，固件体积可控
- 运行时配置灵活，无需重新编译
- 配置错误率 < 5%

**局限性**：
- Kconfig 语法复杂，学习成本高
- 配置项过多时管理困难
- 部分配置需要重启生效

**可复用场景**：
- 嵌入式系统功能裁剪
- 需要支持多种硬件配置的项目
- 需要用户自定义参数的应用

---

**[返回洞察萃取索引](../insight-extraction.md)**