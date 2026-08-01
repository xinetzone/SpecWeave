---
name: loop-engineering-cmd
version: 1.0.0
description: "当用户提到'Loop Engineering'、'循环工程'、'自动迭代'、'验证器设计'、'自动优化循环'、'AI循环'、'Loop设计'、'三要素验证'、'适用性判定'、'循环设计检查'、'Loop风险评估'时，必须使用此技能。提供Loop Engineering设计验证与知识查询能力：适用性判定→三要素验证→五步法设计检查→风险评估→知识库查询。不要凭经验设计Loop——本Skill封装了三要素铁律、四项适用标准、五步设计法、双重风险防控（理解债+认知让渡），确保Loop设计不踩红线、ROI可控。"
argument-hint: "<operation:help/verify/apply/design/risks/query> [options]"
user-invocable: true
paths:
  - ".agents/skills/loop-engineering-cmd/**"
title: "Loop Engineering 命令 Skill"
---
# Loop Engineering 命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，提供Loop Engineering方法论的设计验证与知识查询工具。

## 1. Skill ID
`loop-engineering-cmd`

## 2. 功能描述

提供Loop Engineering全生命周期设计验证能力，六种操作方案：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **help** | ⭐ 查看命令使用说明 | 完整命令清单与参数说明 |
| **verify-three-elements** | ⭐ 验证Loop核心三要素 | 10项检查，确保验证器/状态/停止条件合格 |
| **check-applicability** | ⭐ 判断任务是否适合建Loop | 四项标准评分，ROI前置评估 |
| **check-loop-design** | ⭐ 五步法循环设计完整性检查 | 5个环节逐项验证 |
| **assess-risks** | ⭐ 风险评估（理解债+认知让渡） | 双重风险识别与防范建议 |
| **query-knowledge** | ⭐ 知识库查询 | 概念/数据/案例/风险快速检索 |

核心功能：适用性判定→三要素验证→五步法检查→风险评估→知识查询。

> **为什么用本Skill而非凭经验建Loop？** Loop设计有不可逾越的红线：没有确定性验证器（裁判是LLM自己）必然导致作弊、没有停止条件会无限循环消耗巨额Token、低频任务建Loop ROI严重为负。手动设计容易遗漏这些关键约束，本Skill强制执行六项检查确保Loop可靠可控。

## 3. 何时使用本技能

### 触发词

当用户提到以下任何内容时触发：
- "Loop Engineering"、"循环工程"、"自动迭代"
- "验证器设计"、"自动优化循环"、"AI循环"
- "Loop设计"、"三要素验证"、"适用性判定"
- "循环设计检查"、"Loop风险评估"
- 需要设计自动化迭代/优化循环时
- 需要判断某任务是否适合用Loop自动化时
- 需要查询Loop Engineering相关概念/案例/风险时

### 必用场景
- **新建Loop前**：必须先run check-applicability判定是否值得建
- **Loop设计阶段**：必须run verify-three-elements验证三要素
- **设计评审时**：必须run check-loop-design检查五步法完整性
- **上线前检查**：必须run assess-risks评估理解债和认知让渡风险
- **知识查询**：需要了解Loop Engineering概念/数据/案例/风险时

> **关于触发**：即使没有明确说"用loop命令"，只要涉及自动化循环设计、AI迭代优化、验证器设计相关话题，就应该使用本Skill。Loop是高风险高成本的自动化手段，跳过检查直接建Loop极易导致成本失控或无效循环。

## 4. 方案选择决策树

```
需要Loop Engineering相关操作？
├─ 首次接触/不了解用法？ → help方案（查看命令说明）
├─ 判断任务该不该建Loop？ → check-applicability（四项标准评分）
├─ 设计Loop核心三要素？ → verify-three-elements（验证器/状态/停止条件）
├─ 检查循环设计完整性？ → check-loop-design（五步法逐项验证）
├─ 评估Loop风险？ → assess-risks（理解债+认知让渡双重评估）
└─ 查询概念/案例/数据/风险？ → query-knowledge（知识库检索）
```

### 推荐执行顺序

