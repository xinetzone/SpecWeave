---
id: "templates-ci-quality-gates"
title: "CI/CD 八项质量门禁配置模板"
source: "docs/retrospective/reports/insight-extraction/meta-methodology/retrospective-insight-optimization-cycle/export-suggestions.md"
x-toml-ref: "../../.meta/toml/.agents/templates/ci-quality-gates-template.toml"
version: "1.0.0"
patterns_applied: ["three-tier-governance", "spec-as-code-automated-gates", "toolchain-maturity"]
---
# CI/CD 八项质量门禁配置模板

> **L3标准化模式集成**：本模板已应用 [three-tier-governance](../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md) 三层治理闭环模式与 [toolchain-maturity](../docs/retrospective/patterns/methodology-patterns/tools-automation/toolchain-maturity.md) 工具链成熟度模型。
>
> **适用场景**：新项目建立CI/CD流水线、为现有项目添加提交前质量门禁、统一跨项目质量标准。
>
> **双平台支持**：提供PowerShell（Windows）和Bash（Linux/Mac）双版本脚本，通过 [ci-check-template.ps1](ci-check-template.ps1) 和 [ci-check-template.sh](ci-check-template.sh) 使用。

---

## 一、门禁设计原则

### 1.1 FAIL/WARN 分级阻断

| 级别 | 语义 | 处理方式 | 典型检查项 |
|------|------|---------|-----------|
| 🔴 FAIL | 阻断提交 | 必须修复后才能继续 | 断链、规范违规、安全问题 |
| 🟡 WARN | 警告不阻断 | 记录后可放行，建议修复 | 重复代码、文件过大、非关键项缺失 |
| ⚪ SKIP | 条件跳过 | 不满足前提条件时自动跳过 | 日志不存在、目标目录为空 |

### 1.2 执行顺序约束

检查项必须按**只读→生成→验证**的顺序编排，避免因顺序错误导致误报：

```
只读检查 → 文档生成 → 二次验证
  (1-4,6-7)    (5)       (8)
```

**为什么顺序重要？** 若先做链接检查再生成导航表，会因导航表尚未更新而产生大量误报。正确顺序是先生成再检查。

---

## 二、八项核心门禁配置

### Gate 1/8：仓库合规检查 🔴 FAIL

**检查目的**：确保仓库结构与基础规范合规。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | gitignore规则、vendor目录结构、Mermaid语法、文件命名规范、角色定义 | 覆盖5类基础合规 |
| 阻断级别 | 🔴 FAIL | 不合规直接阻断 |
| 脚本入口 | `repo-check.py all` | 一键全量检查 |
| 阈值 | 0 ERROR | 不允许任何合规错误 |

**自定义扩展**：可通过配置文件添加项目特定的合规规则（如许可证头检查、分支命名规范等）。

---

### Gate 2/8：链接有效性检查 🔴 FAIL

**检查目的**：确保所有Markdown文档中的本地引用链接有效，无断链。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | 所有.md文件内的本地相对路径引用 | 排除外部URL（可配置开启） |
| 阻断级别 | 🔴 FAIL | 断链直接阻断 |
| 脚本入口 | `check-links.py` | 默认全量扫描 |
| 特殊处理 | `{占位符}` 模板链接自动跳过 | 避免模板变量误报 |
| 自动修复 | `--fix` 参数支持相对路径层级自动校正 | |

**常见误报处理**：使用 `{path}` 占位符包裹尚未确定的路径，链接检查器会自动跳过。

---

### Gate 3/8：Spec一致性检查 🟡 WARN

**检查目的**：验证Spec文档（spec.md/tasks.md/checklist.md）之间的一致性。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | Spec文档元数据、任务与检查点对应关系 | |
| 阻断级别 | 🟡 WARN | 警告不阻断，建议修复 |
| 脚本入口 | `spec-tool.py check` | |

**为什么是WARN而非FAIL**：Spec在迭代过程中可能暂时不一致，硬性阻断会影响开发流畅度。

---

### Gate 4/8：模式成熟度检查 🔴 FAIL

