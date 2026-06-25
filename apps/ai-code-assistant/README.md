# AI 编程学习助手 —— 你的 AI 编程导师

> 基于 GPT 的 AI 编程学习 Web 应用，提供代码解释、智能问答、个性化学习路径三大核心功能。
> 让 AI 成为你的编程导师，助你快速成长。

## 项目定位

面向编程初学者和进阶学习者的 AI 辅导工具，解决三大痛点：
1. **读不懂代码**：粘贴代码，AI 按"功能→逻辑→技术点→优化建议"四段式详细讲解
2. **问题没人答**：编程疑问随时提问，附带相关代码获得更精准解答
3. **不知道怎么学**：根据你的水平和目标，生成分阶段的个性化学习路径

## 赛道归属

TRAE AI 创意大赛参赛作品，赛道标签：`学习工作`。

## 目录内容

| 文件/目录 | 类型 | 说明 |
|---|---|---|
| `app.py` | Python | Flask 应用主入口，定义 3 个 API 路由 |
| `pyproject.toml` | TOML | 项目配置与依赖声明（PDM） |
| `.env.example` | 环境变量 | API Key 配置模板 |
| `.gitignore` | Git | 忽略规则配置 |
| `modules/` | 目录 | 核心业务逻辑模块 |
| `modules/code_explainer.py` | Python | 代码解释器：四段式代码讲解 |
| `modules/qa_engine.py` | Python | 智能问答引擎：编程问题解答 |
| `modules/learning_path.py` | Python | 学习路径生成器：个性化学习规划 |
| `templates/index.html` | HTML | 单页面前端（CSS/JS 全部内联） |

## 使用方式

### 1. 环境准备

复制环境变量模板并配置：

```bash
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY
```

### 2. 安装依赖

```bash
pdm install
```

### 3. 启动服务

```bash
pdm run dev
```

### 4. 访问应用

打开浏览器访问 http://localhost:5000

## 核心功能

### 代码解释
- 支持 Python、JavaScript、Java、C++、Go、Rust 六种语言
- 四段式结构化输出：功能概述→核心逻辑→关键技术点→优化建议
- Temperature 0.3，确保解释准确稳定

### 智能问答
- 支持附带相关代码作为上下文
- 提供代码示例帮助理解
- Temperature 0.4，平衡准确性与灵活性

### 学习路径生成
- 根据水平（入门/中级/高级）定制
- 支持多目标选择（Web/数据/AI/后端/移动端/系统）
- 五段式规划：评估→阶段划分→每周任务→推荐资源→实践项目
- Temperature 0.5，给予适当创造性

## 技术架构

```
pyproject.toml ──> app.py ──> modules/
                   │              ├── code_explainer.py ──┐
                   │              ├── qa_engine.py      ──┤──> OpenAI API (gpt-4o-mini)
                   │              └── learning_path.py ──┘
                   └──> templates/index.html (单页面UI)
```

**技术栈**：
- 后端：Flask 3.0 + OpenAI Python SDK
- 前端：原生 HTML/CSS/JavaScript（渐变紫色主题，响应式设计）
- 依赖管理：PDM
- AI 模型：gpt-4o-mini（默认，可通过环境变量配置）

## 设计特点

- **最小可行架构**：约 500 行代码实现完整 Web 应用
- **零前端框架依赖**：无需构建工具，单文件内联所有 CSS/JS
- **提示词工程**：三个模块均有针对编程学习场景优化的 system prompt
- **配置外置**：API Key 和模型名称通过环境变量配置，安全灵活

## 来源

本应用从 `.temp/AI/ai-code-assistant/` 暂存区选择性归档而来，遵循项目 [应用开发生命周期规范](../../.agents/protocols/app-development-workflow.md) §2.2 选择性归档流程完成归档。
