# Hermes Conda 环境创建与源码安装 - Verification Checklist

## 环境创建验证
- [x] Checkpoint 1: conda 可通过完整路径正常执行，`conda --version` 输出有效版本号（conda 26.1.1）
- [x] Checkpoint 2: `hermes` conda 环境已成功创建，`conda env list` 中可见
- [x] Checkpoint 3: 环境中 Python 版本为 3.13.x（3.13.14，满足 >=3.11,<3.14，且为 hermes type-check 目标版本）
- [x] Checkpoint 4: 环境中 pip 可用（pip 26.1.2）

## 安装验证
- [x] Checkpoint 5: `pip install -e ".[web,mcp]"` 执行成功，exit code 为 0
- [x] Checkpoint 6: `pip show hermes-agent` 显示版本 0.20.0，安装模式为 editable（Editable project location 指向源码目录）
- [x] Checkpoint 7: 核心依赖已安装：fastapi 0.133.1、uvicorn、mcp 1.28.1、pydantic 2.13.4、openai 2.24.0、httpx、rich、websockets
- [x] Checkpoint 8: Windows 特有依赖已安装：pywin32 311、pywinpty、tzdata、concurrent-log-handler、psutil
- [x] Checkpoint 9: 无残留的 Python 3.14 兼容性错误（pydantic-core 2.46.4 cp313 wheel 已安装）

## 功能验证
- [x] Checkpoint 10: `hermes --version` 输出 Hermes Agent v0.20.0 (2026.8.3)，无 ImportError
- [x] Checkpoint 11: `hermes --help` 正常输出帮助信息，列出 model、setup、config、doctor、dashboard、serve 等 80+ 子命令
- [x] Checkpoint 12: `python -c "from hermes_cli.main import main"` 输出 import ok，无报错
- [x] Checkpoint 13: `hermes doctor` 可启动无 ImportError 崩溃（无配置时等待交互为预期行为）

## 收尾验证
- [x] Checkpoint 14: 输出清晰的环境使用说明（激活命令、首次配置、启动方式）
- [x] Checkpoint 15: doctor 测试进程已终止，无遗留错误进程
