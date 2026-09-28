"""overlay_core 数据驱动编排内核的离线单测（无 daemon、无子进程）。

三栈 SPEC 直接从 quant/native/monetize 模块导入（T4 后唯一事实源在模块），
内核行为以这三份真实声明驱动；任务注册表面另见 test_tasks_surface.py。
"""

import inspect
import os
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from invoke import Task
from invoke.exceptions import Exit

from jpman_client.tasks import monetize as monetize_mod
from jpman_client.tasks import overlay_core as oc
from jpman_client.tasks import quant as quant_mod
from jpman_client.tasks import native as native_mod

_QUANT = quant_mod.QUANT_SPEC
_NATIVE = native_mod.NATIVE_SPEC
_MONETIZE = monetize_mod.MONETIZE_SPEC
ALL_SPECS = (_QUANT, _NATIVE, _MONETIZE)


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
        paths: set[str] | None = None,
        cdi: bool = False,
        container_logs: str = "",
        image_labels: dict | None = None,
        nvidia_smi_ok: bool = True,
        nvidia_smi_out: str = "",
        image_exists_tags: set[str] | None = None,
        # 按 tag 精确控制 ``inspect -f {{.Id}}`` 返回的镜像 ID；
        # None = 不注入（返回空 stdout，模拟 ID 读取失败）。
        image_ids: dict[str, str] | None = None,
        # _own_host_container_running 的 inspect 假输出
        # （``{{.State.Running}} {{.HostConfig.NetworkMode}}`` 渲染值）。
        # 空串 = 双段判据不成立 → helper 判 False，既有 busy 用例 fail-fast 语义不变。
        net_mode: str = "",
    ):
        self.calls: list[tuple[str, dict]] = []
        self.running = running
        self.stale = stale
        self.image_exists = image_exists
        self.ss_output = ss_output
        self.config_files = config_files
        self.live_ps = live_ps
        self.conmon_ps = conmon_ps
        # C24：容器启动日志（凭证回读源）。默认空串 → 回读解析不到任何凭证，
        # 横幅不增行，既有用例（未声明 running/logs）语义不变。
        self.container_logs = container_logs
        # daemon 报的容器 init PID（inspect State.Pid）与其宿主存活状态；
        # running=True 时默认真活体，假 Up 用例自行设置 init_pid 但 host_alive=False
        self.init_pid = init_pid
        self.host_alive = host_alive
        # 宿主存在的设备路径集合；None=「一律存在」（历史用例的宽松默认，
        # 等价于自动探测命中 /dev/dri）。C19 的预检用例传入精确集合。
        self.paths = paths
        self.cdi = cdi
        # C27：镜像 LABEL 集合（`podman image inspect` 原始 JSON 的 Labels）。
        # None = 不注入 → 返回空 stdout → JSON 解析失败 → 形态「无法判定」，
        # 既有用例（未声明本参数）零影响；{} = 有 Labels 但无 torch 形态键。
        self.image_labels = image_labels
        # NVIDIA CDI 路径的宿主驱动健康探针（check_nvidia_driver_health）：
        # 默认健康；失配用例注入 nvidia_smi_ok=False + 原生报错文本。
        self.nvidia_smi_ok = nvidia_smi_ok
        self.nvidia_smi_out = nvidia_smi_out
        # 按 tag 精确控制镜像存在性；None = 沿用 image_exists 布尔（历史用例）。
        self.image_exists_tags = image_exists_tags
        self.image_ids = image_ids
        self.net_mode = net_mode
        # _runtime_probe_session_bus 的显式探测结果；空串时回退为 paths 集合中
        # 形如 /run/user/<uid>/bus 的首个命中（模拟 daemon 侧按 id -u 自动探测）。
        self.session_bus = ""

    def __call__(self, c, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        if cmd.startswith("test -e ") or cmd.startswith("test -S "):
            path = cmd[len("test -e "):] if cmd.startswith("test -e ") else cmd[len("test -S "):]
            path = path.strip().strip("'\"")
            exists = True if self.paths is None else path in self.paths
            return SimpleNamespace(ok=exists, stdout="", return_code=0 if exists else 1)
        if '"/run/user/$(id -u)/bus"' in cmd:
            # _runtime_probe_session_bus：模拟 daemon 侧三候选自动探测。
            # paths=None 是历史「一律存在」的宽松默认 → 探测命中历史缺省路径；
            # set() = 精确为空（无会话总线）；非空集合取其中 /run/user/<uid>/bus。
            if self.session_bus:
                out = self.session_bus
            elif self.paths is None:
                out = "/run/user/1000/bus"
            else:
                hits = sorted(
                    p for p in self.paths
                    if re.fullmatch(r"/run/user/[^/]+/bus", p)
                )
                out = hits[0] if hits else ""
            return SimpleNamespace(ok=bool(out), stdout=out, return_code=0 if out else 1)
        if "/etc/cdi" in cmd:
            return SimpleNamespace(
                ok=self.cdi,
                stdout="/etc/cdi/nvidia.yaml\n" if self.cdi else "",
                return_code=0 if self.cdi else 2,
            )
        if cmd.strip() == "nvidia-smi":
            return SimpleNamespace(
                ok=self.nvidia_smi_ok,
                stdout=self.nvidia_smi_out if self.nvidia_smi_ok else "",
                stderr="" if self.nvidia_smi_ok else self.nvidia_smi_out,
                return_code=0 if self.nvidia_smi_ok else 9,
            )
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
            tag = cmd.split("image exists", 1)[1].strip()
            if self.image_exists_tags is not None:
                ok = tag in self.image_exists_tags
            else:
                ok = self.image_exists
            return SimpleNamespace(ok=ok, stdout="", return_code=0 if ok else 1)
        if cmd.strip() == "ss -lnt":
            return SimpleNamespace(ok=True, stdout=self.ss_output, return_code=0)
        if "ss -ltnp" in cmd:
            return SimpleNamespace(ok=True, stdout=self.ss_output, return_code=0)
        if " logs " in cmd:
            # C24：凭证回读（podman logs <cid> 2>&1 | head -n N）
            return SimpleNamespace(ok=True, stdout=self.container_logs, return_code=0)
        if "inspect" in cmd:
            if ".Id" in cmd:
                tag = cmd.split()[-1]
                img_id = (self.image_ids or {}).get(tag, "")
                return SimpleNamespace(
                    ok=bool(img_id), stdout=img_id, return_code=0 if img_id else 1
                )
            if "State.Running" in cmd:
                return SimpleNamespace(ok=True, stdout=self.net_mode, return_code=0)
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
    # 为每个 SPEC 建假 overlay 目录与 Containerfile（构建 argv / compose 覆盖类
    # 用例需要 overlay 目录真实存在）。
    for spec in ALL_SPECS:
        d = root / "overlays" / spec.overlay_subdir
        d.mkdir(parents=True, exist_ok=True)
        (d / spec.containerfile).write_text("# fake\n")
    # native 三源码树（仓库根锚点）
    for rel in ("external/chaos/npu_tvm", "external/containers/workspace/dev/npuusertools", "external/chaos/models"):
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
    # C34：B-scheme 预检接触面默认打桩为「socket 已就绪、无需自愈」，保持
    # 既有 up_stack 用例 hermetic（真实宿主探测不可进单测）；失败/自愈形态
    # 由 C34 专用用例自行替换。
    monkeypatch.setattr(oc, "ensure_host_podman_socket", lambda: (True, "", False))
    monkeypatch.setattr(
        oc, "podman_sock_path", lambda: "/run/user/1000/podman/podman.sock"
    )
    monkeypatch.delenv("HOST_PODMAN_SOCK", raising=False)
    monkeypatch.delenv("PODMAN_RUNTIME_UID", raising=False)
    monkeypatch.setattr(oc.time, "sleep", lambda *_a, **_k: None)
    # C21：就绪探测打桩为「立即就绪」，避免单测真的去轮询宿主端口（最长 120s）。
    # 探测语义本身（含 TCP 假阳性守卫）由 test_up_readiness.py 用回环 socket 锁。
    monkeypatch.setattr(
        oc, "wait_http_ready", lambda port, **kw: (True, f"127.0.0.1:{port} → HTTP 302")
    )
    # 清掉三栈 env，避免宿主环境污染（会经 prepare_env 写成 POSIX 串回灌
    # os.environ，不清会跨用例漂移）
    for spec in ALL_SPECS:
        for key in (spec.workspace_env, spec.image_tag_env, spec.ssh_port_env, spec.jupyter_port_env):
            monkeypatch.delenv(key, raising=False)
        monkeypatch.delenv(spec.offline_env_key, raising=False)
        for m in spec.source_mounts:
            monkeypatch.delenv(m.env, raising=False)
    # NATIVE_TEMP_PATH 缺省锚「仓库根上溯四级」，在 tmp 布局下会指到文件系统根之外；
    # 统一钉到 tmp 目录，保证用例 hermetic（也覆盖「非空路径 → 幂等 mkdir」形态）
    monkeypatch.setenv("NATIVE_TEMP_PATH", str(tmp_path / "temp"))
    # C15：build-arg 单一事实源键（无前缀，与 compose 段插值键同键）也必须清空，
    # 否则宿主 export 的 PIP_MIRROR/BASE_IMAGE 会让黄金 argv 断言随环境漂移
    for key in ("PIP_MIRROR", "CONDA_MIRROR", "BASE_IMAGE"):
        monkeypatch.delenv(key, raising=False)
    # C19：GPU 设备令牌同样清空，否则宿主 export 的 GPU_DEVICE 会改变形态断言
    monkeypatch.delenv("GPU_DEVICE", raising=False)
    # C20：torch 形态同理（load 的选档/校验依赖它，宿主 export 会让断言漂移）
    monkeypatch.delenv("TORCH_FLAVOR", raising=False)
    # 透传覆盖的插值键：宿主 export 会改变门禁/渲染断言
    for key in (
        "DBUS_SESSION_BUS_PATH", "HOST_NET_SSHD_PORT", "USB_DEVICE",
        "NATIVE_PASSTHROUGH_IMAGE_TAG",
        # C33：GUI 探测入参与回写令牌
        "HOST_XDG_RUNTIME_DIR", "HOST_WAYLAND_DISPLAY",
        "GUI_WAYLAND_SOCKET", "GUI_X11_SOCKETDIR", "GUI_DISPLAY",
    ):
        monkeypatch.delenv(key, raising=False)

    runner = FakeRunner()
    monkeypatch.setattr(oc, "run_cmd", runner)
    # C27：镜像 LABEL 查询桩。``image_inspect_info`` 内部走 client_core 自己的
    # run_cmd 绑定（不受上面 oc.run_cmd 桩影响，且 kernel 不应跨模块旁路 I/O 缝），
    # 故按既有约定（同 load_image）在 **oc 命名空间**打桩，由 runner.image_labels
    # 驱动；默认 None → labels 空 → 形态「无法判定」，既有用例零影响。
    monkeypatch.setattr(
        oc,
        "image_inspect_info",
        lambda c, tag: {"digest": "", "labels": dict(runner.image_labels or {})},
    )
    return SimpleNamespace(root=root, repo=tmp_path / "repo", runner=runner, tmp=tmp_path)


# ---------------------------------------------------------------------------
# up 横幅：Jupyter 免登录直达 URL（C22）
# ---------------------------------------------------------------------------


def test_jupyter_direct_url_with_token():
    url = oc.jupyter_direct_url("8890", "abc123")
    assert url == "http://localhost:8890/lab?token=abc123"


def test_jupyter_direct_url_strips_whitespace():
    assert oc.jupyter_direct_url("8893", "  t  ") == "http://localhost:8893/lab?token=t"


@pytest.mark.parametrize("empty", ["", "   ", None])
def test_jupyter_direct_url_without_token_returns_empty(empty):
    assert oc.jupyter_direct_url("8890", empty) == ""


# ---------------------------------------------------------------------------
# C24：容器日志凭证解析（.env 留空 → 密码/token 只进启动日志）
# ---------------------------------------------------------------------------

_CRED_BANNER = """
[2026-09-20 10:00:00] [WARN]  USER_PASSWORD not set, generated random password for devuser

    ************************************************
    * [IMPORTANT] devuser password: S3cretPw16
    * SSH login: ssh devuser@<host> -p 22
    ************************************************

    Jupyter Server is running at:
    http://localhost:8888/lab?token=deadbeefdeadbeefdeadbeefdeadbeef
    Token: deadbeefdeadbeefdeadbeefdeadbeef
"""


def test_parse_credentials_from_entrypoint_banner():
    assert oc.parse_container_credentials(_CRED_BANNER) == (
        "devuser",
        "S3cretPw16",
        "deadbeefdeadbeefdeadbeefdeadbeef",
    )


def test_parse_credentials_never_misreads_root_password():
    """只按 `password:` 匹配会先命中 Root password 行——必须用 SSH login 用户名反查。"""
    log = (
        "    * [IMPORTANT] Root password:      rootPw16\n"
        "    * SSH login: ssh devuser@<host> -p 22\n"
    )
    user, password, _ = oc.parse_container_credentials(log)
    assert user == "devuser"
    assert password == ""  # 不得把 root 密码当成 devuser 密码


@pytest.mark.parametrize("text", ["", "   ", None])
def test_parse_credentials_empty_or_no_banner(text):
    assert oc.parse_container_credentials(text) == ("", "", "")


def test_parse_credentials_ssh_only_has_no_token():
    user, password, token = oc.parse_container_credentials(
        "    * SSH login: ssh devuser@<host> -p 22\n"
    )
    assert (user, password, token) == ("devuser", "", "")


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
    # native 自 2026-09-20 起同样声明 gpu_override（GPU opt-in，C18）
    xd = harness.root / "overlays" / "native-dev"
    xargv = oc.compose_argv(_NATIVE, "up", "-d", gpu=True)
    assert xargv == [
        "podman-compose", "--project-name", "native-dev",
        "--file", str(xd / "compose.yaml"),
        "--file", str(xd / "compose.gpu.yaml"),
        "up", "-d",
    ]
    # 非 GPU 栈不允许 gpu=True（工厂也不会暴露 --gpu）
    with pytest.raises(RuntimeError, match="gpu_override"):
        oc.compose_argv(_MONETIZE, "up", "-d", gpu=True)


# ---------------------------------------------------------------------------
# C27：起容器前的 torch 形态一致性校验（`--torch` 单次覆盖的静默盲区）
# ---------------------------------------------------------------------------

_FLAVOR_LABEL = "org.specweave.torch-flavor"


def test_up_warns_when_image_flavor_differs_from_declared(harness, monkeypatch, capsys):
    """`build --torch cpu` 后 `up --skip-build`：.env 声明 cu130 但镜像实为 cpu。

    C15「CLI 旗标只覆盖单次」× C16「up 恒 --no-build」的交叉盲区：存在性预检
    只查 tag、up 形参面无 `--torch`、构建期守卫只比镜像内部自洽（marker vs
    version.cuda），三处都发现不了，只能在此显式化。
    """
    monkeypatch.setenv("TORCH_FLAVOR", "cu130")
    harness.runner.image_labels = {_FLAVOR_LABEL: "cpu"}

    oc.up_stack(None, _NATIVE, skip_build=True)

    out = capsys.readouterr().out
    assert "镜像 torch 形态与声明不一致" in out
    assert "声明（.env TORCH_FLAVOR）: cu130" in out
    assert "镜像实际" in out and "cpu" in out
    assert "容器将以**镜像实际形态**运行" in out


def test_up_silent_when_image_flavor_matches(harness, monkeypatch, capsys):
    """一致时零噪音（默认路径刚由 build_image 重建，必然走此分支）。"""
    monkeypatch.setenv("TORCH_FLAVOR", "cu130")
    harness.runner.image_labels = {_FLAVOR_LABEL: "cu130"}

    oc.up_stack(None, _NATIVE, skip_build=True)

    assert "形态与声明不一致" not in capsys.readouterr().out


def test_up_flavor_check_tolerates_legacy_image_without_label(harness, capsys):
    """改造前的旧镜像无该 LABEL → 无法判定，不得误报（同 C20 旧归档纪律）。"""
    harness.runner.image_labels = {}

    oc.up_stack(None, _NATIVE, skip_build=True)

    assert "形态与声明不一致" not in capsys.readouterr().out


def test_up_flavor_check_never_probes_non_torch_stack(harness, capsys):
    """quant/monetize 未声明 torch_flavor → 既不查询也不提示（零回归）。"""
    harness.runner.image_labels = {_FLAVOR_LABEL: "cu130"}

    oc.up_stack(None, _MONETIZE, skip_build=True)

    assert "形态与声明不一致" not in capsys.readouterr().out
    assert not [c for c in harness.runner.commands if "image inspect" in c]


def test_up_flavor_check_distinguishes_empty_declaration_from_missing_label(
    harness, monkeypatch, capsys
):
    """空串是合法声明（不装 torch），与「无 LABEL」必须分流（entity 判定核心）。

    native-dev 的 `.env TORCH_FLAVOR=`（显式不装）与旧镜像（无标签）在
    client_core._image_torch_flavor 里都归空串；本校验若照搬会把旧镜像误报成
    「声明空、实物 cpu」。故此处锁定：有 LABEL 且值为空串 + 期望空 = 静默。
    """
    monkeypatch.delenv("TORCH_FLAVOR", raising=False)
    harness.runner.image_labels = {_FLAVOR_LABEL: ""}
    oc.up_stack(None, _NATIVE, skip_build=True)
    assert "形态与声明不一致" not in capsys.readouterr().out

    # 反向：有 LABEL 且值为 cpu，但 .env 显式声明不装 → 必须报
    harness.runner.image_labels = {_FLAVOR_LABEL: "cpu"}
    oc.up_stack(None, _NATIVE, skip_build=True)
    assert "形态与声明不一致" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# C19：GPU 设备解析与运行期可用性预检（修复 `inv native.up --gpu` exit 125）
# ---------------------------------------------------------------------------


def test_gpu_override_file_form_dispatch_and_fallback(harness):
    """形态决定覆盖文件；姊妹文件不存在时回退 generic（不必为每形态建文件）。"""
    d = harness.root / "overlays" / "native-dev"
    assert oc.gpu_override_file(_NATIVE) == d / "compose.gpu.yaml"
    assert oc.gpu_override_file(_NATIVE, "wsl") == d / "compose.gpu.yaml"  # 缺文件→回退
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    assert oc.gpu_override_file(_NATIVE, "wsl") == d / "compose.gpu.wsl.yaml"
    argv = oc.compose_argv(_NATIVE, "up", "-d", gpu=True, gpu_form="wsl")
    assert str(d / "compose.gpu.wsl.yaml") in argv
    assert str(d / "compose.gpu.yaml") not in argv  # 两文件互斥，绝不叠加


# ---------------------------------------------------------------------------
# C23：跨平面判据的期望文件集必须与真正下发的 --file 同源
# ---------------------------------------------------------------------------


def test_compose_config_files_label_matches_compose_convention(harness):
    """期望串 = 下发 --file 的逗号原文串（与 podman 标签同格式，不做路径归一）。"""
    d = harness.root / "overlays" / "onnx-quantized"
    assert oc.compose_config_files_label(_QUANT) == str(d / "compose.yaml")
    assert oc.compose_config_files_label(_QUANT, gpu=True) == (
        f"{d / 'compose.yaml'},{d / 'compose.gpu.yaml'}"
    )


def test_argv_files_and_preflight_label_share_one_source(harness):
    """同源锁：argv 的 --file 集合与预检期望串必须逐字一致。

    这是 C23 的结构性回归门——将来再加覆盖文件（offline/形态若干）时，
    只要两者仍由 compose_files() 推导，判据就不会重新变成假阳性。
    """
    d = harness.root / "overlays" / "native-dev"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    for gpu, form in ((False, "generic"), (True, "generic"), (True, "wsl")):
        argv = oc.compose_argv(_NATIVE, "up", "-d", gpu=gpu, gpu_form=form)
        files = [argv[i + 1] for i, a in enumerate(argv) if a == "--file"]
        assert ",".join(files) == oc.compose_config_files_label(
            _NATIVE, gpu=gpu, gpu_form=form
        )


def test_resolve_gpu_device_autoprobes_dri(harness, monkeypatch):
    """未设令牌：探测命中 /dev/dri → generic 形态，并回写 os.environ。"""
    harness.runner.paths = {"/dev/dri"}
    token, form = oc.resolve_gpu_device(None, _NATIVE, {})
    assert (token, form) == ("/dev/dri", "generic")
    assert os.environ["GPU_DEVICE"] == "/dev/dri"


def test_resolve_gpu_device_nvidia_cdi_precedes_dri(harness, monkeypatch):
    """纯 N 卡宿主（2026-09-20 真机故障）：nvidia_drm 也注册 /dev/dri，但
    CDI 规格 + /dev/nvidiactl 双条件满足时必须优先选 CDI——走 /dev/dri 不
    注入 libcuda/nvidia-smi，容器内 CUDA 恒不可用。"""
    monkeypatch.delenv("GPU_DEVICE", raising=False)
    harness.runner.cdi = True
    harness.runner.paths = {"/dev/dri", oc.NVIDIA_CONTROL_NODE}
    token, form = oc.resolve_gpu_device(None, _NATIVE, {})
    assert (token, form) == (oc.NVIDIA_CDI_TOKEN, "generic")
    assert os.environ["GPU_DEVICE"] == oc.NVIDIA_CDI_TOKEN


def test_resolve_gpu_device_cdi_spec_without_nvidiactl_falls_back_to_dri(harness):
    """守卫第二条件失败（有规格无 N 卡控制节点，异常/残留组合）→ 不选 CDI，
    回退 /dev/dri，避免把不存在的设备引用下发给 podman。"""
    harness.runner.cdi = True
    harness.runner.paths = {"/dev/dri"}
    assert oc.resolve_gpu_device(None, _NATIVE, {}) == ("/dev/dri", "generic")


def test_resolve_gpu_device_nvidia_driver_mismatch_fails_fast(
    harness, monkeypatch, capsys
):
    """CDI 路径的宿主驱动健康门禁：nvidia-smi 报 NVML version mismatch
    （内核模块未随驱动升级重载）时必须 up 前 fail-fast 并给重启/重载指引。"""
    monkeypatch.delenv("GPU_DEVICE", raising=False)
    harness.runner.cdi = True
    harness.runner.paths = {"/dev/dri", oc.NVIDIA_CONTROL_NODE}
    harness.runner.nvidia_smi_ok = False
    harness.runner.nvidia_smi_out = (
        "Failed to initialize NVML: Driver/library version mismatch\n"
        "NVML library version: 595.91\n"
    )
    with pytest.raises(Exit) as ei:
        oc.resolve_gpu_device(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "nvidia-smi 无法运行" in out
    assert "version mismatch" in out
    assert "重启宿主" in out
    assert "nvidia-ctk cdi generate" in out


def test_resolve_gpu_device_explicit_cdi_also_requires_healthy_driver(
    harness, monkeypatch, capsys
):
    """显式 CDI 引用同过健康探针：CDI 只搬运宿主要素，不修宿主驱动故障。"""
    monkeypatch.setenv("GPU_DEVICE", "nvidia.com/gpu=all")
    harness.runner.cdi = True
    harness.runner.nvidia_smi_ok = False
    harness.runner.nvidia_smi_out = "Failed to initialize NVML: Driver/library version mismatch"
    with pytest.raises(Exit):
        oc.resolve_gpu_device(None, _NATIVE, {})
    assert "重启宿主" in capsys.readouterr().out


def test_resolve_gpu_device_autoprobes_wsl_requires_all_gpu_paths(
    harness, monkeypatch, capsys
):
    """WSL2 主场景：只有 /dev/dxg + 三条宿主路径**齐备** → wsl 形态（本次故障的修复点）。

    缺**任一**条都必须 fail-fast（2026-09-20 两轮实测）：
      - 缺 libcuda.so.1：容器内 ``CDLL("libcuda.so.1")`` 直接失败；
      - 缺 libdxcore.so 或 /usr/lib/wsl/drivers：libcuda **能**加载，但 ``cuInit()``
        返 100(CUDA_ERROR_NO_DEVICE)、``torch.cuda.is_available()`` 恒 False。
    三类缺失容器内表现不同却同为「CUDA 不可用」，故统一在宿主侧前置拦截，
    不让 compose 的 bind 在 create 阶段裸报错（create_host_path: false 会直接失败）。
    """
    harness.runner.paths = {"/dev/dxg", *oc.WSL_GPU_PATHS}
    token, form = oc.resolve_gpu_device(None, _NATIVE, {})
    assert (token, form) == ("/dev/dxg", "wsl")
    assert os.environ["GPU_DEVICE"] == "/dev/dxg"
    for missing in oc.WSL_GPU_PATHS:
        # 逐条 drop，且清掉成功调用回写的 env，逼走自动探测分支
        monkeypatch.delenv("GPU_DEVICE", raising=False)
        harness.runner.paths = {
            "/dev/dxg",
            *(p for p in oc.WSL_GPU_PATHS if p != missing),
        }
        with pytest.raises(Exit) as ei:
            oc.resolve_gpu_device(None, _NATIVE, {})
        assert ei.value.code == 1
        assert missing in capsys.readouterr().out  # 指引点名缺失路径


def test_resolve_gpu_device_no_device_fails_fast(harness, capsys):
    """两者皆无 → Exit(1) + 中文指引（替代 podman 的 stat/exit 125 裸报错）。"""
    harness.runner.paths = set()
    with pytest.raises(Exit) as ei:
        oc.resolve_gpu_device(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "/dev/dri / /dev/dxg" in out and "均不存在" in out
    assert "nvidia-ctk cdi generate" in out
    assert "GPU_DEVICE" in out


def test_resolve_gpu_device_explicit_missing_path_fails_fast(harness, monkeypatch, capsys):
    """显式设备路径不存在：不得静默回退探测，必须报错（用户意图明确）。"""
    harness.runner.paths = {"/dev/dri"}
    monkeypatch.setenv("GPU_DEVICE", "/dev/dxg")
    with pytest.raises(Exit) as ei:
        oc.resolve_gpu_device(None, _NATIVE, {})
    assert ei.value.code == 1
    assert "GPU_DEVICE=/dev/dxg 在 podman 宿主不存在" in capsys.readouterr().out


def test_resolve_gpu_device_cdi_requires_generated_specs(harness, monkeypatch):
    """非 `/` 开头=CDI 引用：宿主未生成 /etc/cdi/*.yaml 时前置报错。"""
    monkeypatch.setenv("GPU_DEVICE", "nvidia.com/gpu=all")
    harness.runner.cdi = False
    with pytest.raises(Exit) as ei:
        oc.resolve_gpu_device(None, _NATIVE, {})
    assert ei.value.code == 1
    harness.runner.cdi = True
    assert oc.resolve_gpu_device(None, _NATIVE, {}) == ("nvidia.com/gpu=all", "generic")


def test_up_gpu_wsl_form_flows_to_compose_argv(harness, monkeypatch, capsys):
    """端到端：up --gpu 在 WSL2 设备形态下自动改用 compose.gpu.wsl.yaml。"""
    d = harness.root / "overlays" / "native-dev"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    harness.runner.paths = {"/dev/dxg", *oc.WSL_GPU_PATHS}
    oc.up_stack(None, _NATIVE, gpu=True, skip_build=True)
    up_cmd = [c for c in harness.runner.commands if "up -d --no-build" in c][0]
    assert str(d / "compose.gpu.wsl.yaml") in up_cmd
    assert "/dev/dxg 已透传（compose.gpu.wsl.yaml）" in capsys.readouterr().out


def test_up_gpu_wsl_form_for_quant_same_kernel_path(harness):
    """quant 同修：与 native 共用同一解析内核，形态分派不重复实现。"""
    d = harness.root / "overlays" / "onnx-quantized"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    harness.runner.paths = {"/dev/dxg", *oc.WSL_GPU_PATHS}
    oc.up_stack(None, _QUANT, gpu=True, skip_build=True)
    up_cmd = [c for c in harness.runner.commands if "up -d --no-build" in c][0]
    assert str(d / "compose.gpu.wsl.yaml") in up_cmd


def test_up_gpu_on_gpu_created_stack_is_idempotent(harness, capsys):
    """端到端（C23 的用户可见断言）：连续 `up --gpu` 不得再拆栈重建。

    修复前 up_preflight 的期望值写死 compose.yaml，而运行容器标签是两文件，
    故每次 --gpu 都被判「另一控制平面创建」→ 优雅 down + recreate（销毁容器内
    会话并白等 ~66s 首启）。这里断言：真活体 + 标签与本次下发集全等 → 零 down。
    """
    d = harness.root / "overlays" / "native-dev"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    harness.runner.paths = {"/dev/dxg", *oc.WSL_GPU_PATHS}
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = f"{d / 'compose.yaml'},{d / 'compose.gpu.wsl.yaml'}"
    oc.up_stack(None, _NATIVE, gpu=True, skip_build=True)
    assert not any(" down" in c for c in harness.runner.commands)
    assert "另一控制平面" not in capsys.readouterr().out


def test_up_without_gpu_never_probes_devices(harness):
    """默认隔离承诺：不带 --gpu 时不发生任何设备探测（零副作用）。"""
    oc.up_stack(None, _NATIVE, skip_build=True)
    assert not any(c.startswith("test -e ") for c in harness.runner.commands)
    assert "GPU_DEVICE" not in os.environ


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


def test_prepare_env_native_mounts_anchor_repo_root(harness):
    oc.prepare_env(_NATIVE)
    assert os.environ["NPU_TVM_PATH"].endswith("repo/external/chaos/npu_tvm")
    assert os.environ["NPUUSERTOOLS_PATH"].endswith("npuusertools")
    assert os.environ["MODELS_PATH"].endswith("models")


def test_prepare_env_native_temp_mount_default_and_autocreate(harness, monkeypatch):
    """临时目录挂载：缺省锚仓库根上溯四级（根工作区 .temp），缺失幂等 mkdir。

    不在 tmp 布局下实跑缺省值——上溯四级会指到 tmp 之外（文件系统根一带），
    故只做声明式断言；mkdir 语义用显式 env 覆盖实跑。
    """
    spec = next(m for m in _NATIVE.source_mounts if m.env == "NATIVE_TEMP_PATH")
    assert spec.anchor == "repo" and spec.default_rel == "../../../../.temp"
    assert spec.must_exist is False
    target = harness.tmp / "fresh-temp"
    assert not target.exists()
    monkeypatch.setenv("NATIVE_TEMP_PATH", str(target))
    oc.prepare_env(_NATIVE)
    assert target.is_dir()
    assert os.environ["NATIVE_TEMP_PATH"] == oc.to_posix_path(target)


def test_resolve_path_relative_deep_path_autocreates(harness, monkeypatch):
    """守卫不误伤合法相对路径：cwd 下正常深度仍幂等创建并转 POSIX 注入。"""
    monkeypatch.chdir(harness.root)
    got = oc._resolve_path(
        _NATIVE, "scratch-temp", must_exist=False, create=True, label="临时目录"
    )
    target = harness.root / "scratch-temp"
    assert target.is_dir()
    assert got == oc.to_posix_path(target)


def test_resolve_path_filesystem_root_child_fails_fast(harness, monkeypatch, capsys):
    """越界解析守卫：上溯越出检出布局（解析成 /.temp / D:\\.temp）必须 fail-fast
    并指引设 env_key，而非裸 PermissionError（native-overlay 规则 §4① 收口）。"""
    monkeypatch.chdir(harness.tmp)
    with pytest.raises(Exit) as ei:
        oc._resolve_path(
            _NATIVE,
            "../../../../../../../../../../.temp",
            must_exist=False,
            create=True,
            label="临时目录（根工作区 .temp）",
            env_key="NATIVE_TEMP_PATH",
        )
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "NATIVE_TEMP_PATH" in out
    assert "越界" in out


@pytest.mark.skipif(
    os.name == "nt" or getattr(os, "geteuid", lambda: 1)() == 0,
    reason="需非 root POSIX：目录写位才构成真实权限拒绝（Windows 只读位不阻止写入）",
)
def test_resolve_path_mkdir_permission_error_becomes_exit(harness, monkeypatch, capsys):
    """create 分支的 OSError 转为可操作 Exit(1)（含 errno），而非裸 traceback。"""
    inner = harness.tmp / "locked" / "inner"
    inner.mkdir(parents=True)
    os.chmod(inner, 0o500)
    monkeypatch.chdir(inner)
    with pytest.raises(Exit) as ei:
        oc._resolve_path(
            _NATIVE, "grandchild", must_exist=False, create=True, label="临时目录"
        )
    assert ei.value.code == 1
    assert "目录创建失败" in capsys.readouterr().out


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
        oc.gate_platform(_NATIVE)
    assert ei.value.code == 0
    assert "NPU_TVM_PATH" in seen["keys"]
    assert "QUANT_IMAGE_TAG" not in seen["keys"]


def test_gate_platform_windows_no_bridge_message(harness, monkeypatch, capsys):
    """门禁必须原样带出探测原因 + wsl --shutdown 逃生指引（见下条回归）。"""
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    monkeypatch.setattr(
        oc, "wsl_bridge_diagnosis", lambda: "execvpe(/bin/true) failed: I/O error"
    )
    with pytest.raises(Exit) as ei:
        oc.gate_platform(_MONETIZE)
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "[monetize]" in out
    assert "invoke monetize.up" in out
    assert "COMPOSE_WSL_DISTRO" in out
    assert "execvpe(/bin/true) failed: I/O error" in out
    assert "wsl --shutdown" in out


def test_gate_platform_windows_no_bridge_without_diagnosis(harness, monkeypatch, capsys):
    """探测无原因（非 Windows/已关闭）时不打印诊断块，避免噪音。"""
    monkeypatch.setattr(oc, "platform", SimpleNamespace(system=lambda: "Windows"))
    monkeypatch.setattr(oc, "run_in_wsl_bridge", lambda *a, **k: None)
    monkeypatch.setattr(oc, "wsl_bridge_diagnosis", lambda: "")
    with pytest.raises(Exit):
        oc.gate_platform(_MONETIZE)
    out = capsys.readouterr().out
    assert "桥接探测失败" not in out
    assert "wsl --shutdown" not in out


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
    assert oc.container_running(None, _NATIVE) is True
    cmd = harness.runner.commands[-1]
    assert f"label={oc.PROJECT_LABEL}=native-dev" in cmd
    assert f"label={oc.SERVICE_LABEL}=native" in cmd


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
    win = r"D:\spaces\SpecWeave\apps\containers\client\overlays\native-dev\compose.yaml"
    wsl = "/mnt/d/spaces/SpecWeave/apps/containers/client/overlays/native-dev/compose.yaml"
    assert oc.config_paths_diverge(win, wsl) is True
    assert oc.config_paths_diverge(wsl, wsl) is False
    # inspect 失败（actual 为空）时不动作：未知不判分歧
    assert oc.config_paths_diverge("", wsl) is False


def test_up_preflight_reaps_orphan_rootlessport(harness):
    # 无活体项目容器（裸 compose 失败现场），孤儿 rootlessport 占着 2223/8890
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    oc.up_preflight(None, _NATIVE, env={})
    kills = [c for c in harness.runner.commands if c.startswith("kill")]
    assert kills == ["kill 92823"]  # TERM 即生效，不应升级 kill -9
    assert not any(" down" in c for c in harness.runner.commands)


def test_up_preflight_never_kills_other_holders(harness):
    # pasta（jupyter 栈转发器）即使监听端口也绝不回收
    harness.runner.ss_output = _SS_LINES[3]
    oc.up_preflight(None, _NATIVE, env={})
    assert not any(c.startswith("kill") for c in harness.runner.commands)


def test_up_preflight_cross_plane_running_container_triggers_down(harness):
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = (
        r"D:\spaces\SpecWeave\apps\containers\client"
        r"\overlays\native-dev\compose.yaml"
    )
    oc.up_preflight(None, _NATIVE, env={})
    downs = [c for c in harness.runner.commands if " down" in c]
    assert len(downs) == 1 and "--project-name native-dev" in downs[0]
    # 优雅 down 后无活体容器，剩余孤儿同样被回收
    assert any(c.startswith("kill ") and "-9" not in c for c in harness.runner.commands)


def test_up_preflight_same_plane_running_is_noop(harness):
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = str(
        harness.root / "overlays" / _NATIVE.overlay_subdir / "compose.yaml"
    )
    oc.up_preflight(None, _NATIVE, env={})
    assert not any(" down" in c or c.startswith("kill") for c in harness.runner.commands)


# ---- C23：--gpu 的期望文件集（修复「每次 --gpu 都被判成另一控制平面」） ----

def _gpu_plane_label(harness, subdir: str, *names: str) -> str:
    d = harness.root / "overlays" / subdir
    return ",".join(str(d / n) for n in names)


def test_up_preflight_gpu_plane_no_false_divergence(harness):
    """`up --gpu` 对**同样由 --gpu 创建**的栈：标签与本次下发集全等 → 不重建。"""
    d = harness.root / "overlays" / "native-dev"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = _gpu_plane_label(
        harness, "native-dev", "compose.yaml", "compose.gpu.wsl.yaml"
    )
    oc.up_preflight(None, _NATIVE, env={}, gpu=True, gpu_form="wsl")
    assert not any(" down" in c or c.startswith("kill") for c in harness.runner.commands)


def test_up_preflight_gpu_plane_keeps_real_divergence(harness):
    """不对称性必须保留：无 --gpu 的 up 看到 --gpu 创建的栈仍判分歧（真会 recreate）。"""
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = _gpu_plane_label(
        harness, "native-dev", "compose.yaml", "compose.gpu.wsl.yaml"
    )
    oc.up_preflight(None, _NATIVE, env={})  # 本平面只下发 compose.yaml
    assert any(" down" in c for c in harness.runner.commands)


def test_up_preflight_form_change_is_still_divergence(harness):
    """形态切换（generic ↔ wsl）是**真**配置漂移：必须仍走优雅 down。"""
    d = harness.root / "overlays" / "native-dev"
    (d / "compose.gpu.wsl.yaml").write_text("services: {}\n")
    harness.runner.running = True
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.config_files = _gpu_plane_label(
        harness, "native-dev", "compose.yaml", "compose.gpu.yaml"
    )
    oc.up_preflight(None, _NATIVE, env={}, gpu=True, gpu_form="wsl")
    assert any(" down" in c for c in harness.runner.commands)


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
    pid, cid, name = oc.parse_conmon_process(_conmon_line(111413, _CID_STALE_X, "native-dev"))
    assert (pid, cid, name) == (111413, _CID_STALE_X, "native-dev")
    assert oc.parse_conmon_process("  900 /usr/sbin/crun -b /x") is None
    assert oc.parse_conmon_process("not-a-pid /usr/bin/conmon -c x") is None


def test_stale_conmon_detection_double_gate(harness):
    # live：当前运行 native 容器；ps 含 活native / stale-native / stale-quant 三个 conmon
    harness.runner.live_ps = _CID_LIVE[:12]
    harness.runner.conmon_ps = "\n".join([
        _conmon_line(100, _CID_LIVE, "native-dev"),
        _conmon_line(111413, _CID_STALE_X, "native-dev"),
        _conmon_line(200, _CID_STALE_Q, "onnx-quantized"),
    ])
    stale = oc._list_stale_conmons(None, _NATIVE)
    # 只回收：本栈名 + 容器已不在 libpod；活 conmon 与他栈 conmon 都不动
    assert stale == [(111413, _CID_STALE_X[:12])]


def test_up_preflight_reaps_stale_conmon_and_rootlessport(harness):
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.conmon_ps = _conmon_line(111413, _CID_STALE_X, "native-dev")
    oc.up_preflight(None, _NATIVE, env={})
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
    assert oc.container_running(None, _NATIVE) is True  # daemon 视角仍撒谎
    cid = oc._running_project_container(None, _NATIVE)
    assert oc._container_truly_alive(None, _NATIVE, cid) is False
    harness.runner.host_alive = True
    assert oc._container_truly_alive(None, _NATIVE, cid) is True


def test_up_preflight_fake_up_forces_clean_rebuild(harness):
    # daemon 报 running + 报 PID，但 ps -p 宿主查无此进程；端口/孤儿都在
    harness.runner.running = True
    harness.runner.init_pid = 111845
    harness.runner.host_alive = False
    harness.runner.ss_output = "\n".join(_SS_LINES[:3])
    harness.runner.conmon_ps = _conmon_line(111413, _CID_STALE_X, "native-dev")
    oc.up_preflight(None, _NATIVE, env={})
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
        oc.require_running(None, _NATIVE)


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
    x = oc.make_stack_tasks(_NATIVE)
    m = oc.make_stack_tasks(_MONETIZE)
    assert _param_names(q["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]
    assert _param_names(x["build"]) == [
        "tag", "base_image", "pip_mirror", "conda_mirror", "torch", "no_cache",
    ]
    assert _param_names(m["build"]) == ["tag", "base_image", "pip_mirror", "no_cache"]


def test_factory_up_smoke_params_are_capability_union(harness):
    """up/smoke 形参面 = 已声明能力的并集（gpu_override ∪ supports_offline）。

    native 自 2026-09-20 起同时声明两者，故 gpu 与 offline 必须**并存**——
    历史的三路互斥写法会让 --offline 被 gpu 分支吃掉（C18）。
    """
    q, x, m = (oc.make_stack_tasks(s) for s in (_QUANT, _NATIVE, _MONETIZE))
    assert _param_names(q["up"]) == ["gpu", "skip_build"]
    assert _param_names(x["up"]) == [
        "gpu", "passthrough", "gui", "usb", "skip_build", "offline", "no_offline",
    ]
    assert _param_names(m["up"]) == ["skip_build"]
    assert _param_names(q["smoke"]) == ["gpu"]
    assert _param_names(x["smoke"]) == ["gpu", "passthrough", "gui", "usb"]
    assert _param_names(m["smoke"]) == []
    assert _param_names(q["down"]) == ["volumes"]
    assert _param_names(x["logs"]) == ["tail"]


def test_factory_auto_shortflags_quant_on_others_off(harness):
    q = oc.make_stack_tasks(_QUANT)
    x = oc.make_stack_tasks(_NATIVE)
    assert all(t.auto_shortflags is True for t in q.values())
    assert all(t.auto_shortflags is False for t in x.values())


def test_bridge_keys_isolated_per_stack():
    """桥接键下沉后，各栈只带自己的前缀，不枚举其他栈（F-10）。"""
    joined = " ".join(_QUANT.bridge_env_keys)
    assert "NATIVE_" not in joined and "MONETIZE_" not in joined
    assert "QUANT_WORKSPACE" in _QUANT.bridge_env_keys
    assert "NPU_TVM_PATH" in _NATIVE.bridge_env_keys
    assert "NATIVE_TEMP_PATH" in _NATIVE.bridge_env_keys
    assert "MONETIZE_SRC_PATH" in _MONETIZE.bridge_env_keys
    xj = " ".join(_NATIVE.bridge_env_keys)
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


def test_build_task_argv_native_includes_conda(harness):
    tasks = oc.make_stack_tasks(_NATIVE)
    tasks["build"].body(
        None, tag=None, base_image=_NATIVE.default_base_image,
        pip_mirror="aliyun", conda_mirror="tuna", no_cache=False,
    )
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg CONDA_MIRROR=tuna" in build_cmd
    assert "-t localhost/native-dev:latest" in build_cmd
    # C15：三处同键——TORCH_FLAVOR 与 compose.yaml build.args 的 ${TORCH_FLAVOR:-} 同键
    assert "--build-arg TORCH_FLAVOR=" in build_cmd


def test_build_task_argv_native_torch_flavor_flows(harness):
    """--torch cu130 必须落到 podman build 的 --build-arg（C15 三处一致）。"""
    tasks = oc.make_stack_tasks(_NATIVE)
    tasks["build"].body(
        None, tag="localhost/native-dev:cuda", base_image=_NATIVE.default_base_image,
        pip_mirror="official", conda_mirror="official", torch="cu130", no_cache=False,
    )
    build_cmd = [c for c in harness.runner.commands if " build " in c][0]
    assert "--build-arg TORCH_FLAVOR=cu130" in build_cmd
    assert "-t localhost/native-dev:cuda" in build_cmd


def test_compose_torch_flavor_default_matches_kernel_default(harness):
    """C15：compose 段 ``${TORCH_FLAVOR:-<默认>}`` 必须与内核缺省同默认。

    三处同键同默认（`invoke build` / `up` 内联构建 / compose build 段）是层缓存
    不失效的前提；内核缺省为**空串**（不装 torch），compose 段必须逐字一致。
    """
    overlays = Path(__file__).resolve().parents[1] / "overlays"
    text = (overlays / _NATIVE.overlay_subdir / "compose.yaml").read_text(encoding="utf-8")
    m = re.search(r"\$\{TORCH_FLAVOR:-([^}]*)\}", text)
    assert m, f"{_NATIVE.overlay_subdir}/compose.yaml 未声明 TORCH_FLAVOR 构建参数"
    assert m.group(1) == ""


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
    oc.up_stack(None, _NATIVE, gpu=False)
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
    args = oc.resolve_build_args(_NATIVE, {})
    assert args == {
        "base_image": _NATIVE.default_base_image,
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
        assert oc.resolve_build_args(_NATIVE, {}, torch=flavor)["torch_flavor"] == flavor
    assert oc.resolve_build_args(_NATIVE, {}, torch="")["torch_flavor"] == ""
    monkeypatch.setenv("TORCH_FLAVOR", "cu129")
    with pytest.raises(Exit):
        oc.resolve_build_args(_NATIVE, {})
    assert oc.resolve_build_args(_NATIVE, {}, torch="cpu")["torch_flavor"] == "cpu"


def test_build_args_cli_flag_beats_env(harness, monkeypatch):
    """CLI 旗标优先级高于 .env（单次覆盖），但 compose 段看不到旗标。"""
    monkeypatch.setenv("PIP_MIRROR", "tuna")
    args = oc.resolve_build_args(_QUANT, {}, pip_mirror="aliyun")
    assert args["pip_mirror"] == "aliyun"


def test_down_task_volumes_flag(harness):
    tasks = oc.make_stack_tasks(_NATIVE)
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


def test_smoke_stopped_native_guard_only(harness):
    harness.runner.running = False
    oc.smoke_stack(None, _NATIVE)
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
# 离线模式（仅 native 声明 supports_offline；V-1 桥接透传 / V-2 compose --no-build）
# ---------------------------------------------------------------------------


def test_offline_declared_only_for_native():
    assert _NATIVE.supports_offline is True
    assert _QUANT.supports_offline is False and _MONETIZE.supports_offline is False
    assert _NATIVE.offline_env_key == "NATIVE_OFFLINE"
    assert "NATIVE_OFFLINE" in _NATIVE.bridge_env_keys


def test_resolve_offline_flag_written_back_to_env(harness, monkeypatch):
    """V-1：显式旗标必须在 gates（WSL 桥接）之前固化进 os.environ。"""
    monkeypatch.setenv("NATIVE_OFFLINE", "0")
    assert oc.resolve_offline(_NATIVE, True, False) is True
    assert os.environ["NATIVE_OFFLINE"] == "1"
    assert oc.resolve_offline(_NATIVE, False, True) is False
    assert os.environ["NATIVE_OFFLINE"] == "0"


def test_resolve_offline_env_fallback_conflict_and_non_offline_stack(harness, monkeypatch):
    monkeypatch.setenv("NATIVE_OFFLINE", "yes")
    assert oc.resolve_offline(_NATIVE, False, False) is True
    monkeypatch.setenv("QUANT_OFFLINE", "1")
    assert oc.resolve_offline(_QUANT, False, False) is False
    with pytest.raises(Exit):
        oc.resolve_offline(_NATIVE, True, True)


def test_compose_up_tail_always_no_build():
    """C16 取代 V-2 的 offline 分叉：--no-build 对非离线 up 同样必须成立。"""
    assert oc.compose_up_tail() == ["up", "-d", "--no-build"]


def test_offline_exec_env_gated_by_declaration_and_env(harness, monkeypatch):
    monkeypatch.delenv("NATIVE_OFFLINE", raising=False)
    assert oc.offline_exec_env(_NATIVE) == []
    monkeypatch.setenv("NATIVE_OFFLINE", "1")
    assert oc.offline_exec_env(_NATIVE) == ["-e", "NATIVE_OFFLINE=1"]
    assert oc.offline_exec_env(_QUANT) == []


def test_build_image_offline_fails_fast_before_any_command(harness, monkeypatch):
    monkeypatch.setenv("NATIVE_OFFLINE", "1")
    with pytest.raises(Exit) as ei:
        oc.build_image(
            None, _NATIVE, tag=None,
            base_image=_NATIVE.default_base_image, pip_mirror="official",
        )
    assert ei.value.code == 1
    assert harness.runner.commands == []  # 未发生任何 podman 调用


def test_up_offline_forces_skip_build_and_compose_no_build(harness):
    oc.up_stack(None, _NATIVE, offline=True)
    cmds = harness.runner.commands
    assert not any(" build " in c for c in cmds)
    assert any("up -d --no-build" in c for c in cmds)


def test_up_offline_missing_image_exits(harness, capsys):
    harness.runner.image_exists = False
    with pytest.raises(Exit) as ei:
        oc.up_stack(None, _NATIVE, offline=True)
    assert ei.value.code == 1
    assert "离线模式下本地缺少镜像" in capsys.readouterr().out


def test_up_task_body_offline_flag_survives_to_argv(harness, monkeypatch):
    monkeypatch.setenv("NATIVE_OFFLINE", "0")
    tasks = oc.make_stack_tasks(_NATIVE)
    tasks["up"].body(None, skip_build=False, offline=True, no_offline=False)
    assert os.environ["NATIVE_OFFLINE"] == "1"
    assert any("up -d --no-build" in c for c in harness.runner.commands)


def test_save_load_tasks_only_for_offline_stack(harness):
    assert "save" not in oc.make_stack_tasks(_QUANT)
    assert "load" not in oc.make_stack_tasks(_MONETIZE)
    x = oc.make_stack_tasks(_NATIVE)
    assert _param_names(x["save"]) == ["tag", "cache_dir"]
    assert _param_names(x["load"]) == ["path", "cache_dir"]


# ---------------------------------------------------------------------------
# C20：load 的 torch 形态感知（选档过滤 + 显式路径校验）
# ---------------------------------------------------------------------------


def _archive(dir_: Path, flavor: str, ts: str) -> Path:
    """造出可被 archive_flavor 解析的归档名（内容无关，integrity 已打桩）。"""
    stem = f"localhost-native-dev-torch-{flavor}" if flavor else "localhost-native-dev-latest"
    p = dir_ / f"{stem}-abc123def456-{ts}.tar.gz"
    p.write_bytes(b"x")
    return p


@pytest.fixture
def load_env(harness, monkeypatch, tmp_path):
    monkeypatch.setattr(oc, "validate_manifest_integrity", lambda d, p: "")
    loaded: list[Path] = []
    monkeypatch.setattr(
        oc,
        "load_image",
        lambda c, p: (loaded.append(p), SimpleNamespace(loaded=True, message=""))[1],
    )
    cache = tmp_path / "cache"
    cache.mkdir()
    tasks = oc.make_stack_tasks(_NATIVE)

    def run(flavor: str, *, path=None, cache_path=None):
        monkeypatch.setattr(
            oc,
            "_load_env_overrides",
            lambda r: {"TORCH_FLAVOR": flavor} if flavor else {},
        )
        tasks["load"].body(None, path=path, cache_dir=str(cache_path or cache))

    return SimpleNamespace(cache=cache, loaded=loaded, run=run)


def test_load_filters_archive_by_expected_flavor(load_env, capsys):
    """cpu 归档更新，但期望 cu130 → 必须取 cu130（否则静默导入错形态）。"""
    cpu = _archive(load_env.cache, "cpu", "20260920-120000")
    cu130 = _archive(load_env.cache, "cu130", "20260920-110000")
    os.utime(cpu, (2_000_000_000, 2_000_000_000))
    os.utime(cu130, (1_000_000_000, 1_000_000_000))
    load_env.run("cu130")
    assert load_env.loaded == [cu130]
    out = capsys.readouterr().out
    assert "自动选择最新归档" in out and "归档 torch 形态: cu130" in out


def test_load_without_matching_flavor_exits(load_env, capsys):
    _archive(load_env.cache, "cpu", "20260920-120000")
    with pytest.raises(Exit) as ei:
        load_env.run("cu130")
    assert ei.value.code == 1
    assert "未找到该形态归档" in capsys.readouterr().out


def test_load_explicit_path_flavor_mismatch_exits(load_env, capsys):
    cpu = _archive(load_env.cache, "cpu", "20260920-120000")
    with pytest.raises(Exit) as ei:
        load_env.run("cu130", path=str(cpu))
    assert ei.value.code == 1
    assert "形态与 TORCH_FLAVOR 不符" in (ei.value.message or "")
    assert load_env.loaded == []  # 校验先于导入


def test_load_unmarked_legacy_archive_warns_but_passes(load_env, capsys):
    legacy = _archive(load_env.cache, "", "20260920-120000")
    load_env.run("cu130", path=str(legacy))
    assert load_env.loaded == [legacy]
    assert "未标注 torch 形态" in capsys.readouterr().out


def test_load_without_torch_flavor_keeps_latest_semantics(load_env, capsys):
    """期望形态为空（不装 torch）：不过滤，保持历史「取最新」语义（零回归）。"""
    older = _archive(load_env.cache, "cu130", "20260920-110000")
    newer = _archive(load_env.cache, "cpu", "20260920-120000")
    os.utime(older, (1_000_000_000, 1_000_000_000))
    os.utime(newer, (2_000_000_000, 2_000_000_000))
    load_env.run("")
    assert load_env.loaded == [newer]
    assert "归档 torch 形态: cpu" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# C21：up 的服务就绪等待（容器 Up ≠ 服务可访问）
# ---------------------------------------------------------------------------


def test_up_waits_for_jupyter_on_host_port(harness, monkeypatch, capsys):
    """就绪探测必须落在**宿主 Jupyter 端口**上，且带进度反馈通道。"""
    seen: dict = {}

    def fake(port, **kwargs):
        seen["port"] = port
        seen["progress"] = kwargs.get("on_progress")
        return True, f"127.0.0.1:{port} → HTTP 302"

    monkeypatch.setattr(oc, "wait_http_ready", fake)
    oc.up_stack(None, _NATIVE, skip_build=True)
    assert seen["port"] == 8890
    assert callable(seen["progress"])
    out = capsys.readouterr().out
    assert "栈已启动" in out
    assert "Jupyter 已就绪（127.0.0.1:8890 → HTTP 302）" in out


def test_up_ready_timeout_warns_without_failing(harness, monkeypatch, capsys):
    """超时**不判失败**：容器确实 Up，只给指引（否则一次慢启动就中断部署）。"""
    monkeypatch.setattr(
        oc, "wait_http_ready", lambda port, **kw: (False, "RemoteDisconnected（120s 无 HTTP 应答）")
    )
    oc.up_stack(None, _NATIVE, skip_build=True)  # 不抛 Exit
    out = capsys.readouterr().out
    assert "⚠ Jupyter 未在 120s 内应答" in out
    assert f"invoke {_NATIVE.namespace}.logs" in out
    assert "Jupyter localhost:8890" in out  # URL 仍给出，供用户稍后刷新


# ---------------------------------------------------------------------------
# C24：up 横幅回读容器内生成的凭证
# ---------------------------------------------------------------------------


def test_up_banner_prints_readback_credentials(harness, monkeypatch, capsys):
    """密码与直达 URL 取自**容器日志回读**，而非留空的 .env（本轮问题根因）。"""
    monkeypatch.setattr(oc, "_running_project_container", lambda c, s: "cid")
    monkeypatch.delenv("JUPYTER_TOKEN", raising=False)
    harness.runner.container_logs = _CRED_BANNER
    oc.up_stack(None, _NATIVE, skip_build=True)
    out = capsys.readouterr().out
    assert "密码    devuser / S3cretPw16" in out
    assert "直达    http://localhost:8890/lab?token=deadbeefdeadbeefdeadbeefdeadbeef" in out


def test_up_banner_omits_credentials_when_unreadable(harness, monkeypatch, capsys):
    """回读不到（容器未跑 / 日志无横幅）时静默降级：不增行、不报错。"""
    monkeypatch.delenv("JUPYTER_TOKEN", raising=False)
    oc.up_stack(None, _NATIVE, skip_build=True)
    out = capsys.readouterr().out
    assert "密码" not in out
    assert "直达" not in out


def test_up_banner_prints_copyable_ssh_command(harness, capsys):
    """SSH 行必须是**完整可复制命令**（含 -p 与用户名）。

    只印裸地址 `localhost:2223` 时用户按习惯敲 `ssh devuser@localhost` 会落到
    宿主自身 sshd（宿主无 devuser 用户）而必报 Permission denied——ssh 不支持
    user@host:port 语法，端口只能经 -p 表达（04-troubleshooting-guide.md C-I8）。
    """
    oc.up_stack(None, _NATIVE, skip_build=True)
    out = capsys.readouterr().out
    assert "ssh -p 2223 devuser@localhost" in out
    # 端口须随 spec/环境变量漂移，不得写死默认值
    assert "SSH     localhost:" not in out


def test_up_banner_ssh_command_follows_port_env(harness, monkeypatch, capsys):
    """端口经 `.env`/环境覆盖时命令同步变化（否则用户连到错误端口）。"""
    monkeypatch.setenv(_NATIVE.ssh_port_env, "2299")
    oc.up_stack(None, _NATIVE, skip_build=True)
    assert "ssh -p 2299 devuser@localhost" in capsys.readouterr().out


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
    names = oc.compose_echo_names(_NATIVE)
    assert oc.is_benign_compose_noise(_HEX_ID, names=names)
    assert oc.is_benign_compose_noise(f"  {_HEX_ID}  ", names=names)  # 允许两侧空白
    assert oc.is_benign_compose_noise(_NATIVE.project, names=names)
    assert oc.is_benign_compose_noise(f"pod_{_NATIVE.project}", names=names)
    assert oc.is_benign_compose_noise(f"{_NATIVE.project}_default", names=names)
    assert oc.is_benign_compose_noise(_PASTA_DBUS_LINE, names=names)
    # —— 反例：真实错误必须可见（含裸 ID / 名字出现在上下文里） ——
    assert not oc.is_benign_compose_noise(
        f'Error: unable to start container "{_HEX_ID}": netavark: failed to create '
        "aardvark-dns directory /run/user/1000/containers/networks/aardvark-dns: "
        "IO error: No such file or directory (os error 2)",
        names=names,
    )
    assert not oc.is_benign_compose_noise(f"{_NATIVE.project} 端口被占用", names=names)
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
        stdout=f"{_HEX_ID}\n{_HEX_ID2}\n{_NATIVE.project}\n",
        stderr=_PASTA_DBUS_LINE + "\n",
    )
    oc.run_compose_up(None, _NATIVE, *oc.compose_up_tail())
    out = capsys.readouterr().out
    assert _HEX_ID not in out and _HEX_ID2 not in out
    assert "ERROR[0001]" not in out
    assert _NATIVE.project not in out.splitlines()  # 裸名字行被丢弃（执行行含名字）
    assert "已过滤 4 行" in out


def test_run_compose_up_failure_prints_raw_and_exits(harness, monkeypatch, capsys):
    """失败路径零过滤：裸 ID 与真实错误全量原样回放，退出码透传。"""
    err = f'Error: unable to start container "{_HEX_ID}": netavark: IO error'
    _stub_run_cmd(monkeypatch, stdout=f"{_HEX_ID}\n{_NATIVE.project}\n", stderr=err + "\n", ok=False, rc=125)
    with pytest.raises(Exit) as ei:
        oc.run_compose_up(None, _NATIVE, *oc.compose_up_tail())
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


# ---------------------------------------------------------------------------
# 透传覆盖（host 网络 + D-Bus / USB；与 C19/C23 同族 opt-in 门禁）
# ---------------------------------------------------------------------------


def _argv_files(argv: list[str]) -> list[str]:
    return [argv[i + 1] for i, a in enumerate(argv) if a == "--file"]


def test_compose_files_passthrough_usb_order_and_label(harness):
    """文件序 base → GPU → 透传主层 → GUI（Wayland→X11）→ USB；label 同源。"""
    d = harness.root / "overlays/native-dev"
    argv = oc.compose_argv(_NATIVE, "up", "-d", passthrough=True)
    assert _argv_files(argv) == [
        str(d / "compose.yaml"), str(d / "compose.passthrough.yaml"),
    ]
    argv = oc.compose_argv(_NATIVE, "up", "-d", usb=True)
    assert _argv_files(argv) == [
        str(d / "compose.yaml"), str(d / "compose.passthrough.usb.yaml"),
    ]
    argv = oc.compose_argv(
        _NATIVE, "up", "-d", gpu=True, passthrough=True,
        gui=True, gui_forms=("wayland", "x11"), usb=True,
    )
    assert _argv_files(argv) == [
        str(d / "compose.yaml"),
        str(d / "compose.gpu.yaml"),
        str(d / "compose.passthrough.yaml"),
        str(d / "compose.passthrough.gui.yaml"),
        str(d / "compose.passthrough.gui.x11.yaml"),
        str(d / "compose.passthrough.usb.yaml"),
    ]
    assert ",".join(_argv_files(argv)) == oc.compose_config_files_label(
        _NATIVE, gpu=True, passthrough=True,
        gui=True, gui_forms=("wayland", "x11"), usb=True,
    )
    # 单通道形态只加载对应一层
    argv = oc.compose_argv(_NATIVE, "up", "-d", gui=True, gui_forms=("x11",))
    assert _argv_files(argv) == [
        str(d / "compose.yaml"), str(d / "compose.passthrough.gui.x11.yaml"),
    ]
    # 未声明能力的栈收到开关 = 内部不变量违例
    with pytest.raises(RuntimeError, match="passthrough_overlay"):
        oc.compose_files(_QUANT, passthrough=True)
    with pytest.raises(RuntimeError, match="usb_overlay"):
        oc.compose_files(_MONETIZE, usb=True)
    with pytest.raises(RuntimeError, match="gui_overlay"):
        oc.compose_files(_QUANT, gui=True, gui_forms=("wayland",))
    # gui=True 但无探测形态 = 门禁被绕过的内部不变量违例
    with pytest.raises(RuntimeError, match="gui_forms 为空"):
        oc.compose_files(_NATIVE, gui=True)


def test_resolve_passthrough_happy_path_writes_env(harness):
    harness.runner.paths = {"/run/user/1000/bus"}
    dbus, sshd = oc.resolve_passthrough(None, _NATIVE, {})
    assert (dbus, sshd) == ("/run/user/1000/bus", "2223")
    assert os.environ["DBUS_SESSION_BUS_PATH"] == "/run/user/1000/bus"
    assert os.environ["HOST_NET_SSHD_PORT"] == "2223"


def test_resolve_passthrough_env_token_precedence(harness):
    """.env 令牌可换系统总线 / SSH 端口（shell export 不在本用例设置）。"""
    harness.runner.paths = {"/run/dbus/system_bus_socket"}
    dbus, sshd = oc.resolve_passthrough(None, _NATIVE, {
        "DBUS_SESSION_BUS_PATH": "/run/dbus/system_bus_socket",
        "HOST_NET_SSHD_PORT": "2333",
    })
    assert dbus == "/run/dbus/system_bus_socket" and sshd == "2333"
    cmds = harness.runner.commands
    assert "test -S /run/dbus/system_bus_socket" in cmds


def test_resolve_passthrough_missing_dbus_fails_fast(harness, capsys):
    harness.runner.paths = set()
    with pytest.raises(Exit) as ei:
        oc.resolve_passthrough(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "D-Bus 会话总线" in out
    assert "DBUS_SESSION_BUS_PATH=/run/dbus/system_bus_socket" in out
    assert "去掉 --passthrough" in out


def test_resolve_passthrough_auto_probes_non_1000_uid(harness):
    """UID≠1000 的宿主：不再依赖硬编码缺省，按 id -u 探测到真实会话总线。

    2026-09-24 本机回归：UID=1006，总线在 /run/user/1006/bus，历史缺省
    /run/user/1000/bus 必然不存在。
    """
    harness.runner.paths = {"/run/user/1006/bus"}
    dbus, sshd = oc.resolve_passthrough(None, _NATIVE, {})
    assert (dbus, sshd) == ("/run/user/1006/bus", "2223")
    assert os.environ["DBUS_SESSION_BUS_PATH"] == "/run/user/1006/bus"
    probe = [c for c in harness.runner.commands if '"/run/user/$(id -u)/bus"' in c]
    assert len(probe) == 1
    # 探测覆盖三候选：DBUS_SESSION_BUS_ADDRESS / XDG_RUNTIME_DIR / id -u
    assert "DBUS_SESSION_BUS_ADDRESS" in probe[0]
    assert "XDG_RUNTIME_DIR" in probe[0]


def test_resolve_passthrough_explicit_token_skips_probe(harness):
    """显式 DBUS_SESSION_BUS_PATH 最高优先：只做 test -S，不跑自动探测。"""
    harness.runner.paths = {"/run/dbus/system_bus_socket"}
    dbus, _ = oc.resolve_passthrough(None, _NATIVE, {
        "DBUS_SESSION_BUS_PATH": "/run/dbus/system_bus_socket",
    })
    assert dbus == "/run/dbus/system_bus_socket"
    assert not any('"/run/user/$(id -u)/bus"' in c for c in harness.runner.commands)


def test_resolve_passthrough_explicit_invalid_path_guide(harness, capsys):
    """显式令牌指向非 socket：fail-fast 且报出用户指定的路径。"""
    harness.runner.paths = set()
    with pytest.raises(Exit):
        oc.resolve_passthrough(None, _NATIVE, {
            "DBUS_SESSION_BUS_PATH": "/run/user/1000/bus",
        })
    out = capsys.readouterr().out
    assert "/run/user/1000/bus 不是 socket" in out
    assert "XDG_RUNTIME_DIR" in out


def test_resolve_passthrough_probe_miss_fails_fast(harness, capsys):
    """三候选均无 socket（如无 user 会话的最小化 WSL）：fail-fast + 探测顺序说明。"""
    harness.runner.paths = set()
    harness.runner.session_bus = ""
    with pytest.raises(Exit) as ei:
        oc.resolve_passthrough(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "未在 podman" in out
    assert "XDG_RUNTIME_DIR/bus" in out
    assert "/run/user/$(id -u)/bus" in out
    assert "DBUS_SESSION_BUS_PATH=/run/dbus/system_bus_socket" in out
    assert "去掉 --passthrough" in out


def test_runtime_probe_session_bus_returns_empty_on_failure(harness):
    harness.runner.paths = set()
    assert oc._runtime_probe_session_bus(None) == ""


def test_resolve_passthrough_busy_ports_fail_fast(harness, capsys):
    harness.runner.paths = {"/run/user/1000/bus"}
    harness.runner.ss_output = (
        "State  Recv-Q Send-Q Local Address  Peer Address\n"
        "LISTEN 0  0  0.0.0.0:8888  0.0.0.0:*\n"
        "LISTEN 0  0  0.0.0.0:2223  0.0.0.0:*\n"
    )
    with pytest.raises(Exit):
        oc.resolve_passthrough(None, _NATIVE, {})
    out = capsys.readouterr().out
    assert "8888" in out and "2223" in out
    assert "HOST_NET_SSHD_PORT" in out
    # ss 缺失/无输出时不阻断（同族「ss 缺失则跳过」）
    harness.runner.ss_output = ""
    assert oc._runtime_listening_ports(None, ["8888"]) == []


def test_own_host_container_running_helper(harness):
    """helper 判据：无 running 容器不发 inspect；仅「true host」双段为 True。"""
    # 无 running 容器 → False，且不发 inspect 查询
    assert oc._own_host_container_running(None, _NATIVE) is False
    assert not any("State.Running" in cmd for cmd in harness.runner.commands)
    harness.runner.running = True
    # 输出非「true host」精确双段 → False（fail-fast 语义不变）
    for bad in ("true bridge", "false host", "", "true host extra"):
        harness.runner.net_mode = bad
        assert oc._own_host_container_running(None, _NATIVE) is False, bad
    harness.runner.net_mode = "true host"
    assert oc._own_host_container_running(None, _NATIVE) is True
    inspect_cmds = [c for c in harness.runner.commands if "State.Running" in c]
    assert len(inspect_cmds) == 5
    assert inspect_cmds[-1] == (
        "podman inspect --format "
        "'{{.State.Running}} {{.HostConfig.NetworkMode}}' cid"
    )


def test_resolve_passthrough_own_host_busy_ports_pass_through(harness, capsys):
    """重复 up：8888/2223 由本栈 host 形态容器持有 → 提示后放行（幂等场景）。"""
    harness.runner.paths = {"/run/user/1000/bus"}
    harness.runner.running = True
    harness.runner.net_mode = "true host"
    harness.runner.ss_output = (
        "State  Recv-Q Send-Q Local Address  Peer Address\n"
        "LISTEN 0  0  0.0.0.0:8888  0.0.0.0:*\n"
        "LISTEN 0  0  0.0.0.0:2223  0.0.0.0:*\n"
    )
    dbus, sshd = oc.resolve_passthrough(None, _NATIVE, {})
    assert (dbus, sshd) == ("/run/user/1000/bus", "2223")
    out = capsys.readouterr().out
    assert "8888, 2223" in out
    assert "本栈正在运行的 host 形态容器" in out
    assert "不拦截" in out
    assert "podman-compose" in out
    assert "已被占用" not in out


def test_resolve_passthrough_own_bridge_container_still_fails_fast(harness, capsys):
    """bridge 形态容器在跑 ≠ 占用者：端口被其他进程占用时保持 fail-fast。"""
    harness.runner.paths = {"/run/user/1000/bus"}
    harness.runner.running = True
    harness.runner.net_mode = "true bridge"
    harness.runner.ss_output = (
        "State  Recv-Q Send-Q Local Address  Peer Address\n"
        "LISTEN 0  0  0.0.0.0:8888  0.0.0.0:*\n"
    )
    with pytest.raises(Exit):
        oc.resolve_passthrough(None, _NATIVE, {})
    assert "已被占用" in capsys.readouterr().out


def test_resolve_usb_happy_path_writes_env(harness):
    harness.runner.paths = {"/dev/bus/usb"}
    assert oc.resolve_usb_device(None, _NATIVE, {}) == "/dev/bus/usb"
    assert os.environ["USB_DEVICE"] == "/dev/bus/usb"


def test_resolve_usb_missing_fails_with_usbipd_guide(harness, capsys):
    harness.runner.paths = set()
    with pytest.raises(Exit) as ei:
        oc.resolve_usb_device(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "usbipd attach --wsl podman-machine-default" in out
    assert "USB_DEVICE=/dev/bus/usb/001/002" in out
    assert "去掉 --usb" in out


# ── C33：GUI（Wayland/X11）门禁 ──────────────────────────────────────────────


def test_resolve_gui_wslg_dual_forms_writes_env(harness):
    """WSLg 双通道共存：返回两形态并回写四份插值令牌。"""
    harness.runner.paths = {
        "/mnt/wslg/runtime-dir/wayland-0",
        "/mnt/wslg/.X11-unix/X0",
    }
    forms = oc.resolve_gui(None, _NATIVE, {})
    assert forms == ("wayland", "x11")
    assert os.environ["GUI_WAYLAND_SOCKET"] == "/mnt/wslg/runtime-dir/wayland-0"
    assert os.environ["HOST_WAYLAND_DISPLAY"] == "wayland-0"
    assert os.environ["GUI_X11_SOCKETDIR"] == "/mnt/wslg/.X11-unix"
    assert os.environ["GUI_DISPLAY"] == ":0"
    cmds = harness.runner.commands
    assert "test -S /mnt/wslg/runtime-dir/wayland-0" in cmds
    assert "test -S /mnt/wslg/.X11-unix/X0" in cmds
    # WSLg 命中即停：物理回退路径不应再被探测
    assert not any("/run/user/1000/wayland-0" in c for c in cmds)
    assert not any(c.endswith("test -S /tmp/.X11-unix/X0") for c in cmds)


def test_resolve_gui_wayland_only(harness):
    """纯 Wayland 宿主：只挂 Wayland 层，不产生 X11 令牌。"""
    harness.runner.paths = {"/run/user/1000/wayland-0"}
    assert oc.resolve_gui(None, _NATIVE, {}) == ("wayland",)
    assert os.environ["GUI_WAYLAND_SOCKET"] == "/run/user/1000/wayland-0"
    assert "GUI_X11_SOCKETDIR" not in os.environ


def test_resolve_gui_x11_only(harness):
    """纯 X11 宿主（/tmp/.X11-unix 回退候选命中）：只挂 X11 层。"""
    harness.runner.paths = {"/tmp/.X11-unix/X0"}
    assert oc.resolve_gui(None, _NATIVE, {}) == ("x11",)
    assert os.environ["GUI_X11_SOCKETDIR"] == "/tmp/.X11-unix"
    assert "GUI_WAYLAND_SOCKET" not in os.environ


def test_resolve_gui_env_tokens_take_precedence(harness):
    """shell/.env 显式令牌优先于默认候选（物理 Linux 改指）。"""
    harness.runner.paths = {
        "/custom/xdg/wayland-9",
        "/custom/x11/X0",
        "/mnt/wslg/runtime-dir/wayland-0",
        "/mnt/wslg/.X11-unix/X0",
    }
    forms = oc.resolve_gui(None, _NATIVE, {
        "HOST_XDG_RUNTIME_DIR": "/custom/xdg",
        "HOST_WAYLAND_DISPLAY": "wayland-9",
        "GUI_X11_SOCKETDIR": "/custom/x11",
    })
    assert forms == ("wayland", "x11")
    assert os.environ["GUI_WAYLAND_SOCKET"] == "/custom/xdg/wayland-9"
    assert os.environ["HOST_WAYLAND_DISPLAY"] == "wayland-9"
    assert os.environ["GUI_X11_SOCKETDIR"] == "/custom/x11"


def test_resolve_gui_missing_both_fails_fast(harness, capsys):
    """两通道都缺：Exit(1) + 三分支中文指引，且不回写任何令牌。"""
    harness.runner.paths = set()
    with pytest.raises(Exit) as ei:
        oc.resolve_gui(None, _NATIVE, {})
    assert ei.value.code == 1
    out = capsys.readouterr().out
    assert "WSLg" in out and "HOST_XDG_RUNTIME_DIR" in out and "xhost" in out
    assert "去掉 --gui" in out
    assert "GUI_WAYLAND_SOCKET" not in os.environ
    assert "GUI_X11_SOCKETDIR" not in os.environ


def test_up_gui_argv_banner_bridge_form(harness, capsys):
    """--gui（bridge）：文件集含两 GUI 层；端口仍是 8890/2223；横幅 GUI 行。"""
    harness.runner.paths = {
        "/mnt/wslg/runtime-dir/wayland-0",
        "/mnt/wslg/.X11-unix/X0",
    }
    oc.up_stack(None, _NATIVE, gui=True, skip_build=True)
    up_cmd = [c for c in harness.runner.commands if "up -d --no-build" in c][0]
    assert "compose.passthrough.gui.yaml" in up_cmd
    assert "compose.passthrough.gui.x11.yaml" in up_cmd
    assert "compose.passthrough.yaml" not in up_cmd
    out = capsys.readouterr().out
    assert "Jupyter localhost:8890" in out
    assert "Wayland /mnt/wslg/runtime-dir/wayland-0" in out
    assert "X11 /mnt/wslg/.X11-unix" in out


def test_up_gui_gate_fails_before_any_down_or_up(harness, capsys):
    """GUI 门禁失败时绝不拆栈：无 down、无 up（build 可先跑）。"""
    harness.runner.paths = set()
    with pytest.raises(Exit):
        oc.up_stack(None, _NATIVE, gui=True, skip_build=True)
    cmds = harness.runner.commands
    assert not any(" down" in c for c in cmds)
    assert not any("up -d" in c for c in cmds)


def test_smoke_running_native_gui_uses_same_files(harness):
    """栈运行路径的 exec argv 必须与 up 同源（含两层 GUI 覆盖）。"""
    harness.runner.running = True
    harness.runner.paths = {
        "/mnt/wslg/runtime-dir/wayland-0",
        "/mnt/wslg/.X11-unix/X0",
    }
    oc.smoke_stack(None, _NATIVE, gui=True)
    exec_cmd = [c for c in harness.runner.commands if " exec " in c][0]
    assert "compose.passthrough.gui.yaml" in exec_cmd
    assert "compose.passthrough.gui.x11.yaml" in exec_cmd


def test_ensure_passthrough_tag_already_present(harness):
    tags = {"localhost/native-dev:passthrough"}
    harness.runner.image_exists_tags = tags
    tag = oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=True)
    assert tag == "localhost/native-dev:passthrough"
    assert not any(c.startswith("podman tag") for c in harness.runner.commands)


def test_ensure_passthrough_tag_copied_from_base(harness, capsys):
    harness.runner.image_exists_tags = {"localhost/native-dev:latest"}
    tag = oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=False)
    assert tag == "localhost/native-dev:passthrough"
    assert "podman tag localhost/native-dev:latest localhost/native-dev:passthrough" in (
        harness.runner.commands
    )
    assert "打 tag" in capsys.readouterr().out


def test_ensure_passthrough_tag_stale_retagged_from_base(harness, capsys):
    """两 tag 均在但镜像 ID 不一致（重建后透传 tag 陈旧）：重新打 tag 收敛。"""
    tags = {"localhost/native-dev:latest", "localhost/native-dev:passthrough"}
    harness.runner.image_exists_tags = tags
    harness.runner.image_ids = {
        "localhost/native-dev:latest": "sha256:new",
        "localhost/native-dev:passthrough": "sha256:old",
    }
    tag = oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=True)
    assert tag == "localhost/native-dev:passthrough"
    assert "podman tag localhost/native-dev:latest localhost/native-dev:passthrough" in (
        harness.runner.commands
    )
    out = capsys.readouterr().out
    assert "已过期" in out


def test_ensure_passthrough_tag_in_sync_no_action(harness):
    """两 tag 镜像 ID 一致：零操作（幂等）。"""
    tags = {"localhost/native-dev:latest", "localhost/native-dev:passthrough"}
    harness.runner.image_exists_tags = tags
    harness.runner.image_ids = {
        "localhost/native-dev:latest": "sha256:same",
        "localhost/native-dev:passthrough": "sha256:same",
    }
    tag = oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=True)
    assert tag == "localhost/native-dev:passthrough"
    assert not any(c.startswith("podman tag") for c in harness.runner.commands)


def test_ensure_passthrough_tag_id_unreadable_keeps_existing(harness, capsys):
    """ID 读取失败：警告 + 沿用现有透传 tag，不阻断（保守降级）。"""
    tags = {"localhost/native-dev:latest", "localhost/native-dev:passthrough"}
    harness.runner.image_exists_tags = tags
    tag = oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=True)
    assert tag == "localhost/native-dev:passthrough"
    assert not any(c.startswith("podman tag") for c in harness.runner.commands)
    assert "无法读取透传/基础镜像 ID" in capsys.readouterr().out


def test_ensure_passthrough_tag_both_absent_offline_guidance(harness, capsys):
    harness.runner.image_exists_tags = set()
    with pytest.raises(Exit):
        oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=True)
    out = capsys.readouterr().out
    assert "invoke native.save" in out and "invoke native.load" in out
    assert not any(c.startswith("podman tag") for c in harness.runner.commands)


def test_ensure_passthrough_tag_both_absent_build_guidance(harness, capsys):
    harness.runner.image_exists_tags = set()
    with pytest.raises(Exit):
        oc.ensure_passthrough_tag(None, _NATIVE, {}, offline=False)
    assert "invoke native.up --passthrough" in capsys.readouterr().out


def test_up_passthrough_argv_banner_and_ready_port(harness, monkeypatch, capsys):
    """--passthrough：文件集含主层；就绪探测 8888；横幅 host 端口与透传行。"""
    seen = []

    def fake_wait(port, **kw):
        seen.append(port)
        return True, "ok"

    monkeypatch.setattr(oc, "wait_http_ready", fake_wait)
    oc.up_stack(None, _NATIVE, passthrough=True)
    assert seen == [8888]
    up_cmd = [c for c in harness.runner.commands if "up -d --no-build" in c][0]
    assert "compose.passthrough.yaml" in up_cmd
    assert "compose.passthrough.usb.yaml" not in up_cmd
    out = capsys.readouterr().out
    assert "ssh -p 2223 devuser@localhost" in out
    assert "Jupyter localhost:8888" in out
    assert "透传    host 网络 + D-Bus" in out


def test_up_usb_argv_and_banner(harness, capsys):
    oc.up_stack(None, _NATIVE, usb=True)
    up_cmd = [c for c in harness.runner.commands if "up -d --no-build" in c][0]
    assert "compose.passthrough.usb.yaml" in up_cmd
    assert "compose.passthrough.yaml" not in up_cmd
    out = capsys.readouterr().out
    assert "USB     /dev/bus/usb 已透传" in out
    # bridge 形态不变（仍是 8890/2223 映射）
    assert "Jupyter localhost:8890" in out


def test_up_passthrough_gate_fails_before_any_down_or_up(harness, capsys):
    """门禁失败时绝不拆栈：无 down、无 up（build 可先跑）。"""
    harness.runner.paths = set()  # D-Bus 缺失
    with pytest.raises(Exit):
        oc.up_stack(None, _NATIVE, passthrough=True)
    cmds = harness.runner.commands
    assert not any(" down" in c for c in cmds)
    assert not any("up -d" in c for c in cmds)


def test_smoke_running_native_passthrough_uses_same_files(harness):
    """栈运行路径的 exec argv 必须与 up 同源（含透传主层）。"""
    harness.runner.running = True
    harness.runner.paths = {"/run/user/1000/bus", "/dev/bus/usb"}
    # host 形态栈自身占用 8888/2223——冒烟不得判为端口冲突（W-I19 回归）
    harness.runner.ss_output = (
        "LISTEN 0 128 0.0.0.0:8888 0.0.0.0:*\n"
        "LISTEN 0 128 0.0.0.0:2223 0.0.0.0:*\n"
    )
    oc.smoke_stack(None, _NATIVE, passthrough=True, usb=True)
    exec_cmd = [c for c in harness.runner.commands if " exec " in c][0]
    assert "compose.passthrough.yaml" in exec_cmd
    assert "compose.passthrough.usb.yaml" in exec_cmd


def test_resolve_passthrough_check_ports_false_skips_busy_gate(harness, capsys):
    """冒烟调用形态：端口被占也通过；D-Bus 检查与 env 回写仍执行。"""
    harness.runner.paths = {"/run/user/1000/bus"}
    harness.runner.ss_output = "LISTEN 0 128 0.0.0.0:8888 0.0.0.0:*\n"
    dbus, sshd = oc.resolve_passthrough(
        None, _NATIVE, {}, check_ports=False
    )
    assert (dbus, sshd) == ("/run/user/1000/bus", "2223")
    assert os.environ["HOST_NET_SSHD_PORT"] == "2223"


def test_smoke_standalone_native_notes_flags_ignored(harness, capsys):
    harness.runner.running = False
    harness.runner.paths = {"/dev/bus/usb"}
    oc.smoke_stack(None, _NATIVE, usb=True)
    out = capsys.readouterr().out
    assert "--passthrough/--gui/--usb 仅在栈运行路径生效" in out


# ---------------------------------------------------------------------------
# C34：B-scheme 宿主 podman socket 预检与令牌注入（三栈 up 门禁第一位）
#
# 背景：三叠加栈 compose 此前从未挂载宿主 socket，entrypoint 静默回退 DinP
# （嵌套 rootless 必被 newuidmap 拒），Notebook 运行时才 FileNotFoundError。
# resolve_host_podman_socket 是三栈共用的唯一预检点，必须先于一切子进程。
# ---------------------------------------------------------------------------

_DEFAULT_SOCK = "/run/user/1000/podman/podman.sock"


@pytest.mark.parametrize("spec", ALL_SPECS)
def test_resolve_host_podman_socket_injects_token(harness, spec):
    """就绪时：推导令牌同时回写 env dict 与 os.environ（compose 三处插值）。"""
    env = {}
    token = oc.resolve_host_podman_socket(None, spec, env)
    assert token == _DEFAULT_SOCK
    assert env["HOST_PODMAN_SOCK"] == _DEFAULT_SOCK
    assert os.environ["HOST_PODMAN_SOCK"] == _DEFAULT_SOCK


def test_resolve_shell_export_token_has_top_priority(harness, monkeypatch):
    """shell export > .env（env dict）> podman_sock_path() 推导值。"""
    monkeypatch.setenv("HOST_PODMAN_SOCK", "/run/user/1006/podman/podman.sock")
    env = {"HOST_PODMAN_SOCK": "/run/user/9999/podman/podman.sock"}
    token = oc.resolve_host_podman_socket(None, _NATIVE, env)
    assert token == "/run/user/1006/podman/podman.sock"
    assert env["HOST_PODMAN_SOCK"] == "/run/user/1006/podman/podman.sock"
    assert os.environ["HOST_PODMAN_SOCK"] == "/run/user/1006/podman/podman.sock"


def test_resolve_dotenv_token_beats_derived_default(harness, monkeypatch):
    """shell 未 export 时 .env 令牌（env dict）压过推导缺省（物理机 UID 覆盖）。"""
    monkeypatch.delenv("HOST_PODMAN_SOCK", raising=False)
    env = {"HOST_PODMAN_SOCK": "/run/user/1005/podman/podman.sock"}
    token = oc.resolve_host_podman_socket(None, _NATIVE, env)
    assert token == "/run/user/1005/podman/podman.sock"
    assert os.environ["HOST_PODMAN_SOCK"] == "/run/user/1005/podman/podman.sock"


def test_resolve_blank_token_falls_through_to_next_candidate(harness, monkeypatch):
    """纯空白令牌（truthy 串）不得中选：shell 空白 → .env 候选 → 推导缺省。"""
    monkeypatch.setenv("HOST_PODMAN_SOCK", "   ")
    env = {"HOST_PODMAN_SOCK": "  "}
    token = oc.resolve_host_podman_socket(None, _NATIVE, env)
    assert token == _DEFAULT_SOCK
    assert os.environ["HOST_PODMAN_SOCK"] == _DEFAULT_SOCK
    assert env["HOST_PODMAN_SOCK"] == _DEFAULT_SOCK

    # shell 空白、.env 有效 → 取 .env 候选（逐级 strip 判空）
    monkeypatch.setenv("HOST_PODMAN_SOCK", "   ")
    env = {"HOST_PODMAN_SOCK": " /run/user/1005/podman/podman.sock "}
    token = oc.resolve_host_podman_socket(None, _NATIVE, env)
    assert token == "/run/user/1005/podman/podman.sock"


def test_resolve_missing_socket_exits_with_ci5_guidance(harness, monkeypatch, capsys):
    """socket 未就绪 → Exit(1) + C-I5 三步指引 + 自愈失败明细。"""
    monkeypatch.setattr(
        oc,
        "ensure_host_podman_socket",
        lambda: (False, "unit start timed out", False),
    )
    with pytest.raises(Exit):
        oc.resolve_host_podman_socket(None, _NATIVE, {})
    out = capsys.readouterr().out
    assert "[C-I5]" in out
    assert "systemctl --user start podman.socket" in out
    assert "enable-linger" in out
    assert "unit start timed out" in out


@pytest.mark.parametrize("spec", ALL_SPECS)
def test_up_fails_fast_before_any_subprocess_when_socket_missing(
    harness, monkeypatch, spec
):
    """门禁先于 build/镜像预检/compose：失败时 runner 零子进程、无 down/up。"""
    monkeypatch.setattr(
        oc, "ensure_host_podman_socket",
        lambda: (False, "no socket", False),
    )
    with pytest.raises(Exit):
        oc.up_stack(None, spec, skip_build=True)
    assert harness.runner.calls == []


def test_resolve_announces_socket_self_heal(harness, monkeypatch, capsys):
    """本次自动拉起 socket（started=True）时打印自愈提示；False 时静默。"""
    monkeypatch.setattr(
        oc, "ensure_host_podman_socket", lambda: (True, "", True)
    )
    oc.resolve_host_podman_socket(None, _NATIVE, {})
    out = capsys.readouterr().out
    assert "[B-scheme] 已自动启动宿主 rootless podman socket 服务" in out


def test_resolve_silent_when_socket_already_ready(harness, capsys):
    oc.resolve_host_podman_socket(None, _NATIVE, {})
    assert "[B-scheme] 已自动启动" not in capsys.readouterr().out


@pytest.mark.parametrize("spec", ALL_SPECS)
def test_up_passes_socket_token_to_compose_subprocess(
    harness, monkeypatch, spec
):
    """成功路径：compose up 子进程继承的 os.environ 必须带解析后令牌。

    run_compose_up 不显式传 env（compose 插值读进程环境），故在调用时刻
    快照 os.environ 锁定，而不是检查 run_cmd 的 env kwarg。
    """
    inner = harness.runner
    seen_env: dict[str, str] = {}

    def _record(c, cmd, **kw):
        if " up -d" in cmd:
            seen_env.update(os.environ)
        return inner(c, cmd, **kw)

    monkeypatch.setattr(oc, "run_cmd", _record)
    oc.up_stack(None, spec, skip_build=True)
    assert seen_env, "未观察到 compose up -d 调用"
    assert seen_env["HOST_PODMAN_SOCK"] == _DEFAULT_SOCK
