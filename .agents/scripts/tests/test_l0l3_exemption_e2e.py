"""L0-L3 模板探针豁免规则端到端验证测试。

本测试文件验证 stage-guardrails.md §04「L0 探针豁免规则」中描述的豁免逻辑
在 L0-L3 模板实际使用场景中的端到端表现。测试场景对应 L0-L3 模板 §10 中的
使用示例和 §3.3 / §8.3 中的豁免规则定义。

覆盖的场景：
1. L0-L3 模板 §10.1 侧边栏群聊探针（L0 探索级）
2. .temp/baby/ 目录探针（路径识别）
3. 跨阶段探针操作（L0 可在任何阶段操作）
4. 探针升级后重新进入标准流程
5. 规则文档一致性验证（04-interception-approval.md / 05-logging-spec.md）
6. 豁免限制验证（baby_code=False / 正常代码 / 绕过检测）
"""

import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrails import (
    GuardrailRuntime,
    OperationType,
    is_baby_code,
)


@pytest.fixture
def rt():
    """创建一个新的 GuardrailRuntime 实例，默认进入 S1 阶段。"""
    runtime = GuardrailRuntime(session_id='e2e-l0l3-test', enable_bypass_detection=True)
    runtime.enter_stage('S1', 'orchestrator', 'L0-L3 端到端验证起点')
    return runtime


class TestScenario1SidebarChatProbe:
    """场景 1：L0-L3 模板 §10.1 侧边栏群聊探针（L0 探索级）。

    模拟模板 §10.1 的使用示例：
    - 假设：侧边栏群聊能提升协作效率
    - 探针代码：baby-sidebar-chat-probe.tsx
    - 期望：探针代码在 S1 需求阶段编写时不被拦截
    """

    def test_production_code_in_s1_is_intercepted(self, rt):
        """对照实验：S1 阶段编写正式生产代码应被拦截。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='编写侧边栏生产代码',
            file_path='src/components/Sidebar.tsx',
        )
        assert out.is_intercept is True, '正式代码在S1阶段应被拦截'
        assert out.event_type == 'INTERCEPT'

    def test_probe_code_via_baby_prefix_exempted(self, rt):
        """核心验证：S1 阶段编写 baby- 前缀探针代码应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='编写侧边栏群聊探针代码',
            file_path='baby-sidebar-chat-probe.tsx',
        )
        assert out.is_intercept is False, 'baby- 前缀探针代码应被豁免'
        assert out.event_type == 'BOUNDARY_PASS'
        assert 'baby_code' in out.sg_log_line
        assert 'true' in out.sg_log_line.lower()

    def test_probe_code_via_explicit_baby_flag(self, rt):
        """显式 baby_code=True 也应豁免（即使文件名不含 baby- 前缀）。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='探针实验：侧边栏群聊交互验证',
            baby_code=True,
        )
        assert out.is_intercept is False
        assert out.event_type == 'BOUNDARY_PASS'

    def test_probe_does_not_increase_interception_count(self, rt):
        """探针豁免不应增加拦截计数。"""
        before = rt.interception_count
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='侧边栏探针', baby_code=True,
        )
        assert rt.interception_count == before

    def test_probe_sg_log_contains_baby_code_field(self, rt):
        """SG-LOG 必须包含 baby_code: true 字段（05-logging-spec.md 要求）。"""
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='侧边栏探针', file_path='baby-sidebar-chat-probe.tsx',
        )
        check_logs = rt.get_logs_since(event_type='BOUNDARY_CHECK')
        pass_logs = rt.get_logs_since(event_type='BOUNDARY_PASS')
        assert any('baby_code' in line for line in check_logs), \
            'BOUNDARY_CHECK 日志应包含 baby_code 字段'
        assert any('baby_code' in line and 'true' in line for line in pass_logs), \
            'BOUNDARY_PASS 日志应包含 baby_code: true'


class TestScenario2TempBabyDir:
    """场景 2：.temp/baby/ 目录探针（路径识别）。

    验证 L0-L3 模板 §3.3 的探针存放位置约束：
    - 探针代码必须放置在 .temp/baby/ 目录下
    - 运行时应自动识别该路径并豁免
    """

    def test_temp_baby_unix_path_exempted(self, rt):
        """Unix 路径分隔符：.temp/baby/ 下的探针应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='.temp/baby/ 目录探针',
            file_path='.temp/baby/auth-test.py',
        )
        assert out.is_intercept is False
        assert 'baby_code' in out.sg_log_line

    def test_temp_baby_windows_path_exempted(self, rt):
        """Windows 路径分隔符：.temp\\baby\\ 下的探针应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='Windows 路径探针',
            file_path='.temp\\baby\\auth-test.py',
        )
        assert out.is_intercept is False
        assert 'baby_code' in out.sg_log_line

    def test_temp_baby_nested_path_exempted(self, rt):
        """嵌套路径：project/.temp/baby/experiments/ 下的探针应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='嵌套目录探针',
            file_path='project/.temp/baby/experiments/ui-test.ts',
        )
        assert out.is_intercept is False

    def test_temp_without_baby_dir_not_exempted(self, rt):
        """对照实验：.temp/other/ 下的代码不应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='.temp/other/ 下的非探针代码',
            file_path='.temp/other/file.py',
        )
        assert out.is_intercept is True, '.temp/ 但非 .temp/baby/ 的代码不应豁免'

    def test_src_dir_not_exempted(self, rt):
        """对照实验：src/ 目录下的代码不应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='src 目录下的正式代码',
            file_path='src/components/Login.tsx',
        )
        assert out.is_intercept is True


