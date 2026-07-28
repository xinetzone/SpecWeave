---
title: "候选模式记录（单案例，待第二案例验证后正式入库）"
date: 2026-07-28
status: candidate
source_count: 1
candidate_count: 6
phases: [core-logic-fix, cross-platform-enhancement, standards-enforcement]
---

# 候选模式记录

> ⚠️ 以下模式均来自单次bugfix案例，按萃取规范单案例不得入库为正式模式。记录于此，待第二案例出现后升级为正式模式。
> 
> 候选模式1-3来自第一阶段（核心逻辑缺陷修复）；候选模式4-6来自第二阶段（Windows兼容性增强+开发标准落地）。

## 候选模式1：CI门禁工具默认静默模式（Default-Silent for CI Gates）

**与现有模式的关系**：现有 [dual-channel-tiered-logging](../../../patterns/code-patterns/dual-channel-tiered-logging.md) 覆盖"控制台简洁+文件详细"双轨场景，但未覆盖"CI门禁工具默认零诊断输出"场景。本候选模式可作为其补充变体。

**核心差异**：
- 现有模式：Logger=DEBUG，ConsoleHandler=INFO（默认有INFO输出）
- 候选模式：Logger=CRITICAL+1，ConsoleHandler=NullHandler（默认零输出），仅 `-v` 时挂载StreamHandler

**触发场景**：CLI工具被CI/CD流水线或其他脚本消费stdout时，任何stderr诊断输出都会被视为噪音。

**待验证**：需要第二个CI门禁工具案例（如check-sensitive-info、link-check等）确认模式通用性。

---

## 候选模式2：多信号风险类别的严重度平方加权选择（Severity-Squared Weighted Category Selection）

**核心算法**：
```python
cat_scores = {}
for s in signals:
    if s.category == "context":
        continue
    cat_scores[s.category] = cat_scores.get(s.category, 0) + int(s.severity) ** 2
primary = max(cat_scores, key=cat_scores.get)
```

**为什么用平方而非线性**：平方放大了高严重度的权重，确保一个CRITICAL（16分）胜过两个HIGH（9+9=18分仍不够，因为两个HIGH的升级规则已单独处理），避免低严重度信号的"人海战术"淹没真正的高风险类别。

**待验证**：需要其他多信号分类/优先级决策场景（如告警聚合、漏洞优先级排序等）验证算法普适性。

---

## 候选模式3：多规则扫描的展示层二元组去重（Presentation-Layer Deduplication for Rule Scanners）

**核心原则**：
1. 规则层保持独立匹配（不去重），不同规则可能提供不同维度的风险描述
2. 展示层在渲染给用户前必须按 `(description, matched_text)` 二元组去重
3. 去重后按严重度降序，截断到Top N
4. DEBUG日志中记录去重统计供验证

**待验证**：需要第二个多规则扫描工具案例（如SAST/DAST/Lint工具）确认展示层去重是通用需求。

---

## 候选模式4：跨Shell危险命令检测的三生态+双向覆盖（Cross-Shell Dangerous Command Detection with Bidirectional Pattern Coverage）

**与现有模式的关系**：现有 [command-injection-prevention](../../../patterns/code-patterns/command-injection-prevention.md) 关注代码中的命令注入漏洞防御；本候选模式关注**CLI安全检测工具自身**如何跨平台覆盖不同Shell生态的危险命令模式。两者解决不同层面的问题。

**核心问题**：跨平台CLI安全工具在单一环境（如WSL/Linux）开发时，天然遗漏Windows CMD/PowerShell的高危命令，且正则通常只覆盖"命令+参数"标准形式，遗漏管道调用等非标准形式。

**核心原则**：
1. **三生态覆盖**：危险命令模式库必须分别覆盖Unix shell（bash/zsh）、Windows CMD、PowerShell三大生态，每个生态的命令语法和风险等级独立评估
2. **双向正则**：每个高危操作必须同时覆盖两种调用方向：
   - 正向形式：`diskpart\s+(?:select|clean|delete|create)` — 命令在前，操作在后
   - 管道形式：`(?:clean|delete\s+partition)\s*[|]\s*diskpart` — 操作在前，通过管道传入命令
3. **正则边界严格锚定**：盘符等模式必须要求边界字符（分隔符/空白/行尾），避免 `--format c:custom` 这类误报
4. **平台特有风险分级**：同类操作在不同Shell的风险等级可能不同——`Remove-Item -Recurse -Force` 跳过回收站（CRITICAL），`del /s /q` 进入回收站（HIGH）

**核心代码模板（管道场景正则）**：
```python
# Windows磁盘分区清除 - 必须覆盖两种形式
(r'diskpart\s+(?:select|clean|delete|create|format|attach|assign)',
    "危险的Windows diskpart磁盘/分区操作", RiskLevel.CRITICAL, "system"),
(r'(?:clean|delete\s+partition|create\s+partition|format\s+fs)\s*[|]\s*diskpart',
    "通过管道传入diskpart危险指令（echo clean | diskpart）", RiskLevel.CRITICAL, "system"),
```

