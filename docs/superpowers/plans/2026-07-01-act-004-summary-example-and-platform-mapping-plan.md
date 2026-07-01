# ACT-004 发布摘要真实示例与平台语义映射轻量抽象 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为真实 `xlsx` 样本生成正式发布摘要示例，并把现有平台语义映射整理为更清晰、可扩展但行为兼容的轻量配置结构。

**Architecture:** 先通过真实工作簿风格的失败测试锁定摘要示例产物与 `平台影响面` 的期望输出，再对 `.agents/scripts/analyze-xlsx-test-report.py` 中的平台语义映射做轻量抽象，保持现有摘要章节顺序、发布判断口径和 `context` 字段兼容。最后使用真实样本文件生成正式 Markdown 产物，并把产物沉淀到已有 Tuya/XLSX 复盘目录中。

**Tech Stack:** Python、pytest、openpyxl、Markdown、现有 `.agents/scripts` 测试体系

---

## 文件结构

### 新增文件

- `docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.md`

### 修改文件

- `.agents/scripts/analyze-xlsx-test-report.py`
- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

### 参考文件

- `docs/retrospective/templates/release-gate-summary-template.md`
- `docs/superpowers/specs/2026-07-01-act-004-summary-example-and-platform-mapping-design.md`

---

### Task 1: 用真实工作簿风格锁定摘要示例输出

**Files:**
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/analyze-xlsx-test-report.py`

- [ ] **Step 1: 添加真实工作簿风格的失败测试**

在 `test_analyze_xlsx_test_report.py` 末尾追加以下测试：

```python
def test_cli_writes_realistic_summary_with_platform_impact(tmp_path) -> None:
    workbook_path = build_realistic_overview_workbook(tmp_path / "realistic-summary.xlsx")
    full_output = tmp_path / "full.md"
    summary_output = tmp_path / "summary.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--input",
            str(workbook_path),
            "--output",
            str(full_output),
            "--summary-output",
            str(summary_output),
            "--summary-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 0
    assert summary_output.exists()
    content = summary_output.read_text(encoding="utf-8")
    assert "## 结论摘要" in content
    assert "## 平台影响面" in content
    assert "- 弱网" in content or "- 音频" in content
    assert "cloud_push" in content
    assert "status / function" in content
```

- [ ] **Step 2: 运行测试确认红灯**

Run: `python -m pytest d:\AI\.agents\scripts\tests\test_analyze_xlsx_test_report.py -k "realistic_summary_with_platform_impact" -v`

Expected: FAIL，原因应为真实工作簿摘要输出尚未满足断言，或现有实现的字段/格式与测试期望不一致。

- [ ] **Step 3: 如测试直接通过，收紧断言让它真正锁定新产物规则**

将断言补充为必须同时包含以下内容：

```python
assert "## Top 风险" in content
assert "## 阻塞项" in content
assert "`tuya`.camera" in content
```

Run: `python -m pytest d:\AI\.agents\scripts\tests\test_analyze_xlsx_test_report.py -k "realistic_summary_with_platform_impact" -v`

Expected: FAIL；若仍通过，说明真实产物规则已被现有实现完全覆盖，可跳过本步骤并在执行记录中注明“红灯已被现有能力满足”。

---

### Task 2: 为平台语义映射增加可测试的轻量抽象层

**Files:**
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`

- [ ] **Step 1: 先写抽象层失败测试**

在测试文件中追加以下用例：

```python
def test_get_platform_semantic_profile_merges_defaults() -> None:
    report = load_report_module()

    profile = report.get_platform_semantic_profile("弱网")

    assert profile is not None
    assert profile["ha_domain"] == "tuya"
    assert profile["entity_scope"] == "camera"
    assert profile["integration_traits"] == ("hub", "cloud_push")
    assert "diagnostics" in profile["observation_surfaces"]
```

- [ ] **Step 2: 运行测试确认红灯**

Run: `python -m pytest d:\AI\.agents\scripts\tests\test_analyze_xlsx_test_report.py -k "get_platform_semantic_profile_merges_defaults" -v`

Expected: FAIL，原因应为 `get_platform_semantic_profile` 尚不存在。

- [ ] **Step 3: 在脚本中引入默认配置和风险配置拆分**

把当前 `PLATFORM_SEMANTIC_MAP` 重构为以下两层结构：

```python
PLATFORM_SEMANTIC_DEFAULTS = {
    "ha_domain": "tuya",
    "entity_scope": "camera",
}

PLATFORM_RISK_PROFILES = {
    "重启恢复": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "status_range", "diagnostics"),
        "diagnostic_focus": "优先核对设备在线状态恢复、关键 DP 状态刷新与诊断导出中的异常恢复痕迹。",
    },
    "弱网": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "diagnostics"),
        "diagnostic_focus": "结合实体状态刷新延迟、云侧推送连续性与诊断字段，复核弱网下的重连与状态同步风险。",
    },
    "存储回放": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "重点映射录像、回放和存储相关能力字段，确认平台侧是否能观测到存储异常。",
    },
    "音频": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "结合摄像头实体能力与诊断字段，复核音视频相关功能项是否存在异常状态或能力缺口。",
    },
    "升级稳定性": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "diagnostics", "token_info"),
        "diagnostic_focus": "复核升级后的在线状态恢复、云侧令牌续期与设备诊断信息是否保持稳定。",
    },
    "预览稳定性": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "重点关注实时预览相关实体能力、状态变化和功能范围，确认平台侧是否能反映画面链路异常。",
    },
}
```

- [ ] **Step 4: 增加抽象访问函数**

在 `analyze-xlsx-test-report.py` 中新增：

