"""containers 容器只读探测测试（CLI 路径，打桩 run_cmd）。"""
from jpman_common import containers


# FakeContext 为 tests 目录内的本地替身（test_proc 中另有同名夹具）。
class FakeResult:
    def __init__(self, stdout=""):
        self.stdout = stdout


class FakeContext:
    def __init__(self, stdout):
        self._stdout = stdout
        self.calls: list[str] = []

    def run(self, cmd, **kwargs):
        self.calls.append(cmd)
        return FakeResult(self._stdout)


def test_container_exists_true():
    c = FakeContext("mybox\n")
    assert containers.container_exists(c, "podman", "mybox") is True
    assert "ps -a" in c.calls[0]
    assert "name=^mybox$" in c.calls[0]
    assert "{{.Names}}" in c.calls[0]


def test_container_exists_false_when_name_mismatch():
    c = FakeContext("otherbox\n")
    assert containers.container_exists(c, "podman", "mybox") is False


def test_container_running_uses_ps_without_a():
    c = FakeContext("mybox\n")
    assert containers.container_running(c, "podman", "mybox") is True
    cmd = c.calls[0]
    assert " ps " in cmd
    assert "ps -a" not in cmd
