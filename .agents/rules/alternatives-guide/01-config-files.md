---
id: "rules-alt-config-files"
title: "01 配置文件管理"
source: "alternatives-guide.md#config-files"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/01-config-files.toml"
---
# 01 配置文件管理


## 适用场景

配置参数（`HARD-CFG`）、URL/端点（`HARD-URL`）、功能开关、阈值参数、第三方服务配置。

## 实施步骤

1. 在项目 `config/` 目录下创建配置文件，推荐使用 YAML 格式（可读性优于 JSON，生态成熟）。
2. 定义配置结构，按模块或功能域分层组织，每层对应一个配置节。
3. 编写配置加载器，负责读取解析配置文件并合并多层级源。
4. 实现环境变量覆盖机制，优先级为：**环境变量 > 配置文件 > 默认值**。
5. 在代码中仅通过配置加载器获取配置，杜绝直接字面量。

## 示例代码

**`config/default.yaml`**

```yaml
# 服务配置
server:
  host: "0.0.0.0"
  port: 8080
  debug: false

# 数据库配置
database:
  driver: "postgresql"
  host: "localhost"
  port: 5432
  name: "app_db"
  pool:
    min_size: 5
    max_size: 20
    timeout_ms: 30000

# 第三方服务
services:
  payment:
    base_url: "https://api.payment.example.com"
    timeout_ms: 10000
    retry: 3

# 功能开关
features:
  new_checkout_flow: false
  experimental_search: false
```

**`config/config_loader.py`**

```python
"""配置加载器：支持 YAML 配置文件读取与环境变量覆盖。"""

import os
import yaml
from typing import Any


class ConfigLoader:
    """读取配置文件并以环境变量覆盖对应值。

    环境变量命名规范：APP_<SECTION>_<KEY>
    示例：APP_DATABASE_HOST=prod-db.example.com
    分隔符 `.` 替换为 `_`，全大写。
    """

    def __init__(self, config_dir: str = "config", env: str | None = None):
        self.config_dir = config_dir
        self.env = env or os.getenv("APP_ENV", "development")
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        # 1. 加载默认配置
        default_path = os.path.join(self.config_dir, "default.yaml")
        with open(default_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f) or {}

        # 2. 合并环境特定配置（可选）
        env_path = os.path.join(self.config_dir, f"{self.env}.yaml")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                env_data = yaml.safe_load(f) or {}
                self._deep_merge(self._data, env_data)

        # 3. 环境变量覆盖（最高优先级）
        self._apply_env_overrides(self._data)

    def _apply_env_overrides(self, data: dict, prefix: str = "APP") -> None:
        """递归遍历配置字典，以 APP_SECTION_KEY 覆盖对应值。"""
        for key, value in data.items():
            env_key = f"{prefix}_{key.upper()}"
            if isinstance(value, dict):
                self._apply_env_overrides(value, prefix=env_key)
            else:
                if env_key in os.environ:
                    raw = os.environ[env_key]
                    # 尝试类型转换（保持与 YAML 解析值的类型一致）
                    data[key] = self._coerce(raw, value)

    @staticmethod
    def _coerce(raw: str, reference: Any) -> Any:
        """根据参考值类型对环境变量字符串做类型转换。"""
        if isinstance(reference, bool):
            return raw.lower() in ("true", "1", "yes")
        if isinstance(reference, int):
            return int(raw)
        if isinstance(reference, float):
            return float(raw)
        return raw

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> None:
        """深度合并字典，override 中的值覆盖 base 中的同名字段。"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ConfigLoader._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """通过点分隔路径获取配置值。"""
        keys = key_path.split(".")
        node = self._data
        for k in keys:
            if isinstance(node, dict):
                node = node.get(k)
                if node is None:
                    return default
            else:
                return default
        return node

    @property
    def data(self) -> dict[str, Any]:
        """返回完整的配置字典（只读）。"""
        return dict(self._data)


# 全局单例
config = ConfigLoader()
```

**使用示例**

```python
from config.config_loader import config

# 原有硬编码写法（禁止）：
#   timeout = 10
#   db_url = "postgresql://localhost:5432/app_db"

# 推荐写法：
timeout = config.get("services.payment.timeout_ms", default=10000)
db_host = config.get("database.host")
debug = config.get("server.debug", default=False)

if config.get("features.new_checkout_flow"):
    use_new_checkout()
```
---

## 相关模式

- [硬编码治理](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

**[返回索引](../alternatives-guide.md)** | 下一章: [02 环境变量](02-env-vars.md) →
