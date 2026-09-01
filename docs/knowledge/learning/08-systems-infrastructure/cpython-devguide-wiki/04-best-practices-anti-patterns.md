---
type: Wiki Tutorial

id: cpython-devguide-04
title: "04 - 最佳实践与反模式"
date: 2026-08-19
tags: [cpython, best-practices, anti-patterns, checklist, mental-models, growth]
source:
  - devguide.python.org
  - github.com/python/cpython
  - external/libs/python/devguide
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/cpython-devguide-wiki/04-best-practices-anti-patterns.toml"
maturity: L1-draft
---
# 04 - 最佳实践与反模式

本章总结了新贡献者最容易犯的10个错误，提供PR提交前检查清单，帮助你建立正确的贡献心智模型。

## 🚫 10个常见反模式

### 反模式1：读完所有文档才开始

**错误做法**：花几天时间通读DevGuide、PEP 8、PEP 7、所有内部文档，觉得"准备好了"再开始贡献。

**为什么错**：
- CPython文档量极大，一次性读完不现实
- 纸上得来终觉浅，实际做一个PR比读100页文档收获更多
- DevGuide本身设计为渐进式披露，需要时查相关部分即可

**正确做法**：
- 先读本wiki的00和01章（15分钟）
- 找一个`easy`标签的Issue或一个明显的typo
- 边做边查需要的文档
- 犯错误没关系，reviewer会指出来

---

### 反模式2：在main分支直接改代码

**错误做法**：
```bash
git switch main
# 直接编辑文件...
git commit -m "fix bug"
git push  # 失败！因为你没有main的push权限
```

**为什么错**：
- 你的main分支与upstream/main会产生分叉
- 后续同步会产生混乱的merge commit
- 无法同时处理多个PR

**正确做法**：始终从`upstream/main`创建特性分支：
```bash
git switch main
git pull upstream main
git switch -c gh-12345-fix-description upstream/main
# 在这个分支上工作
```

---

### 反模式3：提交非pydebug版本

**错误做法**：
```bash
./configure && make -j$(nproc)  # 没有--with-pydebug！
# 或者Windows上忘记加-d
PCbuild\build.bat  # 没有-e -d！
```

**为什么错**：
- 非debug版本会禁用`assert()`断言
- CPython内部有大量断言用于捕获编程错误
- 内存分配调试功能关闭，无法发现引用计数bug
- 你的代码可能在debug模式下有问题但在release模式下"看起来正常"
- CI在debug模式下测试，你本地跑的结果和CI不一致

**正确做法**：
```bash
# Unix/macOS
./configure --with-pydebug && make -j$(nproc)

# Windows
PCbuild\build.bat -e -d
```

---

### 反模式4：PR期间force-push/squash/rebase

**错误做法**：
```bash
# reviewer提了意见，修改后：
git add -p
git commit -m "fix"
git rebase -i main  # 不必要！
git push --force     # ❌ 严重错误！
```

**为什么错**：
- Force-push会让reviewer看不到增量diff，必须重新review整个PR
- 之前review中的评论会失去上下文（显示"outdated"但无法看到对比）
- Squash/rebase浪费时间，因为GitHub合并时会自动squash
- 可能丢失commit历史中的讨论线索

**正确做法**：review期间直接追加commit：
```bash
git add -p
git commit -m "Address review comments"
git push  # 正常push，不需要force
# 可以追加任意多个commit，squash merge会清理一切
```

> ⚠️ **唯一例外**：PR创建后还没有人review时，发现提交了密码/密钥等敏感信息，或明显的错误commit，可以amend+force-push。一旦有人开始review，绝对不要force-push。

---

### 反模式5：只跑相关模块测试

**错误做法**：
```bash
# 只改了Lib/os.py，所以只跑test_os
./python -m test test_os -v
# 然后直接提交PR
```

**为什么错**：
- 你的修改可能影响其他模块（例如修改了基础类行为）
- 测试之间可能有隐含的依赖关系
- CI会跑全量测试，本地不跑全量可能导致CI失败后才发现问题

**正确做法**：
```bash
# 开发阶段可以跑相关模块快速迭代
./python -m test test_os -v

# 提交前必须跑全量测试
./python -m test -j0

# 对于核心修改，还要跑严格模式
./python -bb -E -Wd -m test -r -w -uall -j0
```

