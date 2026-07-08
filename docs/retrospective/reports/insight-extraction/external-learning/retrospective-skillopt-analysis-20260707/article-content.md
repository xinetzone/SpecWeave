---
title: "最近 SkillOpt 很火。微软的这个开源项目已经拿下 9000+ Star"
source: "https://mp.weixin.qq.com/s/vSbob20fVnS3ODro2F7ETQ?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-skillopt-analysis-20260707/article-content.toml"
author: "开源日记（微信公众号）"
extracted: "2026-07-07"
extract_method: "defuddle --md"
---
# 最近 SkillOpt 很火。微软的这个开源项目已经拿下 9000+ Star

> 来源：开源日记（微信公众号）
> 提取方式：defuddle --md
> 提取时间：2026-07-07

---

最近 SkillOpt 很火，微软的这个开源项目已经拿下 9000+ Star。SkillOpt 是一个专门帮 Agent 打磨 skill.md 的工具——像训练模型一样，通过系统化的迭代流程不断优化技能文档质量。

平时写技能文档就是这样的：你觉得自己写得很清楚了，Agent 执行起来还是出错；你改了一版，不知道改对了没有；就像补课但是没有考试、没有分数、不知道是对是错。没有系统的方法，没有反馈，全靠试错。

SkillOpt 把深度学习训练的成熟范式迁移到了文本域，提出了四步训练法：

## 一、前向传播：记录执行过程

让 Agent 用现有的技能文档运行一组任务，全程记录执行轨迹——包括工具调用序列、中间步骤、验证反馈、最终结果。这就像让新手拿着菜谱先做一遍菜，全程录下来，看看他哪里做错了。

## 二、梯度计算：问题定位

用一个独立的分析模型（teacher model）分析执行轨迹：对于失败案例，定位具体是哪条规则导致了失败，找到"梯度方向"（应该修改什么）；对于成功案例，识别哪些规则是不能动的基石。就像看完新手做菜的录像，指出"你这里盐放早了"、"那里火候不够"。

## 三、参数更新：受控修改

根据分析结果修改技能文档，但严格遵守"文本学习率"约束——默认每次最多修改 4 处（增/删/改）。不贪多，小步迭代。这直接借鉴了深度学习中"学习率不能太大否则震荡不收敛"的经验。就像改菜谱，一次只改 4 个地方，改多了你也不知道是哪个改动起了作用。

## 四、门控验证：验证与拒绝

修改后的技能文档必须在独立的验证集上运行，只有**严格提高整体性能**的修改才被接受；如果性能下降，这次修改被拒绝并记入"拒绝编辑缓冲区"，避免以后再犯同样的错误。就像改完菜谱让新手再做一遍，如果做出来比之前还差，说明这次改错了，退回去，这次的修改方向记下来以后不要再试。

## 五、亮点：跨模型迁移能力

还有一个亮点：GPT-5.5 上训练出的技能文档，可以直接应用到 GPT-5.4-mini 上；Codex 上训练的技能，可以迁移到 Claude Code。因为 SkillOpt 优化的是"技能文档"（方法论），而不是特定模型的权重——好的工作流程、清晰的指令本质上是模型无关的。

这意味着你可以用能力强但成本高的模型作为 teacher 训练优化，然后把优化后的技能文档部署到成本低的小模型上，获得接近大模型的效果。

## 六、测试结果怎么样？

数据说话：
- 52 个测试场景，SkillOpt 全部为最好或并列最好
- GPT-5.5 平均提高了 23.5 个百分点
- 在 ALFWorld 上，GPT-5.4-mini 由原来的 70.9% 提升到了 85.8%
- 关键是：只用了 4 个被接受的编辑，就达到了这样的提升

每个有效编辑平均带来近 6 个百分点的性能提升，这投入产出比非常惊人。

## 七、如果你也想试一下

部署的时候，你不需要额外的推理开销，不需要调用优化器模型，它只是多了一个 Markdown 文件。

使用流程：
1. **安装**：`git clone https://github.com/microsoft/SkillOpt.git && cd SkillOpt && pip install -e .`
2. **配置**：复制 `.env.example` 到 `.env`，填入 OpenAI/Azure/Anthropic 的 API 密钥，可以指定 teacher 和 student 模型
3. **准备数据**：自动划分或手动划分训练集/验证集
4. **开始训练**：`python scripts/train.py --config configs/searchqa/default.yaml`
5. **查看结果**：`best_skill.md` 是最终产物，`skills/`、`steps/`、`history.json` 记录训练过程
6. **部署使用**：把 `best_skill.md` 放到 system prompt 里就行，零额外开销

## 八、写到最后

写到最后，有一个问题值得思考：Agent 的能力上限，到底是受限于模型本身，还是技能文档的质量？

过去我们总觉得模型越强，Agent 自然越好。但 SkillOpt 告诉我们，模型是硬件，技能文档是软件——没有好的软件，再强的硬件也发挥不出全部潜力。这可能会成为 Agent 工具链发展的重要方向。

项目地址：https://github.com/microsoft/SkillOpt，MIT 协议，欢迎 Star 和试用。
