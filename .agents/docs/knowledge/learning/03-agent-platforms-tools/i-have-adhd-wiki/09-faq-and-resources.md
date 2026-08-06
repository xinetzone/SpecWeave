---
id: i-have-adhd-wiki-faq
title: 十、FAQ与资源汇总
source: i-have-adhd常见问题与参考资源整理
---

# 十、FAQ与资源汇总

本章汇总 i-have-adhd 使用中的常见问题、快速参考卡、参考资源和许可说明，方便快速查阅。

---

## 10.1 常见问题 FAQ

### Q1: 我必须确诊 ADHD 才能用这个吗？

**A**: 不需要！i-have-adhd 的 Slogan 就是 **"No ADHD diagnosis needed"**（无需 ADHD 确诊）。这套输出风格的本质是"行动优先、减少认知摩擦"，任何喜欢直接高效输出、讨厌废话套话的人都能从中受益，无论是否真的有 ADHD。

设计灵感来源于 ADHD 大脑的认知特征，但优化结果对所有人都友好——就像路边的坡道最初是为轮椅设计的，但推婴儿车、拉行李箱的人也都在用。

---

### Q2: 这和简单说一句"让回复简洁一点"有什么区别？

**A**: "简洁"只是短，i-have-adhd 是**有结构的行动导向输出**，二者有本质区别：

| 维度 | "让回复简洁一点" | i-have-adhd 模式 |
|------|------------------|------------------|
| 结构 | 随机缩短，可能丢失关键信息 | 首行行动→编号步骤→状态重述→下一步，结构固定 |
| 信息保留 | 容易删掉执行上下文（文件路径、命令、行号） | 短但不丢失执行信息，关键数据重复给出 |
| 认知依据 | 凭直觉 | 基于工作记忆、注意力、启动门槛等认知科学原理 |
| 可验证性 | 无法判断"够不够简洁" | 有首尾验证法、自检清单可客观检查 |
| 例外处理 | 一刀切，所有场景都要短 | 明确列出例外场景（创意、共情、概念解释） |

简单说："简洁"关注的是**长度**，i-have-adhd 关注的是**可执行性**。

---

### Q3: 如何关闭 i-have-adhd 模式？

**A**: 分两种情况：

1. **临时关闭（当前会话）**：
   - 直接说 `stop adhd mode` 或 `normal mode`，当前会话恢复默认输出风格
   - 开新会话需要重新激活

2. **永久关闭 always-on 模式**：
   - 删除 flag 文件：
     ```bash
     # Claude Code
     rm ~/.claude/.i-have-adhd-always
     
     # 其他平台类似，删除对应的配置标记
     ```
   - 完全重启 AI 助手后生效

3. **彻底卸载**：
   ```bash
   # Claude Code
   claude plugin uninstall i-have-adhd
   claude plugin marketplace remove i-have-adhd
   
   # Cursor/OpenCode
   npx skills remove i-have-adhd
   
   # 或手动删除 skills 目录下的 i-have-adhd 文件夹
   ```

---

### Q4: 会影响回答的正确性吗？

**A**: 不会，i-have-adhd 的评测框架将**正确性（Correctness）**权重设为最高（35%），发布门槛有硬性要求：

1. **正确性不下降**是 Release Gate 的必要条件——任何导致正确性下降的改动都会被拦截
2. Safety（安全性）也是 blocker 维度——出现危险指令、幻觉会立即 block
3. 从实际评测数据看，1.0 版本相对于 baseline：
   - 正确性持平或微升（因为规则要求"直接给答案"减少了绕弯导致的错误）
   - 可执行性提升 28%
   - 安全性持平
   - 简洁性提升，平均回复长度缩短约 40%

简洁的目标是"去掉废话"，不是"去掉信息"。

---

### Q5: 可以只在某些项目中使用，其他项目保持默认吗？

**A**: 可以，支持项目级配置：

- **Claude Code**：在项目根目录创建 `.claude/.i-have-adhd-always` 文件，则只有在该项目目录下开会话才自动激活
- **Cursor**：在项目根目录的 `.cursor/rules/` 下配置 always-on 规则
- **OpenCode/Trae**：在项目的 `.agents/skills/` 目录放置 i-have-adhd 技能，并配置项目级 AGENTS.md 自动加载
- **通用方式**：不开启 always-on，只在需要的项目中手动输入 `/i-have-adhd` 激活

配置粒度支持：全局 → 项目级 → 会话级，按需选择。

---

### Q6: 与其他 Skill/插件冲突怎么办？

**A**: i-have-adhd 只控制**输出格式**，不改变任务逻辑，冲突概率很低。如果确实发生冲突：

1. **规则 vs 宿主系统提示冲突**：宿主系统提示优先（i-have-adhd 规则中有明确的例外条款）
2. **规则 vs 其他 Skill 输出冲突**：
   - 如果是格式冲突：后激活的 Skill 优先（建议按需激活，不要同时开多个输出风格 Skill）
   - 如果是内容冲突：任务逻辑相关的 Skill 优先