---

### 反模式6：忘记NEWS/文档/测试

**错误做法**：修改了代码就直接提交PR，忘记添加测试、更新文档、添加NEWS条目。

**为什么错**：
- 没有测试的bug修复可能在未来被重新引入
- 没有文档的功能用户无法发现和使用
- 没有NEWS条目用户不知道新版本中有什么改进
- 这些缺失会被reviewer指出，来回拖慢PR流程

**正确做法**：
```bash
# 运行patchcheck，它会自动检查常见遗漏
make patchcheck
# Windows: .\python.bat Tools\patchcheck\patchcheck.py

# 检查清单：
# - [ ] 添加/更新了测试？
# - [ ] 用户可见变更添加了NEWS条目？
# - [ ] 更新了相关文档（Doc/目录）？
# - [ ] patchcheck通过？
```

**NEWS例外（不需要NEWS的情况）**：
- 纯文档修改
- 纯测试补充/修复
- Typo修正
- 不影响用户的内部重构
- 注释/空白清理

---

### 反模式7：一个PR包含多个不相关变更

**错误做法**：
```bash
# 一个PR里同时：
# 1. 修复了os.scandir的引用泄漏
# 2. 重写了datetime的文档
# 3. 重构了test_json
# 4. 修复了一个无关的typo
```

**为什么错**：
- Reviewer难以审查，每个变更需要不同的专业知识
- 如果一个部分有问题，整个PR被block
- 回滚困难——如果其中一个修复有问题，无法单独回滚
- cherry-pick/backport困难
- PR描述和commit message无法准确描述所有变更

**正确做法**：原子性PR，一个PR解决一个问题：
- 不同的bug修复 → 不同的PR
- 文档改进和代码修复 → 如果不直接关联，分开提交
- 如果在修复过程中发现其他问题 → 创建新分支/PR处理，或在当前PR中只做必要的关联修改

---

### 反模式8：基于维护分支而非main提PR

**错误做法**：
```bash
git switch -c fix-3.13 3.13  # 从3.13维护分支创建
# 修复代码并提交PR到3.13分支
```

**为什么错**：
- 所有修复必须先合入main，然后backport到维护分支
- 直接提交到维护分支的PR会被要求重新提交到main
- 维护分支只接受backport（通过miss-islington或cherry_picker）
- 新功能只进入main分支，不会进入维护分支

**正确做法**：
- 所有修复首先提交PR到 `main` 分支
- 合入main后，由Core Dev添加 `needs backport to 3.Y` 标签
- miss-islington bot会自动创建backport PR
- 如果有冲突，使用cherry_picker手动backport

---

### 反模式9：AI生成代码不加审查

**错误做法**：
- 让ChatGPT/Copilot生成一段代码
- 看都不看直接copy-paste提交PR
- AI生成的测试用例没有验证是否真的能捕获bug
- 无法解释为什么这样写

**为什么错**：
- AI会生成看似正确但有微妙bug的代码
- AI可能不了解CPython的内部约定和最佳实践
- AI可能"幻觉"出不存在的API
- 你对提交的代码负全部责任
- Reviewer可能要求你解释某行代码，你答不上来

**正确做法**：
- AI输出可以作为起点，但你必须逐行审查
- 理解每一行代码的作用
- 运行测试验证AI代码确实正确工作
- 手动添加边界条件测试
- 在PR描述中披露AI的使用（推荐但非强制）

---

### 反模式10：PR被拒就放弃

**错误做法**：
- PR收到批评性review → 觉得自己不够好 → 放弃贡献
- PR被标记为"wontfix" → 觉得被拒绝 → 不再尝试
- Reviewer要求大量修改 → 觉得太麻烦 → 关闭PR走人

**为什么错**：
- CPython维护是一门**平衡的艺术**——每个变更都有收益和风险，被拒不是因为你不行
- 即使是Core Dev的PR也经常被要求修改甚至拒绝
- Review是**礼物**——有人花时间认真读你的代码并给反馈，说明他们关心你的贡献
- 第一个PR被要求修改是完全正常的

