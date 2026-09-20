"""overlay_core 数据驱动编排内核的离线单测（无 daemon、无子进程）。

三栈 SPEC 直接从 quant/xmnn/monetize 模块导入（T4 后唯一事实源在模块），
内核行为以这三份真实声明驱动；任务注册表面另见 test_tasks_surface.py。
"""

import inspect
import os
import re
from types import SimpleNamespace

import pytest
from invoke import Task
from invoke.exceptions import Exit

from jpman_client.tasks import monetize as monetize_mod
from jpman_client.tasks import overlay_core as oc
from jpman_client.tasks import quant as quant_mod
from jpman_client.tasks import xmnn as xmnn_mod
from jpman_client.tasks import xmnnrt as xmnnrt_mod

_QUANT = quant_mod.QUANT_SPEC
_XMNN = xmnn_mod.XMNN_SPEC
_MONETIZE = monetize_mod.MONETIZE_SPEC
ALL_SPECS = (_QUANT, _XMNN, _MONETIZE)


# ---------------------------------------------------------------------------
# 夹具：打桩全部宿主/子进程接触面
# ---------------------------------------------------------------------------


class FakeRunner:
    """记录 run_cmd 调用；按命令内容返回可控结果。"""

    def __init__(
        self,
        *,
        running: bool = False,
        stale: str = "",
        image_exists: bool = True,
        ss_output: str = "",
        config_files: str = "",
        live_ps: str = "",
        conmon_ps: str = "",
        init_pid: int = 1234,
        host_alive: bool = True,
    ):
        self.calls: list[tuple[str, dict]] = []
        self.running = running
        self.stale = stale
        self.image_exists = image_exists
        self.ss_output = ss_output
        self.config_files = config_files
        self.live_ps = live_ps
        self.conmon_ps = conmon_ps
        # daemon 报的容器 init PID（inspect State.Pid）与其宿主存活状态；
        # running=True 时默认真活体，假 Up 用例自行设置 init_pid 但 host_alive=False
        self.init_pid = init_pid
        self.host_alive = host_alive

    def __call__(self, c, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if "ps -a -q" in cmd:
            return SimpleNamespace(ok=True, stdout=self.stale, return_code=0)
        if "ps -q" in cmd:
            return SimpleNamespace(ok=True, stdout="cid" if self.running else "", return_code=0)
        if "ps -aq" in cmd:
            return SimpleNamespace(ok=True, stdout=self.live_ps, return_code=0)
        if "ps -p" in cmd:
            return SimpleNamespace(
                ok=self.host_alive,
                stdout=f"  {self.init_pid}\n" if self.host_alive else "",
                return_code=0,
            )
        if "ps -eo" in cmd:
            return SimpleNamespace(ok=True, stdout=self.conmon_ps, return_code=0)
        if "image exists" in cmd:
            return SimpleNamespace(ok=self.image_exists, stdout="", return_code=0 if self.image_exists else 1)
        if "ss -ltnp" in cmd:
            return SimpleNamespace(ok=True, stdout=self.ss_output, return_code=0)
        if "inspect" in cmd:
            if "State.Pid" in cmd:
                return SimpleNamespace(
                    ok=True, stdout=str(self.init_pid) if self.init_pid else "0", return_code=0
                )
            return SimpleNamespace(ok=True, stdout=self.config_files, return_code=0)
        if cmd.startswith("kill ") and "-9" not in cmd:
            # 模拟 TERM 后对应进程退出：只从各自数据源移除点名 PID（真机行为）
            killed = set(cmd.split()[1:])
            self.ss_output = "\n".join(
                line for line in self.ss_output.splitlines()
                if not any(f"pid={p}" in line for p in killed)
            )
            self.conmon_ps = "\n".join(
                line for line in self.conmon_ps.splitlines()
                if line.split(None, 1)[0] not in killed
            )
        return SimpleNamespace(ok=True, stdout="", return_code=0)

    @property
    def commands(self) -> list[str]:
        return [c for c, _ in self.calls]


@pytest.fixture
def harness(monkeypatch, tmp_path):
    root = tmp_path / "repo" / "apps" / "containers" / "client"
    root.mkdir(parents=True)
    for spec in ALL_SPECS:
        d = root / "overlays" / spec.overlay_subdir
        d.mkdir(parents=True, exist_ok=True)
        (d / spec.containerfile).write_text("# fake\n")
    # xmnn 三源码树（仓库根锚点）
    for rel in ("external/chaos/npu_tvm", "external/chaos/npuusertools", "external/chaos/models"):
        (tmp_path / "repo" / rel).mkdir(parents=True)
    (tmp_path / "repo" / "apps" / "agent-monetize").mkdir(parents=True)

    monkeypatch.setattr(oc, "_project_root", lambda: root)
    monkeypatch.setattr(oc, "_load_env_overrides", lambda r: {})
    monkeypatch.setattr(oc, "detect_runtime", lambda: "podman")
    monkeypatch.setattr(oc, "check_runtime_ready", lambda: (True, ""))
    monkeypatch.setattr(oc, "ensure_workspace_checkpoint_writable", lambda p: None)
    # 只替换 overlay_core 内的 platform 绑定，不污染 jpman_common 的真实平台探测
    # （to_posix_path 依赖 platform.system()=="Windows" 做 /mnt/c 转换）。
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Linux"))
    monkeypatch.setattr(oc.shutil, "which", lambda name: "/usr/bin/podman-compose")
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    monkeypatch.setattr(oc, "ensure_wsl_rootless_runtime", lambda: None)
    monkeypatch.setattr(oc.time, "sleep", lambda *_a, **_k: None)
    # 清掉三栈 env，避免宿主环境污染
    for spec in ALL_SPECS:
        for key in (spec.workspace_env, spec.image_tag_env, spec.ssh_port_env, spec.jupyter_port_env):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.delenv(spec.offline_env_key, raising=False)
        for m in spec.source_mounts:
            monkeypatch.delenv(m.env, raising=False)
    # C15：build-arg 单一事实源键（无前缀，与 compose 段插值键同键）也必须清空，
    # 否则宿主 export 的 PIP_MIRROR/BASE_IMAGE 会让黄金 argv 断言随环境漂移
    for key in ("PIP_MIRROR", "CONDA_MIRROR", "BASE_IMAGE"):
        monkeypatch.delenv(key, raising=False)

    runner = FakeRunner()
    monkeypatch.setattr(oc, "run_cmd", runner)
    return SimpleNamespace(root=root, repo=tmp_path / "repo", runner=runner, tmp=tmp_path)


# ---------------------------------------------------------------------------
# compose_argv 黄金快照
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_compose_argv_common_tails(spec, harness):
    d = harness.root / "overlays" / spec.overlay_subdir
    assert oc.compose_argv(spec, "up", "-d") == [
        "podman-compose", "--project-name", spec.project,
        "--file", str(d / "compose.yaml"), "up", "-d",
    ]
    assert oc.compose_argv(spec, "down")[-1] == "down"
    assert oc.compose_argv(spec, "down", "--volumes")[-2:] == ["down", "--volumes"]
    assert oc.compose_argv(spec, "ps")[-1] == "ps"
    assert oc.compose_argv(spec, "logs", "--follow", "--tail=200")[-3:] == [
        "logs", "--follow", "--tail=200",
    ]
    assert oc.compose_argv(
        spec, "exec", "-T", spec.service, "/bin/python", "/opt/x.py"
    )[-5:] == ["exec", "-T", spec.service, "/bin/python", "/opt/x.py"]


def test_compose_argv_gpu_override_stacks(harness):
    d = harness.root / "overlays" / "onnx-quantized"
    argv = oc.compose_argv(_QUANT, "up", "-d", gpu=True)
    assert argv == [
        "podman-compose", "--project-name", "onnx-quantized",
        "--file", str(d / "compose.yaml"),
        "--file", str(d / "compose.gpu.yaml"),
        "up", "-d",
    ]
    # xmnn 自 2026-09-20 起同样声明 gpu_override（GPU opt-in，C18）
    xd = harness.root / "overlays" / "xmnn-dev"
    xargv = oc.compose_argv(_XMNN, "up", "-d", gpu=True)
    assert xargv == [
        "podman-compose", "--project-name", "xmnn-dev",
        "--file", str(xd / "compose.yaml"),
        "--file", str(xd / "compose.gpu.yaml"),
        "up", "-d",
    ]
    # 非 GPU 栈不允许 gpu=True（工厂也不会暴露 --gpu）
    for spec in (_MONETIZE, xmnnrt_mod.XMNNRT_SPEC):
        with pytest.raises(RuntimeError, match="gpu_override"):
            oc.compose_argv(spec, "up", "-d", gpu=True)


def test_run_compose_quotes_every_token(harness, monkeypatch):
    """AC-2 反例断言：旧 quant.py 裸 '" ".join(argv)' 遇到含空格路径会断词。"""
    spaced = harness.tmp / "dir with space" / "client"
    (spaced / "overlays" / "onnx-quantized").mkdir(parents=True)
    monkeypatch.setattr(oc, "_project_root", lambda: spaced)
    oc.run_compose(None, _QUANT, "down")
    cmd = harness.runner.commands[-1]
    # shlex.quote 对含空格的路径整体加单引号（旧 quant.py 裸 join 会在此断词）
    assert re.search(r"'[^']*dir with space[^']*'", cmd), cmd
    # extends.file 由 podman-compose 按引用文件目录重写（1.6.0 L2845），无需 cd
    assert cmd.startswith("podman-compose")


# ---------------------------------------------------------------------------
# prepare_env
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_prepare_env_workspace_default_and_checkpoint(spec, harness, monkeypatch):
    called = []
    monkeypatch.setattr(oc, "ensure_workspace_checkpoint_writable", lambda p: called.append(p))
    oc.prepare_env(spec)
    ws_local = (harness.root / "workspace").resolve()
    # 注入子进程环境的是 POSIX 串（/mnt/c/...）；checkpoint 放宽作用于宿主本地路径
    assert os.environ[spec.workspace_env] == oc.to_posix_path(ws_local)
    assert ws_local.exists()
    assert called == [ws_local]
    # POSIX 化（无反斜杠/盘符冒号）
    assert "\\" not in os.environ[spec.workspace_env]


@pytest.mark.parametrize("spec", ALL_SPECS, ids=lambda s: s.namespace)
def test_prepare_env_missing_source_mount_hard_fails(spec, harness, monkeypatch):
    if not spec.source_mounts:
        pytest.skip("quant 无源码挂载")
    monkeypatch.setenv(spec.source_mounts[0].env, str(harness.tmp / "no-such-dir"))
    with pytest.raises(Exit) as ei:
        oc.prepare_env(spec)
    assert ei.value.code == 1


def test_prepare_env_xmnn_mounts_anchor_repo_root(harness):
    oc.prepare_env(_XMNN)
    assert os.environ["NPU_TVM_PATH"].endswith("repo/external/chaos/npu_tvm")
    assert os.environ["NPUUSERTOOLS_PATH"].endswith("npuusertools")
    assert os.environ["MODELS_PATH"].endswith("models")


def test_prepare_env_empty_placeholder_does_not_override(harness, monkeypatch):
    """C9：空字符串 env 占位不得覆盖默认值（or 链穿透空串）。"""
    monkeypatch.setenv("QUANT_SSH_PORT", "")
    monkeypatch.setenv("QUANT_IMAGE_TAG", "")
    env = oc.prepare_env(_QUANT)
    assert oc.image_tag(_QUANT, env) == "localhost/onnx-quantized:latest"
    assert oc._env_port(_QUANT, env, "QUANT_SSH_PORT", "2222") == "2222"


# ---------------------------------------------------------------------------
# 门禁
# ---------------------------------------------------------------------------


def test_gate_platform_linux_noop(harness):
    oc.gate_platform(_QUANT)  # 不抛


def test_gate_platform_windows_bridge_passes_stack_keys(harness, monkeypatch):
    """F-10：桥接透传键来自 spec.bridge_env_keys，utils 不枚举具体栈。"""
    seen = {}

    def fake_bridge(argv=None, extra_env_keys=()):
        seen["keys"] = tuple(extra_env_keys)
        return "podman-machine-default"

    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", fake_bridge)
    with pytest.raises(Exit) as ei:
        oc.gate_platform(_XMNN)
    assert ei.value.code == 0
    assert "NPU_TVM_PATH" in seen["keys"]
    assert "QUANT_IMAGE_TAG" not in seen["keys"]


def test_gate_platform_windows_no_bridge_message(harness, monkeypatch, capsys):
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    with pytest.raises(Exit) as ei:
        oc.gate_platform(_MONETIZE)
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "[monetize]" in out
    assert "invoke monetize.up" in out
    assert "COMPOSE_WSL_DISTRO" in out


def test_gate_compose_binary_missing(harness, monkeypatch, capsys):
    monkeypatch.setattr(oc.shutil, "which", lambda name: None)
    with pytest.raises(Exit):
        oc.gate_compose_binary(_QUANT)
    assert "[quant]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 标签探测 / reconcile
# ---------------------------------------------------------------------------


def test_container_running_label_filters(harness):
    harness.runner.running = True
    assert oc.container_running(None, _XMNN) is True
    cmd = harness.runner.commands[-1]
    assert f"label={oc.PROJECT_LABEL}=xmnn-dev" in cmd
    assert f"label={oc.SERVICE_LABEL}=xmnn" in cmd


def test_reconcile_no_stale_is_noop(harness):
    harness.runner.stale = ""
    oc.reconcile_stale_containers(None, _QUANT, env={})
    assert not any("down" in c for c in harness.runner.commands)


def test_reconcile_stale_triggers_compose_down(harness):
    harness.runner.stale = "dead-cid"
    oc.reconcile_stale_containers(None, _QUANT, env={})
    cmd = harness.runner.commands[-1]
    assert "podman-compose" in cmd and " down" in cmd
    assert "--project-name onnx-quantized" in cmd


# ---- up_preflight：ss 解析 / 路径归一 / 孤儿回收 / 跨控制平面 ----

_SS_LINES = (
    "LISTEN 0 4096          0.0.0.0:2223       0.0.0.0:*  "
    ' users:(("rootlessport",pid=92823,fd=10))',
    "LISTEN 0 4096          [::]:2223          [::]:*     "
    ' users:(("rootlessport",pid=92823,fd=11))',
    "LISTEN 0 4096          0.0.0.0:8890       0.0.0.0:*  "
    ' users:(("rootlessport",pid=92823,fd=12))',
    "LISTEN 0 128          0.0.0.0:2222       0.0.0.0:*  "
    ' users:(("pasta.avx2",pid=27066,fd=6))',
)


def test_parse_ss_port_holders_realworld():
    port, holders = oc.parse_ss_port_holders(_SS_LINES[0])
    assert port == "2223" and holders == [("rootlessport", 92823)]
    port, holders = oc.parse_ss_port_holders(_SS_LINES[3])
    assert port == "2222" and holders == [("pasta.avx2", 27066)]
    assert oc.parse_ss_port_holders("State Recv-Q Send-Q") == (None, [])
    port, holders = oc.parse_ss_port_holders("LISTEN 0 0 0.0.0.0:80 0.0.0.0:*")
    assert port == "80" and holders == []


def test_config_paths_diverge_is_raw_string_compare():
    # compose config-hash 按原文计算：指向同一文件的 D:\ 与 /mnt/d 仍算分歧
    win = r"D:\spaces\SpecWeave\apps\containers\client\overlays\xmnn-dev\compose.yaml"
    wsl = "/mnt/d/spaces/SpecWeave/apps/containers/client/overlays/xmnn-dev/compose.yaml"
    assert oc.config_paths_diverge(win, wsl) is True
    assert oc.config_paths_diverge(wsl, wsl) is False
    # inspect 失败（actual 为空）时不动作：未知不判分歧
    assert oc.config_paths_diverge("", wsl) is False


def test_up_preflight_reaps_orphan_rootlessport(harness):
    # 无活体项目容器（裸 compose 失败现场），孤儿 rootlessport 占着 2223/8890
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    oc.up_preflight(None, _XMNN, env={})
    kills = [c for c in harness.runner.commands if c.startswith("kill")]
    assert kills == ["kill 92823"]  # TERM 即生效，不应升级 kill -9
    assert not any(" down" in c for c in harness.runner.commands)


def test_up_preflight_never_kills_other_holders(harness):
    # pasta（jupyter 栈转发器）即使监听端口也绝不回收
    harness.runner.ss_output = _SS_LINES[3]
    oc.up_preflight(None, _XMNN, env={})
    assert not any(c.startswith("kill") for c in harness.runner.commands)


def test_up_preflight_cross_plane_running_container_triggers_down(harness):
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = (
        r"D:\spaces\SpecWeave\apps\containers\client"
        r"\overlays\xmnn-dev\compose.yaml"
    )
    oc.up_preflight(None, _XMNN, env={})
    downs = [c for c in harness.runner.commands if " down" in c]
    assert len(downs) == 1 and "--project-name xmnn-dev" in downs[0]
    # 优雅 down 后无活体容器，剩余孤儿同样被回收
    assert any(c.startswith("kill ") and "-9" not in c for c in harness.runner.commands)


def test_up_preflight_same_plane_running_is_noop(harness):
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = str(
        harness.root / "overlays" / _XMNN.overlay_subdir / "compose.yaml"
    )
    oc.up_preflight(None, _XMNN, env={})
    assert not any(" down" in c or c.startswith("kill") for c in harness.runner.commands)


# ---- stale conmon 回收（跨平面循环残留，2026-09-15 真机实证） ----

_CID_LIVE = "bc7cc1ada5a16c0d5ccde73f3ea7a67e21f5b483465461bc023ca823edf69b58"
_CID_STALE_X = "2e3e696f821bc5868ec1efe867f746959466c1b968c22f06a576d407643c8802"
_CID_STALE_Q = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _conmon_line(pid: int, cid: str, name: str) -> str:
    return (
        f" {pid} /usr/bin/conmon --api-version 1 -c {cid} -u {cid} -r /usr/bin/crun "
        f"-b /home/user/.local/share/containers/storage/overlay-containers/{cid}/userdata "
        f"-n {name} --exit-dir /run/user/1000/libpod/tmp/exits --syslog"
    )


def test_parse_conmon_process_realworld():
    pid, cid, name = oc.parse_conmon_process(_conmon_line(111413, _CID_STALE_X, "xmnn-dev"))
    assert (pid, cid, name) == (111413, _CID_STALE_X, "xmnn-dev")
    assert oc.parse_conmon_process("  900 /usr/sbin/crun -b /x") is None
    assert oc.parse_conmon_process("not-a-pid /usr/bin/conmon -c x") is None


def test_stale_conmon_detection_double_gate(harness):
    # live：当前运行 xmnn 容器；ps 含 活xmnn / stale-xmnn / stale-quant 三个 conmon
    harness.runner.live_ps = _CID_LIVE[:12]
    harness.runner.conmon_ps = "\n".join([
        _conmon_line(100, _CID_LIVE, "xmnn-dev"),
        _conmon_line(111413, _CID_STALE_X, "xmnn-dev"),
        _conmon_line(200, _CID_STALE_Q, "onnx-quantized"),
    ])
    stale = oc._list_stale_conmons(None, _XMNN)
    # 只回收：本栈名 + 容器已不在 libpod；活 conmon 与他栈 conmon 都不动
    assert stale == [(111413, _CID_STALE_X[:12])]


def test_up_preflight_reaps_stale_conmon_and_rootlessport(harness):
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.conmon_ps = _conmon_line(111413, _CID_STALE_X, "xmnn-dev")
    oc.up_preflight(None, _XMNN, env={})
    kills = [c for c in harness.runner.commands if c.startswith("kill ") and "-9" not in c]
    # 一次 rootlessport(92823) + 一次 stale conmon(111413)，分别精确点名
    assert "kill 92823" in kills
    assert "kill 111413" in kills
    # 绝不出现他栈/活容器 PID
    joined = " ".join(kills)
    assert "100 " not in joined and "200 " not in joined


# ---- 假 Up：daemon 记 running 但 init 进程在宿主已死（WSL 回收循环） ----

def test_container_truly_alive_gate(harness):
    harness.runner.running = True
    harness.runner.init_pid = 111845
    harness.runner.host_alive = False
    assert oc.container_running(None, _XMNN) is True  # daemon 视角仍撒谎
    cid = oc._running_project_container(None, _XMNN)
    assert oc._container_truly_alive(None, _XMNN, cid) is False
    harness.runner.host_alive = True
    assert oc._container_truly_alive(None, _XMNN, cid) is True


def test_up_preflight_fake_up_forces_clean_rebuild(harness):
    # daemon 报 running + 报 PID，但 ps -p 宿主查无此进程；端口/孤儿都在
    harness.runner.running = True
    harness.runner.init_pid = 111845
    harness.runner.host_alive = False
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.conmon_ps = _conmon_line(111413, _CID_STALE_X, "xmnn-dev")
    oc.up_preflight(None, _XMNN, env={})
    cmds = harness.runner.commands
    # 必须先 compose down 清失实状态（不是 no-op），再回收孤儿，再 up 由调用方执行
    assert any(" down" in c for c in cmds)
    kills = [c for c in cmds if c.startswith("kill ") and "-9" not in c]
    assert "kill 92823" in kills and "kill 111413" in kills


def test_require_running_rejects_fake_up(harness):
    harness.runner.running = True
    harness.runner.init_pid = 111845
    harness.runner.host_alive = False
    with pytest.raises(Exit):
        oc.require_running(None, _XMNN)


# ---------------------------------------------------------------------------
# 任务工厂表面
# ---------------------------------------------------------------------------


def _param_names(task: Task) -> list[str]:
    return [p for p in inspect.signature(task.body).parameters if p != "c"]


def test_factory_tasks_and_docs(harness):
    for spec in ALL_SPECS:
        tasks = oc.make_stack_tasks(spec)
        expected = {"build", "up", "down", "ps", "logs", "smoke"}
        if spec.supports_offline:
            expected |= {"save", "load"}
        assert set(tasks) == expected
        assert all(isinstance(t, Task) for t in tasks.values())
        assert tasks["build"].__doc__ == spec.docs.build
        assert tasks["up"].__doc__ == spec.docs.up
        assert tasks["smoke"].__doc__ == spec.docs.smoke


def test_factory_build_signature_conda_variant(harness):
    q = oc.make_stack_tasks(_QUANT)
    x = oc.make_stack_tasks(_XMNN)
    m = oc.make_stack_tasks(_MONETIZE)
    assert _param_names(q["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]
    assert _param_names(x["build"]) == [
        "tag", "base_image", "pip_mirror", "conda_mirror", "torch", "no_cache",
    ]
    assert _param_names(m["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]


def test_factory_up_smoke_params_are_capability_union(harness):
    """up/smoke 形参面 = 已声明能力的并集（gpu_override ∪ supports_offline）。

    xmnn 自 2026-09-20 起同时声明两者，故 gpu 与 offline 必须**并存**——
    历史的三路互斥写法会让 --offline 被 gpu 分支吃掉（C18）。
    """
    q, x, m = (oc.make_stack_tasks(s) for s in (_QUANT, _XMNN, _MONETIZE))
    assert _param_names(q["up"]) == ["gpu", "skip_build"]
    assert _param_names(x["up"]) == ["gpu", "skip_build", "offline", "no_offline"]
    assert _param_names(m["up"]) == ["skip_build"]
    assert _param_names(q["smoke"]) == ["gpu"]
    assert _param_names(x["smoke"]) == ["gpu"]
    assert _param_names(m["smoke"]) == []
    assert _param_names(q["down"]) == ["volumes"]
    assert _param_names(x["logs"]) == ["tail"]


def test_factory_auto_shortflags_quant_on_others_off(harness):
    q = oc.make_stack_tasks(_QUANT)
    x = oc.make_stack_tasks(_XMNN)
    assert all(t.auto_shortflags is True for t in q.values())
    assert all(t.auto_shortflags is False for t in x.values())


def test_bridge_keys_isolated_per_stack():
    """桥接键下沉后，各栈只带自己的前缀，不枚举其他栈（F-10）。"""
    joined = " ".join(_QUANT.bridge_env_keys)
    assert "XMNN_" not in joined and "MONETIZE_" not in joined
    assert "QUANT_WORKSPACE" in _QUANT.bridge_env_keys
    assert "NPU_TVM_PATH" in _XMNN.bridge_env_keys
    assert "MONETIZE_SRC_PATH" in _MONETIZE.bridge_env_keys
    xj = " ".join(_XMNN.bridge_env_keys)
    assert "QUANT_" not in xj and "MONETIZE_" not in xj


# ---------------------------------------------------------------------------
# 端到端：任务体执行（仍全部离线打桩）
# ---------------------------------------------------------------------------


def test_build_task_argv_quant_no_conda(harness):
    tasks = oc.make_stack_tasks(_QUANT)
    tasks["build"].body(None, tag="t:1", base_image="b:1", pip_mirror="tuna", no_cache=True)
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg BASE_IMAGE=b:1" in build_cmd
    assert "--build-arg PIP_MIRROR=tuna" in build_cmd
    assert "-t t:1" in build_cmd
    assert "--no-cache" in build_cmd
    assert "CONDA_MIRROR" not in build_cmd


def test_build_task_argv_xmnn_includes_conda(harness):
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["build"].body(
        None, tag=None, base_image=_XMNN.default_base_image,
        pip_mirror="aliyun", conda_mirror="tuna", no_cache=False,
    )
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg CONDA_MIRROR=tuna" in build_cmd
    assert "-t localhost/xmnn-dev:latest" in build_cmd
    # C15：三处同键——TORCH_FLAVOR 与 compose.yaml build.args 的 ${TORCH_FLAVOR:-} 同键
    assert "--build-arg TORCH_FLAVOR=" in build_cmd


def test_build_task_argv_xmnn_torch_flavor_flows(harness):
    """--torch cu130 必须落到 podman build 的 --build-arg（C15 三处一致）。"""
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["build"].body(
        None, tag="localhost/xmnn-dev:cuda", base_image=_XMNN.default_base_image,
        pip_mirror="official", conda_mirror="official", torch="cu130", no_cache=False,
    )
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg TORCH_FLAVOR=cu130" in build_cmd
    assert "-t localhost/xmnn-dev:cuda" in build_cmd


def test_build_missing_base_image_exits(harness):
    harness.runner.image_exists = False
    with pytest.raises(Exit):
        oc.build_image(
            None, _MONETIZE, tag=None,
            base_image="localhost/missing:latest", pip_mirror="official",
        )


def test_up_skip_build_reconcile_and_up_argv(harness):
    oc.up_stack(None, _QUANT, gpu=False, skip_build=True)
    cmds = harness.runner.commands
    assert not any(" build " in c for c in cmds)
    assert any("up -d --no-build" in c for c in cmds)


# ---------------------------------------------------------------------------
# C16：构建执行者唯一（内核为镜像存在性负责 → compose 段恒 --no-build）
# ---------------------------------------------------------------------------


def test_up_inline_build_runs_exactly_once(harness):
    """默认 up：内联构建一次，compose 段被 --no-build 抑制（此前会构建两次）。"""
    oc.up_stack(None, _QUANT)
    assert len([c for c in harness.runner.commands if " build " in c]) == 1
    assert any("up -d --no-build" in c for c in harness.runner.commands)


def test_up_skip_build_without_local_image_exits_with_guidance(harness, capsys):
    """--skip-build 不再由 compose 段兜底构建：镜像缺失必须 fail-fast 且可执行。"""
    harness.runner.image_exists = False
    with pytest.raises(Exit) as ei:
        oc.up_stack(None, _QUANT, skip_build=True)
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "--skip-build 置位但本地缺少镜像" in out
    assert "invoke quant.build" in out
    assert not any("up -d" in c for c in harness.runner.commands)  # 未起容器


# ---------------------------------------------------------------------------
# C15：build-arg 单一事实源（.env 无前缀键贯通 build / up 内联构建 / compose 段）
# ---------------------------------------------------------------------------


def test_up_inline_build_reads_env_build_args(harness, monkeypatch):
    """up 内联构建的 build-arg 必须读 .env 无前缀键，而非硬编码 official。"""
    monkeypatch.setenv("PIP_MIRROR", "tuna")
    monkeypatch.setenv("CONDA_MIRROR", "aliyun")
    monkeypatch.setenv("BASE_IMAGE", "localhost/base:env")
    oc.up_stack(None, _XMNN, gpu=False)
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg PIP_MIRROR=tuna" in build_cmd
    assert "--build-arg CONDA_MIRROR=aliyun" in build_cmd
    assert "--build-arg BASE_IMAGE=localhost/base:env" in build_cmd


def test_build_task_defaults_follow_env(harness, monkeypatch):
    """显式 build 不传旗标时同样跟随 .env——三处同键才可能命中同一层缓存。"""
    monkeypatch.setenv("PIP_MIRROR", "tuna")
    tasks = oc.make_stack_tasks(_QUANT)
    tasks["build"].body(None)
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg PIP_MIRROR=tuna" in build_cmd
    assert f"--build-arg BASE_IMAGE={_QUANT.default_base_image}" in build_cmd


def test_build_args_fall_back_to_defaults_without_env(harness, monkeypatch):
    """未设 .env 键时回退 spec 默认（回归保护：旧行为零变化）。"""
    monkeypatch.delenv("TORCH_FLAVOR", raising=False)
    args = oc.resolve_build_args(_XMNN, {})
    assert args == {
        "base_image": _XMNN.default_base_image,
        "pip_mirror": "official",
        "conda_mirror": "official",
        "torch_flavor": "",
    }
    assert "conda_mirror" not in oc.resolve_build_args(_QUANT, {})
    assert "torch_flavor" not in oc.resolve_build_args(_QUANT, {})


def test_build_args_torch_flavor_whitelist(harness, monkeypatch):
    """TORCH_FLAVOR 白名单在解析期拦截（构建一次代价极高，错误必须前置）。"""
    monkeypatch.delenv("TORCH_FLAVOR", raising=False)
    for flavor in ("", "cpu", "cu130"):
        assert oc.resolve_build_args(_XMNN, {}, torch=flavor)["torch_flavor"] == flavor
    assert oc.resolve_build_args(_XMNN, {}, torch="")["torch_flavor"] == ""
    monkeypatch.setenv("TORCH_FLAVOR", "cu129")
    with pytest.raises(Exit):
        oc.resolve_build_args(_XMNN, {})
    assert oc.resolve_build_args(_XMNN, {}, torch="cpu")["torch_flavor"] == "cpu"


def test_build_args_cli_flag_beats_env(harness, monkeypatch):
    """CLI 旗标优先级高于 .env（单次覆盖），但 compose 段看不到旗标。"""
    monkeypatch.setenv("PIP_MIRROR", "tuna")
    args = oc.resolve_build_args(_QUANT, {}, pip_mirror="aliyun")
    assert args["pip_mirror"] == "aliyun"


def test_down_task_volumes_flag(harness):
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["down"].body(None, volumes=True)
    assert harness.runner.commands[-1].endswith("down --volumes")


def test_smoke_running_uses_exec_all_scripts(harness):
    harness.runner.running = True
    oc.smoke_stack(None, _QUANT, gpu=False)
    exec_cmds = [c for c in harness.runner.commands if " exec " in c]
    assert len(exec_cmds) == 3
    for script in ("smoke_dynamic_int8.py", "smoke_fp16.py", "smoke_static_qdq.py"):
        assert any(script in c for c in exec_cmds)


def test_smoke_stopped_quant_runs_three_standalone(harness):
    harness.runner.running = False
    oc.smoke_stack(None, _QUANT)
    run_cmds = [c for c in harness.runner.commands if " run --rm " in c]
    assert len(run_cmds) == 3
    assert not any(" exec " in c for c in harness.runner.commands)


def test_smoke_stopped_xmnn_guard_only(harness):
    harness.runner.running = False
    oc.smoke_stack(None, _XMNN)
    run_cmds = [c for c in harness.runner.commands if " run --rm " in c]
    assert len(run_cmds) == 1
    assert "_toolchain_guards.py" in run_cmds[0]
    assert "smoke_mounts.py" not in run_cmds[0]


def test_smoke_running_monetize_two_scripts(harness):
    harness.runner.running = True
    oc.smoke_stack(None, _MONETIZE)
    exec_cmds = [c for c in harness.runner.commands if " exec " in c]
    assert "_toolchain_guards.py" in exec_cmds[0]
    assert "smoke_native.py" in exec_cmds[1]


# ---------------------------------------------------------------------------
# 离线模式（仅 xmnn 声明 supports_offline；V-1 桥接透传 / V-2 compose --no-build）
# ---------------------------------------------------------------------------


def test_offline_declared_only_for_xmnn():
    assert _XMNN.supports_offline is True
    assert _QUANT.supports_offline is False and _MONETIZE.supports_offline is False
    assert _XMNN.offline_env_key == "XMNN_OFFLINE"
    assert "XMNN_OFFLINE" in _XMNN.bridge_env_keys


def test_resolve_offline_flag_written_back_to_env(harness, monkeypatch):
    """V-1：显式旗标必须在 gates（WSL 桥接）之前固化进 os.environ。"""
    monkeypatch.setenv("XMNN_OFFLINE", "0")
    assert oc.resolve_offline(_XMNN, True, False) is True
    assert os.environ["XMNN_OFFLINE"] == "1"
    assert oc.resolve_offline(_XMNN, False, True) is False
    assert os.environ["XMNN_OFFLINE"] == "0"


def test_resolve_offline_env_fallback_conflict_and_non_offline_stack(harness, monkeypatch):
    monkeypatch.setenv("XMNN_OFFLINE", "yes")
    assert oc.resolve_offline(_XMNN, False, False) is True
    monkeypatch.setenv("QUANT_OFFLINE", "1")
    assert oc.resolve_offline(_QUANT, False, False) is False
    with pytest.raises(Exit):
        oc.resolve_offline(_XMNN, True, True)


def test_compose_up_tail_always_no_build():
    """C16 取代 V-2 的 offline 分叉：--no-build 对非离线 up 同样必须成立。"""
    assert oc.compose_up_tail() == ["up", "-d", "--no-build"]


def test_offline_exec_env_gated_by_declaration_and_env(harness, monkeypatch):
    monkeypatch.delenv("XMNN_OFFLINE", raising=False)
    assert oc.offline_exec_env(_XMNN) == []
    monkeypatch.setenv("XMNN_OFFLINE", "1")
    assert oc.offline_exec_env(_XMNN) == ["-e", "XMNN_OFFLINE=1"]
    assert oc.offline_exec_env(_QUANT) == []


def test_build_image_offline_fails_fast_before_any_command(harness, monkeypatch):
    monkeypatch.setenv("XMNN_OFFLINE", "1")
    with pytest.raises(Exit) as ei:
        oc.build_image(
            None, _XMNN, tag=None,
            base_image=_XMNN.default_base_image, pip_mirror="official",
        )
    assert ei.value.code == 1
    assert harness.runner.commands == []  # 未发生任何 podman 调用


def test_up_offline_forces_skip_build_and_compose_no_build(harness):
    oc.up_stack(None, _XMNN, offline=True)
    cmds = harness.runner.commands
    assert not any(" build " in c for c in cmds)
    assert any("up -d --no-build" in c for c in cmds)


def test_up_offline_missing_image_exits(harness, capsys):
    harness.runner.image_exists = False
    with pytest.raises(Exit) as ei:
        oc.up_stack(None, _XMNN, offline=True)
    assert ei.value.code == 1
    assert "离线模式下本地缺少镜像" in capsys.readouterr().out


def test_up_task_body_offline_flag_survives_to_argv(harness, monkeypatch):
    monkeypatch.setenv("XMNN_OFFLINE", "0")
    tasks = oc.make_stack_tasks(_XMNN)
    tasks["up"].body(None, skip_build=False, offline=True, no_offline=False)
    assert os.environ["XMNN_OFFLINE"] == "1"
    assert any("up -d --no-build" in c for c in harness.runner.commands)


def test_save_load_tasks_only_for_offline_stack(harness):
    assert "save" not in oc.make_stack_tasks(_QUANT)
    assert "load" not in oc.make_stack_tasks(_MONETIZE)
    x = oc.make_stack_tasks(_XMNN)
    assert _param_names(x["save"]) == ["tag", "cache_dir"]
    assert _param_names(x["load"]) == ["path", "cache_dir"]


# ---------------------------------------------------------------------------
# C17：up 路径过滤 podman 原生回显噪声（失败时零过滤）
# ---------------------------------------------------------------------------

_HEX_ID = "2096d7b4741154ed6b11724720913345fd086b01221328c93317ac94fabd2c56"
_HEX_ID2 = "d3f33bf7e541578efb71e6d2c0afa889e12a1adbf3bd525ede151e036d48bf43"
_PASTA_DBUS_LINE = (
    "ERROR[0001] failed to move the rootless netns pasta process to the "
    "systemd user.slice: dbus: couldn't determine address of session bus"
)


def test_is_benign_compose_noise_whitelist_only():
    """判据为白名单三式；真实错误一律返回 False（宁可多显示，不可吞）。"""
    names = oc.compose_echo_names(_XMNN)
    assert oc.is_benign_compose_noise(_HEX_ID, names=names)
    assert oc.is_benign_compose_noise(f"  {_HEX_ID}  ", names=names)  # 允许两侧空白
    assert oc.is_benign_compose_noise(_XMNN.project, names=names)
    assert oc.is_benign_compose_noise(f"pod_{_XMNN.project}", names=names)
    assert oc.is_benign_compose_noise(f"{_XMNN.project}_default", names=names)
    assert oc.is_benign_compose_noise(_PASTA_DBUS_LINE, names=names)
    # —— 反例：真实错误必须可见（含裸 ID / 名字出现在上下文里） ——
    assert not oc.is_benign_compose_noise(
        f'Error: unable to start container "{_HEX_ID}": netavark: failed to create '
        "aardvark-dns directory /run/user/1000/containers/networks/aardvark-dns: "
        "IO error: No such file or directory (os error 2)",
        names=names,
    )
    assert not oc.is_benign_compose_noise(f"{_XMNN.project} 端口被占用", names=names)
    assert not oc.is_benign_compose_noise("abc123", names=names)  # 非 64 位十六进制
    assert not oc.is_benign_compose_noise(
        "ERROR[0001] failed to move the rootless netns pasta process to the "
        "systemd user.slice: dbus: some other failure",
        names=names,
    )


def _stub_run_cmd(monkeypatch, *, stdout: str = "", stderr: str = "", ok: bool = True, rc: int = 0):
    def fake(c, cmd, **kwargs):
        return SimpleNamespace(ok=ok, stdout=stdout, stderr=stderr, return_code=rc)

    monkeypatch.setattr(oc, "run_cmd", fake)


def test_run_compose_up_filters_echo_noise(harness, monkeypatch, capsys):
    """up 成功路径：ID/资源名/无会话总线提示被过滤，其余行原样保留。"""
    _stub_run_cmd(
        monkeypatch,
        stdout=f"{_HEX_ID}\n{_HEX_ID2}\n{_XMNN.project}\n",
        stderr=_PASTA_DBUS_LINE + "\n",
    )
    oc.run_compose_up(None, _XMNN, *oc.compose_up_tail())
    out = capsys.readouterr().out
    assert _HEX_ID not in out and _HEX_ID2 not in out
    assert "ERROR[0001]" not in out
    assert _XMNN.project not in out.splitlines()  # 裸名字行被丢弃（执行行含名字）
    assert "已过滤 4 行" in out


def test_run_compose_up_failure_prints_raw_and_exits(harness, monkeypatch, capsys):
    """失败路径零过滤：裸 ID 与真实错误全量原样回放，退出码透传。"""
    err = f'Error: unable to start container "{_HEX_ID}": netavark: IO error'
    _stub_run_cmd(monkeypatch, stdout=f"{_HEX_ID}\n{_XMNN.project}\n", stderr=err + "\n", ok=False, rc=125)
    with pytest.raises(Exit) as ei:
        oc.run_compose_up(None, _XMNN, *oc.compose_up_tail())
    assert ei.value.code == 125
    out = capsys.readouterr().out
    assert _HEX_ID in out and "netavark" in out
    assert "原始输出如下" in out
    assert "已过滤" not in out


def test_up_stack_captures_compose_up_output(harness):
    """up 必须走捕获路径（hide=True/echo=False）——否则过滤无从生效。"""
    oc.up_stack(None, _QUANT, skip_build=True)
    kw = [k for cmd, k in harness.runner.calls if "up -d --no-build" in cmd][0]
    assert kw["hide"] is True and kw["echo"] is False and kw["pty"] is False
