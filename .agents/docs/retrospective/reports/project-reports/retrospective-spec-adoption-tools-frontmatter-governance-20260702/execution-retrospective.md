---
id: "retrospective-spec-adoption-tools-20260702-execution"
title: "规范度量工具增强与Frontmatter治理执行过程复盘"
source: "session:spec-adoption-tools-frontmatter"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-spec-adoption-tools-frontmatter-governance-20260702/execution-retrospective.toml"
---
# 执行过程复盘

## 1. 任务背景

本次工作承接前序frontmatter元数据统一任务，核心目标：
1. 运行check-spec-adoption.py度量当前规范落地情况，识别薄弱区域
2. 针对.agents/区frontmatter覆盖率低（约60%）问题，批量补全所有文件
3. 增强check-spec-adoption.py工具，添加目录/文件排除参数，解决专用schema文件干扰评分问题
4. 修复工具产出物治理漏洞（.pytest_cache/、.coverage、htmlcov/未加入.gitignore）
5. 完成原子提交，确保每个提交可独立回滚

## 2. 执行流程时间线

| 阶段 | 关键动作 | 产出物 |
|------|----------|--------|
| 度量阶段 | 运行check-spec-adoption.py，发现.agents/区评分62.2（D级），frontmatter合规率仅68.5% | 初始评分报告 |
| 问题定位 | 识别skills/等专用目录SKILL.md/ONBOARDING.md为特殊schema文件，非标准Markdown | 问题分析 |
| 工具增强 | 为check-spec-adoption.py添加--exclude-dirs/--exclude-files参数，默认排除.pytest_cache | check-spec-adoption.py v2 |
| 评分验证 | 重新运行，排除专用目录后.agents/合规率提升至98.5%，综合评分68.4（D级） | 修正后评分报告 |
| 批量补全 | 开发add-agents-frontmatter.py脚本，补全85个新文件frontmatter四字段，修复11个旧文件缺失，处理2个格式错误文件 | add-agents-frontmatter.py + 98个文件更新 |
| .gitignore修复 | 添加.pytest_cache/到Python缓存忽略列表，同步.coverage/htmlcov/治理 | .gitignore更新 |
| 原子提交 | 按单一职责拆分5个提交：gitignore→工具链→frontmatter→模式库→复盘报告 | 5个原子commit |
| 复盘流程 | S1收集事实→S2分析过程→S3洞察萃取→S4模式检查→S5生成报告→S6导出 | 本复盘报告 |

## 3. 关键问题与修复

### 问题1：check-spec-adoption.py目录排除逻辑缺陷

**现象**：初始--exclude参数按路径前缀匹配，无法正确排除skills/等子目录中的专用schema文件
**根因**：仅用`not any(d in parts[0] for d in exclude_dirs)`检查顶层目录，无法覆盖嵌套子目录
**修复方案**：改为双重过滤——先检查目录名集合，再检查相对路径前缀匹配
**代码修复**：
```python
rel_parts = Path(rel_path).parts
if exclude_dirs:
    if any(part in exclude_dirs for part in rel_parts):
        continue
    if any(rel_path.startswith(d.replace('\\', '/') + '/') for d in exclude_dirs):
        continue
```

### 问题2：Windows PowerShell Git中文commit message编码乱码

**现象**：使用`git commit -F <file>`读取UTF-8文件后，commit message仍然存储为乱码
**根因**：PowerShell 5默认GBK编码管道传递，即使文件本身是UTF-8，Git接收到的仍然是GBK编码字节
**修复方案**：使用Python subprocess以stdin-bytes方式直接传递UTF-8原始字节给Git
**修复代码**：
```python
proc = subprocess.Popen(
    ['git', 'commit', '-F', '-'],
    stdin=subprocess.PIPE,
    cwd=repo_root
)
proc.communicate(input=msg.encode('utf-8'))
```
**经验**：Windows平台中文Git操作必须绕过shell编码层，直接传递原始字节。

### 问题3：工具产出物.gitignore同步遗漏

**现象**：运行pytest --html后生成.coverage、htmlcov/，运行check-spec-adoption后生成.pytest_cache/，均未被.gitignore忽略
**根因**：新增工具/命令时缺乏"产出物→.gitignore"同步检查清单
**修复方案**：更新.gitignore添加.pytest_cache/，与__pycache__/、.coverage、htmlcov/归组
**模式关联**：[gitignore-validation](../../../patterns/code-patterns/gitignore-validation.md)需增强此案例

### 问题4：frontmatter TOML/YAML混合格式错误

**现象**：.agents/rules/cmd-log-specification.md和.agents/skills/README.md使用`id = "value"`（TOML语法）却包裹在YAML的`---`分隔符中，导致解析器无法识别id字段
**根因**：手动编辑时混淆了TOML和YAML语法，且缺少自动化校验
**修复方案**：批量将`=`替换为`:`，并补充缺失的x-toml-ref字段
**模式关联**：[metadata-layering](../../../patterns/architecture-patterns/metadata-layering.md)的自动校验功能可拦截此类错误

## 4. 关键决策记录

### 决策1：专用schema文件排除策略——参数化而非硬编码

**选项A**：在代码中硬编码排除skills/目录
- 优点：简单直接
- 缺点：不可配置，未来新增大类特殊文件需改代码

**选项B**：新增--exclude-dirs/--exclude-files CLI参数，默认添加.pytest_cache（最终选择）
- 优点：灵活可配置，用户可根据项目结构自行调整排除范围
- 缺点：增加了CLI参数复杂度

**决策依据**：度量工具的通用性要求——不同项目可能有不同的专用目录（如vendor/、node_modules/），硬编码排除无法适应所有场景。

### 决策2：frontmatter批量补全方式——自动化脚本而非手动编辑

**选项A**：手动逐文件补全98个文件
- 优点：精确控制每个文件
- 缺点：耗时估计30+分钟，极易出错（路径计算、字段遗漏）

**选项B**：开发add-agents-frontmatter.py脚本自动推导和补全（最终选择）
- 优点：一次开发，可复用；id/title/source/x-toml-ref自动推导；秒级完成
- 缺点：需要开发和测试脚本（约350行）

**决策依据**：遵循"机械心算必错原则"，超过3层重复操作必须工具化。手动补全98个文件的x-toml-ref相对路径计算是典型的高错误率心算场景。

### 决策3：原子提交拆分策略——按变更类型而非按时间

**拆分方案**：
1. `chore(gitignore): 添加.pytest_cache/到Python缓存忽略列表` — 配置文件
2. `feat(scripts): 新增规范度量与frontmatter工具链` — 工具代码
3. `docs(agents): 批量补全.agents区frontmatter四字段` — 文档元数据
4. `feat(patterns): 从frontmatter洞察沉淀新模式并升级现有模式成熟度` — 模式库
5. `docs(retrospective): 更新frontmatter洞察报告与MDI项目复盘` — 复盘文档

**决策依据**：遵循atomic-commit-cmd的单一职责原则，每个提交只包含一种类型的变更，确保bisect和revert的精确性。
