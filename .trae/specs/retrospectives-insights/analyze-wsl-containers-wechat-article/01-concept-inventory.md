---
id: "01-concept-inventory"
title: "R阶段：WSL Containers文章专业技术概念清单"
source: "article-content.md"
type: "concept-inventory"
phase: "R-Retrospective-事实采集"
created_at: 2026-07-13
concept_count: 40
---

# 01 - 专业技术概念清单（R阶段·事实采集）

> **R阶段原则**：纯客观事实提取，无因果推断词，无评价判断。

| 序号 | 术语名称 | 出现章节 | 原文行号范围 | 原文表述摘录 | 概念分类 |
|------|---------|---------|-------------|------------|---------|
| 1 | WSL Containers | 引言、一、二、三、四、五、六、七、八、总结 | 22, 28-39, 44, 60, 95, 134, 138-156, 170, 178, 190, 200-202 | "WSL Containers正式开放公开预览"、"WSL内置了一个原生、企业级、语法仿Docker的Linux容器运行时"、"WSL Containers = 一个内置在WSL里的、企业就绪的Linux容器解决方案" | 核心 |
| 2 | wslc.exe | 二、三、四、五、八 | 46-48, 89, 95, 106-134, 155, 202 | "wslc.exe —— 命令行工具（重点）"、"更新WSL后，这个二进制会自动加到PATH里"、"它的命令语法和Docker高度相似" | 核心 |
| 3 | container.exe别名 | 二 | 48 | "微软还贴心给了个别名container.exe" | 核心 |
| 4 | WSL Container API | 二、五 | 50-54, 147 | "WSL Container API —— 给程序员的'容器遥控器'"、"以NuGet包形式分发，支持C/C++/C#"、"每个调用API的应用有独立轻量VM（Hyper-V）" | 核心 |
| 5 | OCI容器镜像 | 一 | 38 | "它跑的是标准的OCI容器镜像——也就是你今天从Docker Hub拉的那些ubuntu、nginx、nvidia/cuda" | 核心 |
| 6 | Hyper-V | 一、五、八 | 38, 147, 194 | "底层是在Hyper-V轻量虚拟机上跑Linux容器"、"每个调用API的应用有独立轻量VM（Hyper-V）"、"它要求Windows 11（Hyper-V依赖）" | 核心 |
| 7 | WSL 2 | 一、六、总结 | 32, 38, 170, 200 | "不是WSL 2的继任者，而是基于现有WSL 2基础设施之上的一层新功能"、"wslc直接复用WSL 2已有的内核" | 核心 |
| 8 | NuGet包 | 二 | 52 | "以NuGet包形式分发，支持C/C++/C#" | 核心 |
| 9 | Docker Compose | 五、八 | 150, 155, 190 | "Docker Compose：首发暂不支持"、"重度依赖Compose编排、喜欢图形界面的团队，Docker Desktop还得留着"、"没有Docker Compose：多容器编排（compose.yml）目前不支持" | 核心 |
| 10 | CDI | 五 | 149 | "GPU支持：支持（CDI方式）" | 核心 |
| 11 | 9P文件系统 | 六 | 170 | "底层都是同一套9P文件系统"、"微软也承认这是已知短板" | 核心 |
| 12 | GPO/ADMX | 五 | 146 | "企业管控：GPO/ADMX模板 + 镜像允许列表 + Intune（即将上线）+ Defender" | 核心 |
| 13 | Intune | 五 | 146 | "GPO/ADMX模板 + 镜像允许列表 + Intune（即将上线）+ Defender" | 核心 |
| 14 | SLAT | 三 | 100 | "64位且支持SLAT的处理器" | 核心 |
| 15 | Docker socket转发 | 五 | 153 | "它会支持Docker兼容的socket转发"、"VS Code的Docker插件照样能用" | 核心 |
| 16 | MSBuild | 二 | 52 | "它还能和MSBuild、CMake集成，项目文件加几行配置，容器的构建部署就自动融进编译流程" | 核心 |
| 17 | CMake | 二 | 52 | "它还能和MSBuild、CMake集成" | 核心 |
| 18 | hello-world镜像 | 三、总结 | 95, 202 | "wslc run --rm hello-world"、"wslc run --rm hello-world，你的第一个WSL容器就起来了" | 核心 |
| 19 | Docker Desktop | 引言、五、六 | 12, 18, 138-156, 170, 178 | "不用装Docker"、"结果先得装一个几百兆的Docker Desktop"、"一张表看清：WSL Containers vs Docker Desktop" | 支撑 |
| 20 | Docker Hub | 一 | 38 | "也就是你今天从Docker Hub拉的那些ubuntu、nginx、nvidia/cuda" | 支撑 |
| 21 | PowerShell | 三 | 62-64 | "以管理员身份打开Windows终端（PowerShell）"、"按Ctrl+Shift+1切到PowerShell" | 支撑 |
| 22 | Enable-WindowsOptionalFeature | 三 | 69 | "Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform"" | 支撑 |
| 23 | VirtualMachinePlatform | 三 | 69 | "FeatureName "Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform"" | 支撑 |
| 24 | Microsoft-Windows-Subsystem-Linux | 三 | 69 | "FeatureName "Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform"" | 支撑 |
| 25 | WSL 1 | 总结 | 200 | "WSL 1让Linux二进制能跑、WSL 2给完整内核、Build 2026又补齐了原生容器层" | 支撑 |
| 26 | Build 2026 | 引言、总结 | 22, 200 | "Build 2026大会上，微软端出了一道硬菜——WSL Containers" | 支撑 |
| 27 | GPU透传 | 四、五 | 116, 131, 149 | "调用GPU：docker run --gpus all ..."、"AI/ML场景：把宿主机GPU透传给容器"、"GPU支持：支持（CDI方式）" | 支撑 |
| 28 | NVIDIA CUDA | 一、四 | 38, 116, 131 | "nvidia/cuda"、"wslc run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi" | 支撑 |
| 29 | CLI | 五 | 151, 155 | "纯CLI，无界面"、"WSL Containers是给'想要极简CLI工作流'或'CI/CD场景不愿装整套Docker引擎'的开发者准备的" | 支撑 |
| 30 | Docker Business | 五 | 146 | "需Docker Business才较完善" | 支撑 |
| 31 | Windows Defender | 五 | 146 | "GPO/ADMX模板 + 镜像允许列表 + Intune（即将上线）+ Defender" | 支撑 |
| 32 | Docker Scout | 五 | 153 | "Docker提供了优秀的GUI、Compose和Scout安全扫描" | 支撑 |
| 33 | CI/CD | 五 | 153 | "CI/CD场景不愿装整套Docker引擎的开发者" | 支撑 |
| 34 | VS Code Docker插件 | 五 | 153 | "VS Code的Docker插件照样能用" | 支撑 |
| 35 | compose.yml | 八 | 190 | "多容器编排（compose.yml）目前不支持" | 支撑 |
| 36 | nginx镜像 | 一、四、六 | 38, 111, 125, 165-166 | "nginx"、"wslc run -it --rm -d -p 8080:80 --name web nginx"、"冷启动nginx" | 支撑 |
| 37 | ubuntu镜像 | 一、四、七 | 38, 110, 122, 178 | "ubuntu"、"wslc run --rm -it ubuntu:latest bash"、"ubuntu:latest一行就能拉起" | 支撑 |
| 38 | base image | 七 | 178 | "Ubuntu都是容器世界里最常见的base image之一" | 支撑 |
| 39 | 预发布通道(pre-release) | 三 | 60, 77 | "WSL Containers走的是预发布通道（pre-release）"、"wsl --update --pre-release" | 支撑 |
| 40 | BIOS/UEFI虚拟化 | 三 | 100 | "BIOS/UEFI里开启虚拟化" | 支撑 |
