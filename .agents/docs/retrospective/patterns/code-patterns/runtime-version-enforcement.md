---
id: "runtime-version-enforcement"
source:
  - "../../../../../../.trae/specs/standards-tools/establish-pwsh7-windows-standard/spec.md"
  - "../../reports/project-governance/standards-governance/retrospective-pwsh7-windows-standard-20260729/README.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/runtime-version-enforcement.toml"
maturity: "L2"
validation_count: 1
reuse_count: 0
tags: ["version-enforcement", "runtime-check", "ci-gate", "migration-tool", "powershell", "cross-platform", "governance"]
related_patterns:
  - "cross-platform-encoding-enforcement"
  - "ci-integration-three-interface"
  - "docker-timezone-configuration"
  - "playbook-onboarding-guide"
---
# 运行时版本强制规范：统一开发工具版本的可执行治理模式

## 模式概述

本模式描述了如何在项目中强制统一开发工具/运行时版本（如PowerShell/Python/Node.js/CMake版本），通过"低版本声明+自校验友好错误"、"检查器+修复器+模板三件套"、"warn-only→strict渐进CI"三个核心机制，确保规范可执行、可验证、可自动修复，而不是仅仅停留在文档约定层面。

本模式在pwsh7 Windows统一规范建立中首次验证，解决了PowerShell版本碎片化（5.1 vs 7.x）导致的脚本语法不兼容、行为不一致、CI/CD失败等问题。

## 问题现象

项目中存在多个版本的运行时/工具时，会出现以下典型问题：

1. **隐式版本依赖**：脚本在开发者机器上正常运行，但在CI或其他开发者机器上因版本过低崩溃
2. **默认版本陷阱**：Windows自带PowerShell 5.1，但新脚本使用了pwsh7语法（`??`、三元运算符、`$PSNativeCommandErrorActionPreference`）
3. **文档规范失效**：README中写了"需要pwsh7"，但没人看，新人第一天就踩坑
4. **批量迁移困难**：手动修改数十个脚本容易遗漏，且没有自动化验证
5. **CI突然中断**：直接启用strict检查导致现有PR全部挂掉，团队怨声载道

典型错误场景（PowerShell）：
```powershell
# 脚本使用了pwsh7新特性
$config = $null
$value = $config ?? "default"  # 在5.1中报错：ParserError

# 或者
$PSNativeCommandErrorActionPreference = "Stop"  # 5.1中无此变量
```

在低版本中直接报语法错误，没有任何友好提示，用户不知道是版本问题还是脚本问题。

## 解决方案

本模式采用**七层防护体系**，从脚本自校验到CI门禁逐层保障：

### 步骤1：自校验代码块（脚本入口第一道防线）

在每个脚本最开头添加**双声明**：
1. 低版本`#Requires`声明（让旧版本也能解析）
2. 自定义版本校验代码块（必须兼容新旧版本，提供友好错误）

**关键原则**：校验代码本身必须能在最低支持版本和被禁止的旧版本中都能运行——否则在旧版本中会直接报语法错误，无法给出友好提示。

### 步骤2：标准模板（新脚本零成本合规）

在`.agents/templates/`下提供标准脚本模板，预置：
- 版本校验块
- ErrorActionPreference/编码设置
- 结构化日志参考
- 豁免标记注释位置

新脚本从模板创建，自动合规，无需开发者记忆规范。

### 步骤3：检查器linter（自动化批量验证）

编写独立的检查脚本（Python），批量扫描项目目录：
- 检查必需模式是否存在（如`#Requires -Version 7.x`、版本校验块）
- 检查违规模式是否存在（如`#Requires -Version 5.1`）
- 支持排除目录（vendor/、.venv/、.temp/等）
- 支持豁免标记（`# PWSH7-EXEMPT: 原因`）

### 步骤4：修复器fixer（批量迁移自动修复）

提供一键修复脚本，自动为旧脚本添加：
- `#Requires`声明
- 版本校验代码块
- 保持原有脚本内容不变

批量迁移时使用，避免手动修改的遗漏和错误。

### 步骤5：CI渐进集成（warn-only→strict两阶段）

**绝对不要**一开始就用strict模式阻塞CI——这会导致所有现有PR失败，团队会抵触规范。正确的做法是：

1. **warn-only过渡期**（建议2周）：CI只警告不阻塞，让团队有时间修复
2. **strict正式期**：过渡期结束后切换到strict模式，不合规脚本阻塞PR合并

### 步骤6：文档三处更新（规范可见性）