**待验证**：需要第二个跨平台CLI安全检测工具案例（如敏感信息扫描、代码审计工具等）确认三生态+双向覆盖的通用性。

---

## 候选模式5：多编码回退链文件读取（Multi-Encoding Fallback Chain for File Reading）

**与现有模式的关系**：现有 [cross-platform-encoding-enforcement](../../../patterns/code-patterns/cross-platform-encoding-enforcement.md) 解决的是**输出编码**问题（stdout/stderr写入时的UnicodeEncodeError），覆盖PYTHONIOENCODING、stdout.reconfigure()、三层防御体系等。本候选模式解决的是**输入编码**问题（读取用户提供的外部文件时的UnicodeDecodeError），两者互补。

**核心问题**：硬编码 `encoding="utf-8"` 读取文件在中文Windows GBK环境下崩溃（.bat/.ps1/.reg等批处理文件默认GBK编码），且不同场景可能遇到UTF-8-SIG（BOM头）、GB18030等编码。

**核心原则**：
1. **回退链顺序**：utf-8 → utf-8-sig → gbk → gb18030 → latin-1，按常见度排序
2. **latin-1兜底保证永不失败**：latin-1是单字节编码，任意字节序列都能成功解码（不会抛UnicodeDecodeError），即使产生乱码也不会导致流程中断
3. **DEBUG记录实际编码**：回退成功后在DEBUG日志中记录实际使用的编码，便于排查乱码问题
4. **不要假设外部文件编码**：即使项目本身统一使用UTF-8，用户输入的外部文件（扫描目标）可能是任意编码

**核心代码模板**：
```python
def _read_file_text(filepath):
    """跨平台读取文本文件，多编码回退链保证不抛UnicodeDecodeError。"""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb18030', 'latin-1']
    for enc in encodings:
        try:
            content = filepath.read_text(encoding=enc)
            if enc != 'utf-8':
                logger.debug(f"文件 {filepath} 使用编码 {enc} 读取成功")
            return content
        except UnicodeDecodeError:
            continue
    return filepath.read_text(encoding='latin-1')  # 兜底，永不失败
```

**待验证**：需要第二个需要读取外部文件的跨平台工具案例（如配置文件解析器、日志分析工具等）确认回退链顺序和latin-1兜底策略的通用性。

---

## 候选模式6：首Bug主动闭环模式（First-Bug Proactive Closure Pattern）

**与现有模式的关系**：现有 [second-exposure-governance-loop](../../../patterns/methodology-patterns/retrospective-knowledge/second-exposure-governance-loop.md) 要求**同一问题第二次出现**时才启动治理闭环。本候选模式补充了其边界条件：当首次发现的bug具有架构级/模式级特征时，即使没有第二次暴露，也应主动完成"修复→预防→标准固化"三阶段闭环，而非等待第二次事故。

**核心问题**：second-exposure-governance-loop的触发条件是"问题第二次出现"，但架构级/模式级缺陷（如默认日志架构错误、缺少去重层、跨平台覆盖不全）一旦被发现，就应该在第一次修复时就完成标准固化——等待第二次暴露意味着另一个开发者/另一个工具会再次踩坑，造成不必要的返工。

**判断标准（闭环必要性判定）**：
如果回答以下任一问题为"是"，则首Bug必须主动闭环（不等待第二次暴露）：
1. **跨工具共性**：这个问题是否会在其他同类工具中复现？（如"所有CI门禁工具都需要静默日志"）
2. **架构/模式级缺陷**：问题根因是否是架构选择错误或缺少通用模式，而非单点编码笔误？
3. **无自然拦截机制**：这个bug能否被现有测试/审查/CI门禁自动检测到？如果不能（如默认输出格式问题只能在CI环境观察到），则必须固化为规范
4. **修复已验证可行**：修复方案已通过实际验证，提炼为原则的成本低、收益高

**三阶段闭环SOP**：
1. **修复（Fix）**：定位缺陷→修改代码→验证通过
2. **预防（Prevention）**：5-Whys根因分析→提炼可复用原则→评估同类问题在其他模块的风险
3. **闭环（Closure）**：将原则写入开发标准/检查清单/自动化检查器→更新CHANGELOG
4. **完成判定**：问自己"如果另一个开发者明天开发一个类似工具，他会不会犯同样的错误？"——如果"可能会"，说明闭环未完成

**标准固化优先级**：自动化检查器（CI门禁） > 检查清单 > 文档规范 > 口头约定

**与second-exposure-governance-loop的边界**：
- 平凡修复（笔误、拼写错误、变量名错误）：首Bug点修复即可，不需要闭环
- 架构级/模式级缺陷（本模式适用）：首Bug主动闭环，不等待第二次暴露
- 跨文件/跨领域同类问题第二次出现：启动second-exposure-governance-loop六步流程（更重型的治理）

**待验证**：需要第二个"首Bug即主动闭环"的案例（如另一个工具开发中发现架构级缺陷后直接推动标准更新）确认判定标准和SOP的通用性。
