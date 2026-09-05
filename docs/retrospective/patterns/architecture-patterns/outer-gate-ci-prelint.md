---
type: Pattern
id: "outer-gate-ci-prelint"
source:
  - "session:sc-20260904-okf-ci-fix（awesome-okf-xs CI runs/33830000544 pages.yml L82 冒号空格 YAML 解析错误修复）"
  - "projects/awesome-okf-xs/.github/workflows/pages.yml#L82-L82"
  - ".agents/scripts/tests/test_doc_navbar_options.py#L233-L272（T4b pages.yml 硬编码扫描 pytest 断言）"
maturity: "L1-draft"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  - "incremental-regression-verification"
  - "preflight-checks-script"
  - "full-process-defense-depth"
  - "event-driven-guardian"
tags:
  - github-actions
  - yaml-syntax-trap
  - ci-prelint
  - self-bootstrap-blind-spot
  - three-layer-defense
  - quality-gate-architecture
  - workflow-config
  - pytest-static-assertion
---

# 门外守门：入口配置文件的独立 lint 三层防线架构模式

## 模式概述

在 **CI/CD 入口配置文件本身就是调度器**（.github/workflows/*.yml、GitLab CI、Jenkinsfile、docker-compose.yml、Kubernetes manifest）、
且 **"配置文件内部写了一个检查自己的 job"**（如 pages.yml 的 gates job 内有 actionlint）的项目中：

当 **入口文件出现语法错误**（YAML 冒号+空格歧义 / Tab 空格混用 / HCL 缩进错位 等低级错误）
时，**调度层会在解析入口文件时直接拒绝整个文件**，导致"检查配置的那个 job 自己都跑不起来"——
错误信息只显示 `Invalid workflow file: .github/workflows/pages.yml#L82 You have an error in your yaml syntax on line 82`，
无任何上下文，debug 成本是本地 lint 的 5-10×，且反馈周期从秒级变分钟级。

本模式使用 **「入口清单识别 + 三层防线 + pytest 静态扫描断言」** 三组件：

1. **入口识别**：把"能调度别的 job / 能自举"的配置文件列入 `PRELINT_ENTRY_FILES` 清单，区别于普通业务代码 / 普通 yml data 文件
2. **三层防线**（从快到慢，从近到远）：
   - L1 本地 IDE 实时校验（YAML/actionlint 插件，≤ 0.5s 反馈）
   - L2 pre-commit 钩子 / 本地 pytest 扫描（commit 前自动触发，≤ 3s 反馈）
   - L3 独立 preflight job（和被检查的 workflow 解耦，另一套 workflow / 另一个 job 专门 lint 入口文件，≤ 30s 反馈）
3. **pytest 静态扫描**：把"高危 YAML 模式"（未引号字符串内的 `KEY:` + 空格、Tab 缩进、`{{` 与 `}}` 配对缺失）写成 pytest 断言，和 T4b/T5b 等业务回归测试一起跑，模式漏报 = 单元测试直接红

**核心洞察**：质量门的自举悖论（"守门人谁来守门"）在 CI 配置层是真实存在的。把 lint 挪到门外面——入口文件解析之前、独立于 workflow 之外——才能真正拦住。不要把所有安全关在被保护的那扇门里面。

> 模式抽象层级：架构层 L2（architecture-patterns），不限 GitHub Actions；跨 GitLab CI / Docker Compose / Terraform / K8s manifest 通用。
> 成熟度 L1-draft（单案例验证，见文末 SINGLE_CASE_WARNING）

## 问题现象（典型触发场景）

当配置文件内部写了"检查自己"的 job 时，会出现三类假阴性：

| 应用领域 | 问题表现（症状） | 错误信息 |
|---|---|---|
| GitHub Actions `.github/workflows/pages.yml` | CI 界面显示 **Failure**，但是点开 **没有任何 job 运行**，只有 Workflow run summary 区有 1 条 Annotation | `Invalid workflow file: .github/workflows/<job>.yml#LN You have an error in your yaml syntax on line N` |
| GitLab CI `.gitlab-ci.yml` | Pipeline 卡在 `Created` 状态，所有 job 列表为空，只在侧边栏有红色 "YAML syntax error" 气泡 | `(<unknown>): mapping values are not allowed in this context at line N column N` |
| Docker Compose v2 `docker-compose.yml` | `docker compose up` 第一步就死，所有 service 都没起，container/network 全为空 | `yaml.scanner.ScannerError: mapping values are not allowed here` / `expected <block end>, but found '<scalar>'` |
| Terraform HCL `main.tf` | `terraform plan` 在 Setup 阶段直接死，state 未被 lock，Plan 0 行变更 | `Error: Invalid character` / `Error: Extra characters after interpolation expression` |

根因：**入口配置文件是"解析调度器本身的代码"**，它的语法错误会让调度器在"跑第一个 job 之前"就挂掉。
把 actionlint / yamllint 写在同一个 workflow 里 = 把钥匙锁在保险箱内再用这把钥匙开保险箱——逻辑上等号于没有校验。

---

## 触发场景

**✅ 适用于（三条同时满足）：**

1. **入口配置文件 = 调度器**：.github/workflows/*.yml、.gitlab-ci.yml、Jenkinsfile、docker-compose.yml、k8s manifest、terraform `*.tf`（这些文件的解析器 = job 调度器 / runtime 本身）
2. **配置文件规模 > 60 行**：< 60 行肉眼直接扫一遍可；> 60 行后 `冒号+空格 / Tab空格混 / {{ 配对` 等低级错靠不住
3. **团队成员 ≥ 2 人** 会修改这些入口文件：单人 + 小文件可依赖个人习惯；多人协作时不同编辑器默认缩进不同，是这种低级错的高发来源

工程实例：
- GitHub Pages 自动部署流水线（本次 awesome-okf-xs pages.yml 232 行，多 job 多 step 嵌套）
- Monorepo 根目录 `.github/workflows/ci.yml`（8 子包 + 矩阵 + 条件 job）
- Terraform 云基础设施中心仓库（150+ 资源 / 3 个 provider / 多环境 workspace）
- Docker Compose 微服务开发环境（12 service + 3 network + 8 volume）

**❌ 不适用于（任一命中即不推荐）：**

1. 入口文件 < 40 行、单人维护、改完立刻手跑一遍（管理成本 > 三层 lint 成本）
2. 纯粹的 YAML 数据文件（如 OpenAPI spec / i18n translation yml）——不是调度器，没有自举困境
3. 已经使用 Dhall / CUE / Jsonnet 等配置生成器统一生成 YAML（类型系统在生成时已经拦住了 95% 的低级语法错，不需要额外三层防线，仅保留 L1 IDE 即可）

---

## 核心做法（6 步）

### Step 1：建立 `PRELINT_ENTRY_FILES` 清单（项目级）
在 `pyproject.toml` 或 `invoke tasks.py` 中维护一份显式清单，不要靠目录名模糊匹配：
```toml
[tool.okf.prelint]
entries = [
  ".github/workflows/pages.yml",
  ".github/workflows/ci.yml",
]
scanner_rules = [
  "name_unquoted_colon_space",   # name: VALUE 中未引号的 KEY: + 空格  →  报错
  "tab_indent",                  # Tab 缩进（YAML 标准是空格，GitLab CI也推荐空格）
  "jinja2_mustache_unbalanced",  # {{ }} 数量不匹配（GitHub Actions expression 常见错）
]
```

### Step 2：L1 本地 IDE 插件实时校验（人人都装，不装不允许提 PR）
| 入口类型 | 推荐插件（VS Code / JetBrains 通用） | 关键配置项 |
|---|---|---|
| GitHub Actions yml | **GitHub Actions**（official ext）+ **YAML** by Red Hat | `yaml.schemas` → 把 `.github/workflows/*.yml` 关联到 `https://json.schemastore.org/github-workflow.json` |
| 通用 YAML | YAML by Red Hat | `yaml.validate: true` + `yaml.format.enable: true`（保存时自动规范缩进为空格） |
| Docker Compose | Docker（official ext）+ YAML | `yaml.schemas` → `docker-compose*.yml` 关联 `https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json` |
| Terraform HCL | HashiCorp Terraform（official ext）| `terraform.languageServer.enable = true`（保存时自动 fmt + validate） |

### Step 3：L2 pre-commit 钩子 / 本地 pytest 静态扫描（commit 前 ≤ 3s）
在 `.pre-commit-config.yaml` 中增加两层钩子，**优先选 actionlint/yamllint 的原生二进制，不要选 python reimplementation**：
```yaml
  - repo: https://github.com/rhysd/actionlint
    rev: v1.7.7
    hooks:
      - id: actionlint
        types: [yaml]
        files: ^\.github/workflows/.+\.ya?ml$
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        args: ["-d", "{rules: {truthy: disable, line-length: disable, key-duplicates: enable, colon-check: enable, indentation: {spaces: 2, check-mapping-sequence: true}}}"]
```
**同时**把核心规则重写成 pytest 断言（示例：扫描 name 字段未引号冒号+空格），和业务回归一起跑——这是把"临时 lint"沉淀成"不可被忘记的质量约束"。

### Step 4：把高危模式写成 pytest 静态断言（和 T4b/T5b 一样跑 CI）
伪代码示例：
```python
import yaml, re, pytest
PRELINT_ENTRIES = [
    Path(".github/workflows/pages.yml"),
]

@pytest.mark.parametrize("entry", PRELINT_ENTRIES)
def test_prelint_entry_name_no_unquoted_colon_space(entry):
    """name: VALUE 中，若 VALUE 含冒号+空格且未引号 → FAIL（YAML 解析会挂）。"""
    text = entry.read_text(encoding="utf-8")
    for ln, line in enumerate(text.splitlines(), 1):
        m = re.match(r'^(\s*-\s+name:)\s*(.*)$', line)
        if not m:
            continue
        val = m.group(2)
        # 如果值不是以引号开头、且内部存在 ":" + 空格 → 高危
        if val[:1] not in ('"', "'") and re.search(r':\s', val):
            pytest.fail(f"{entry}:{ln}  name 字段值未引号且含冒号+空格: {val[:80]!r}")
```
这类断言的价值：就算团队成员忘了装 pre-commit / 本地 IDE 没启用，CI 的 pytest 一定能拦住。

### Step 5：L3 独立 preflight job（和被检查的 workflow 解耦）
**关键**：这个 preflight job 必须和 pages.yml 是**两个不同的 workflow 文件**，或者如果必须写在同一个文件里，那它必须是**第一个 job 且 `if: always()`**（即使后面语法错也会走到至少解析层，GitHub 在解析 yaml 阶段还是会全挂，所以最佳实践是**另一个 workflow**）。

示例：新建 `.github/workflows/preflight.yml`：
```yaml
name: preflight (workflow self-lint outside of main pages pipeline)
on: [pull_request, push]
jobs:
  prelint:
    runs-on: ubuntu-latest
    timeout-minutes: 3
    steps:
      - uses: actions/checkout@v5
      - uses: rhysd/actionlint@v1
        with:
          files: .github/workflows
          fail-on-error: true
      - name: PyYAML safe_load sanity check (second parser cross-valid)
        run: |
          python -c "
          import yaml, sys, glob
          for f in glob.glob('.github/workflows/*.yml'):
              with open(f, encoding='utf-8') as fh:
                  yaml.safe_load(fh.read())
              print('OK', f)
          "
```
- 选 **两个不同的 YAML 解析器**（actionlint 的 Go yaml.v3 + PyYAML libyaml）交叉验证，避免一个 parser 对某个 edge case 有 bug。
- 这个 job 3 分钟以内必须跑完，比 main pages pipeline 的 gates job（15 min）快 5 倍，是真正的"前置红灯"。

### Step 6：修改入口文件后的 Mandatory Checklist（手动三问）
每次提交修改 PRELINT_ENTRY_FILES 中的文件，提交前手动勾三项（写在 PR 模板里）：
- [ ] **本地跑了一次 `python -c "import yaml; yaml.safe_load(open('<entry>.yml'))"` 零 WARNING**（最小 sanity check，2 秒）
- [ ] **IDE 对修改行附近没有红/黄波浪提示**（L1 防御视觉确认）
- [ ] **`invoke gates.all` / `pytest test_prelint_*` 通过**（L2 防御回归）

---

## ≥3 个反模式（每一个都来自真实踩坑教训）

### 反模式-1：「我在 gates job 里写了 actionlint，所以 workflow 文件的语法错肯定会被拦住」
**后果**：本次 awesome-okf-xs 的实际踩坑。pages.yml 的 gates job 里确实有 actionlint（line 41-45），但 line 82 的 YAML 错让整个 workflow 解析失败，gates job 根本没有被调度的机会——**Actionlint 一次都没运行**，错误直接显示在 Workflow Annotations 顶层。
**纠正法**：actionlint 的运行位置必须 ≥ 一层在 workflow 之外（pre-commit / 独立 preflight.yml），"在同一个 workflow 内"的 actionlint 只能拦非语法类错误（如 secret 泄露、job needs 死循环等）。

### 反模式-2：「我用 VS Code 打开 pages.yml 看起来没红，应该没问题」
**后果**：VS Code YAML 插件默认不会开启 "mapping values ambiguity" 的扫描（因为这属于语法解析层错误，静态提示偶尔漏报，尤其是中文字符 + 半角冒号 + 全角空格混排场景）。本次 line 82 的 `L2-A: 仅单文件` 在某些字体下中文字符的全角/半角边界模糊，插件会漏判。
**纠正法**：IDE 无红波浪 ≠ 解析通过。必须加一道 `yaml.safe_load()` 的真正解析，这是"最终真相"。

### 反模式-3：「CI 红了我再查嘛，反正构建也就 2 分钟」
**后果**：入口文件的语法错反馈链路 = push → GitHub runner 调度 → 解析 workflow → 报错，实际耗时 30s-2min。更糟糕的是错误信息**只有行号 + 一句"yaml syntax error"**，没有列号、没有上下文、没有建议修复，debug 时需要自己打开文件一行行数列号或者本地跑 safe_load 才能定位，总耗时从本地 lint 的 2 秒变到线上 3-15 分钟。且如果是多人同时提 PR，一个人的低级错会阻塞后面所有人。
**纠正法**：三层防线把错误拉回本地秒级。时间成本：本地 2s × 100 次提交 = 200s；线上 10min × 1 次踩坑 = 600s。明显前者更省。

### 反模式-4：「bash 的 $d 只是循环变量，写在 ${{ steps.*.outputs.$d }} 里挺方便的」
**后果**：本次 awesome-okf-xs 的连续第二个坑（VC-11，Run 47 `Unexpected symbol: '$d'`）。GitHub Actions 的执行时序是：**先整体做 GHA expression 解析（处理所有 `${{ ... }}`），再把结果送 bash/sh 执行**。因此 `${{ }}` 内的所有字符都必须是合法的 GHA 字面量/标识符，**绝对不能出现 bash 层的动态变量语法（`$d` / `$VAR` / `${VAR}`）**——GHA parser 遇到 `$d` 根本不认识它，直接报 "Unexpected symbol"。哪怕你在 shell 层面 `eval` 包装也绕不过，因为 shell 还没来得及跑，expression 层已经挂了。
**纠正法**：① 先用 **字面量键名展开** 把所有可能用到的 `${{ steps.*.outputs.<literal> }}` 一次赋值给独立 bash 变量（`OUT_meta=...`、`OUT_guoxue=...` 九条），② 再在 bash 循环里用**间接引用**取到值（`_v="OUT_$d"; CHANGED="${!_v}"`），彻底把 expression 层和 shell 层切断，绝不让跨层嵌套发生。

### 反模式-5：「我只是把 ${{ }} 写在 bash 注释里，GHA 不会处理注释的吧」
**后果**：本次 awesome-okf-xs 的连续第三个坑（Run 48 `An expression was expected`，Line 141 Col 14）。**GHA expression parser 工作在 YAML 字符串层面，根本不理解 bash 注释语法**——它只做字符串级别的模式匹配，只要在 run 块里扫到 `${{` 就会尝试解析成 expression，无论你这一行前缀有没有 `#`。所以即使是在 bash `# 注释` 里写的 `${{ }}`，GHA parser 也会真实去求值；如果里面没有合法 expression 内容（空的 `}}` 截断或乱码），就会报 "An expression was expected"。IDE 的 shell 语法高亮永远不会在这里提示你有问题。
**纠正法**：在整个 `run: |` 块内（包括注释行），把 **"GHA 表达式"这五个汉字** 当作字面量 `${{ }}` 的替代表述；如果你一定要写标记示例（比如说明文档），必须把 `${` 中间断开（`$ { {`、`\${{` 或者先在表达式外拼接），让 GHA 模式匹配器匹配不到。经验法则：**run 块内的任何位置出现 `${{`，GHA 都会解析，不区分 code / comment / heredoc**。

### 反模式-6：「我用的 action 是 Docker 类型的，跟 Composite/Node 一样可以自定义 with 键吧」
**后果**：本次 awesome-okf-xs 的连续第五个坑（Run 49 gates job L41-L45，"Unexpected input(s) 'files', 'fail-on-error', valid inputs are ['entryPoint', 'args']"）。**Docker Container Action（`runs.using: docker`）的 `with:` 块只允许 2 个合法键：`entryPoint`（覆盖容器入口点）和 `args`（传给 CLI 的参数字符串）**——它没有 `inputs:` 声明机制，任何你自定义的键（如 `files`/`fail-on-error`/`verbose` 等）GHA 都会报 WARNING，并在严格模式下直接让 setup 阶段失败。本次把 `rhysd/actionlint@v1.7.12` 当成 Composite Action 写了两个自定义键，导致 gates job 的后续 4 个 step（setup-python / install deps / UTF-8 gate / toctrees gate / bundles gate）全部被跳过，完整质量门一次都没运行，整次 run 因 setup 类 WARNING 被标记 Failure。
**纠正法**：
1. **三问 uses**：`uses:` 任何第三方 action 前先打开它的 `action.yml` 看 `runs.using` 字段：
   - `using: docker` → with 块**仅**允许 `entryPoint` / `args`，想传 flag 和路径全部塞到 `args: '-flag1 -flag2 path/to/scan'` 一个字符串里
   - `using: composite` → with 键由顶层 `inputs:` 声明决定，只能用声明过的 key 名
   - `using: node16/node20` → with 键同样由顶层 `inputs:` 声明决定
2. **fail-on-error 无需额外键**：Docker Action 的 CLI 默认非零退出码就会让 step 失败，这正是你想要的 "lint 出错误就拦构建"；如果想只收集不拦截，在 `args:` 里传 `-no-fail` 类参数，不要在 with 块里发明自定义键。
3. **路径参数放到 args**：原来写 `files: .github/workflows` 等价于 `args: '<其它flag> .github/workflows'`，容器会把 args 整条字符串拼接在入口点命令后面。
4. **pytest 静态加固**：在 `test_prelint_actions_with_keys.py` 里加一条 T 级规则：当 `uses:` 匹配 `*/actionlint@*` / 其他已知 Docker Action 名单时，白名单仅允许 `{entryPoint, args}` 两键，CI 本地拦截而不等到 push 到 GitHub 才 WARNING。

---

## 明确检验标准（做完怎么知道做对了）

| # | 检验项 | 通过标准 | 工具/方法 |
|---|---|---|---|
| V1 | 所有 `PRELINT_ENTRY_FILES` 能被 PyYAML safe_load | 0 WARNING 0 ERROR，返回 dict 对象 | `python -c "import yaml, pathlib; [yaml.safe_load(pathlib.Path(f).read_text()) for f in ENTRIES]"` |
| V2 | actionlint + yamllint 两个不同实现的 lint 都零错误 | 两者 exit code = 0 | pre-commit run / CI preflight job |
| V3 | pytest 静态扫描 ≥ 3 条高危规则全部通过（name 冒号空格、Tab 缩进、{{ 不配对）| 所有 `test_prelint_*` 用例 PASS | pytest 集成测试报告 |
| V4 | 最近 5 次提交入口文件变动，GitHub annotations 没有出现 `Invalid workflow file` | 检查最近 5 次 CI 的 annotations 页 | GitHub UI / gh cli |
| V5 | pre-commit 钩子清单中至少包含 1 个 YAML / actionlint 类钩子 | `.pre-commit-config.yaml` 中存在对应 repo/id | grep / cat |

---

## 跨领域迁移示例（≥1 个非本领域）

### 迁移场景：Terraform 基础设施中心仓库（非 GitHub Actions 领域）
OKF 模式原样迁移，名词替换：
- 原「GitHub Pages workflow 文件」 → 替换为 「Terraform `aws/*.tf` / `gcp/*.tf` 环境 manifest」
- 原「gates job 内的 actionlint」 → 替换为 「`terraform validate` 命令（它需要先 init 后端 + 下载 provider，而 syntax error 会让 init 直接死）」
- 原「PyYAML safe_load 交叉解析」 → 替换为 「`hcl2json < main.tf`（Go 实现 HCL parser，和 Terraform 内部 parser 是同一个库，交叉验证）」
- 原「pytest 静态 name 字段扫描」 → 替换为 「pytest 扫描 `resource "` 行的字符串引号配对（HCL heredoc 常被漏写终止符）」

迁移后三层防线完全同构：L1 HashiCorp Terraform VS Code 插件实时 fmt + validate；L2 pre-commit 的 `terraform fmt --check` + `tflint` 钩子 + pytest 断言；L3 独立 `.github/workflows/tf-preflight.yml` 在 plan 前先做 fmt / tflint / hcl2json 三重检查，把错误从 plan 阶段（3-8 min）提前到 preflight 阶段（30s）。

### 迁移场景：Docker Compose 微服务开发环境（非 CI 领域）
- 原「workflow 文件 yaml syntax」 → 替换为「`docker-compose.tests.yml` services 段的 YAML」
- 原「冒号+空格歧义」 → 替换为「environment 段的 `KEY=VALUE` 等号和 YAML 冒号冲突」
- 三层防线映射为：L1 Docker 官方插件 schema 校验；L2 yamllint + `docker compose config` 静态解析（不启动任何 container）；L3 独立 `compose-config.yml` workflow 在 PR 时跑 `docker compose config --quiet`。

---

## ≥2 案例支撑 → 成熟度 L1（下一版本 L2 待增补第 2 案例）

### 案例-1（本案例，已验证 ✅）
| 项 | 值 |
|---|---|
| 项目 | awesome-flexloop/awesome-okf（GitHub 开源仓库）|
| 入口文件 | `.github/workflows/pages.yml`，版本：commit 4676119 |
| 错误位置 | line 82 / column 57 |
| 错误原文 | `mapping values are not allowed here`，触发 token：`L2-A: 仅` |
| 触发方式 | push main 分支（合并操作 `Merge branches 'main' and 'main'`）|
| 修复前 | `  - name: Cache Sphinx environment.pickle (P1-D L2-A: 仅单文件 + 精确key + 7d)` |
| 修复后 | `  - name: "Cache Sphinx environment.pickle (P1-D L2-A: 仅单文件 + 精确key + 7d)"` |
| 交叉验证 | PyYAML safe_load：4 jobs 解析成功；T4b/T5b/T6c/T8 共 4 项 pytest 全部 PASSED（0.19s） |
| 本次模式采纳 | 采纳 Step 1（PRELINT_ENTRIES 清单） + Step 4（pytest `test_prelint_entry_name_no_unquoted_colon_space`）+ Step 6 手动三问（commit message 附 `[prevent: test-case]`） |

### SINGLE_CASE_WARNING（L1-draft 成熟度标注）
> ⚠️ 本模式当前仅有 1 个实战案例支撑，抽象边界、反模式清单、迁移适用性的普适性未在 ≥2 异质项目中独立验证。复用前请在目标项目中先执行 **dry-run 对照**：把 Step 3-5 的三层防线搭起来但不拦截（只 WARNING 不 FAIL）观察 20 次提交中高危模式的实际命中频次，再决定是否打开 FAIL 开关。新增 ≥1 异质项目案例后，可提交 PR 将 maturity 升级为 `L2-validated`。

---

## 关联阅读（复用链）

- 本模式的 pytest 断言技术：参考 [checklist-to-assertion-conversion](../code-patterns/checklist-to-assertion-conversion.md)（把人工 checklist 转化为自动化 pytest 静态扫描的通用模式）
- 本模式的三层防御理念：参考 [full-process-defense-depth](full-process-defense-depth.md)（架构治理的全流程防御深度通用原则）
- 本模式的 preflight 思想：参考 [preflight-checks-script](../code-patterns/preflight-checks-script.md)（"跑业务代码前先跑独立前置检查"的脚本通用骨架）
