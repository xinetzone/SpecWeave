---
id: "inurl-byok-testing-and-build"
title: "测试与构建"
source: "../README.md"
---
# 测试与构建

> 内容迁移自根 README §7。

```bash
conda run -n py314 python -m pytest -q --cov=inurl_byok_token_hub
conda run -n py314 python -m ruff check .
```

- 覆盖：整体 **87.6%**（170 项测试全通过；阈值：整体 ≥80%、关键模块 ≥90%）
- 关键模块：crypto **100%** / compression **96%** / vault **95%** / token_service **94%** / router **92%** / billing **92%** / providers **91~95%** / api/deps **100%**
- CLI 冒烟已纳入 pytest（[tests/test_cli.py](../tests/test_cli.py)），不再是「只有人工跑过」的证据
- 构建后端：**scikit-build-core**（`apps/*` Python 子项目的仓库默认；`apps/agent-monetize` 的 setuptools 属历史违规，不可作为先例）
- 新增测试须保持：无 `from __future__` 导入、无令牌/密钥字面量、无 file 协议本地绝对路径（[tests/test_audit.py](../tests/test_audit.py) 静态门禁会自动拦截）
- 覆盖率口径：本机 `conda run -n py314 python -m pytest -q --cov=inurl_byok_token_hub`
