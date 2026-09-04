# Spec：claude-vision-skill OKF 知识包

> 来源：macrozheng《DeepSeek V4 Pro 也能看图了！》（2026-08-21）
> URL：https://mp.weixin.qq.com/s/3AZbLPVwg45PrQSuvcJDHQ
> 模式：blog-article-to-okf-bundle L2（技术教程完整骨架，含 examples/）

## 产出位置

- Bundle：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/claude-vision-skill/`
- 归属：ai 域 / ai-agent 组（与 anthropics-skills、book-to-skill 同组）

## 文件骨架（12 文件）

| 文件 | 内容 |
|------|------|
| index.md | 知识包入口、机制图、分层导航、信任声明、已知边界 |
| concepts/index.md | 概念学习路径（3篇） |
| concepts/00-problem-vision-gap.md | 视觉鸿沟：[Unsupported Image]、DeepSeek视觉现状、直连vs中转对比 |
| concepts/01-transcription-architecture.md | 视觉转录架构：链路、角色分工、模型选型与成本、可迁移性 |
| concepts/02-skill-mechanism.md | Skill自动触发机制：SKILL.md规范、model-invoked、两个安装坑 |
| examples/index.md | 实战索引（2篇） |
| examples/00-install-and-config.md | 安装配置5步：clone→路径替换→.env→dotenv→验证+检查清单 |
| examples/01-usage-scenarios.md | 三场景实战：自动触发/manual三命令/回退逻辑+时序图 |
| references/index.md | 信源索引（官方文档链接） |
| references/article-source.md | F-001~F-035 事实登记 |
| references/verification.md | P0核验报告（6✅+3时效补充） |
| log.md | 变更日志 |

## 事实基数

35条事实（F-001~F-035）；6项P0核验全部 ✅；3项时效性补充（DeepSeek官方视觉模型08-21上线、README安装方式差异、omni成本4倍）。

## 质量门

- G1（事实）：35条编号登记，主信源逐字提取 ✅
- G2（核验）：6项P0全✅，3项补充不掩盖 ✅
- G3（结构）：三级toctree、相对链接、无file:///、UTF-8严格解码14/14 ✅
- G4（索引）：bundles 278→279、ai域105→106、ai-agent 26→27（frontmatter与toctree条目数一致27=27）✅
