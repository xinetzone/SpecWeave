---
okf_version: "0.2"
---

# PyInvoke Wiki 教程

> Pythonic 的任务执行工具——用纯 Python 定义 CLI 任务，替代 Make 和 Shell 脚本。

本教程基于 **PyInvoke v3.0.3** 源码编写，遵循 OKF v0.2 规范，所有 API 描述均经过源码验证。

## 📖 项目概览

* [项目介绍与定位](overview/intro.md) - PyInvoke 是什么、核心价值、设计哲学、适用场景
* [安装指南](overview/installation.md) - pip 安装、版本要求、安装验证
* [5 分钟快速上手](overview/quickstart.md) - 创建第一个任务、CLI 调用、Python API 调用
* [与同类工具对比](overview/comparison.md) - 与 Make/Fabric/Nox/Tox/Shell Script 的定位差异
* [核心架构总览](overview/architecture.md) - Task→Collection→Parser→Executor→Context→Runner 调用链

## 🧩 核心概念

* [Task 与 @task 装饰器](core-concepts/task.md) - 任务定义、参数规范、Call 对象、pre/post 钩子
* [Collection 与命名空间](core-concepts/collection.md) - 任务集合、命名空间组织、dotted name 查找
* [Context 执行上下文](core-concepts/context.md) - run()/sudo()、cd/prefix 上下文管理器、config 代理、MockContext
* [Runner 命令执行](core-concepts/runner.md) - Runner 抽象基类、Local 实现、Result/Promise、PTY、异步执行
* [Executor 执行器](core-concepts/executor.md) - 任务执行流程、pre/post 展开、去重、call chain
* [Config 配置系统](core-concepts/config.md) - DataProxy、配置层级、配置合并、运行时修改
* [Program CLI 入口](core-concepts/program.md) - CLI 解析流程、core_args、任务发现、--list/--help
* [Parser 参数解析](core-concepts/parser.md) - Argument/ParserContext/ParseResult、短标志、underscore→dash
* [Loader 任务加载](core-concepts/loader.md) - FilesystemLoader、tasks.py 发现、模块加载
* [Watcher 流监控](core-concepts/watcher.md) - StreamWatcher、Responder、FailingResponder、自动应答

## 💻 CLI 参考

* [基本用法](cli/basic-usage.md) - 调用语法、任务指定、多任务执行、默认任务
* [全局选项](cli/global-options.md) - 所有命令行选项详解（--help/--list/--echo/--dry 等）
* [任务参数](cli/task-arguments.md) - 参数传递、位置参数、布尔 flag、iterable/incrementable 值
* [命名空间](cli/namespaces.md) - dotted name 调用、子集合默认任务
* [Shell 补全](cli/completion.md) - Bash/Zsh/Fish 自动补全启用方法

## 🐍 Python API

* [编程式调用](python-api/programmatic-usage.md) - Context().run()、Executor.execute()
* [自定义 Program](python-api/custom-program.md) - Binary 分发、namespace 配置、入口点
* [自定义 Executor](python-api/custom-executor.md) - 继承 Executor 自定义执行策略
* [自定义 Runner](python-api/custom-runner.md) - 继承 Runner/Local 自定义命令执行
* [测试与 Mock](python-api/testing.md) - MockContext、预设 Result、命令匹配模式

## ⚙️ 配置系统

* [配置系统总览](configuration/overview.md) - DataProxy 访问模式、配置入口
* [配置层级](configuration/hierarchy.md) - defaults→system→user→project→env→runtime→overrides 详解
* [配置文件格式](configuration/file-formats.md) - YAML/JSON/Python 配置文件、搜索路径
* [环境变量](configuration/env-vars.md) - INVOKE_* 前缀环境变量映射
* [配置合并规则](configuration/merge-rules.md) - merge_dicts 行为、嵌套键合并、Collection 配置

## 🎯 常用模式

* [任务组织模式](patterns/organizing-tasks.md) - 单文件/包结构/多层 namespace
* [Pre/Post 任务链](patterns/pre-post-tasks.md) - 前置后置任务、call() 参数化、setup/teardown
* [目录与环境管理](patterns/cd-prefix.md) - cd/prefix 上下文管理器、虚拟环境激活
* [Sudo 使用](patterns/sudo.md) - sudo 密码配置、FailingResponder 机制
* [自定义 Watcher](patterns/custom-watchers.md) - StreamWatcher 实现交互式命令自动化
* [错误处理](patterns/error-handling.md) - warn=True、UnexpectedExit、Failure 处理模式
* [并发与异步](patterns/parallel-execution.md) - Promise 异步模式、threading 并发
* [任务测试](patterns/testing-tasks.md) - MockContext 测试策略

## 📑 速查参考

* [API 速查表](reference/api-cheatsheet.md) - 核心类/方法/装饰器/异常速查
* [异常体系](reference/exceptions.md) - 所有异常类清单、触发场景、继承关系
* [CLI 标志速查](reference/cli-flags.md) - 命令行标志速查表
* [配置键速查](reference/config-keys.md) - 所有配置键及默认值

## 🔧 方法论萃取

* [通用提示词模板](references/prompt-template.md) - "开源项目学习→OKF Wiki 教程"通用提示词模板
* [标准工作流](references/workflow.md) - 源码学习→Bundle骨架→概念文档→验证→萃取 的标准工作流
* [类型体系定义](references/type-system.md) - 本 Bundle 使用的 type 值定义

## 🔗 相关资源

* [🏠 返回上级：工具与库](../README.md)
* [📚 知识库首页](../../../../README.md)
* [PyInvoke 官方文档](https://docs.pyinvoke.org/)
* [PyInvoke GitHub](https://github.com/pyinvoke/invoke)
