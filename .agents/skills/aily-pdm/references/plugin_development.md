# PDM插件开发指南

## 插件概述

PDM采用插件化设计，通过入口点（entry points）发现和加载插件。

## 快速开始

### 1. 创建插件项目

```toml
# pyproject.toml
[project]
name = "pdm-my-plugin"
version = "0.1.0"
dependencies = ["pdm"]

[project.entry-points.pdm]
my_plugin = "my_plugin:activate"
```

### 2. 安装为开发插件

```bash
# 在pyproject.toml中添加
[tool.pdm]
plugins = [
    "-e file:///${PROJECT_ROOT}"
]

# 安装
pdm install --plugins
```

## 命令扩展

### 创建自定义命令

```python
from pdm.cli.commands.base import BaseCommand

class HelloCommand(BaseCommand):
    """向指定的人打招呼。"""

    def add_arguments(self, parser):
        parser.add_argument("-n", "--name", help="要问候的人的姓名")

    def handle(self, project, options):
        name = options.name or project.config.get("hello.name", "World")
        print(f"Hello, {name}!")
```

### 注册命令

```python
def activate(core):
    core.register_command(HelloCommand, "hello")
```

### 发布入口点

```toml
[project.entry-points.pdm]
hello = "my_plugin:activate"
```

## 配置项扩展

### 创建配置项

```python
from pdm.project.config import ConfigItem

def activate(core):
    # 注册配置项
    core.add_config(
        "hello.name",
        ConfigItem(
            description="默认问候名称",
            default="World",
            global_only=False,
            env_var="HELLO_NAME"
        )
    )
```

### ConfigItem参数

| 参数 | 类型 | 说明 |
|------|------|------|
| description | str | 配置项描述 |
| default | Any | 默认值 |
| global_only | bool | 是否仅全局配置 |
| env_var | str | 环境变量名 |

## 信号系统

### 监听信号

```python
from pdm.core import signals

def on_post_init(sender, project, **kwargs):
    print(f"项目已初始化: {project.root}")

# 连接到信号
signals.post_init.connect(on_post_init)
```

### 可用信号

| 信号 | 说明 | 参数 |
|------|------|------|
| pre_init | 初始化前 | project |
| post_init | 初始化后 | project |
| pre_lock | 锁定前 | resolution, hooks |
| post_lock | 锁定后 | resolution |
| pre_install | 安装前 | candidates, wet_run |
| post_install | 安装后 | candidates |
| pre_build | 构建前 | artifact |
| post_build | 构建后 | artifact |

## 完整示例

```python
"""
pdm-hello: 一个简单的PDM插件示例
"""

from pdm.cli.commands.base import BaseCommand
from pdm.core import signals
from pdm.project.config import ConfigItem


class HelloCommand(BaseCommand):
    """向指定的人打招呼。"""

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--name",
            help="要问候的人的姓名"
        )
        parser.add_argument(
            "-u", "--uppercase",
            action="store_true",
            help="使用大写字母"
        )

    def handle(self, project, options):
        name = options.name or project.config.get("hello.name", "World")
        message = f"Hello, {name}!"
        
        if options.uppercase:
            message = message.upper()
        
        print(message)


def activate(core):
    """激活插件。"""
    # 注册命令
    core.register_command(HelloCommand, "hello")
    
    # 添加配置项
    core.add_config(
        "hello.name",
        ConfigItem(
            description="默认问候名称",
            default="World"
        )
    )
    
    # 连接信号
    signals.post_init.connect(on_post_init)


def on_post_init(sender, project, **kwargs):
    """项目初始化后的钩子。"""
    # 可以在这里执行初始化任务
    pass
```

## pyproject.toml配置

```toml
[project]
name = "pdm-hello"
version = "0.1.0"
description = "PDM打招呼插件"
requires-python = ">=3.9"
dependencies = ["pdm>=2.0.0"]

[project.entry-points.pdm]
hello = "pdm_hello:activate"

[tool.pdm]
plugins = ["-e ."]
```

## 测试插件

### 使用pytest fixtures

```python
# conftest.py
import pytest
from pdm.pytest import PDM_RUN_LOCAL

@pytest.fixture(scope="package")
def pdm():
    return PDM_RUN_LOCAL
```

### 测试命令

```python
def test_hello_command(pdm):
    result = pdm(["hello", "-n", "Test"])
    assert result.exit_code == 0
    assert "Hello, Test!" in result.output
```

### 安装测试依赖

```bash
pdm add -dG test pytest pytest-cov
pdm add -dG test pdm[pytest]
```

## 发布插件

### 打包配置

```toml
# 使用pdm-backend
[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
```

### 发布到PyPI

```bash
pdm build
pdm publish
```

## 常用插件参考

### 官方插件

- [pdm-packer](https://github.com/pdm-project/pdm-packer) - 打包插件
- [pdm-bump](https://github.com/pdm-project/pdm-bump) - 版本号更新

### 社区插件

查看 [Awesome PDM](https://github.com/pdm-project/awesome-pdm)

## 调试技巧

### 启用调试模式

```bash
PDM_DEBUG=1 pdm <command>
```

### 查看日志

```bash
pdm -vv <command>
```

### 插件列表

```bash
pdm plugin list
# 或
pdm self list --plugins
```

## 最佳实践

1. **遵循PEP 621** - 使用标准项目元数据
2. **良好的错误处理** - 提供有意义的错误信息
3. **文档完善** - 编写清晰的README和使用示例
4. **版本兼容性** - 声明支持的PDM版本范围
5. **测试覆盖** - 编写单元测试和集成测试
