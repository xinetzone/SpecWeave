---
module: ps1_syntax
version: 1.1.0
source: lib/ps1_test_cases.py
generated: 2026-07-29
tags: [crossplatform, newline, BOM, CR, CRLF, LF, here-string]
---

# PS1 Syntax 跨平台测试用例说明

> 本文档详细说明 ps1_syntax v1.1.0 新增的 11 个跨平台测试用例，覆盖 PowerShell 7+ 在 Linux/macOS/Windows 三平台下的换行符差异与 UTF-8 BOM 场景。

## 背景

PowerShell 5.1 仅运行于 Windows，脚本文件统一使用 CRLF (`\r\n`) 换行。PowerShell 7+ 实现跨平台后，脚本可能使用以下三种换行符：

| 换行符 | 十六进制 | 使用平台 | 出现场景 |
|--------|----------|----------|----------|
| LF | `0x0A` (`\n`) | Linux / macOS | 跨平台脚本、Git 默认配置 |
| CRLF | `0x0D 0x0A` (`\r\n`) | Windows | Windows 编辑器默认、PowerShell 5.1 原生 |
| CR | `0x0D` (`\r`) | 老式 Mac OS (Classic) | 极少数遗留文件 |

此外，部分 Windows 编辑器（如 Notepad、PowerShell 5.1 `Out-File`）可能生成带 UTF-8 BOM（`0xEF 0xBB 0xBF`，即 Unicode 字符 `\ufeff`）的文件，解析时需跳过。

## 测试用例分类

11 个用例分为两类：

- **HereString 类（7 个）**：直接测试 `_skip_ps1_here_string` / `Skip-Ps1HereString` 的 here-string 跳过逻辑
- **InsertPoint 类（4 个）**：测试 `find_top_level_insert_point` / `Find-Ps1TopLevelInsertPoint` 在跨平台场景下的插入点检测

---

## 一、HereString 类测试用例（7 个）

### 1. hs_skip_cr_only_newline

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_cr_only_newline` |
| **名称** | CR-only 换行（老式 Mac 风格）的 here-string |
| **分类** | HereString |
| **标签** | `crossplatform`, `cr` |

**测试场景**：双引号 here-string (`@"..."@`) 全文使用 CR (`\r`) 换行符，模拟老式 Mac 风格文件。

```
@"\rcr line1\rcr line2\r"@
```

**输入位置**：`position=0`（起始位置）

**预期结果**：
- 解析器正确识别 CR 作为行结束符
- 起始标记 `@"` 后第一个 CR 正确跳过多行内容
- 行首检测：CR 后为行首，遇到 `"@` 在行首则结束 here-string
- `expected_new_pos` = here-string 全长（即 `"@` 之后的位置）

**验证点**：
- CR 换行符不被误判为普通字符
- 结束标记 `"@` 仅在行首被识别

---

### 2. hs_skip_cr_single_quoted

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_cr_single_quoted` |
| **名称** | CR-only 换行的单引号 here-string |
| **分类** | HereString |
| **标签** | `crossplatform`, `cr`, `single-quoted` |

**测试场景**：单引号 here-string (`@'...'@`) 全文使用 CR (`\r`) 换行符。

```
@'\rcr single line1\rcr single line2\r'@
```

**输入位置**：`position=0`

**预期结果**：
- 单引号 here-string 在 CR 换行下同样正确解析
- 结束标记 `'@` 在行首被正确识别
- `expected_new_pos` = here-string 全长

**验证点**：
- 单引号变体与双引号变体行为一致
- CR 换行对两种引号类型均生效

---

### 3. hs_skip_mixed_newlines_cr_lf

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_mixed_newlines_cr_lf` |
| **名称** | 混合换行符（CR+LF混合）的here-string |
| **分类** | HereString |
| **标签** | `crossplatform`, `mixed-newlines` |

**测试场景**：同一个 here-string 内部混合使用 LF、CRLF、CR 三种换行符，模拟文件在不同平台间拷贝/编辑导致的换行符混乱。

```
@"\nlf line\r\ncrlf line\rcr line\n"@
```

**逐行解析**：
| 位置 | 内容 | 换行类型 |
|------|------|----------|
| `@"` 后 | `\n` | LF（第一行空行） |
| `lf line` 后 | `\r\n` | CRLF |
| `crlf line` 后 | `\r` | CR |
| `cr line` 后 | `\n` | LF |
| `"@` | 行首结束标记 | — |

