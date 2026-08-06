---
id: "thin-wrapper-pattern"
title: "薄包装模式"
type: "code"
date: "2026-08-02"
maturity: "L2-validated"
source: "retrospective-nativebuild-automation-20260802"
related_patterns: ["configurable-by-default-principle", "cmake-four-layer-modular-architecture"]
tags: ["powershell", "code-reuse", "wrapper", "dry", "build-scripts", "parameterization"]
validation_count: 2
reuse_count: 4
---

# 薄包装模式

## 触发场景
- 当通用构建/部署脚本需要适配多个相似但各有差异的项目（不同项目名、Python版本要求、构建类型、配置参数）时
- 适用于：多项目构建脚本、多环境部署脚本、相似工具链配置、按项目定制的通用工具入口
- 不适用于：项目间差异极大、无公共逻辑可抽取的场景、单项目一次性脚本

## 核心做法
1. **通用核心抽取**：将所有公共逻辑（环境发现、DevShell加载、CMake构建、安装验证、日志输出）抽取到一个参数化的通用脚本（如build_native_ext.ps1），所有可配置项通过参数传入
2. **薄包装层**：每个项目一个极薄（约10-20行）的包装脚本，仅做两件事：
   - 定义项目特定的默认参数（项目名、Conda环境名、VS路径、架构、构建类型）
   - 调用通用脚本并透传所有参数
3. **参数透传**：未知参数通过splatting（PowerShell的`@Args`或Python的`**kwargs`）透传给通用脚本，支持`-VerboseBuild`、`-Clean`、`-SkipVerify`等通用开关
4. **共享模块层**：将可复用的工具函数放在模块文件（如.psm1、.py模块）中，通用脚本和薄包装脚本共享同一套函数实现
5. **约定优于配置**：薄包装脚本的命名遵循约定（如build_<project-name>.ps1），便于批量操作和发现

## 反模式（不要这么做）
- ❌ 每个项目复制粘贴完整构建脚本（代码重复率>90%）：修改一处逻辑需要同步修改N个副本，极易遗漏导致不一致
- ❌ 薄包装层包含业务逻辑：包装层应该只做参数映射，任何条件判断、流程控制都应该放在通用核心中
- ❌ 参数不透传：每个新的通用开关都要在所有薄包装中添加一遍，维护成本随项目数线性增长
- ❌ 没有共享模块：工具函数在每个通用脚本中重复定义，同样的Bug要修N次
- ❌ 薄包装太厚：超过50行的包装脚本说明抽象不够，公共逻辑没有完全抽到核心中

## 检验标准
做完之后怎么知道做对了？
- 标准1：薄包装脚本长度在10-20行之间，不包含任何流程控制（if/for/while）或业务逻辑
- 标准2：通用脚本修改一次，所有项目立即生效，无需修改任何薄包装
- 标准3：新增项目只需创建一个新的薄包装脚本（复制现有包装改3-5个参数），5分钟内完成
- 标准4：所有通用参数（如-Clean、-Verbose）在所有项目上都可用，无需逐个适配
- 标准5：工具函数修改一次，所有调用方自动获得修复，无重复定义

## 迁移示例
这个模式还能用在什么其他场景？
- 场景1（微服务部署）：通用deploy.sh脚本 + 每个服务的deploy-<service>.sh薄包装（指定镜像名、端口、副本数）
- 场景2（CI/CD流水线）：通用CI模板 + 每个项目的小配置文件（指定语言、构建命令、测试命令）
- 场景3（CLI工具）：通用命令框架 + 子命令薄包装（每个子命令只定义参数和帮助信息）
- 场景4（非技术场景-餐饮）：通用炒菜流程（热锅→放油→下调料→翻炒→出锅）+ 每道菜的菜谱卡片（只写菜名、食材、火候、时间）
- 场景5（非技术场景-邮件）：通用邮件模板（称呼→正文结构→落款）+ 每封邮件只填具体内容（收件人、具体事项）

## 参考实现
- PowerShell实现：
  - 通用核心：[build_native_ext.ps1](file:///d:/spaces/SpecWeave/.agents/scripts/build_native_ext.ps1)（~230行，6阶段构建流程）
  - 薄包装示例：[build_caffe_ffi.ps1](file:///d:/spaces/SpecWeave/.agents/scripts/build_caffe_ffi.ps1)（~15行）、build_npu_ffi.ps1、build_demo_ffi.ps1、build_xuan_ext_demo.ps1
  - 共享模块：[NativeBuild.psm1](file:///d:/spaces/SpecWeave/.agents/scripts/lib/NativeBuild.psm1)
- 验证案例：4个C++扩展项目均使用约15行薄包装适配同一个通用构建器