class TestScenario3CrossStageExemption:
    """场景 3：跨阶段探针操作（L0 可在任何阶段操作）。

    验证 L0-L3 模板 §3.3 的阶段豁免约束：
    - 探针代码可在任何标准阶段（需求/设计/实现）编写
    - 不触发阶段守卫拦截
    """

    @pytest.mark.parametrize('stage,role,operation', [
        ('S1', 'orchestrator', OperationType.WRITE_CODE),
        ('S2', 'architect', OperationType.WRITE_CODE),
        ('S2', 'architect', OperationType.MODIFY_BUSINESS_CODE),
        ('S3', 'orchestrator', OperationType.WRITE_CODE),
        ('S4', 'developer', OperationType.MODIFY_ARCHITECTURE),
        ('S5', 'tester', OperationType.WRITE_CODE),
        ('S6', 'reviewer', OperationType.WRITE_CODE),
        ('S7', 'orchestrator', OperationType.WRITE_CODE),
    ])
    def test_probe_exempted_in_all_stages(self, stage, role, operation):
        """探针代码在任何阶段都应豁免。"""
        rt = GuardrailRuntime(session_id=f'cross-stage-{stage}')
        rt.enter_stage(stage, role, f'进入{stage}阶段测试探针豁免')

        out = rt.guard_operation(
            operation, role,
            detail=f'{stage} 阶段的探针操作',
            baby_code=True,
        )
        assert out.is_intercept is False, \
            f'探针代码在 {stage} 阶段应被豁免（操作: {operation.value}）'

    def test_normal_code_intercepted_in_all_stages(self):
        """对照实验：正常代码在任何阶段都遵循标准守卫规则。"""
        rt = GuardrailRuntime(session_id='cross-stage-normal')
        rt.enter_stage('S1', 'orchestrator', '测试正式代码拦截')

        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='正式生产代码',
            file_path='src/components/Production.tsx',
        )
        assert out.is_intercept is True, '正式代码在 S1 阶段应被拦截'


class TestScenario4ProbeUpgradeToStandard:
    """场景 4：探针升级后重新进入标准流程。

    验证 L0-L3 模板 §10.1 的升级路径：
    - 探针验证通过 → 升级到 L1/L2 → 必须重新进入标准阶段守卫
    - 不得延续豁免状态
    """

    def test_probe_then_standard_code_in_same_session(self, rt):
        """同一会话中，先写探针再写正式代码，正式代码应被拦截。"""
        out_probe = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='探针验证侧边栏方案',
            file_path='baby-sidebar-chat-probe.tsx',
        )
        assert out_probe.is_intercept is False, '探针应豁免'

        out_standard = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='正式实现侧边栏',
            file_path='src/components/Sidebar.tsx',
        )
        assert out_standard.is_intercept is True, \
            '探针升级后，正式代码必须重新遵循标准阶段守卫'

    def test_probe_exemption_does_not_persist(self, rt):
        """探针豁免不会"污染"后续操作——每次操作独立判定。"""
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='第一次探针', baby_code=True,
        )
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='第二次正式代码',
        )
        assert out.is_intercept is True, '不传 baby_code 的操作不应延续豁免'


