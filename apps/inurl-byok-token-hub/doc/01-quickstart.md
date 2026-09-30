---
id: "inurl-byok-quickstart"
title: "快速开始"
source: "../README.md"
---
# 快速开始

> 内容迁移自根 README §1。

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

## 其他子命令

```bash
python -m inurl_byok_token_hub catalog --capability text   # 目录统计与条目
python -m inurl_byok_token_hub strategies                  # 19 种策略
python -m inurl_byok_token_hub route inurl --combo "latency_first>round_robin"
python -m inurl_byok_token_hub compress ultra --text "..."
python -m inurl_byok_token_hub vault add --provider zhipu --api-key sk-xxx --password <口令> --user <user_id>
python -m inurl_byok_token_hub launcher                    # 启动器说明（含供应链差异）
```

启动器「只生成说明，不下载、不内嵌密钥」的供应链差异见 [08-assumptions-and-differences.md](08-assumptions-and-differences.md) A7。
