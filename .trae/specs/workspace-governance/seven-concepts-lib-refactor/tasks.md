# seven-concepts-cmd 三层分离重构 - The Implementation Plan

## [x] Task 1: 创建目录结构与领域层 - 常量与模型 ✅
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目录 `.agents/scripts/lib/seven_concepts/`
  - 创建 `__init__.py`（占位，后续导出API）
  - 创建 `constants.py`，迁移 CONCEPTS/WORKFLOWS/QUALITY_GATES/ANTI_PATTERN_WARNINGS 字典
  - 创建 `models.py`，迁移 MatchResult dataclass
  - 所有迁移内容原样复制，不修改逻辑
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: `python -c "from lib.seven_concepts.constants import CONCEPTS; print(len(CONCEPTS))"` 输出 7，无错误
  - `programmatic` TR-1.2: `python -c "from lib.seven_concepts.models import MatchResult; m = MatchResult(scenario='test', confidence=90, concepts=['R'], workflow=None); print(m.scenario)"` 输出 test
  - `human-judgement` TR-1.3: 检查 constants.py 和 models.py 中没有 import argparse/sys，没有 print() 调用

## [x] Task 2: 迁移核心匹配逻辑到 matcher.py（纯函数） ✅
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `matcher.py`
  - 将原 seven-concepts-trigger.py 的 `match_task(text)` 函数原封不动迁移
  - 修正import：从 `.constants` 和 `.models` 导入依赖
  - 创建 `scenarios.py`，迁移场景列表数据（从list_scenarios中提取数据部分）
  - 保证纯函数：相同输入→相同输出，无副作用
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: `python -c "from lib.seven_concepts.matcher import match_task; r = match_task('Sprint结束做复盘'); print(r[0].scenario, r[0].confidence)"` 输出包含"里程碑"，置信度95
  - `programmatic` TR-2.2: 调用 match_task 不产生任何stdout输出（通过capsys或重定向验证）

## [x] Task 3: 迁移渲染层到 formatters.py（纯格式化，不直接print） ✅
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `formatters.py`
  - 迁移原print_result为 `format_match_result(result, index=0) -> str`（返回字符串而非print）
  - 迁移原list_scenarios的渲染部分为 `format_scenario_list() -> str`（返回字符串）
  - 可添加 `format_match_result_dict(result) -> dict` 为后续JSON输出预留
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: format_match_result 返回的字符串包含 "🎯 场景"、"置信度"、"概念组合" 等关键字段
  - `human-judgement` TR-3.2: formatters.py 中没有直接调用 print() 或 argparse

## [x] Task 4: 更新 __init__.py 导出公开API ✅
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 更新 `__init__.py`，导出稳定公开API：
    MatchResult, match_task, format_match_result, format_scenario_list,
    CONCEPTS, WORKFLOWS, QUALITY_GATES, get_all_scenarios
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: `python -c "from lib.seven_concepts import match_task, MatchResult; print('ok')"` 输出 ok

## [x] Task 5: 将原入口脚本改造为薄CLI壳 ✅
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 保留 seven-concepts-trigger.py 文件名
  - 删除已迁移代码，只保留平台层：
    - 头部添加项目标准 sys.path 设置
    - create_parser() 保留（argparse属平台层）
    - main() 改为调用 lib 层函数
    - 使用 lib.cli 的共享输出工具（如适用）
  - 最终有效代码行数 < 100行
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: `python .agents/scripts/seven-concepts-trigger.py "Sprint结束做复盘"` 正常输出场景结果
  - `programmatic` TR-5.2: `python .agents/scripts/seven-concepts-trigger.py --list` 正常列出所有场景
  - `programmatic` TR-5.3: `python .agents/scripts/seven-concepts-trigger.py --top 2 "重构加复盘"` 返回前2个结果
  - `programmatic` TR-5.4: 有效代码行数统计 < 100（不含空行/注释）

## [x] Task 6: 运行现有黑盒测试验证等价性 ✅
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行 `python .agents/scripts/test-seven-concepts-trigger.py`
  - 保证所有19个测试用例100%通过
  - 如有输出格式小差异导致失败，微调formatters使其与原格式兼容
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 测试脚本输出 "准确率：19/19 = 100%"，exit code 0

## [x] Task 7: 新增领域层单元测试 ✅
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 新建 `.agents/scripts/tests/test_seven_concepts_lib.py`
  - 直接import lib.seven_concepts写单元测试，不用subprocess：
    - 测试每个核心场景（W1-W5、P0、简单修改、无匹配等）匹配正确
    - 测试边界情况（空字符串、中英混合）
    - 测试置信度排序
    - 测试MatchResult字段完整性
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 运行 `pytest .agents/scripts/tests/test_seven_concepts_lib.py -v` 全部通过
  - `programmatic` TR-7.2: 测试文件中没有 subprocess.run 调用