**输入位置**：`position=0`

**预期结果**：
- 三种换行符在同一字符串内均被正确识别
- 每种换行符后的位置都被视为新行首
- `"@` 在最终 LF 后的行首被正确识别
- `expected_new_pos` = 32（整个 here-string 长度）

**验证点**：
- 换行符检测逻辑不依赖于统一的换行类型
- CRLF 优先于 CR 匹配（避免将 `\r\n` 误拆为 CR + 普通 `\n`）

---

### 4. hs_skip_cr_indented_end

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_cr_indented_end` |
| **名称** | CR换行下缩进的结束标记不关闭 |
| **分类** | HereString |
| **标签** | `crossplatform`, `cr`, `indented-end` |

**测试场景**：CR 换行的 here-string 内部出现缩进的 `"@`（前面有空格），不应被识别为结束标记。

```
@"\rcr line1\r  "@\rstill inside cr\rreal cr end\r"@
```

**关键内容**：第三行为 `  "@`（前面有2个空格缩进），不是行首。

**输入位置**：`position=0`

**预期结果**：
- 缩进的 `"@`（非行首）被视为普通内容，不结束 here-string
- 继续扫描到真正的行首 `"@` 才结束
- `expected_new_pos` = 整个 here-string 全长（包含 `real cr end` 行后的 `"@`）

**验证点**：
- 行首判定逻辑在 CR 换行下同样严格
- 缩进的 `"@` 不触发结束条件

---

### 5. hs_skip_utf8_bom_at_start

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_utf8_bom_at_start` |
| **名称** | UTF-8 BOM 开头的 here-string 应跳过 BOM |
| **分类** | HereString |
| **标签** | `crossplatform`, `bom` |

**测试场景**：文件以 UTF-8 BOM (`\ufeff`) 开头，紧接着是双引号 here-string。BOM 应被自动跳过，不影响 here-string 起始标记 `@"` 的识别。

```
\ufeff@"\nbom content\n"@
```

**输入位置**：`position=0`（从 BOM 位置开始）

**预期结果**：
- 当 `position=0` 且首字符为 BOM (`\ufeff`) 时，自动跳过 BOM 从位置 1 开始解析
- 位置 1 的 `@"` 被正确识别为 here-string 起始
- here-string 正常解析到结束
- `expected_new_pos` = 含 BOM 的全长（BOM + here-string 内容）

**验证点**：
- BOM 不被当作非空白字符干扰解析
- BOM 跳过仅在位置 0 生效（避免误跳字符串内部的 BOM）

---

### 6. hs_skip_bom_crlf

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_bom_crlf` |
| **名称** | UTF-8 BOM + CRLF 换行的 here-string |
| **分类** | HereString |
| **标签** | `crossplatform`, `bom`, `crlf` |

**测试场景**：BOM 开头 + CRLF 换行的 here-string，模拟 Windows 平台 PowerShell 5.1 生成的默认文件编码格式。

```
\ufeff@"\r\nbom crlf line1\r\nbom crlf line2\r\n"@
```

**输入位置**：`position=0`

**预期结果**：
- BOM 正确跳过
- CRLF 换行正确识别
- 两者组合使用时逻辑互不干扰
- `expected_new_pos` = 含 BOM 的全长

**验证点**：
- BOM 跳过与换行符处理的组合场景
- Windows 默认编码文件的兼容性

---

### 7. hs_skip_cr_with_backtick_escape

| 属性 | 值 |
|------|-----|
| **ID** | `hs_skip_cr_with_backtick_escape` |
| **名称** | CR换行下双引号here-string反引号转义 |
| **分类** | HereString |
| **标签** | `crossplatform`, `cr`, `backtick-escape` |

**测试场景**：CR 换行的双引号 here-string 内含反引号转义的 `"@`（`` `"@ ``），被转义的 `"@` 不应被识别为结束标记。

