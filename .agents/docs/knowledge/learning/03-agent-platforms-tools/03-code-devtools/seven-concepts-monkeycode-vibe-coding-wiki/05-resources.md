---
id: "resources"
title: "第五章 - 资源扩展链接"
source: "公开资源整理"
version: "1.0"
created_at: "2026-07-14"
tags: ["资源链接", "MonkeyCode", "Vibe Coding", "开源项目", "私有化部署"]
---

# 第五章 - 资源扩展链接

本章汇总MonkeyCode、Vibe Coding、私有化部署相关的官方资源、开源项目、学习资料和工具链接，方便读者进一步深入学习和实践。

---

## 一、官方资源

### 1. MonkeyCode GitHub仓库
- **链接**：https://github.com/chaitin/MonkeyCode/
- **描述**：MonkeyCode官方开源仓库，包含完整源代码、部署脚本、文档和Issue跟踪。采用GNU AGPL v3.0协议开源，可自由查看、修改和分发。建议Star关注最新更新。

### 2. MonkeyCode在线体验地址
- **链接**：https://monkeycode-ai.com/console/tasks
- **描述**：官方提供的在线Demo环境，无需部署即可体验MonkeyCode的AI编码能力，适合快速了解产品功能和交互流程。

### 3. MonkeyCode官方文档
- **链接**：https://github.com/chaitin/MonkeyCode/tree/main/docs
- **描述**：GitHub仓库内的官方文档目录，包含详细的安装指南、配置说明、API文档、最佳实践等，是部署和使用的权威参考。

### 4. 企业微信群交流
- **链接**：查看GitHub README中的二维码
- **描述**：官方维护的企业微信用户交流群，可以和其他用户、开发团队直接沟通，获取技术支持、反馈问题、交流使用经验。

---

## 二、开源社区

### 1. GitHub开源协议（GNU AGPL v3.0）
- **链接**：https://www.gnu.org/licenses/agpl-3.0.html
- **描述**：MonkeyCode采用的开源协议，要求网络服务场景下也需要开源修改后的代码，适合了解开源义务和合规要求。

### 2. Issue/PR贡献指南
- **链接**：https://github.com/chaitin/MonkeyCode/blob/main/CONTRIBUTING.md
- **描述**：参与MonkeyCode开源贡献的指南，说明如何提交Bug报告、功能建议、代码贡献的流程和规范。

### 3. GitHub Discussions社区讨论
- **链接**：https://github.com/chaitin/MonkeyCode/discussions
- **描述**：GitHub官方讨论区，用于社区交流、想法分享、问题求助，是用户之间互助的平台。

### 4. Docker Hub官方镜像
- **链接**：https://hub.docker.com/r/chaitin/monkeycode
- **描述**：官方维护的Docker镜像仓库，可直接拉取预构建镜像快速部署，无需本地编译。

---

## 三、Vibe Coding相关

### 1. Vibe Coding概念起源
- **链接**：https://x.com/karpathy/status/1886192184808149383
- **描述**：Andrej Karpathy在Twitter（X）上首次提出Vibe Coding概念的原始推文，定义了"凭感觉编程"这一新范式。

### 2. Karpathy编程准则
- **链接**：https://karpathy.ai/
- **描述**：Andrej Karpathy的个人网站，包含他对AI编程、软件工程的思考和文章，是理解Vibe Coding理念的重要参考。

### 3. Prompt Engineering指南
- **链接**：https://platform.openai.com/docs/guides/prompt-engineering
- **描述**：OpenAI官方的提示工程指南，系统介绍如何编写高质量提示词，提高AI代码生成质量，是Vibe Coding的核心技能。

### 4. 主流AI编码工具对比
- **链接**：https://github.com/features/copilot
- **描述**：GitHub Copilot官方网站，可对比Cursor、Windsurf、Continue、MonkeyCode等主流AI编码工具的功能差异。

### 5. 七概念方法论参考
- **链接**：../../
- **描述**：本知识库内七概念方法论的相关资源，R-I-E-C-A-F-V七概念框架为Vibe Coding提供系统化的实践指导。

---

## 四、私有化部署相关

### 1. Docker官方部署指南
- **链接**：https://docs.docker.com/engine/install/
- **描述**：Docker官方安装文档，包含各Linux发行版、Windows、macOS的详细安装步骤和配置说明，是私有化部署的基础。