**检查目的**：确保可复用模式文档达到最低质量标准。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | `docs/retrospective/patterns/` 下所有模式文件 | |
| 阻断级别 | 🔴 FAIL | 低质量模式阻断提交 |
| 脚本入口 | `pattern-maturity.py check` | |
| 通过阈值 | ≥L1（元数据完整+基本描述） | 新创建的模式至少达到L1 |
| L2要求 | 有实际案例验证+反模式说明 | 推荐标准 |
| L3要求 | 3个以上独立项目验证+标准化流程 | 成熟模式 |

---

### Gate 5/8：文档自动生成 🔴 FAIL

**检查目的**：自动生成并更新导航表、执行看板、应用清单等派生产物。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 生成范围 | 导航表(nav)、执行看板(dashboard)、应用清单(apps) | |
| 阻断级别 | 🔴 FAIL | 生成失败阻断提交 |
| 脚本入口 | `docgen.py all` | 一键生成所有派生产物 |
| 幂等性 | 多次运行结果相同 | 仅覆盖标记区域内内容 |
| 安全区 | `<!-- nav -->` / `<!-- changelog -->` 等标记包裹区域 | 标记外人工内容不受影响 |

**⚠️ 注意**：此步骤是**写操作**，会修改文档中的标记区域。生成的diff属于预期变更，应正常提交。

---

### Gate 6/8：重复代码检测 🟡 WARN

**检查目的**：检测跨文件重复代码，推动共享库提取。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | `.agents/scripts/` 下的Python脚本 | |
| 阻断级别 | 🟡 WARN | 警告不阻断 |
| 脚本入口 | `check-duplication.py` | |
| 检测阈值 | ≥10行相同代码（N元语法指纹） | 支持变量名不同的"变形重复"检测 |
| 处理方式 | 重复逻辑提取到 `.agents/scripts/lib/` 共享库 | 参考 `lib/README.md` |

---

### Gate 7/8：阶段守卫日志合规 🔴 FAIL

**检查目的**：验证阶段守卫（Stage Guardrail）日志中无违规记录。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 检查范围 | `.agents/logs/` 下最新日志文件 | |
| 阻断级别 | 🔴 FAIL | 违规直接阻断 |
| 脚本入口 | `check-stage-guardrails.py --log-file <file> --strict` | strict模式零容忍 |
| 环境变量 | `STAGE_GUARDRAIL_LOG` 指定日志路径 | 未设置时自动查找最新日志 |
| 跳过条件 | 无日志文件时自动SKIP | 不报错 |

---

### Gate 8/8：SG可视化仪表盘生成 🟡 WARN

**检查目的**：生成阶段守卫合规仪表盘HTML报告，便于可视化监控。

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 生成范围 | `.agents/reports/sg-dashboard.html` | 可视化仪表盘 |
| 阻断级别 | 🟡 WARN | 生成失败不阻断 |
| 脚本入口 | `generate-sg-dashboard.py` | |
| 跳过条件 | 无日志文件时自动SKIP | |

---

## 三、快速检查模式（开发中使用）

开发过程中不需要每次跑全量8项，可快速执行4个核心阻断项：

```bash
# 快速预检（约10秒）
python .agents/scripts/repo-check.py all      # Gate 1
python .agents/scripts/check-links.py         # Gate 2
python .agents/scripts/pattern-maturity.py check  # Gate 4
python .agents/scripts/check-duplication.py   # Gate 6
```

提交前必须执行全量检查（含文档生成和日志验证）。

---

## 四、扩展门禁（按需添加）

除核心8项外，可根据项目需要添加以下扩展检查：

| 扩展项 | 脚本 | 阻断级别 | 适用场景 |
|--------|------|---------|---------|
| RACI权责合规 | `check-raci-compliance.py` | 🔴 FAIL | 多人协作项目 |
| 硬编码检测 | `check-hardcode.py --threshold 60` | 🔴 FAIL | 安全敏感项目 |
| 文件大小门禁 | `check-file-size.py --warn-only` | 🟡 WARN | 大型项目 |
| README存在性 | `generate-readme.py --check` | 🔴 FAIL | 多模块项目 |
| Skill质量评分 | `check-skill-quality.py --threshold 70` | 🔴 FAIL | Skill开发项目 |
| PowerShell安全 | `check-powershell-pipe-safety.py` | 🟡 WARN | Windows重度使用项目 |
| 版本涟漪检查 | `check-version-ripple.py --bootstrap` | 🔴 FAIL | 模式频繁更新项目 |