设计Loop的标准流程：
1. **check-applicability**：先判定是否值得建（ROI评估）
2. **verify-three-elements**：验证三要素设计是否合格
3. **check-loop-design**：检查五步法设计完整性
4. **assess-risks**：识别并防范风险
5. **query-knowledge**：随时查询知识点参考

> **为什么按这个顺序？** 先判定适用性（不值得建的就不要继续），再验证核心要素（三要素是Loop的基石），然后检查设计完整性（五步法确保流程闭环），最后评估风险（理解债和认知让渡是隐性杀手）。顺序错了会导致在错误方向上投入过多精力。

## 5. 快速开始

```
步骤1：使用PowerShell执行命令（脚本目录：.agents/skills/loop-engineering-cmd/）

步骤2：判定适用性（先判断该不该建）：
   .\loop-engineering-cmd.ps1 check-applicability --frequency yes --verifiable $true --budget $true --environment $true
   # 或使用配置文件
   .\loop-engineering-cmd.ps1 check-applicability --config loop-config.json

步骤3：验证三要素：
   .\loop-engineering-cmd.ps1 verify-three-elements --VerifierNonLLM $true --VerifierLocked $true ...

步骤4：检查五步法设计：
   .\loop-engineering-cmd.ps1 check-loop-design --Step1Explore $true --Step2Score $true ...

步骤5：评估风险：
   .\loop-engineering-cmd.ps1 assess-risks --Iterations 20 --CodeUnderstandable $true ...

步骤6：查询知识库：
   .\loop-engineering-cmd.ps1 query-knowledge --keyword 验证器 --category concept
```

### 配置文件格式（JSON）

各子命令均支持 `--config` 参数读取JSON配置文件，示例结构：
```json
{
  "frequency": "yes",
  "verifiable": true,
  "budget": true,
  "environment": true,
  "verifier": {
    "nonLLM": true,
    "locked": true,
    "deterministic": true
  },
  "state": {
    "history": true,
    "resume": true,
    "noRepeat": true
  },
  "stop": {
    "rounds": true,
    "threshold": true,
    "budget": true,
    "diminishing": true
  },
  "steps": {
    "step1": true,
    "step2": true,
    "step3": true,
    "step4": true,
    "step5": true
  },
  "iterations": 20,
  "comprehension": {
    "codeUnderstandable": true,
    "changelog": true
  },
  "cognitive": {
    "humanInvolvement": true,
    "verifierQuality": true,
    "reviewMechanism": true
  }
}
```

## 6. 返回码规范

| 返回码 | 含义 |
|--------|------|
| 0 | 检查通过/操作成功 |
| 1 | 检查失败/致命错误/硬性不满足 |
| 2 | 有警告/部分满足需改进 |

## 7. 核心检查清单

### 三要素验证清单（verify-three-elements）
- [ ] 验证器非LLM实现（确定性代码）
- [ ] 验证器锁定不可篡改（只读权限）
- [ ] 验证器确定性输出（相同输入→相同输出）
- [ ] 状态文件记录历史（每次迭代留痕）
- [ ] 状态文件支持断点续传（中断可恢复）
- [ ] 状态文件避免重复尝试（去重机制）
- [ ] 停止条件：轮次限制（防无限循环）
- [ ] 停止条件：阈值达标（明确成功标准）
- [ ] 停止条件：预算限制（Token/时间上限）
- [ ] 停止条件：收益递减（收敛自动停止）

### 四项适用标准（check-applicability）
- [ ] 频率：每周至少重复一次（否则ROI不足）
- [ ] 验证自动化：能写出确定性验证脚本（无验证器不建Loop）
- [ ] 预算：有足够Token承受试错冗余（10-50次迭代）
- [ ] 环境：Agent能访问真实运行环境（非沙箱模拟）

> **为什么四项缺一不可？** 频率不足ROI为负、无验证器Loop是盲人骑瞎马、无预算会成本失控、无真实环境验证是纸上谈兵。有一项不满足就属于"不要建Loop"的情况。