**正确做法**：
- 把review当作学习机会
- 如果不同意review意见，礼貌地解释你的理由（技术讨论是正常的）
- 如果你觉得改不动了，直接说出来——可能有其他人能帮忙
- 被拒绝的PR不等于失败——你从中学到了东西
- 看看其他被合并的PR，学习它们的风格和方法

---

## ✅ PR提交前检查清单

提交PR前，逐项确认以下检查项：

### 环境准备

- [ ] 使用pydebug/debug版本编译（`--with-pydebug` 或 `build.bat -e -d`）
- [ ] 分支基于最新的 `upstream/main`（已执行 `git pull upstream main`）
- [ ] 在独立的特性分支上工作（不是main分支）
- [ ] pre-commit hooks已安装（`pre-commit install`）

### 代码质量

- [ ] Python代码遵循PEP 8风格
- [ ] C代码遵循PEP 7风格
- [ ] 没有混入无关的修改（原子性PR）
- [ ] 没有trailing whitespace或tab/space混合
- [ ] 注释清晰，代码是自解释的
- [ ] 保持向后兼容（除非是有意的breaking change且已讨论）

### 测试

- [ ] 添加了对应的测试用例
- [ ] Bug修复的测试在修复前能复现bug（失败），修复后通过
- [ ] 相关模块测试通过：`./python -m test test_MODULE -v`
- [ ] 全量测试通过：`./python -m test -j0`
- [ ] 对于核心修改，严格模式测试通过：`./python -bb -E -Wd -m test -r -w -uall`
- [ ] 没有引入flaky test（多次运行稳定通过）

### 文档与记录

- [ ] 如果修改了公共API/行为，更新了Doc/目录下的文档
- [ ] 用户可见的变更添加了NEWS条目（`blurb add`）
- [ ] 纯文档/测试/typo/内部变更标记为"skip news"（不需要NEWS）
- [ ] Docstring与代码行为一致
- [ ] 新增API在文档中有版本标记（如 `.. versionadded:: 3.14`）

### Git与PR

- [ ] Commit message格式正确：`gh-ISSUENUM: 描述`（祈使句，首字母大写，无句号）
- [ ] PR标题与commit message一致
- [ ] PR描述清晰说明：改了什么、为什么改、怎么测试的
- [ ] PR关联Issue（`Fixes gh-NNNNN`）
- [ ] review期间没有force-push/squash/rebase（追加commit即可）
- [ ] 已签署CLA（首次贡献）
- [ ] `make patchcheck` 通过

---

## 📈 贡献者成长路径

### Level 1：新手贡献者（0-5个PR）

**目标**：熟悉流程，建立信心

- 适合的贡献：typo修复、文档改进、easy issue、补充测试
- 重点学习：Git工作流、PR流程、编译测试
- 心态：不要怕犯错，reviewer会帮助你
- 时间线：第1-2周

### Level 2：活跃贡献者（5-20个PR）

**目标**：深入特定模块，开始参与triage

- 适合的贡献：非easy的bug修复、模块内的功能改进、更多测试覆盖
- 发展：
  - 找到1-2个感兴趣的模块深入了解
  - 开始在他人的PR上提供review意见
  - 帮助triage新Issue（复现bug、添加标签）
  - 学习C代码（如果有兴趣）
- 时间线：1-3个月

### Level 3：领域专家（20+个PR）

**目标**：成为特定模块的go-to person

- 适合的贡献：复杂bug修复、性能优化、C层改进、新功能
- 发展：
  - 成为某个模块的专家
  - 加入Triage Team
  - 参与PEP讨论
  - 开始被考虑为Core Dev候选人
- 时间线：3-12个月

### Level 4：Core Developer

**目标**：维护CPython，帮助社区成长

- 能力：合并PR、参与投票、指导新贡献者
- 责任：代码质量守门人、社区建设者
- 注意：这是自然结果，不是刻意追求的目标

> 💡 **核心洞察**：专注于做出好的贡献，帮助社区成长，Core Dev身份是水到渠成的事情，不是终点或奖励。如果你从一开始就为了当Core Dev而贡献，你可能会失望；如果你专注于让Python变得更好，认可自然到来。

---

## 🧠 心智模型：贡献者的思维方式

### 1. 维护是平衡的艺术

