"""containers 容器只读探测测试（CLI 路径，打桩 run_cmd）。"""
from jpman_common import containers


# FakeContext 为 tests 目录内的本地替身（test_proc 中另有同名夹具）。
class FakeResult:
    def __init__(self, stdout="", ok=True):
        self.stdout = stdout
        self.ok = ok


class FakeContext:
    """result_spec：单条 stdout 字符串，或按调用次序返回的 (stdout, ok) 序列。"""

    def __init__(self, result_spec):
        if isinstance(result_spec, str):
            self._results = [(result_spec, True)]
        else:
            self._results = list(result_spec)
        self.calls: list[str] = []
        self._idx = 0

    def run(self, cmd, **kwargs):
        self.calls.append(cmd)
        if self._idx < len(self._results):
            stdout, ok = self._results[self._idx]
            self._idx += 1
        else:
            stdout, ok = "", True
        return FakeResult(stdout, ok)


def test_container_exists_true():
    # -q 输出容器 ID，非空即命中（零引号，免疫 Windows invoke pwsh 包装截断）
    c = FakeContext("a1b2c3d4\n")
    assert containers.container_exists(c, "podman", "mybox") is True
    assert "ps -aq" in c.calls[0]
    assert "name=^mybox$" in c.calls[0]
    assert '"' not in c.calls[0]


def test_container_exists_false_when_empty_output():
    # -q + ^name$ 锚定下，空输出是「不存在」的唯一形态（不可能返回他名容器）
    c = FakeContext("")
    assert containers.container_exists(c, "podman", "mybox") is False


def test_container_running_uses_ps_without_a():
    c = FakeContext("mybox\n")
    assert containers.container_running(c, "podman", "mybox") is True
    cmd = c.calls[0]
    assert " ps " in cmd
    assert "ps -a" not in cmd


# ── container_phase 四态 ──────────────────────────────────────────────


def test_phase_running_short_circuits_with_single_probe():
    c = FakeContext("ce0dd6d98b4f\n")
    assert containers.container_phase(c, "podman", "mybox") == containers.PHASE_RUNNING
    # 命中运行态后不得再发第二次探测
    assert len(c.calls) == 1
    assert "ps -a" not in c.calls[0]
    assert "status=running" in c.calls[0]
    # Windows invoke 通道铁律：探针命令不得含双引号
    assert '"' not in c.calls[0]


def test_phase_stopped_when_only_ps_a_matches():
    # 第一次 ps（运行态）空；第二次 ps -a 匹配 → stopped 残留
    c = FakeContext([("", True), ("mybox\n", True)])
    assert containers.container_phase(c, "podman", "mybox") == containers.PHASE_STOPPED
    assert "ps -a" in c.calls[1]


def test_phase_absent_when_both_probes_empty():
    c = FakeContext([("", True), ("", True)])
    assert containers.container_phase(c, "podman", "mybox") == containers.PHASE_ABSENT


def test_phase_unknown_when_running_probe_fails():
    # 探测命令失败（warn=True 吞错，ok=False）→ unknown，且不得误判为 absent
    c = FakeContext([("", False)])
    assert containers.container_phase(c, "podman", "mybox") == containers.PHASE_UNKNOWN
    assert len(c.calls) == 1


def test_phase_unknown_when_all_probe_fails():
    c = FakeContext([("", True), ("", False)])
    assert containers.container_phase(c, "podman", "mybox") == containers.PHASE_UNKNOWN