3. **特定场景下不想用**：直接说 "normal mode for this task"（本次任务用普通模式）即可
4. **冲突无法解决**：可以 Fork 后自定义 SKILL.md，调整规则优先级（详见第八章）

---

### Q7: 可以自定义规则吗？

**A**: 完全可以，i-have-adhd 设计为 100% 可定制：

1. **最简单方式**：Fork 官方仓库 `ayghri/i-have-adhd`，直接编辑 `skills/i-have-adhd/SKILL.md`
2. **可定制内容**：
   - 增减规则条目（删掉对你没用的，加你自己需要的）
   - 调整规则严格度（比如放宽列表 5 项上限到 7 项）
   - 添加领域特定规则（如"代码必须带类型注解"）
   - 修改语气风格（更友好/更正式/特定 emoji 习惯）
   - 调整例外场景列表
3. **自定义版本安装**：
   ```bash
   claude plugin marketplace add <your-username>/i-have-adhd
   claude plugin install i-have-adhd@i-have-adhd
   ```
4. **核心原则**：所有规则都在 `SKILL.md` 一个文件里，没有隐藏硬编码，改这一个文件就改变所有行为。

详细自定义流程见第八章：[07-customization-and-troubleshooting.md](./07-customization-and-troubleshooting.md)

---

### Q8: 支持中文吗？

**A**: 支持，规则本身是**语言无关**的：

1. SKILL.md 中的规则是结构性要求（首行行动、编号步骤、状态重述等），不依赖特定语言
2. AI 会自动用你提问的语言回复——你用中文问就用中文答，用英文问就用英文答
3. 10 条规则同样适用于中文输出：
   - 中文同样有"好的，让我来帮你..."这类开场白
   - 中文同样有"希望这有帮助"这类客套结束语
   - 中文用户同样有工作记忆、启动门槛等认知局限
4. 中文场景下的小提示：
   - 规则 10 的禁用开头词在中文里是："好的"、"没问题"、"让我看看"、"这个问题很好"等
   - 禁用结束语在中文里是："希望能帮到你"、"有问题随时问"、"还有什么需要吗"等

---

### Q9: Trae IDE 能用吗？怎么安装？

> **【SpecWeave 方法论补充】** 以下 Trae IDE 安装方法基于 Agent Skills 开放标准推理得出，非原项目官方文档内容。

**A**: 可以，Trae 兼容 Agent Skills 标准，参考 Cursor 方式安装：

1. **手动安装（推荐）**：
   ```bash
   # 1. 克隆或下载仓库
   git clone https://github.com/ayghri/i-have-adhd.git
   
   # 2. 复制 skills 目录到 Trae 的 skills 目录
   # Windows: %USERPROFILE%\.trae\skills\
   # macOS/Linux: ~/.trae/skills/
   cp -r i-have-adhd/skills/i-have-adhd ~/.trae/skills/
   ```

2. **验证安装**：
   - 完全重启 Trae IDE
   - 新建会话，输入 `/i-have-adhd`，看是否能激活
   - 测试一个问题，确认输出首行是行动

3. **Always-On 配置**：
   - 在 Trae 的全局或项目配置中设置自动加载 i-have-adhd 技能
   - 或参考其他平台的 flag 文件机制适配

Trae 对 Agent Skills 标准的兼容性很好，核心 SKILL.md 不需要修改即可直接使用。

---

### Q10: 为什么叫 "i-have-adhd" 这个名字？

**A**: 名字来源于项目的**设计灵感**：

1. **出发点**：项目最初是为一位有 ADHD 的开发者设计的——他发现普通 AI 助手的输出风格对 ADHD 大脑非常不友好：太多铺垫、太多客套、结构混乱、找不到行动项
2. **泛化发现**：做完后自己用，发现即使没有 ADHD，这种风格也大幅提升了效率——因为它解决的是所有人都有的认知局限（工作记忆有限、注意力易分散、启动需要明确第一步）
3. **命名考虑**：
   - 直接点明设计目标，让有同样困扰的人一眼能找到
   - 副标题 "No ADHD diagnosis needed" 明确说明所有人都能用
   - 有点自嘲和幽默感，降低使用的心理门槛
4. **类似的命名哲学**：
   - "无障碍设施"不是只有残障人士能用
   - "老年模式"不是只有老人能用
   - i-have-adhd 优化的输出风格，所有人都能从中受益

名字只是标签，核心是"减少认知摩擦，行动优先"的设计理念。

---

## 10.2 快速参考卡（Cheat Sheet）

10 条核心规则一句话速查表：

| 规则 # | 英文名称 | 一句话总结 |
|--------|----------|-----------|
| **1** | Lead with the next action | 首行必须是可直接执行的行动（命令/代码/路径），不是铺垫 |
| **2** | Number multi-step tasks | 多步骤用编号列表，每步单一动作，步数尽量少 |
| **3** | End with one concrete next action | 结尾给出一个**两分钟内可完成**的具体下一步，避免开放性结尾 |
| **4** | Suppress tangents | 一次只解决一个问题，其他旁枝问题在结尾一次性提出 |
| **5** | Restate state every turn | 每轮重述当前进度（"第X步/共Y步已完成"），不假设用户记得上下文 |
| **6** | Give specific time estimates | 给出具体时间估计（分钟/小时），带条件分支，不用"一点"、"很快" |
| **7** | Make completed work visible | 明确说明"什么现在可以工作了"，并给出立即可验证的方式 |
| **8** | Matter-of-fact tone for errors | 错误客观陈述（位置→现象→原因→修复），不用"哎呀"、"糟糕"等情绪化表达 |
| **9** | Cap lists at 5 items | 列表不超过 5 项，超过则拆分为"立即做"和"以后做"两组 |
| **10** | No preamble, no recap, no closing | 无开场白、无冗余回顾、无客套结束语，直接开始直接结束 |