class TestScenario5DocConsistency:
    """场景 5：规则文档一致性验证。

    验证代码实现与以下文档描述完全一致：
    - 04-interception-approval.md「L0 探针豁免规则」章节
    - 05-logging-spec.md「baby_code 日志示例」
    - l0-l3-process-tier-template.md §3.3 / §8.3
    """

    def test_doc_trigger_condition_1_baby_prefix(self):
        """文档描述：文件名以 baby- 开头 → 识别为探针。"""
        assert is_baby_code('baby-sidebar-chat-probe.tsx') is True
        assert is_baby_code('baby-auth-test.py') is True
        assert is_baby_code('baby-') is True

    def test_doc_trigger_condition_2_temp_baby_dir(self):
        """文档描述：文件路径包含 .temp/baby/ 片段 → 识别为探针。"""
        assert is_baby_code('.temp/baby/auth-test.py') is True
        assert is_baby_code('.temp\\baby\\auth-test.py') is True
        assert is_baby_code('project/.temp/baby/experiments/ui-test.ts') is True

    def test_doc_non_trigger_normal_code(self):
        """文档描述：不满足以上条件的代码不识别为探针。"""
        assert is_baby_code('src/components/Login.tsx') is False
        assert is_baby_code('Login.tsx') is False
        assert is_baby_code('.temp/other/file.py') is False
        assert is_baby_code('') is False
        assert is_baby_code('not-baby-file.ts') is False

    def test_doc_exemption_scope_boundary_check_pass(self, rt):
        """文档描述：BOUNDARY_CHECK 和 BOUNDARY_PASS 都应标记 baby_code。"""
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='文档一致性验证', baby_code=True,
        )
        check_logs = rt.get_logs_since(event_type='BOUNDARY_CHECK')
        pass_logs = rt.get_logs_since(event_type='BOUNDARY_PASS')
        assert any('baby_code' in line for line in check_logs), \
            'BOUNDARY_CHECK 日志应标记 baby_code（04-interception-approval.md 要求）'
        assert any('baby_code' in line and 'true' in line for line in pass_logs), \
            'BOUNDARY_PASS 日志应标记 baby_code: true（05-logging-spec.md 要求）'

    def test_doc_exemption_no_approval_needed(self, rt):
        """文档描述：探针代码的跨阶段操作不需要审批。

        验证方式：探针操作后 interception_count 不增加，
        且不产生 INTERCEPT 或 JUMP_REQUEST 日志。
        """
        before_count = rt.interception_count
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='不需要审批的探针', baby_code=True,
        )
        assert rt.interception_count == before_count, '探针豁免不应增加拦截计数'

        intercept_logs = rt.get_logs_since(event_type='INTERCEPT')
        jump_logs = rt.get_logs_since(event_type='JUMP_REQUEST')
        assert len(intercept_logs) == 0, '探针豁免不应产生 INTERCEPT 日志'
        assert len(jump_logs) == 0, '探针豁免不应产生 JUMP_REQUEST 日志'