> 扩展项添加方法：在 [ci-check-template.ps1](ci-check-template.ps1) / [ci-check-template.sh](ci-check-template.sh) 中按现有格式插入新步骤，调整 `$totalSteps` / `TOTAL` 计数即可。

---

## 五、接入指南

### 5.1 新项目接入步骤

1. **复制脚本**：将 `ci-check-template.ps1` 和 `ci-check-template.sh` 复制到项目的 `.agents/scripts/` 目录
2. **调整路径**：根据项目实际目录结构，修改脚本中 `$root` / `ROOT` 变量的路径计算
3. **裁剪门禁**：根据项目需要，注释掉不适用的检查项，调整 `$totalSteps` / `TOTAL`
4. **配置阈值**：修改各检查项的阈值参数（如硬编码检测阈值、Skill质量评分阈值）
5. **首次运行**：执行全量检查，根据结果修复初始问题或调整误报规则
6. **接入pre-commit**：配置Git pre-commit钩子自动执行CI检查

### 5.2 pre-commit钩子配置示例

**Windows (PowerShell)**：
```powershell
# .git/hooks/pre-commit
powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check.ps1
if ($LASTEXITCODE -ne 0) { exit 1 }
```

**Linux/Mac (Bash)**：
```bash
# .git/hooks/pre-commit
bash .agents/scripts/ci-check.sh
```

### 5.3 GitHub Actions集成示例

```yaml
name: CI Quality Gates
on: [push, pull_request]
jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run CI checks
        run: bash .agents/scripts/ci-check.sh
```

---

## 六、常见问题排查

| 问题现象 | 可能原因 | 处理方式 |
|---------|---------|---------|
| PowerShell执行策略阻止 | Windows默认限制脚本执行 | 使用 `-ExecutionPolicy Bypass` 参数 |
| 文档生成后有意外diff | 标记区域内有手动编辑内容 | 将手动内容移到标记区域外 |
| 日志检查SKIP | 本次会话无阶段守卫日志 | 正常现象，无需处理 |
| UTF-8编码乱码 | PowerShell 5默认编码非UTF-8 | 脚本已自动设置，如仍乱码改用PowerShell 7+ |
| 重复代码检测误报 | 确实是必要重复或相似但不同逻辑 | 评估后可暂时接受，记录后续优化 |
| 链接检查报模板变量错 | 使用了 `{ }` 以外的占位符 | 改用 `{占位符}` 格式或添加白名单 |

---

## 七、质量成熟度自评

使用以下清单评估项目CI门禁成熟度：

### L0 基础门禁（必须）
- [ ] Gate 1（仓库合规）已接入并通过
- [ ] Gate 2（链接检查）已接入并通过
- [ ] Gate 5（文档生成）已接入
- [ ] 提交前手动执行CI检查

### L1 标准门禁（推荐）
- [ ] 全部8项核心门禁已接入
- [ ] 配置了pre-commit钩子自动执行
- [ ] FAIL项零容忍，无绕过记录
- [ ] WARN项有跟踪记录

### L2 高级门禁（优化）
- [ ] 接入了RACI/硬编码/版本涟漪等扩展门禁
- [ ] CI/CD流水线（GitHub Actions/GitLab CI）已集成
- [ ] 有可视化仪表盘持续监控
- [ ] 门禁规则根据项目演进持续迭代

---

## 关联参考

- [three-tier-governance](../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md) - 三层治理闭环模式
- [toolchain-maturity](../docs/retrospective/patterns/methodology-patterns/tools-automation/toolchain-maturity.md) - 工具链五阶段成熟度模型
- [spec-as-code-automated-gates](../docs/retrospective/patterns/methodology-patterns/tools-automation/spec-as-code-automated-gates.md) - 规范即代码自动化门禁
- [three-tier-quality-gate-template.md](three-tier-quality-gate-template.md) - 通用三层质量门禁模板
- [ci-check-template.ps1](ci-check-template.ps1) - Windows PowerShell脚本模板
- [ci-check-template.sh](ci-check-template.sh) - Linux/Mac Bash脚本模板
