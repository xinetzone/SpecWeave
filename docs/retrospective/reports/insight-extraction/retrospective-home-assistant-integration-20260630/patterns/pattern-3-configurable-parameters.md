+++
id = "pattern-3-configurable-parameters"
name = "配置化参数模式"
category = "security"
maturity = "L2"
source = "ha_api.py"
created_at = "2026-06-30"
+++

# 配置化参数模式

## 核心理念

通过环境变量和配置文件管理参数，避免硬编码敏感信息，支持灵活的多环境配置。

## 问题背景

在应用程序中，敏感信息（如 API Token、数据库密码）如果硬编码到代码中，会带来安全风险。同时，不同环境（开发、测试、生产）可能需要不同的配置。配置化参数模式解决了这些问题，通过环境变量和配置文件管理参数。

## 实现方式

### 1. 配置优先级

定义配置优先级，从高到低：

1. 命令行参数（最高优先级）
2. 环境变量
3. .env 文件
4. 默认值（最低优先级）

### 2. 加载配置

```python
def load_config() -> HAConfig:
    config = HAConfig(
        ha_url=os.getenv("HA_URL", ""),
        ha_token=os.getenv("HA_TOKEN", ""),
    )

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key == "HA_URL" and not config.ha_url:
                        config.ha_url = value.strip('"').strip("'")
                    elif key == "HA_TOKEN" and not config.ha_token:
                        config.ha_token = value.strip('"').strip("'")

    return config
```

### 3. 使用配置

```python
config = load_config()
ha_url = args.ha_url or config.ha_url
ha_token = args.ha_token or config.ha_token
```

## 应用场景

- 敏感信息管理
- 多环境配置（开发、测试、生产）
- 容器化部署
- CI/CD 集成

## 核心特点

| 特点 | 说明 |
|------|------|
| **安全** | 避免硬编码敏感信息 |
| **灵活** | 支持多种配置方式 |
| **可扩展** | 易于添加新的配置项 |
| **可维护** | 配置集中管理，便于修改 |

## 安全措施

| 措施 | 说明 |
|------|------|
| **不提交配置文件** | 将 .env 文件添加到 .gitignore |
| **权限控制** | 限制配置文件的访问权限 |
| **加密存储** | 对于敏感配置，使用加密存储 |
| **轮换策略** | 定期轮换敏感凭证 |

## 代码示例

```python
# ha_api.py 中的配置加载

import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class HAConfig:
    ha_url: str = ""
    ha_token: str = ""

def load_config() -> HAConfig:
    config = HAConfig(
        ha_url=os.getenv("HA_URL", ""),
        ha_token=os.getenv("HA_TOKEN", ""),
    )

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key == "HA_URL" and not config.ha_url:
                        config.ha_url = value.strip('"').strip("'")
                    elif key == "HA_TOKEN" and not config.ha_token:
                        config.ha_token = value.strip('"').strip("'")

    return config
```

## .env 文件格式

```bash
# .env 文件示例
HA_URL=http://homeassistant.local:8123
HA_TOKEN=your_long_lived_access_token_here
```

## 最佳实践

1. **不提交配置文件**：将 .env 文件添加到 .gitignore
2. **提供示例文件**：创建 .env.example 文件，展示配置项和格式
3. **优先级清晰**：明确配置优先级，避免混淆
4. **默认值合理**：为非敏感配置项提供合理的默认值
5. **文档说明**：在文档中说明配置方式和优先级

## 适用范围

| 场景 | 是否适用 | 原因 |
|------|---------|------|
| API Token 管理 | ✅ | 避免硬编码敏感信息 |
| 数据库连接配置 | ✅ | 支持多环境配置 |
| 外部服务地址 | ✅ | 灵活配置 |
| 常量定义 | ❌ | 常量应直接定义在代码中 |