```
@"\rhello `"@ not end cr\rworld cr\r"@
```

**关键内容**：第一行内容为 `` hello `"@ not end cr ``，其中 `` `"@ `` 是反引号转义序列。

**输入位置**：`position=0`

**预期结果**：
- 反引号（`` ` ``）作为转义字符正确识别
- 反引号后的 `"@` 被视为普通字符（转义），不触发结束
- 真正的行首 `"@` 正确结束 here-string
- `expected_new_pos` = 整个 here-string 全长

**验证点**：
- 反引号转义在 CR 换行下仍然有效
- 转义优先级高于结束标记检测

---

## 二、InsertPoint 类测试用例（4 个）

### 8. hs_cr_only_toplevel

| 属性 | 值 |
|------|-----|
| **ID** | `hs_cr_only_toplevel` |
| **名称** | 37. CR-only 换行 here-string 在顶层（跨平台） |
| **分类** | InsertPoint |
| **标签** | `crossplatform`, `cr`, `toplevel` |

**测试场景**：整个脚本使用 CR (`\r`) 换行，顶层包含双引号 here-string 赋值语句。

```
$text = @"\rHello {World}\rCR newline test\r"@\rWrite-Host $text\r
```

**结构分析**：
1. `$text = @"` — here-string 赋值开始
2. `Hello {World}` / `CR newline test` — here-string 内容（含假花括号 `{World}`）
3. `"@` — here-string 结束
4. `Write-Host $text` — here-string 后的语句

**预期关键字**：`$text =`

**预期结果**：
- here-string 内的 `{World}` 不影响括号深度计算（花括号在 here-string 内无语法意义）
- 插入点应在 `Write-Host $text` 之前（顶层括号深度为 0 的位置）
- CR 换行的 here-string 正确跳过，后续代码正常分析

**验证点**：
- 顶层 CR 换行 here-string 不干扰插入点检测
- here-string 内假花括号被正确忽略

---

### 9. hs_bom_toplevel

| 属性 | 值 |
|------|-----|
| **ID** | `hs_bom_toplevel` |
| **名称** | 38. UTF-8 BOM 开头 + here-string |
| **分类** | InsertPoint |
| **标签** | `crossplatform`, `bom`, `toplevel` |

**测试场景**：BOM 开头的脚本，紧跟 here-string 赋值语句。

```
\ufeff$text = @"\nbom content\n{fake braces}\n"@\nWrite-Host $text\n
```

**预期关键字**：`$text =`

**预期结果**：
- `find_non_whitespace` 自动跳过位置 0 的 BOM
- 从 `$text` 开始正常分析
- here-string 内的 `{fake braces}` 不影响括号深度
- 正确找到顶层插入点

**验证点**：
- BOM 不导致第一个非空白位置误判为 0
- BOM 后的代码正常进行 here-string 检测和括号深度分析

---

### 10. hs_bom_param_default

| 属性 | 值 |
|------|-----|
| **ID** | `hs_bom_param_default` |
| **名称** | 39. UTF-8 BOM + param here-string 默认值 |
| **分类** | InsertPoint |
| **标签** | `crossplatform`, `bom`, `param` |

**测试场景**：BOM 开头 + `param()` 块内使用 here-string 作为参数默认值，这是 PowerShell 配置脚本的常见模式。

```
\ufeffparam(\n    [string]$Config = @"\nserver=localhost\n"@\n)\nStart-App\n
```

**结构分析**：
1. BOM → 跳过
2. `param(...)` — 参数声明块
3. `[string]$Config = @"..."@` — here-string 作为 $Config 默认值
4. `)` — param 块闭合
5. `Start-App` — param 后的第一个可执行语句

**预期关键字**：`Start-App`
**expected_min_pos**：50（插入位置应在 param 块闭合之后，`Start-App` 之前）

