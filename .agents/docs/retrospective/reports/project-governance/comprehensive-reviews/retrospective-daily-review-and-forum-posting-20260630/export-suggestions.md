---
id: "retrospective-daily-review-and-forum-posting-20260630-export"
title: "导出建议"
source: "execution-retrospective.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-daily-review-and-forum-posting-20260630/export-suggestions.toml"
---
# 导出建议

## 一、改进建议（按优先级排序）

### P0 - 立即改进

| # | 建议 | 责任人 | 预期收益 |
|---|------|--------|---------|
| 1 | 在forum-posting SKILL.md中补充Ember/Discourse composer的框架感知操作模式（nativeSetter设值+事件链触发） | developer | 避免未来DOM直接设值失败 |
| 2 | 在SKILL.md中补充同名按钮消歧策略（枚举→排除→父容器验证） | developer | 减少点错按钮的试错成本 |
| 3 | 更新forum-bot.py或MCP操作指南，添加提交后多信号验证步骤 | developer | 避免"提交了但没看到"的重复操作 |

### P1 - 短期优化

| # | 建议 | 责任人 | 预期收益 |
|---|------|--------|---------|
| 4 | 萃取SPA框架感知textarea设值为可复用JS工具函数，存入scripts/lib/ | developer | 跨项目复用，其他SPA场景也适用 |
| 5 | 在MCP浏览器操作中建立"先诊断再操作"原则：操作按钮前先用evaluate枚举所有候选 | developer | 降低确认偏误导致的误操作 |
| 6 | 提交后等待时间标准化（至少3秒），并通过URL/DOM数量/页面高度三重验证 | developer | 提高异步操作验证可靠性 |

### P2 - 中期建设

| # | 建议 | 责任人 | 预期收益 |
|---|------|--------|---------|
| 7 | 建立SPA自动化操作模式库，覆盖React/Vue/Ember等主流框架的表单交互模式 | architect | 系统性解决SPA自动化难题 |
| 8 | 考虑在context recovery后自动重新验证中间状态（而非信任summary中的状态描述） | developer | 降低上下文压缩带来的状态丢失风险 |

## 二、模式萃取建议

### 建议入库的新模式

| 模式名称 | 建议分类 | 成熟度 | 说明 |
|---------|---------|--------|------|
| SPA框架感知textarea设值 | tools-automation/ | L2 | nativeSetter+事件链，解决框架双向绑定绕过问题 |
| 同名按钮消歧策略 | tools-automation/ | L2 | 枚举→排除→父容器验证三步法 |
| 异步操作多信号验证 | tools-automation/ | L2 | URL+DOM数量+页面高度+内容四重验证 |

### 建议更新的已有模式

| 模式 | 更新内容 |
|------|---------|
| forum-bot.py/MCP双方案模式 | 补充"双方案不仅是功能互补，更是调试能力互补"的洞察 |
| 前置诊断高ROI | 增加"10秒枚举节省15分钟返工"的实证案例 |

## 三、经验教训总结

### 做对的事

1. **切换方案果断**：forum-bot.py失败后，没有花大量时间调试Playwright脚本，而是直接切换到MCP方案
2. **诊断系统化**：失败后通过browser_evaluate检查DOM状态，而非盲目重试
3. **多信号验证**：最终通过URL变化、页面高度增加、"刚刚发布"文本、截图四层验证确认成功
4. **JS灵活操作**：充分利用browser_evaluate执行JS，绕过单纯click/type的限制

### 需要改进的事

1. **操作前未充分枚举**：按钮选择时急于点击，没有先列出所有候选进行分析
2. **框架知识缺失**：对Ember composer的双向绑定机制不了解，导致DOM设值方式过于简单
3. **验证时机过早**：提交后立即刷新，没有等待异步操作完成
4. **重复错误模式**：前两次点错按钮后，没有停下来系统性分析为什么错，导致第三次才找到正确按钮

### 下次执行类似任务时

1. 操作按钮前先 `Array.from(querySelectorAll).map(b=>({text,classes,rect}))` 枚举所有候选
2. 对SPA框架的表单输入，默认使用nativeSetter+事件链方式，而非直接设value
3. 提交/点击后等待3-5秒，观察URL/DOM/高度变化再判断结果
4. 失败两次后必须停下来系统性诊断，禁止继续盲目重试