规范不能只存在于检查脚本中，必须在三个地方同时更新：
1. **AGENTS.md/global-core-rules.md**：AI协作者和开发者必读入口
2. **开发环境配置指南/ONBOARDING.md**：新人入门文档
3. **README.md**：项目首页明确标注技术要求

### 步骤7：豁免机制（特殊场景例外通道）

确实无法迁移的脚本（如依赖COM对象、WMI的遗留脚本），允许通过注释标记豁免：
```powershell
# PWSH7-EXEMPT: 此脚本依赖WMI查询，仅在Windows PowerShell 5.1下运行
```

检查器识别此标记并跳过检查，但必须写明原因——没有理由的豁免不被允许。

## 代码示例

### PowerShell 7 版本校验块（pwsh7规范实际使用）

此代码块必须兼容PowerShell 5.1和7.x，在5.1中运行时给出友好提示而非语法错误：

```powershell
#Requires -Version 5.1
# 注意：上面的#Requires -Version 5.1是故意的！
# 目的是让PowerShell 5.1也能解析到这个脚本，然后执行下面的自定义版本检查，
# 给出友好的错误提示，而不是直接报语法错误。
# 真正的版本要求是7.4+，由下面的代码块强制执行。

# ============================================================
# pwsh7 版本校验与友好引导
# ============================================================
if ($PSEdition -ne 'Core' -or $PSVersionTable.PSVersion.Major -lt 7 -or 
    ($PSVersionTable.PSVersion.Major -eq 7 -and $PSVersionTable.PSVersion.Minor -lt 4)) {
    $currentVersion = if ($PSEdition -eq 'Core') { "pwsh $($PSVersionTable.PSVersion)" } else { "Windows PowerShell $($PSVersionTable.PSVersion)" }
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  错误：PowerShell 版本不满足要求" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  当前版本: $currentVersion" -ForegroundColor Yellow
    Write-Host "  需要版本: pwsh 7.4 或更高版本（LTS）" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  安装命令（一键安装）：" -ForegroundColor Cyan
    Write-Host "    winget install Microsoft.PowerShell" -ForegroundColor White
    Write-Host ""
    Write-Host "  文档参考：" -ForegroundColor Cyan
    Write-Host "    .agents/ONBOARDING.md" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    exit 1
}

# 过了版本检查后，设置ErrorActionPreference和编码
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

**关键设计点**：
1. `#Requires -Version 5.1`不是真的要求5.1，而是让5.1能解析这个脚本——否则脚本第一行如果是`#Requires -Version 7.0`，5.1根本不会执行后面的代码，直接报错
2. 版本检查逻辑使用5.1也支持的语法（没有用`??`、三元运算符等），确保能在旧版本中运行
3. 错误信息包含：当前版本、所需版本、一键安装命令、文档链接——用户复制粘贴即可解决
4. 退出码统一为1，便于CI检测失败
5. 版本检查通过后才设置7.x才有的偏好设置（如`$PSNativeCommandErrorActionPreference`）

### 检查器linter核心逻辑（伪代码）

```python
def check_script(filepath: Path) -> list[Issue]:
    issues = []
    content = filepath.read_text(encoding="utf-8")
    
    # 1. 检查豁免标记
    if "# PWSH7-EXEMPT:" in content:
        return issues  # 豁免，跳过检查
    
    # 2. 检查必需模式
    if "#Requires -Version 7" not in content and "#Requires -Version 7.0" not in content:
        issues.append(Issue("missing-requires", "缺少#Requires -Version 7.x声明"))
    
    if "$PSEdition -ne 'Core'" not in content:
        issues.append(Issue("missing-version-check", "缺少自定义版本校验逻辑"))
    
    # 3. 检查违规模式
    if "#Requires -Version 5" in content:
        issues.append(Issue("forbidden-version", "禁止声明#Requires -Version 5.x"))
    
    return issues
```

## 反模式

### 反模式1：仅依赖文档约定

```markdown
<!-- ❌ 错误：只在README里写一句，没人会看 -->
## 环境要求
- 需要 PowerShell 7 或更高版本
```

**为什么是反模式**：文档是被动的，用户不会每次运行脚本前都去读README。规范必须在脚本运行时主动拦截。

### 反模式2：#Requires用高版本声明

```powershell
# ❌ 错误：第一行就#Requires -Version 7.0，5.1根本不会执行后面的代码
#Requires -Version 7.0
# 版本检查...（5.1中永远执行不到这里）
```