### 终极验证测试（首尾验证法）

只读回复的**第一行**和**最后一行**，问两个问题：
1. 第一行：我现在立刻知道该做什么吗？
2. 最后一行：我知道已经完成了什么/下一步做什么吗？

两个答案都是"是" → 回复合格。

---

## 10.3 参考资源

### 官方资源

- **官方 GitHub 仓库**: [https://github.com/ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
  - 最新版本、Issue 反馈、PR 贡献都在这里
  - 仓库包含所有平台的适配文件和评测脚本

- **Agent Skills 标准**: [https://agentskills.io](https://agentskills.io)
  - i-have-adhd 遵循的跨平台 Skill 标准
  - 了解如何开发自己的 Agent Skill

### 参考书籍与认知科学背景

- **《The Adult ADHD Tool Kit》** by J. Russell Ramsay & Anthony L. Rostain
  - 成人 ADHD 的认知行为疗法工具包
  - i-have-adhd 中"启动门槛"、"工作记忆外部化"、"成果可见性"等设计思路的认知科学来源之一
  - 推荐章节：第 3 章（任务启动）、第 5 章（工作记忆策略）、第 7 章（动机维持）

- **推荐延伸阅读**：
  - 《注意力分散时代》（The Distracted Mind）- Adam Gazzaley
  - 《拖延心理学》- Jane B. Burka & Lenora M. Yuen
  - 《Thinking, Fast and Slow》（思考，快与慢）- Daniel Kahneman（系统1/系统2理论解释了为什么"短≠容易理解"）

### SpecWeave 相关 Wiki

- **Agent Skills 开放标准 Wiki**: [../../01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md](../../01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md)
  - Agent Skills 标准详解、开发指南、跨平台适配

- **七概念方法论**: [../../../../../commands/seven-concepts.md](../../../../../commands/seven-concepts.md)
  - 本 Wiki 使用的 R-I-E-C-A-F-V 七概念方法论
  - 了解模式萃取、复盘、洞察等知识沉淀方法

- **i-have-adhd Wiki 目录**: [README.md](./README.md)
  - 本 Wiki 的索引页，含所有章节链接

### 各平台插件文档

- **Claude Code Plugins**: 参考官方文档了解 plugin.json、hooks 等开发
- **Gemini Extensions**: 参考 Gemini CLI 文档了解 gemini-extension.json、GEMINI.md 格式
- **Cursor Skills**: 参考 Cursor 官方文档了解 .cursor/skills/ 目录结构

---

## 10.4 许可说明

i-have-adhd 采用 **MIT License** 开源许可：

```
MIT License

Copyright (c) 2025 ayghri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 你可以自由：

- ✅ **使用**：个人和商业场景都可以免费用
- ✅ **修改**：Fork 后自定义规则，适配自己的需求
- ✅ **分发**：分享给其他人，或集成到你的产品/工作流中
- ✅ **私有化**：可以私有修改，不需要开源你的修改版本（但欢迎回馈上游）

### 只需要：

- ⚠️ 保留原始版权声明和许可声明（MIT License 文本）
- ⚠️ 不使用作者名义做背书（不能说"官方推荐"之类的，除非你确实是官方）

完整许可证文本见源项目根目录 LICENSE 文件（`external/libs/i-have-adhd/LICENSE`，源项目归档路径）：

---

## 索引：i-have-adhd Wiki 完整章节

| 章节 | 文件路径 |
|------|---------|
| 一、概述与设计哲学 | [00-overview.md](./00-overview.md) |
| 二、设计哲学与认知原理 | [01-design-philosophy.md](./01-design-philosophy.md) |
| 三、核心规则（10条详解） | [02-core-rules.md](./02-core-rules.md) |
| 四、例外场景与自检清单 | [03-exceptions-and-checklist.md](./03-exceptions-and-checklist.md) |
| 五、多平台安装指南 | [04-installation-guide.md](./04-installation-guide.md) |
| 六、Always-On 自动激活机制 | [05-always-on-mechanism.md](./05-always-on-mechanism.md) |
| 七、评估框架（A/B测试Rubric） | [06-evaluation-framework.md](./06-evaluation-framework.md) |
| 八、自定义开发与故障排查 | [07-customization-and-troubleshooting.md](./07-customization-and-troubleshooting.md) |
| 九、可复用模式萃取（本章之前） | [08-patterns-extracted.md](./08-patterns-extracted.md) |
| 十、FAQ与资源汇总（本章） | 当前文件 |
