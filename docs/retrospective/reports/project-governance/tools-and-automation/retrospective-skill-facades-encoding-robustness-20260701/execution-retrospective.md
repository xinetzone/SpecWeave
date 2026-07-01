# 执行复盘

## 时间线与关键事件

### 阶段1：Skill命令门面化框架开发

| 时间节点 | 事件 | 产出物 |
|---------|------|--------|
| 会话启动 | 更新action-items.md标记完成项 | action-items.md |
| T+0 | 规划并生成前3个高频脚本Skill框架 | link-check-cmd/atomization-finalize-cmd/docgen-cmd SKILL.md |
| T+1 | 生成剩余2个Skill框架 | ci-check-cmd/check-duplication-cmd SKILL.md |
| T+2 | 应用5个Skill到项目并更新索引 | README.md/capability-registry.md/ONBOARDING.md/AGENTS.md |
| T+3 | check-skill-quality.py质量检查 | 发现docgen-cmd缺少dry-run机制 |
| T+4 | 补充dry-run预览文档 | docgen-cmd SKILL.md更新 |

**关键决策**：遵循渐进式披露三层架构（L0 ONBOARDING <100行 / L1 SKILL.md <500行 / L2 深度文档），而非将所有信息塞进单一SKILL.md文件。这确保了AI智能体在决策时能快速匹配触发词，同时在需要深入时能获取完整实现细节。

### 阶段2：测试体系建设

| 时间节点 | 事件 | 结果 |
|---------|------|------|
| T+5 | 创建test_link_fixer.py | 初始3个测试失败 |
| T+5 | 诊断并修复测试失败 | 调整测试fixture目录结构、避免特殊文件名、修复chdir可靠性问题 |
| T+6 | 创建test_check_duplication.py/test_docgen.py | 通过 |
| T+7 | 运行完整pytest套件 | 全部通过 |
| T+8 | 用户报告YAML未加引号值中#被截断 | 定位正则表达式问题 |
| T+9 | 修复frontmatter.py正则表达式 | 将`[ \t]*(?:#.*)?$`改为`(?:[ \t]+#.*)?[ \t]*$` |
| T+10 | 创建test_benchmarks.py性能基准 | 28个benchmark测试建立基线 |
| T+11 | 首次原子提交 | 编码错误暴露（GBK终端UnicodeEncodeError） |

**测试失败分析**：3个link_fixer测试失败的根本原因是测试fixture设计缺陷而非代码bug：
1. `test_file_moved_one_level_deeper`：源文件放置层级不正确，导致`../`回溯次数不够
2. `test_file_url_same_file_becomes_anchor`：使用`README.md`触发了特殊目录索引文件名逻辑
3. `test_no_agents_dir_returns_cwd`：sandbox环境下`monkeypatch.chdir`不可靠

### 阶段3：Windows编码边界修复（核心事件）

| 时间节点 | 事件 | 修复内容 |
|---------|------|---------|
| T+12 | 用户要求检查边界情况，特别是Windows编码 | 系统性审查cli.py |
| T+12 | 发现6个边界问题 | isatty无保护/cp65001缺失/KeyError/冗余标签/encoding类型/reconfigure无保护 |
| T+13 | 实现修复 | 新增_is_tty()安全封装、更新_UTF8_ENCODINGS、dict.get()防御、getattr+callable保护 |
| T+14 | 补充33个边界测试用例 | test_cli.py从17→50个测试 |
| T+15 | 完整测试验证 | 282个测试全部通过 |
| T+16 | 原子提交 | f18c260 fix(cli) |
| T+17 | 提交遗留的README RACI索引链接 | a6744b9 docs(readme) |

## 问题与根因分析

### 问题1：YAML未加引号值中#被误判为注释

**现象**：`README.md#yaml-unquoted`被截断为`README.md`

**5-Whys根因分析**：
1. 为什么截断？正则表达式把`#`当作注释开始
2. 为什么当作注释？正则`[ \t]*(?:#.*)?$`允许`#`前零个空白
3. 为什么零个空白？编写时只考虑了`key: value # comment`的标准场景
4. 为什么没考虑值内含#？因为测试用例只覆盖了带引号的值
5. 为什么测试没覆盖？初始测试设计遗漏了"URL fragment包含#"这一真实场景

**修复**：将注释识别改为要求`#`前至少一个空白字符（`[ \t]+#`），符合YAML规范。

### 问题2：cli.py在非标准stream对象下崩溃

**现象**：在pytest capsys、mock替换、无reconfigure方法的Dummy流等场景下，`_supports_unicode()`、`_symbol()`、`setup_safe_output()`可能抛出AttributeError/KeyError/TypeError。

**5-Whys根因分析**：
1. 为什么崩溃？直接访问`stream.isatty()`、`stream.encoding`、`dict[kind]`无保护
2. 为什么无保护？假设stream是"标准的"sys.stdout/stderr
3. 为什么假设标准？开发时只在真实终端环境测试
4. 为什么没考虑测试环境？因为"测试环境也是终端"的错误认知——pytest capsys替换了sys.stdout
5. 根因：**"正常路径"思维**——代码只考虑了"一切正常"的happy path，没有对输入做防御性检查。

**6个具体边界问题**：

| # | 问题 | 触发场景 | 修复方式 |
|---|------|---------|---------|
| 1 | `isatty()`直接调用无保护 | stream无isatty方法/None/不可调用/抛异常 | 新增`_is_tty()`函数：getattr→callable→try-except三层防护 |
| 2 | 不认识cp65001 | Windows设置UTF-8代码页 | 添加到`_UTF8_ENCODINGS`白名单 |
| 3 | `_symbol()`用`dict[key]` | 传入无效kind参数 | 改为`dict.get(key, fallback)` |
| 4 | 输出冗余`'✓ [PASS]'` | 符号+标签重复 | 改为纯符号`'✓'`/`'⚠'`/`'✗'` |
| 5 | `encoding.lower()`无类型检查 | encoding为None/非字符串 | 添加`isinstance(encoding, str)`检查 |
| 6 | `_color()`/`setup_safe_output()`直接属性访问 | 非标准stream对象 | 统一使用`_is_tty()`和`getattr`+`callable`保护 |

### 问题3：性能基准测试首次运行时GBK编码崩溃

**现象**：`UnicodeEncodeError: 'gbk' codec can't encode character '\u2713'`

**根因**：benchmark测试本身调用了print函数输出Unicode符号，但测试运行时未设置`PYTHONIOENCODING=utf-8`。这恰好暴露了cli.py的编码问题，形成了**问题→发现→修复**的正循环。

## 成功因素

1. **测试先行发现问题**：性能基准测试在GBK终端下的崩溃直接触发了边界审查
2. **系统性边界审查方法**：不是"遇到一个修一个"，而是对cli.py所有stream相关操作做完整审计
3. **防御性编程模式应用**：getattr→callable→try-except三层防护成为标准模板
4. **原子提交规范执行**：每个提交单一职责，编码修复和README索引更新分开提交
5. **完整回归验证**：282个测试全量运行，确保修复不引入新问题