**为什么是反模式**：PowerShell看到`#Requires -Version 7.0`在5.1中直接终止脚本，显示PowerShell默认的晦涩错误信息，用户不知道怎么解决。必须用低版本`#Requires`让脚本有机会执行自定义友好提示。

### 反模式3：直接strict模式阻塞CI

```yaml
# ❌ 错误：第一天就开strict，所有PR挂掉
- name: Check pwsh7 compliance
  run: python .agents/scripts/check-pwsh7-compliance.py --strict
```

**为什么是反模式**：没有过渡期的规范会遭到团队抵触。大家正在赶项目进度，突然CI红了，第一反应是"谁加的烂检查"而不是"我来修复脚本"。warn-only给大家缓冲时间。

### 反模式4：校验代码使用新版本语法

```powershell
# ❌ 错误：版本检查代码用了7.x才有的??运算符，在5.1中直接语法错误
if ($PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt (7,4) ?? false) {
    # 友好提示...（5.1中执行不到这里，因为上面那行已经语法报错了）
}
```

**为什么是反模式**：版本校验代码的第一原则是——它自己必须能在要禁止的旧版本上运行，否则就失去了"友好提示"的意义，退化成反模式2。

### 反模式5：没有豁免机制，一刀切

```
# ❌ 错误：不允许任何例外，遗留脚本要么改要么死
```

**为什么是反模式**：现实项目中总有特殊情况（如依赖遗留COM组件、需要和旧系统交互）。没有豁免机制会导致团队要么绕过检查（删除检查脚本），要么在脚本里写hack规避检查。明确的豁免机制+审批流程，比暗箱操作更可控。

## 迁移验证

本模式可迁移到以下场景：

| 场景 | 最低版本要求示例 | 注意事项 |
|------|-----------------|---------|
| Python版本统一 | Python 3.10+ | 校验代码用兼容3.8/3.9的语法，shebang用低版本python3 |
| Node.js版本统一 | Node.js 18+ | 使用process.version检查，nvm/npx引导 |
| CMake版本统一 | CMake 3.20+ | cmake_minimum_required用低版本，然后自定义版本检查 |
| Go版本统一 | Go 1.21+ | 使用build constraint和runtime.Version() |
| Java版本统一 | Java 17+ | 使用System.getProperty("java.version")检查 |
| Docker版本统一 | Docker 24+ | docker version --format检查 |
| Git版本统一 | Git 2.40+ | git --version解析，提供各平台安装命令 |
| Bash版本统一 | Bash 5.0+ | 使用BASH_VERSION检查，提供brew/apt安装命令 |

**迁移验证检查清单**：
- [ ] 版本校验代码本身兼容要禁止的旧版本
- [ ] 错误信息包含：当前版本、所需版本、一键安装命令、文档链接
- [ ] 提供标准模板，新脚本自动合规
- [ ] 提供检查器支持批量扫描
- [ ] 提供修复器支持批量迁移旧脚本
- [ ] CI先warn-only运行至少2周，再切换strict
- [ ] AGENTS.md/ONBOARDING.md/README三处文档同步更新
- [ ] 有明确的豁免标记格式和审批机制

## 与其他模式的关系

- 借鉴[cross-platform-encoding-enforcement](cross-platform-encoding-enforcement.md)的"入口自防御"思想：编码问题在脚本入口设置，版本问题也在脚本入口检查
- 与[ci-integration-three-interface](ci-integration-three-interface.md)配合使用：检查器实现CLI/Python/CI三个接口，warn→strict渐进策略是CI集成的最佳实践
- 与[playbook-onboarding-guide](playbook-onboarding-guide.md)配合使用：环境配置步骤明确到新人文档，版本要求是onboarding的第一课
- 与[docker-timezone-configuration](docker-timezone-configuration.md)同属"环境一致性治理"类模式：一个解决运行时版本，一个解决容器环境配置

## 实际案例

### 案例1：SpecWeave项目pwsh7 Windows统一规范（本模式原始来源）

2026-07-29，SpecWeave项目建立pwsh7 Windows统一规范，将项目中27个PowerShell脚本全部迁移到pwsh7合规状态：
- 所有脚本添加双声明+自校验代码块
- 提供check-pwsh7-compliance.py检查器
- CI集成warn-only模式，过渡期2周
- 27个脚本全部一次性合规通过检查

详见复盘报告：[retrospective-pwsh7-windows-standard-20260729](../../reports/project-governance/standards-governance/retrospective-pwsh7-windows-standard-20260729/README.md)