**预期结果**：
- BOM 正确跳过
- `param()` 块内的 here-string 正确识别和跳过
- 插入点在 `)` 之后、`Start-App` 之前
- here-string 内的等号和内容不被误识别为顶层语句

**验证点**：
- BOM + param + here-string 默认值三者组合场景
- 插入点位置不早于 `expected_min_pos=50`

---

### 11. hs_cr_in_function

| 属性 | 值 |
|------|-----|
| **ID** | `hs_cr_in_function` |
| **名称** | 40. CR换行 here-string 在函数体内 |
| **分类** | InsertPoint |
| **标签** | `crossplatform`, `cr`, `function` |

**测试场景**：CR 换行脚本，函数体内包含 here-string 赋值。这是最复杂的组合场景：函数体（括号深度+1）+ CR换行 + here-string。

```
function Show-Msg {\r    $msg = @"\r    {fake cr}\r    cr test\r"@\r    Write-Host $msg\r}\rShow-Msg\r
```

**结构分析**：
1. `function Show-Msg {` — 函数定义（括号深度+1）
2. `$msg = @"..."@` — 函数体内的 here-string 赋值（CR换行，内含 `{fake cr}` 假花括号）
3. `Write-Host $msg` — 函数体内语句
4. `}` — 函数闭合（括号深度回到0）
5. `Show-Msg` — 顶层函数调用

**预期关键字**：`function Show-Msg`

**预期结果**：
- 函数体内 CR 换行的 here-string 正确跳过
- here-string 内 `{fake cr}` 不增加括号深度
- 函数体 `}` 正确识别（括号深度回到0）
- 由于函数在顶层且函数体内存在 here-string，插入点应在 `function Show-Msg` 之前（顶层第一个有效位置之前）

**验证点**：
- 括号深度跟踪在 CR 换行 here-string 场景下正确
- 函数体内 here-string 的假花括号不干扰括号计数
- 函数闭合后括号深度正确归零

---

## 测试覆盖矩阵

| 用例ID | LF | CRLF | CR | BOM | 单引号 | 双引号 | 顶层 | 函数内 | param内 | 反引号转义 | 缩进结束标记 | 混合换行 |
|--------|:--:|:----:|:--:|:---:|:------:|:------:|:----:|:------:|:-------:|:----------:|:------------:|:--------:|
| hs_skip_cr_only_newline | | | ✅ | | | ✅ | ✅ | | | | | |
| hs_skip_cr_single_quoted | | | ✅ | | ✅ | | ✅ | | | | | |
| hs_skip_mixed_newlines_cr_lf | ✅ | ✅ | ✅ | | | ✅ | ✅ | | | | | ✅ |
| hs_skip_cr_indented_end | | | ✅ | | | ✅ | ✅ | | | | ✅ | |
| hs_skip_utf8_bom_at_start | ✅ | | | ✅ | | ✅ | ✅ | | | | | |
| hs_skip_bom_crlf | | ✅ | | ✅ | | ✅ | ✅ | | | | | |
| hs_skip_cr_with_backtick_escape | | | ✅ | | | ✅ | ✅ | | | ✅ | | |
| hs_cr_only_toplevel | | | ✅ | | | ✅ | ✅ | | | | | |
| hs_bom_toplevel | ✅ | | | ✅ | | ✅ | ✅ | | | | | |
| hs_bom_param_default | ✅ | | | ✅ | | ✅ | | | ✅ | | | |
| hs_cr_in_function | | | ✅ | | | ✅ | | ✅ | | | | |

---

## 双端对齐验证

所有 11 个用例在 Python 端（[ps1_syntax.py](../lib/ps1_syntax.py)）和 PowerShell 端（[encoding-safety.ps1](../lib/encoding-safety.ps1)）共享同一 JSON 数据源（[ps1_syntax_cases.json](./ps1_syntax_cases.json)），确保双端行为完全一致。

**运行命令**：

```bash
# Python 端
cd .agents/scripts
python -m pytest tests/test_ps1_syntax.py -q

# PowerShell 端
pwsh -NoProfile -File .agents/scripts/tests/test_ps1_syntax_unified.ps1
```