### 2. Docker Compose文档
- **链接**：https://docs.docker.com/compose/
- **描述**：Docker Compose官方文档，MonkeyCode使用Compose编排多容器服务，理解Compose有助于定制化部署。

### 3. Ollama本地模型运行
- **链接**：https://ollama.com/
- **描述**：Ollama官方网站，可一键在本地运行开源大模型（Qwen、Llama、DeepSeek等），配合MonkeyCode实现完全离线的私有化编码环境。

### 4. vLLM推理加速框架
- **链接**：https://github.com/vllm-project/vllm
- **描述**：高性能LLM推理服务框架，支持PagedAttention等技术，可大幅提升本地模型的推理速度和并发能力，适合企业级部署。

### 5. 企业内网安全最佳实践
- **链接**：https://owasp.org/www-project-top-ten/
- **描述**：OWASP Top 10安全风险清单，私有化部署时参考的Web应用安全标准，帮助构建安全的内部AI编码平台。

### 6. Nginx反向代理配置
- **链接**：https://nginx.org/en/docs/
- **描述**：Nginx官方文档，生产环境部署MonkeyCode时推荐使用Nginx做反向代理、HTTPS配置、负载均衡。

---

## 五、大模型资源

### 1. 智谱GLM
- **链接**：https://open.bigmodel.cn/
- **描述**：智谱AI开放平台，提供GLM-4、GLM-4V等系列模型API，中文能力优秀，适合国内用户使用。

### 2. 月之暗面Kimi
- **链接**：https://platform.moonshot.cn/
- **描述**：Moonshot AI开放平台，Kimi模型支持超长上下文（最高200万字），适合处理大型代码库和长文档。

### 3. MiniMax
- **链接**：https://www.minimaxi.com/
- **描述**：MiniMax开放平台，提供abab系列模型，M3等模型在代码生成和Agent任务上表现出色。

### 4. 阿里通义千问Qwen
- **链接**：https://tongyi.aliyun.com/
- **描述**：阿里云通义千问开放平台，Qwen-Coder系列模型专为代码生成优化，开源版本可本地部署。

### 5. DeepSeek深度求索
- **链接**：https://platform.deepseek.com/
- **描述**：DeepSeek开放平台，DeepSeek-Coder是目前代码能力最强的开源模型之一，V2版本在多项基准测试中表现优异。

### 6. OpenAI API文档
- **链接**：https://platform.openai.com/docs/introduction
- **描述**：OpenAI官方API文档，GPT-4o、GPT-4 Turbo等模型的参考，也是OpenAI兼容API协议的标准参考。

### 7. Anthropic Claude文档
- **链接**：https://docs.anthropic.com/
- **描述**：Anthropic官方API文档，Claude 3 Opus/Sonnet模型在代码理解和生成上表现优秀，支持长上下文。

---

## 六、长亭科技相关

### 1. 长亭科技官网
- **链接**：https://www.chaitin.cn/
- **描述**：长亭科技官方网站，了解公司背景、技术团队、产品矩阵，MonkeyCode是长亭在AI编码领域的开源产品。

### 2. 长亭安全产品介绍
- **链接**：https://www.chaitin.cn/product
- **描述**：长亭科技全线安全产品，包括雷池WAF、洞鉴X-Ray、牧云主机安全等，了解MonkeyCode背后的安全技术积累。

### 3. 长亭科技GitHub
- **链接**：https://github.com/chaitin
- **描述**：长亭科技GitHub组织，除MonkeyCode外还有其他安全开源项目，可关注更多安全技术输出。

### 4. 长亭科技技术博客
- **链接**：https://www.chaitin.cn/blog
- **描述**：长亭技术博客，包含安全研究、AI技术、工程实践等高质量技术文章，理解MonkeyCode的设计理念。

---

## 七、其他学习资源

### 1. SpecWeave七概念知识库
- **链接**：../../
- **描述**：本知识库所在位置，使用R-I-E-C-A-F-V七概念方法论系统化学习AI Agent、编程工具等各类技术主题。

### 2. MonkeyCode常见问题解答
- **链接**：./04-faq.md
- **描述**：本Wiki第四章FAQ，汇总部署、使用、配置、安全、故障排查的17个常见问题解决方案。

---

## 继续阅读

上一章：[第四章 - 常见问题解答（FAQ）](./04-faq.md)

下一章：[第六章 - 学习评估](./06-assessment.md)