### 五步法设计检查（check-loop-design）
- [ ] 环节1：清晰探索文档与边界约束（什么能改什么不能改）
- [ ] 环节2：评分脚本锁定、禁止Agent修改（裁判不能被运动员改）
- [ ] 环节3：变更范围限定（仅允许修改指定文件/目录）
- [ ] 环节4：真实环境执行（非静态分析/纸上谈兵）
- [ ] 环节5：自动化评估、优胜劣汰（自动保留最优方案）

### 风险评估（assess-risks）
- [ ] 迭代次数≤25轮（防理解债累积）
- [ ] 代码保持可理解性（不过度优化）
- [ ] 变更日志完整（记录每次改动原因）
- [ ] 人类参与关键节点（不完全自动驾驶）
- [ ] 验证器由人类设计审核（裁判不能是Agent自己）
- [ ] 最终结果有人工验收（不能直接采用Loop输出）

## 8. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为"——不会报错但会导致Loop失效或成本失控的隐性陷阱。

- **验证器作弊是最高频的失败模式**：Agent会很快发现可以通过修改验证器（删除断言、放宽阈值、篡改测试用例）来"通过"检查。这不是Agent"坏"，而是优化目标使然——如果修改验证器比改代码更容易得高分，它一定会这么做。**防范**：验证器必须设只读、独立目录、版本控制锁定。
- **低频任务建Loop是最大的ROI陷阱**：Loop建造成本约相当于5-10次人工执行，任务需要重复≥10次才能回本。每月一次的任务建Loop，可能还没用到第二次任务就变了，前期投入全部浪费。**严格执行**：频率不达标直接"不要建Loop"。
- **单一停止条件等于没有停止条件**：只设轮次限制但达到阈值不停止会浪费资源；只设阈值但无轮次限制可能永远达不到而无限循环；只设预算无轮次限制可能快速烧钱。**必须设置多重停止条件**（轮次+阈值+预算+收益递减组合）。
- **理解债是沉默的维护杀手**：Loop跑20轮后出来的代码"能工作但没人懂为什么"，后续维护成本极高，甚至不如从头重写。**防范**：限制迭代次数、强制变更日志、关键节点人工审查。
- **纸上谈兵的Loop是自欺欺人**：在沙箱/模拟环境中验证通过的方案，在真实环境可能完全不工作。Loop会针对模拟环境的特征"过拟合"，产出应试方案。**必须在真实环境执行验证**。
- **认知让渡比技术失败更危险**：技术失败（Loop跑不出来）最多损失Token；认知让渡（人类失去判断力，盲目信任Loop输出）可能导致线上事故、架构腐化、团队能力退化。**人类必须始终在环（Human-in-the-loop）**。

## 9. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 主脚本 | [loop-engineering-cmd.ps1](loop-engineering-cmd.ps1) | 命令入口 |
| 知识库数据 | [data/knowledge.json](data/knowledge.json) | 概念/数据/案例/风险完整数据 |
| help子命令 | [scripts/help.ps1](scripts/help.ps1) | 查看命令使用说明 |
| 三要素验证 | [scripts/verify-three-elements.ps1](scripts/verify-three-elements.ps1) | 验证器/状态文件/停止条件检查 |
| 适用性判定 | [scripts/check-applicability.ps1](scripts/check-applicability.ps1) | 四项标准评分 |
| 设计检查 | [scripts/check-loop-design.ps1](scripts/check-loop-design.ps1) | 五步法完整性验证 |
| 风险评估 | [scripts/assess-risks.ps1](scripts/assess-risks.ps1) | 理解债/认知让渡评估 |
| 知识查询 | [scripts/query-knowledge.ps1](scripts/query-knowledge.ps1) | 知识库检索 |

## 10. 输出格式

所有子命令支持两种输出格式（通过 `--format` 参数）：
- **markdown**（默认）：人类可读的彩色控制台输出
- **json**：结构化JSON输出，便于脚本集成和自动化处理

## 11. Changelog

- **v1.0.0** (2026-08-01): 初始版本，支持help/verify-three-elements/check-applicability/check-loop-design/assess-risks/query-knowledge六个子命令，封装三要素验证、四项适用标准、五步法设计检查、双重风险评估，内置知识库包含8个核心概念、4组参考数据、5个正反案例、6类风险点。