CPython有数百万用户，每个变更都要权衡：
- **正确性 vs 兼容性**：修复bug可能破坏依赖bug行为的代码
- **新功能 vs 复杂度**：每个新功能都是长期维护负担
- **性能 vs 可读性**：更快的代码可能更难维护
- **完美 vs 足够好**：追求完美可能导致永远不合入

> "Language design is not about what you can add, but about what you can take away."

### 2. 代码即文档，测试即规范

- 代码应该自解释，如果需要大量注释说明代码在做什么，考虑重写代码
- 测试用例是**最好的行为规范**——它精确描述了代码应该如何工作
- 文档描述承诺的行为，测试验证实际行为

### 3. 小PR > 大PR

- 小PR review快、合并快、bug少
- 大PR review慢、容易积压、合并风险高
- 如果一个PR超过500行，考虑拆分
- "Perfect is the enemy of good"——渐进式改进优于大规模重写

### 4. 先讨论，再编码

- 对于大的变更（新功能、API变更），先在Issue或Discourse上讨论
- 得到正面反馈后再投入大量时间编码
- 避免"我花了一周做了这个，你们必须接受"的情况
- 对于小的bug修复，直接PR即可

### 5. Review是礼物

- 有人花时间读你的代码、思考你的设计、给你反馈——这是最宝贵的礼物
- 即使review意见很尖锐，也要感谢对方的时间和反馈
- 就事论事地讨论技术问题，不要把不同意见当作个人攻击
- 好的reviewer会让你的代码变得更好

### 6. 社区是长期关系

- 你不是在提交一次性的补丁——你在加入一个社区
- 尊重现有维护者的工作和决定
- 帮助其他新贡献者（教是最好的学习方式）
- 耐心、友善、专业

---

## 🔧 实用技巧

### 找到适合你的Issue

```bash
# GitHub搜索
# 适合新手
label:easy is:issue is:open label:type-bug

# 特定模块
label:easy is:issue is:open label:stdlib

# 文档相关
is:issue is:open label:docs

# 需要帮助的
is:issue is:open label:"awaiting review"
```

在GitHub Issues页面使用Filters搜索，或直接访问：
- [Easy issues](https://github.com/python/cpython/issues?q=is%3Aissue+is%3Aopen+label%3Aeasy)
- [Documentation issues](https://github.com/python/cpython/issues?q=is%3Aissue+is%3Aopen+label%3Adocs)

### 写好PR描述模板

```markdown
# 改动内容

<!-- 简要描述你的改动做了什么 -->

# 问题原因

<!-- 解释为什么会有这个问题，根因分析 -->

# 解决方案

<!-- 描述你如何修复的，关键设计决策 -->

# Issue关联

Fixes gh-NNNNN

# 测试

- [ ] 运行了相关测试：`./python -m test test_MODULE -v`
- [ ] 运行了全量测试：`./python -m test -j0`
- [ ] 添加了新测试用例
- [ ] `make patchcheck` 通过
- [ ] NEWS条目已添加（或不需要，理由：___）

# 备注

<!-- 其他需要说明的事项、截图、性能数据等 -->
```

### Review他人的PR

Review代码本身就是极好的学习方式：
- 从简单的文档PR开始review
- 你不需要是Core Dev也可以review
- 善意的、建设性的评论总是受欢迎的
- 即使只是测试PR是否工作也是有价值的review
- Review时关注：正确性、测试覆盖、代码风格、向后兼容

### 处理合并冲突

如果PR分支与main发生冲突：

```bash
# ⚠️ 使用merge而非rebase来解决冲突！
# rebase会重写历史，导致review上下文丢失

# 首先更新main
git switch main
git pull upstream main

# 回到你的分支并merge main
git switch your-branch
git merge main
# 解决冲突文件中的冲突
git add <resolved-files>
git commit -m "Merge branch 'main' into your-branch"
git push
# 不需要force-push！
```

> ⚠️ 解决冲突使用 `git merge`，不是 `git rebase`！Rebase会重写你的PR分支上的commit历史，导致review评论失效。

---

## 下一步

👉 [05 - FAQ与资源：常见问题解答、术语表、源码目录地图与参考资源](05-faq-resources.md)