```python
def get_platform_semantic_profile(risk_label: str) -> dict[str, object] | None:
    profile = PLATFORM_RISK_PROFILES.get(risk_label)
    if profile is None:
        return None
    return {
        "ha_domain": PLATFORM_SEMANTIC_DEFAULTS["ha_domain"],
        "entity_scope": PLATFORM_SEMANTIC_DEFAULTS["entity_scope"],
        "integration_traits": profile["integration_traits"],
        "observation_surfaces": profile["observation_surfaces"],
        "diagnostic_focus": profile["diagnostic_focus"],
    }
```

- [ ] **Step 5: 让 `build_platform_semantic_mapping()` 改为消费抽象访问函数**

将函数主体改成：

```python
def build_platform_semantic_mapping(risk_clusters: list[str]) -> list[dict[str, object]]:
    mappings: list[dict[str, object]] = []
    for label in risk_clusters[:5]:
        semantic = get_platform_semantic_profile(label)
        if semantic is None:
            continue
        mappings.append({"risk_label": label, **semantic})
    return mappings
```

- [ ] **Step 6: 运行两条测试确认转绿**

Run: `python -m pytest d:\AI\.agents\scripts\tests\test_analyze_xlsx_test_report.py -k "get_platform_semantic_profile_merges_defaults or realistic_summary_with_platform_impact" -v`

Expected: PASS

---

### Task 3: 用真实样本生成正式示例摘要产物

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Create: `docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.md`

- [ ] **Step 1: 确定真实示例产物路径常量只用于命令层，不写死到脚本默认输入**

不要给脚本新增固定输入路径。仅在执行命令时使用以下目标路径：

```text
d:\AI\docs\retrospective\reports\insight-extraction\retrospective-tuya-projects-for-xlsx-agentization-20260701\example-release-gate-summary-20260327.md
```

- [ ] **Step 2: 运行真实样本生成命令**

Run:

```bash
python .agents/scripts/analyze-xlsx-test-report.py --input "d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx" --output "d:\AI\.temp\ignore-full-report.md" --summary-output "d:\AI\docs\retrospective\reports\insight-extraction\retrospective-tuya-projects-for-xlsx-agentization-20260701\example-release-gate-summary-20260327.md" --summary-only
```

Expected:
- 退出码 `0`
- 生成 `example-release-gate-summary-20260327.md`
- 不生成 `d:\AI\.temp\ignore-full-report.md`

- [ ] **Step 3: 检查真实产物内容是否满足最低标准**

打开生成文件，确认至少包含以下文本片段：

```text
## 结论摘要
## Top 风险
## 阻塞项
## 平台影响面
## 复测建议
```

以及至少一条类似以下形式的平台影响面：

```text
- 弱网: `tuya`.camera (特征: hub / cloud_push; 观察面: status / function / diagnostics)
```

- [ ] **Step 4: 若真实产物过长，仅微调摘要展示层，不改上下文字段**

允许调整的唯一代码位置：

```python
def format_platform_impact_lines(platform_mapping: list[dict[str, object]]) -> str:
    ...
```

允许的最小改法示例：

```python
for item in platform_mapping[:2]:
    ...
```

或：

```python
surfaces = " / ".join(str(value) for value in item["observation_surfaces"][:2])
```

不允许修改：
- `extract_report_context()`
- `release_judgment`
- `risk_clusters`

---

### Task 4: 全量回归与收尾验证

**Files:**
- Verify: `.agents/scripts/analyze-xlsx-test-report.py`
- Verify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Verify: `docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.md`

- [ ] **Step 1: 跑完整脚本测试集**

Run: `python -m pytest d:\AI\.agents\scripts\tests\test_analyze_xlsx_test_report.py -v`

Expected: 全部 PASS

- [ ] **Step 2: 检查诊断**

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/analyze-xlsx-test-report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/tests/test_analyze_xlsx_test_report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.md)`
Expected: 无诊断错误

- [ ] **Step 3: 检查示例产物与设计文档一致**

核对以下约束：

```text
1. 真实摘要中包含“平台影响面”
2. 平台影响面只展示风险标签、域/实体范围、集成特征、关键观察面
3. 未修改 DI / 严重问题数门槛
4. 未引入新的风险类别
```

- [ ] **Step 4: 原子提交**

```bash
git add .agents/scripts/analyze-xlsx-test-report.py .agents/scripts/tests/test_analyze_xlsx_test_report.py docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.md docs/superpowers/specs/2026-07-01-act-004-summary-example-and-platform-mapping-design.md docs/superpowers/plans/2026-07-01-act-004-summary-example-and-platform-mapping-plan.md
git commit -m "feat(xlsx): 补齐真实摘要示例并整理平台语义映射"
```

Expected: 生成单一职责提交，覆盖“真实摘要示例 + 平台映射轻量抽象”。

---

## 自检结论

### Spec 覆盖

- 真实 `summary.md` 示例产物：Task 1、Task 3 覆盖
- 平台语义映射轻量抽象：Task 2 覆盖
- 行为兼容与测试回归：Task 1、Task 4 覆盖
- 不修改发布判断口径与风险类别：Task 3、Task 4 的约束检查覆盖

### 占位符扫描

- 无 `TBD` / `TODO`
- 所有修改文件、命令、目标产物路径与预期结果均已明确
- 所有代码变更步骤均附带了实际代码片段

### 类型与命名一致性

- 抽象访问函数固定命名为 `get_platform_semantic_profile`
- 真实示例产物固定命名为 `example-release-gate-summary-20260327.md`
- `platform_semantic_mapping` 字段继续作为渲染输入，不改名
