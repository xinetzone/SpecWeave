---
title: docker commit保留临时ENTRYPOINT导致容器执行失败Bug修复复盘
date: 2026-07-18
type: bug-fix
status: completed
tags: [Docker, docker-commit, ENTRYPOINT, CMD, 镜像导出, Shell]
source: "d:\spaces\SpecWeave\external\xmhub"
chain: R->I->E->Export
depth: standard
---

# docker commit保留临时ENTRYPOINT导致容器执行失败Bug修复复盘

## 概览

| 属性 | 值 |
|------|-----|
| 任务类型 | Bug修复（Docker镜像配置缺陷） |
| 问题现象 | docker run -it --rm xmnn-runtime:1.2.1-fix-cp314 bash 报错 /usr/bin/bash: /usr/bin/bash: cannot execute binary file |
| 根本原因 | docker commit 将临时保活容器的 --entrypoint /bin/bash + sleep CMD 原样保存到新镜像，导致后续 docker run 参数被当作bash脚本而非命令执行 |
| 修复方案 | 在导出脚本的 docker commit 命令中添加 --change ENTRYPOINT 和 --change CMD 重置入口配置 |
| 修复文件 | do_export.sh、export_runtime.sh |
| 验证结果 | bash/python3/默认shell 三种方式均正常 |
| 萃取模式 | 1个（docker commit 镜像配置重置模式） |

## 快速导航

- [执行复盘](execution-retrospective.md) - 时间线、事实清单、变更摘要
- [洞察萃取](insight-extraction.md) - 根因分析、3条核心洞察
- [导出建议](export-suggestions.md) - 可复用模式、行动项

<!-- changelog -->
- 2026-07-18 | fix | 修复docker commit保留临时ENTRYPOINT导致的容器执行失败问题
