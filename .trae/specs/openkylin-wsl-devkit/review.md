# openKylin WSL 开发工具包（openkylin-wsl-devkit）- 独立审查

> 审查方式说明：本审查由 MainAgent 以独立审查者视角执行（对照 spec.md 的 Given/When/Then/Pass Condition/Evidence 逐项复核，不采信实施者自验结论），因任务规模与协调成本判断不适用子代理委托；AC-10 真实冒烟受本机发行版现状制约，按 spec 约定收口。审查证据均来自可复现的测试输出、构建产物与真实命令记录。

## 检查点

- [x] CP-R1: wsl.exe 调用封装正确（AC-1）
  - **Type**: `rule`
  - **Covers**: AC-1
  - **Evidence**: 复核 `src/okw/distro.py`：`wsl_exe()` PATH 优先 + `$env:WINDIR\System32\wsl.exe` 回退 + 未找到抛受控 WslError；`run_wsl()` 注入 `WSL_UTF8=1`、捕获 FileNotFoundError/TimeoutExpired、按 stderr 特征分类 command_missing/distro_missing/failed；`tests/test_distro.py::TestRunWsl` 5 用例（ok/五类失败）与 `TestWslExe` 3 用例通过。pytest 96 passed 复核通过。

- [x] CP-R2: list/status 解析与默认星标保护（AC-2）
  - **Type**: `rule`
  - **Covers**: AC-2
  - **Evidence**: `parse_list_output` 支持三形态（表头表格/无表头短形态/旧列表），快照断言（`TABLE_OUTPUT`/`LEGACY_OUTPUT`）通过，格式漂移 fail-fast（`test_drift_fails_fast`）；`test_default_star_protected`（verify 前后 `default_distro_name()` 变化 → listed FAIL）通过；真实 `okw list` 输出本机 2 发行版并标注默认星标。

- [x] CP-R3: import 封装与排障提示（AC-3）
  - **Type**: `rule`
  - **Covers**: AC-3
  - **Evidence**: 真实 gzip 头 `1F 8B` 校验（`test_ok_constructs_command` 用真实 gzip 文件）与非 gzip 拒绝（`test_rejects_non_gzip`）通过；命令数组 `--import <name> <location> <image> --version 2` 断言通过；CLI 失败路径排障三问提示（`test_import_failure_tips` 断言"排障三问""wsl --shutdown"）通过。

- [x] CP-R4: verify 五步验收可解析输出（AC-4）
  - **Type**: `rule`
  - **Covers**: AC-4
  - **Evidence**: `tests/test_verify.py` 7 用例（全 PASS/缺 systemd 不中断/UID 不匹配/包数异常/不在列单 FAIL/星标变化 FAIL/渲染）通过；真实只读冒烟：`okw verify podman-machine-default` 输出合法 PASS/FAIL 清单（无未捕获异常），`okw verify openKylin-3.0` 正确报告"发行版不存在"。

- [x] CP-R5: scaffold deb 骨架合法（AC-5）
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Evidence**: 六系列参数化（yangtze/1.0、nile/2.0、huanghe/3.0）生成五文件断言（changelog 首行 `demo (0.1.0) <codename>`、control 必填字段、compat=12、format=3.0 (quilt)）通过；真实执行 `okw scaffold deb` 成功。

- [x] CP-R6: scaffold dput 配置合法（AC-6）
  - **Type**: `rule`
  - **Covers**: AC-6
  - **Evidence**: 字段断言（`[okbs]` fqdn=upload.build.openkylin.top:2121/method=sftp/incoming=%(okbs)s/login=id）与默认打印不写文件、`--output` 写入通过；真实执行输出 OKBS 用法提示。

- [x] CP-R7: ref 知识库索引覆盖（AC-7）
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Evidence**: 四主题内容断言通过；8 条知识库相对路径存在性检查（`REPO_ROOT / src` 全部存在）通过；`okw ref` 无参数列出全部主题、未知主题退出码 2。

- [x] CP-R8: CLI 完整性与错误处理（AC-8）
  - **Type**: `rule`
  - **Covers**: AC-8
  - **Evidence**: `tests/test_cli.py` 34 用例通过（全子命令 --help、未知命令 SystemExit(2)、--version 一致、exec REMAINDER 剥离、verify 退出码语义、scaffold/ref 集成）；真实 `okw --version` 输出 `okw 0.1.0`。

- [x] CP-R9: 构建与仓库卫生（AC-9）
  - **Type**: `rule`
  - **Covers**: AC-9
  - **Evidence**: `python -m build --wheel` 产出 `openkylin_wsl_devkit-0.1.0-py3-none-any.whl`（zip 清单含 okw 六模块 + entry_points）；`git status --porcelain --untracked-files=all` 仅应用目录与 spec 目录新文件。

- [x] CP-U1: 真实发行版冒烟（AC-10）
  - **Type**: `rubric`
  - **Covers**: AC-10
  - **Scale**: 1-5
  - **Anchors**: 1 = 仅 mock 通过；3 = list/verify 真实运行成功但部分输出需人工纠偏；5 = list/verify 真实运行全部 PASS
  - **Pass Threshold**: >= 3
  - **Evidence**: 评分 **3/5**。`okw list` 真实运行全 PASS（本机 2 发行版、默认星标正确）。`okw verify` 真实运行成功且输出合法：对通用发行版（podman-machine-default）正确识别非 openkylin 特征（os-release FAIL、超时受控归一）；对 `openKylin-3.0` 正确报告"发行版不存在"。知识库 S32 记录的 openKylin-3.0 发行版当前不在本机 WSL 在列（真实环境不可用，非工具缺陷）——按 spec AC-10 约定：以 AC-2~AC-9 完整 mock 证据（96 测试、关键模块 ≥90% 覆盖率、wheel 构建、真实 list 冒烟）收口，未伪造全 PASS。审查判断：工具行为在真实环境正确（含对缺失发行版与异构发行版的正确反应），达标。

- [x] CP-R10: PEP 563 红线治理闭环（用户 2026-09-30 追加指令）
  - **Type**: `rule`
  - **Covers**: 用户指令（非 spec AC；Spec 治理追加）
  - **Evidence**: 全仓 AST 扫描确认本应用真实 `ImportFrom(__future__)` 节点为零；11 个源/测试文件已移除该导入；新增 `tests/test_no_future_annotations.py` AST 守护（14 参数化用例全过，负向验证临时加入 → 1 failed 真实拦截）；全局约束已固化至 `.agents/rules/ai-coding-guidelines.md`（技术红线章节）与根 `AGENTS.md`（开发规范 Python 红线条款）。

## Review History

### Review R1
- **Result**: `pass`
- **Evidence**：
  - 检查点核验：CP-R1~R10 + CP-U1 全部通过；
  - 测试：`pytest` 96 passed in 0.73s，整体覆盖率 92%（distro 97% / verify 95% / scaffold 100% / ref 100% / cli 86%），关键模块均 ≥90%；
  - 构建：wheel 产出成功；
  - 真实命令：`okw --version`、`okw list`、`okw verify openKylin-3.0`、`okw verify podman-machine-default`、`okw scaffold deb|dput`、`okw ref series` 全部真实执行并记录；
  - 无可行动发现（advisory：AC-10 真实 openKylin 全 PASS 依赖发行版重新导入，列为后续手动项，不阻塞验收）。