class TestScenario6ExemptionLimits:
    """场景 6：豁免限制验证。

    验证 L0-L3 模板 §3.3 和 04-interception-approval.md「豁免限制」中的约束：
    - baby_code=False 显式声明不豁免
    - 正常代码文件路径不触发豁免
    - 探针豁免不触发绕过检测
    """

    def test_baby_code_false_not_exempted(self, rt):
        """baby_code=False 显式声明不应豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='显式非探针', baby_code=False,
        )
        assert out.is_intercept is True

    def test_baby_code_false_with_normal_file_path(self, rt):
        """baby_code=False + 正常文件路径 → 不豁免。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='正式代码', baby_code=False,
            file_path='src/components/Login.tsx',
        )
        assert out.is_intercept is True

    def test_baby_code_true_overrides_normal_file_path(self, rt):
        """baby_code=True 优先于 file_path 判定（即使 file_path 不是探针）。"""
        out = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='强制探针标记',
            baby_code=True,
            file_path='src/normal-code.ts',
        )
        assert out.is_intercept is False, 'baby_code=True 应优先于 file_path 判定'

    def test_probe_does_not_trigger_bypass_detection(self, rt):
        """探针豁免的写代码操作不应被误判为绕过之前的拦截。"""
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='第一次操作（被拦截）',
        )
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='探针豁免操作', baby_code=True,
        )
        assert rt.bypass_count == 0, '探针豁免不应触发绕过检测'

    def test_consecutive_probes_no_bypass(self, rt):
        """连续多次探针操作都不应触发绕过检测。"""
        for i in range(3):
            rt.guard_operation(
                OperationType.WRITE_CODE, 'orchestrator',
                detail=f'连续探针 #{i+1}', baby_code=True,
            )
        assert rt.bypass_count == 0
        assert rt.interception_count == 0

    def test_mixed_probe_and_standard_no_false_bypass(self, rt):
        """混合操作（探针 + 被拦截的正式代码）不应误触发绕过检测。"""
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='探针 #1', baby_code=True,
        )
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='正式代码（被拦截）',
        )
        rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='探针 #2', baby_code=True,
        )
        assert rt.bypass_count == 0, '探针豁免不应被误判为绕过之前的拦截'


class TestScenario7FullL0Workflow:
    """场景 7：完整 L0 探索级工作流端到端验证。

    模拟 L0-L3 模板 §3.2 中定义的 L0 三步流程：
    L0-① 假设定义 → L0-② 探针实现 → L0-③ 结论归档
    """

    def test_full_l0_workflow_sidebar_chat(self):
        """完整模拟 §10.1 侧边栏群聊探针的 L0 工作流。"""
        rt = GuardrailRuntime(session_id='l0-workflow-sidebar-chat')

        rt.enter_stage('S1', 'orchestrator',
                        'L0-① 假设定义：侧边栏群聊能提升协作效率')

        out_hypothesis = rt.guard_operation(
            OperationType.CLARIFY_REQUIREMENT, 'orchestrator',
            detail='明确假设：侧边栏群聊能提升协作效率',
        )
        assert out_hypothesis.is_intercept is False, '需求澄清操作应被允许'

        out_probe = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='L0-② 探针实现：编写 baby-sidebar-chat-probe.tsx',
            file_path='baby-sidebar-chat-probe.tsx',
        )
        assert out_probe.is_intercept is False, '探针代码应被豁免'
        assert 'baby_code' in out_probe.sg_log_line

        out_test = rt.guard_operation(
            OperationType.RUN_TEST, 'orchestrator',
            detail='L0-② 运行探针测试验证假设',
            file_path='baby-sidebar-chat-probe.tsx',
        )
        assert out_test.is_intercept is False, '探针测试操作应被豁免'

        out_conclusion = rt.guard_operation(
            OperationType.WRITE_SPEC, 'orchestrator',
            detail='L0-③ 结论归档：假设成立，升级到 L1',
        )
        assert out_conclusion.is_intercept is False, '写 spec 操作在 S1 阶段应被允许'

        assert rt.interception_count == 0, 'L0 工作流全程不应有拦截'
        assert rt.bypass_count == 0, 'L0 工作流全程不应触发绕过检测'

    def test_l0_to_l2_upgrade_requires_standard_guard(self):
        """L0 升级到 L2 后，正式代码必须重新遵循标准阶段守卫。"""
        rt = GuardrailRuntime(session_id='l0-to-l2-upgrade')

        rt.enter_stage('S1', 'orchestrator', 'L0 探索阶段')

        out_probe = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='L0 探针验证',
            file_path='baby-sidebar-chat-probe.tsx',
        )
        assert out_probe.is_intercept is False, '探针应豁免'

        out_standard = rt.guard_operation(
            OperationType.WRITE_CODE, 'orchestrator',
            detail='L0 验证通过，正式实现生产代码',
            file_path='src/components/Sidebar.tsx',
        )
        assert out_standard.is_intercept is True, \
            '正式代码必须重新遵循标准阶段守卫，不得延续豁免状态'
