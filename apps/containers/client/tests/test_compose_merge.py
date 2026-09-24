"""compose extends 公共段抽取的离线等价验证（T5 / AC-3）。

真机 podman-machine-default 已灭失，无法跑 ``podman-compose config`` 做渲染
diff；本测试按 OKF podman-compose 知识包 concepts/06-config-pipeline.md
（L83-103）记载、并经本机与 vendor 双份 podman-compose 1.6.0 源码
（vendor/podman-compose/podman_compose.py）resolve_extends/rec_merge
实证的合并语义，实现最小合并模拟器，直接渲染仓库内真实 YAML：

- extends：``rec_merge({}, 基服务, 当前服务)``，dict 深合并 / 普通 list 追加 /
  command、entrypoint 无条件整体替换；
- volumes 特殊去重（vendor L2289-L2297，逐字核实）：**仅短语法字符串**参与，
  取覆盖方 target 集合删除基方碰撞项后整体 extend——**覆盖方获胜且移至尾部**；
  **长语法 dict 项永不参与去重**（``":" in dict`` 是键判断），同 target 会重复；
- 多文件 -f 顺序：文件循环先 rec_merge（compose ◁ override），循环后才
  resolve_extends（base ◁ merged），优先级 base < compose < override。

模拟器保真边界（只模拟三栈真实用到的 YAML 子集，勿外推）：
- 支持 ``!reset`` 标签（native 透传主层使用：整键删除，对齐 vendor ResetTag
  L2253-2255）；不支持 ``!override``；
- 不模拟 normalize_service 预处理（build.args dict→list、env/labels list→dict、
  security_opt str→list）；三栈 env/labels 均为 dict 形态故渲染无差异；
- 插值仅支持 ``${NAME}``/``${NAME:-default}``（default 段不含花括号则支持**嵌套**
  ——逐轮替换最内层至不动点，与 1.6.0 实测行为一致，见 ``_expand``），
  不支持 ``:?``/``$$``/服务互引；
- 类型冲突（dict↔list 等）真实 rec_merge_one 抛 ValueError，模拟器同样抛出；
  **唯一例外是 depends_on**：上游在 rec_merge_one 内做 list↔dict 归一化
  （vendor pin 含上游 96a2043），故 list+dict 不抛冲突，见 ``merge_one`` 注释；
- 对照基准为 **vendor 子模块 pin**（仓库 gitlink 权威源；vendor/AGENTS.md：
  third_party 只读依赖以 pin commit 为准），本机安装态仅作 fallback——
  2026-09-21 实测两份「1.6.0」**并非同一快照**，详见 ``_real_podman_compose``。

AC-3 正向条款：rootless 三必需不重不漏、env 键并集一致、labels 一致、
privileged 缺失、栈专属字段（image/build/ports/volumes）原样保留。
"""

import copy
import re
import sys
from pathlib import Path

import pytest
import yaml

OVERLAYS = Path(__file__).resolve().parents[1] / "overlays"
SHARED = OVERLAYS / "_shared" / "base-rootless.yaml"
# vendor 只读子模块中的权威源码：pin = v1.6.0-97-ge3df104（发布后的 main；
# __version__ 仍写 1.6.0，与 pip 装的本机发布版并非同一快照，差异见
# _real_podman_compose 的 docstring）
_VENDOR_PC = Path(__file__).resolve().parents[4] / "vendor" / "podman-compose"

_INTERP = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^{}]*))?\}")

# 三栈黄金期望（抽取前逐栈 compose.yaml 的等价清单）
GOLDEN = {
    "quant": {
        "dir": "onnx-quantized", "service": "quant",
        "component": "onnx-quantized",
        "image": "localhost/onnx-quantized:latest",
        "container_name": "onnx-quantized",
        "dockerfile": "Containerfile.quantized",
        "ports": ["2222:22", "8888:8888"],
        "volume_targets": ["/workspace", "/var/lib/jpman/ssh-host-keys"],
        "env": {
            "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
        },
    },
    "native": {
        "dir": "native-dev", "service": "native",
        "component": "native-dev",
        "image": "localhost/native-dev:latest",
        "container_name": "native-dev",
        "dockerfile": "Containerfile.native-dev",
        "ports": ["2223:22", "8890:8888"],
        "volume_targets": [
            "/workspace", "/workspace/npu_tvm", "/workspace/npuusertools",
            "/workspace/models", "/workspace/temp", "/root/.ccache",
            "/home/devuser/.local/share/jupyter",
            "/var/lib/jpman/ssh-host-keys",
        ],
        "env": {
            "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
            "PYTHONPATH", "TVM_LIBRARY_PATH", "LD_LIBRARY_PATH",
            "NPU_TOOLS_ROOT", "XMNN_TOOLS_ROOT", "OMP_NUM_THREADS", "NUITKA_JOBS",
        },
    },
    "monetize": {
        "dir": "agent-monetize-dev", "service": "monetize",
        "component": "monetize",
        "image": "localhost/agent-monetize-dev:latest",
        "container_name": "agent-monetize-dev",
        "dockerfile": "Containerfile.agent-monetize",
        "ports": ["2224:22", "8892:8888"],
        "volume_targets": [
            "/workspace", "/workspace/agent-monetize",
            "/var/lib/jpman/ssh-host-keys",
        ],
        "env": {
            "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
            "PYTHONPATH", "LD_LIBRARY_PATH",
        },
    },
}

# ── 最小合并模拟器（语义对齐 podman-compose 1.6.0 rec_merge_one）──────────────

_REPLACE_KEYS = {"command", "entrypoint"}
_MISSING = object()


class _ResetMarker:
    """``!reset`` 标签标记（对应 vendor ResetTag：单例语义）。"""


_RESET = _ResetMarker()


def _construct_reset(loader, node):  # noqa: ARG001
    return _RESET


# 与 vendor ResetTag.from_yaml 同效：忽略节点内容（!reset [] 亦为裸标记）
yaml.SafeLoader.add_constructor("!reset", _construct_reset)


def _pick(match, env):
    """取插值结果：环境值优先（空串视为未设），否则 default 原文。"""
    name, default = match.group(1), match.group(2)
    if name in env and env[name] != "":
        return env[name]
    return default if default is not None else ""


def _expand(text, env, *, max_rounds=8):
    """逐轮替换**最内层**表达式至不动点——嵌套插值的等价实现（C28）。

    podman-compose 1.6.0 实测支持嵌套：``${A:-x:${B:-y}}`` 四态（无变量 /
    ``B`` 有值 / 显式覆盖 / 空串回落）全部正确。模拟器若沿用单轮 ``[^}]*``
    正则会在**首个 ``}`` 截断**（把内层当外层 default 的一部分），渲染出
    错误串而假失败。
    max_rounds 仅是防呆上界：真实嵌套深度 ≤2，正常情况下第 2 轮即不动点。
    """
    for _ in range(max_rounds):
        expanded = _INTERP.sub(lambda m: _pick(m, env), text)
        if expanded == text:
            break
        text = expanded
    return text


def _interpolate(node, env):
    if isinstance(node, dict):
        return {k: _interpolate(v, env) for k, v in node.items()}
    if isinstance(node, list):
        return [_interpolate(v, env) for v in node]
    if isinstance(node, str):
        return _expand(node, env)
    return node


def _volume_target(item):
    if isinstance(item, dict):
        return item.get("target")
    if isinstance(item, str):
        parts = item.split(":")
        return parts[1] if len(parts) > 1 else None
    return None


def merge_one(a, b, key=None):
    """对齐 podman-compose 1.6.0 ``rec_merge_one``（vendor L2225-L2308）。

    - command/entrypoint：不看类型，覆盖方整体替换（L2263-L2265）；
    - None + dict：按空 dict 合并（L2272-L2273）；
    - 其余类型不一致：ValueError（L2283-L2286）；
    - volumes：仅短语法字符串按 target 去重，覆盖方获胜并移至尾部，
      长语法 dict 不去重（L2289-L2297）；
    - 普通 list 追加；dict 递归；标量后值覆盖。
    !reset 在 dict 分支按整键删除处理；不含 !override 语义。
    """
    if a is _MISSING:
        return copy.deepcopy(b)
    # command/entrypoint 在真实实现中先于类型检查无条件替换
    if key in _REPLACE_KEYS:
        return copy.deepcopy(b)
    if a is None and isinstance(b, dict):
        a = {}
    # depends_on 在真实实现中先做 list↔dict 归一化再合并（L2276-L2281）：
    # list 形态等价于 {项: {}}，故 list+dict 不抛类型冲突
    if key == "depends_on":
        if isinstance(a, list) and isinstance(b, dict):
            a = {x: {} for x in a}
        elif isinstance(a, dict) and isinstance(b, list):
            b = {x: {} for x in b}
    if isinstance(a, dict) and isinstance(b, dict):
        out = copy.deepcopy(a)
        for k, v in b.items():
            existing = out.get(k, _MISSING)
            # ResetTag 语义（vendor L2253-2255）：任一侧 !reset → 整键删除
            if v is _RESET or existing is _RESET:
                out.pop(k, None)
            elif existing is _MISSING:
                out[k] = copy.deepcopy(v)
            else:
                out[k] = merge_one(existing, v, k)
        # 仅 target 残留的 reset（source 无此键）同样删除（vendor L2241-2243）
        for k in [k for k, v in out.items() if v is _RESET]:
            del out[k]
        return out
    if isinstance(a, list) and isinstance(b, list):
        if key == "volumes":
            # pts 只取覆盖方（b）中「含冒号的字符串」的 target；
            # 基方（a）中同 target 的短语法条目被删，dict 项与匿名卷保留；
            # 随后覆盖方整体 extend（dict 项原样追加，故长语法同 target 会重复）
            pts = {
                v.split(":", 2)[1] for v in b
                if isinstance(v, str) and ":" in v
            }
            out = [
                copy.deepcopy(v) for v in a
                if not (isinstance(v, str) and ":" in v
                        and v.split(":", 2)[1] in pts)
            ]
            out.extend(copy.deepcopy(b))
            return out
        return [*copy.deepcopy(a), *copy.deepcopy(b)]
    if not isinstance(b, type(a)):
        raise ValueError(
            f"can't merge value of [{key}] of type {type(a)} and {type(b)}"
        )
    return copy.deepcopy(b)


def merge(*dicts):
    out = {}
    for d in dicts:
        out = merge_one(out, d)
    return out


def _load(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def render_stack(
    stack: str, env=None, *, gpu=False, gpu_file="compose.gpu.yaml",
    passthrough=False, gui_forms=(), usb=False,
):
    """模拟 resolve_extends + 多文件 rec_merge 后的服务 dict。

    ``gpu_file`` 对应 GPU 设备形态（C19）：内核按设备形态选 ``compose.gpu.<形态>.yaml``
    （缺失回退 compose.gpu.yaml），真实管线**只加载一个**设备覆盖文件。
    ``passthrough``/``gui_forms``/``usb`` 按内核文件顺序（base → GPU → 透传主层
    → GUI（Wayland → X11）→ USB 层）逐文件 rec_merge。
    """
    g = GOLDEN[stack]
    odir = OVERLAYS / g["dir"]
    doc = _interpolate(_load(odir / "compose.yaml"), env or {})
    svc = doc["services"][g["service"]]
    # extends.file 由 1.6.0 解析阶段按引用文件目录重写（vendor L2844-L2849）：
    # 以栈目录为基准解析并锁定指向 _shared 基文件
    base_rel = svc["extends"]["file"]
    base_path = (odir / base_rel).resolve()
    assert base_path == SHARED.resolve() and base_path.exists()
    base_doc = _interpolate(_load(base_path), env or {})
    base_svc = base_doc["services"][svc["extends"]["service"]]
    # 覆盖文件按真实下发顺序逐个 rec_merge（compose ◁ ov1 ◁ ov2 …）
    overlay_files = []
    if gpu:
        overlay_files.append(gpu_file)
    if passthrough:
        overlay_files.append("compose.passthrough.yaml")
    if "wayland" in gui_forms:
        overlay_files.append("compose.passthrough.gui.yaml")
    if "x11" in gui_forms:
        overlay_files.append("compose.passthrough.gui.x11.yaml")
    if usb:
        overlay_files.append("compose.passthrough.usb.yaml")
    stacked = svc
    for name in overlay_files:
        # 真实管线：文件循环先逐文件 rec_merge（L2851），
        # 循环后才 resolve_extends（rec_merge({}, base, merged)，L2919）
        ov = _interpolate(_load(odir / name), env or {})
        stacked = merge(stacked, ov["services"][g["service"]])
    merged = merge({}, base_svc, stacked)
    return merged


# ── 基文件自查 ───────────────────────────────────────────────────────────────


def test_base_file_contains_only_pathless_fields():
    base = _load(SHARED)
    assert set(base["services"]) == {"rootless-base"}
    svc = base["services"]["rootless-base"]
    # 严禁任何路径/构建字段（F-3 单一事实源边界）
    assert not ({ "volumes", "build", "env_file", "ports", "image",
                  "container_name", "hostname" } & set(svc))
    assert svc["devices"] == ["/dev/fuse:/dev/fuse"]
    assert svc["security_opt"] == ["label=disable"]
    assert svc["cgroupns"] == "host"
    assert svc["network_mode"] == "bridge"
    assert set(svc["environment"]) == {
        "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }
    assert "privileged" not in svc and "cap_add" not in svc


def test_base_declares_podman_readable_log_driver():
    """C24 前置条件：日志驱动必须是 podman 可读的 k8s-file。

    2026-09-20 实证：本机发行版默认驱动为 journald
    （/usr/share/containers/containers.conf），在 WSL 嵌套 systemd 命名空间下
    ``podman logs`` 返回 0 字节（日志进了宿主 journal，只有 journalctl 能读），
    会同时打挂 up 凭证回读与 ``invoke <ns>.logs``。故基段显式声明 k8s-file，
    三栈同构继承——本断言锁死该声明，防止有人「顺手删掉」而静默回退。
    """
    base = _load(SHARED)
    assert base["services"]["rootless-base"]["logging"] == {"driver": "k8s-file"}
    for stack in GOLDEN:
        assert render_stack(stack)["logging"] == {"driver": "k8s-file"}


# ── AC-3 三栈渲染等价 ────────────────────────────────────────────────────────


@pytest.mark.parametrize("stack", list(GOLDEN))
def test_rendered_rootless_essentials_once_and_no_privileged(stack):
    svc = render_stack(stack)
    assert svc["devices"] == ["/dev/fuse:/dev/fuse"]
    assert svc["security_opt"] == ["label=disable"]
    assert svc["cgroupns"] == "host"
    assert svc["network_mode"] == "bridge"
    assert "privileged" not in svc
    assert "cap_add" not in svc


@pytest.mark.parametrize("stack", list(GOLDEN))
def test_rendered_env_keys_equal_golden(stack):
    svc = render_stack(stack)
    assert set(svc["environment"]) == GOLDEN[stack]["env"]
    # 凭证插值空值语义保持（留空串；GRANT_SUDO 默认 yes）
    env = svc["environment"]
    assert env["USER_PASSWORD"] == ""
    assert env["JUPYTER_TOKEN"] == ""
    assert env["SSH_PUBLIC_KEY"] == ""
    assert env["GRANT_SUDO"] == "yes"


@pytest.mark.parametrize("stack", list(GOLDEN))
def test_rendered_labels_merge_and_restart(stack):
    svc = render_stack(stack)
    assert svc["labels"] == {
        "org.specweave.managed-by": "jupyter-podman-client",
        "org.specweave.component": GOLDEN[stack]["component"],
    }
    assert svc["restart"] == "unless-stopped"


@pytest.mark.parametrize("stack", list(GOLDEN))
def test_rendered_stack_specific_fields_preserved(stack):
    g = GOLDEN[stack]
    svc = render_stack(stack)
    assert svc["image"] == g["image"]
    assert svc["container_name"] == g["container_name"]
    assert svc["build"]["dockerfile"] == g["dockerfile"]
    assert svc["ports"] == g["ports"]
    assert [_volume_target(v) for v in svc["volumes"]] == g["volume_targets"]
    # 全部 bind 保长语法 + create_host_path（G1）
    for v in svc["volumes"]:
        if isinstance(v, dict) and v["type"] == "bind":
            assert v["bind"]["create_host_path"] is True


def test_quant_gpu_override_appends_dri_without_duplicating_fuse():
    plain = render_stack("quant")
    gpu = render_stack("quant", gpu=True)
    assert plain["devices"] == ["/dev/fuse:/dev/fuse"]
    # 多文件 list 追加：fuse 来自 base，dri 来自 override，顺序锁定
    # 单 token 形态（C19 与 native 同构）：裸设备路径，缺省 /dev/dri
    assert gpu["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dri"]
    # 其余字段不被 override 影响
    assert gpu["environment"] == plain["environment"]
    assert gpu["ports"] == plain["ports"]


def test_quant_gpu_device_double_form_interpolation():
    """quant 与 native 同键同语义：`/` 开头=device 路径，否则=CDI 引用（C19）。"""
    assert render_stack("quant", env={"GPU_DEVICE": "nvidia.com/gpu=all"}, gpu=True)[
        "devices"
    ] == ["/dev/fuse:/dev/fuse", "nvidia.com/gpu=all"]
    assert render_stack("quant", env={"GPU_DEVICE": "/dev/nvidia0"}, gpu=True)[
        "devices"
    ] == ["/dev/fuse:/dev/fuse", "/dev/nvidia0"]


@pytest.mark.parametrize("stack", ["native", "quant"])
def test_wsl_gpu_override_passes_dxg_and_mounts_wsl_libs(stack):
    """WSL2 形态（C19）：/dev/dxg + 三条只读 bind，且**不动**栈自带环境。

    三条 bind（libcuda.so.1 单文件 + libdxcore.so 单文件 + /usr/lib/wsl/drivers
    目录）同为最小充分条件（2026-09-20 两轮实测）：只挂 libcuda 时容器内
    ``CDLL("libcuda.so.1")`` 成功，但 ``cuInit()`` 返 100(CUDA_ERROR_NO_DEVICE)
    ——**「库能加载」≠「设备可见」**，故断言锁定 target 全集而非单条。

    关键约束：environment 为 mapping 替换语义——若在此文件里写
    ``LD_LIBRARY_PATH=/usr/lib/wsl/lib`` 会整体冲掉 compose.yaml 已声明的 TVM
    库路径。故本形态靠把库挂进基底默认搜索目录 /usr/lib 来实现，
    环境变量**零改动**（2026-09-20 实测结论）。
    """
    plain = render_stack(stack)
    wsl = render_stack(stack, gpu=True, gpu_file="compose.gpu.wsl.yaml")
    assert wsl["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dxg"]
    assert wsl["environment"] == plain["environment"]
    # 长语法 dict bind 不参与 rec_merge 去重（同 target 会重复），故按 target 建映射
    binds = {
        v["target"]: v
        for v in wsl["volumes"]
        if isinstance(v, dict) and str(v.get("target", "")).startswith("/usr/lib/")
    }
    assert {t: v["source"] for t, v in binds.items()} == {
        "/usr/lib/libcuda.so.1": "/usr/lib/wsl/lib/libcuda.so.1",
        "/usr/lib/libdxcore.so": "/usr/lib/wsl/lib/libdxcore.so",
        "/usr/lib/wsl/drivers": "/usr/lib/wsl/drivers",
    }
    for mount in binds.values():
        assert mount["read_only"] is True
        assert mount["bind"]["create_host_path"] is False  # 缺失即报错，不误建空文件


def test_native_gpu_override_is_opt_in_and_single_device():
    """native 的 GPU opt-in（C18）与 quant 同构，但设备项是单条插值（双形态）。"""
    plain = render_stack("native")
    assert plain["devices"] == ["/dev/fuse:/dev/fuse"]
    gpu = render_stack("native", gpu=True)
    # 单 token 形态：裸设备路径（`--device /dev/dri` 等价于 :/dev/dri 显式映射），
    # 不可写成 /dev/dri:/dev/dri —— CDI 引用形态会因此变成非法串
    assert gpu["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dri"]
    assert gpu["environment"] == plain["environment"]
    assert gpu["ports"] == plain["ports"]


def test_native_gpu_device_double_form_interpolation():
    """GPU_DEVICE 双形态：`/` 开头=宿主机设备路径；否则=CDI 引用（与 invoke run --gpu 同语义）。

    关键：override 内**只有一条** devices 项——podman-compose 1.6.0 把列表项原样
    下传为 `--device <item>`（vendor L1382-L1383，不做冒号拆分），两条并列必有一条非法。
    """
    cdi = render_stack("native", env={"GPU_DEVICE": "nvidia.com/gpu=all"}, gpu=True)
    assert cdi["devices"] == ["/dev/fuse:/dev/fuse", "nvidia.com/gpu=all"]
    path = render_stack("native", env={"GPU_DEVICE": "/dev/dri/renderD128"}, gpu=True)
    assert path["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dri/renderD128"]
    # 空串回退默认（与 _interpolate 的 `${NAME:-default}` 语义一致）
    empty = render_stack("native", env={"GPU_DEVICE": ""}, gpu=True)
    assert empty["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dri"]


def test_native_passthrough_main_layer_host_network_and_dbus():
    """透传主层：host 网络 + ports 整键删除 + 专用 tag + D-Bus bind/env。"""
    plain = render_stack("native")
    pt = render_stack("native", passthrough=True)
    assert pt["network_mode"] == "host"
    assert "ports" not in pt  # !reset → 整键删除（host 网络禁端口发布）
    assert pt["image"] == "localhost/native-dev:passthrough"
    # D-Bus socket bind：长语法、ro、源缺失绝不自动创建
    dbus = [
        v for v in pt["volumes"]
        if isinstance(v, dict) and v["target"] == "/tmp/runtime-user/bus"
    ]
    assert len(dbus) == 1
    assert dbus[0]["source"] == "/run/user/1000/bus"
    assert dbus[0]["read_only"] is True
    assert dbus[0]["bind"]["create_host_path"] is False
    env = pt["environment"]
    assert env["XDG_RUNTIME_DIR"] == "/tmp/runtime-user"
    assert env["DBUS_SESSION_BUS_ADDRESS"] == "unix:path=/tmp/runtime-user/bus"
    assert env["SSHD_PORT"] == "2223"
    # rootless 必需与栈原生 volumes 保留（只增不改）
    assert pt["devices"] == plain["devices"]
    targets = [_volume_target(v) for v in pt["volumes"]]
    assert "/tmp/runtime-user/bus" in targets
    for t in ("/workspace", "/workspace/npu_tvm", "/root/.ccache"):
        assert t in targets


def test_native_passthrough_env_interpolation_overrides():
    """主层四个插值键均可经 env 覆盖。"""
    pt = render_stack("native", env={
        "NATIVE_PASSTHROUGH_IMAGE_TAG": "registry.example/x:p",
        "DBUS_SESSION_BUS_PATH": "/run/dbus/system_bus_socket",
        "HOST_NET_SSHD_PORT": "2333",
    }, passthrough=True)
    assert pt["image"] == "registry.example/x:p"
    assert pt["environment"]["SSHD_PORT"] == "2333"
    dbus = [
        v for v in pt["volumes"]
        if isinstance(v, dict) and v["target"] == "/tmp/runtime-user/bus"
    ][0]
    assert dbus["source"] == "/run/dbus/system_bus_socket"


def test_native_usb_layer_appends_device_without_network_change():
    """USB 层：devices 追加，bridge 网络与端口不动。"""
    plain = render_stack("native")
    usb = render_stack("native", usb=True)
    assert usb["devices"] == [
        "/dev/fuse:/dev/fuse", "/dev/bus/usb:/dev/bus/usb",
    ]
    assert usb["network_mode"] == "bridge"
    assert usb["ports"] == plain["ports"]
    # USB_DEVICE 精确指定单设备
    one = render_stack(
        "native", env={"USB_DEVICE": "/dev/bus/usb/001/002"}, usb=True
    )
    assert one["devices"][-1] == "/dev/bus/usb/001/002:/dev/bus/usb"


def test_native_passthrough_and_usb_combined_merge_order():
    """主层 + USB：host 形态下 devices 仍追加合并（fuse+usb）。"""
    svc = render_stack("native", passthrough=True, usb=True)
    assert svc["network_mode"] == "host"
    assert "ports" not in svc
    assert svc["devices"] == [
        "/dev/fuse:/dev/fuse", "/dev/bus/usb:/dev/bus/usb",
    ]
    assert svc["image"] == "localhost/native-dev:passthrough"


def _volume_map(svc):
    return {v["target"]: v for v in svc["volumes"] if isinstance(v, dict)}


def test_native_gui_wayland_layer_defaults_to_wslg():
    """GUI Wayland 层（C33）：WSLg 缺省路径 bind + 两寻址 env；bridge 不动。"""
    plain = render_stack("native")
    wl = render_stack("native", gui_forms=("wayland",))
    vm = _volume_map(wl)
    assert vm["/tmp/runtime-user/wayland-0"]["source"] == (
        "/mnt/wslg/runtime-dir/wayland-0"
    )
    assert vm["/tmp/runtime-user/wayland-0"]["bind"]["create_host_path"] is False
    assert wl["environment"]["XDG_RUNTIME_DIR"] == "/tmp/runtime-user"
    assert wl["environment"]["WAYLAND_DISPLAY"] == "wayland-0"
    # GUI 不要求 host 网络：bridge 形态与端口逐字不动
    assert wl["network_mode"] == "bridge"
    assert wl["ports"] == plain["ports"]
    assert wl["image"] == plain["image"]


def test_native_gui_wayland_env_overrides():
    """物理 Linux：HOST_XDG_RUNTIME_DIR/HOST_WAYLAND_DISPLAY 改指源与 target。"""
    wl = render_stack("native", env={
        "GUI_WAYLAND_SOCKET": "/run/user/1000/wayland-1",
        "HOST_WAYLAND_DISPLAY": "wayland-1",
    }, gui_forms=("wayland",))
    vm = _volume_map(wl)
    assert vm["/tmp/runtime-user/wayland-1"]["source"] == "/run/user/1000/wayland-1"
    assert wl["environment"]["WAYLAND_DISPLAY"] == "wayland-1"


def test_native_gui_x11_layer_mounts_dir_and_display():
    """X11 层：挂 socket **目录**（非单文件）+ DISPLAY；不注入 Wayland 变量。"""
    x11 = render_stack("native", gui_forms=("x11",))
    vm = _volume_map(x11)
    assert vm["/tmp/.X11-unix"]["source"] == "/mnt/wslg/.X11-unix"
    assert vm["/tmp/.X11-unix"]["bind"]["create_host_path"] is False
    assert x11["environment"]["DISPLAY"] == ":0"
    assert "WAYLAND_DISPLAY" not in x11["environment"]
    assert "XDG_RUNTIME_DIR" not in x11["environment"]
    one = render_stack("native", env={
        "GUI_X11_SOCKETDIR": "/tmp/.X11-unix", "GUI_DISPLAY": ":1",
    }, gui_forms=("x11",))
    assert _volume_map(one)["/tmp/.X11-unix"]["source"] == "/tmp/.X11-unix"
    assert one["environment"]["DISPLAY"] == ":1"


def test_native_gui_dual_forms_and_full_combo():
    """Wayland+X11 两层并存；全家桶（gpu+passthrough+gui+usb）字段不冲突。"""
    gui = render_stack("native", gui_forms=("wayland", "x11"))
    vm = _volume_map(gui)
    assert "/tmp/runtime-user/wayland-0" in vm and "/tmp/.X11-unix" in vm
    assert gui["environment"]["WAYLAND_DISPLAY"] == "wayland-0"
    assert gui["environment"]["DISPLAY"] == ":0"
    # volumes 追加语义：基座 9 条卷一个不少
    assert len(gui["volumes"]) == len(render_stack("native")["volumes"]) + 2

    full = render_stack(
        "native", gpu=True, gpu_file="compose.gpu.wsl.yaml",
        passthrough=True, gui_forms=("wayland", "x11"), usb=True,
    )
    assert full["network_mode"] == "host"
    assert "ports" not in full
    # 裸 token 设备项由 podman-compose 运行时原样下传（C18：不做冒号拆分），
    # 模拟器不做归一，故保持 /dev/dxg 原形。
    assert full["devices"] == [
        "/dev/fuse:/dev/fuse",
        "/dev/dxg",
        "/dev/bus/usb:/dev/bus/usb",
    ]
    assert full["image"] == "localhost/native-dev:passthrough"


def test_nested_interpolation_simulator_innermost_first():
    """模拟器自证：嵌套插值必须**最内层先算**（单轮 `[^}]*` 会截断出错误串）。"""
    assert _expand("${A:-x:${B:-y}}", {}) == "x:y"
    assert _expand("${A:-x:${B:-y}}", {"B": "z"}) == "x:z"
    assert _expand("${A:-x:${B:-y}}", {"A": "w", "B": "z"}) == "w"
    assert _expand("${A:-x:${B:-y}}", {"A": ""}) == "x:y"  # 空串=未设


def test_env_override_flows_through_interpolation():
    svc = render_stack("native", env={
        "NATIVE_IMAGE_TAG": "registry.example/x:9", "NATIVE_SSH_PORT": "2300",
        "NUITKA_JOBS": "16", "GRANT_SUDO": "no",
    })
    assert svc["image"] == "registry.example/x:9"
    assert svc["ports"] == ["2300:22", "8890:8888"]
    assert svc["environment"]["NUITKA_JOBS"] == "16"
    assert svc["environment"]["GRANT_SUDO"] == "no"


# ── 模拟器自证（防止模拟器本身写错导致假阳性）────────────────────────────────


def test_simulator_dict_deep_merge_and_scalar_override():
    assert merge({"a": {"x": 1, "y": 2}}, {"a": {"y": 3, "z": 4}}) == {
        "a": {"x": 1, "y": 3, "z": 4},
    }


def test_simulator_list_append_but_command_replaces():
    assert merge_one(["a"], ["b"], key="security_opt") == ["a", "b"]
    assert merge_one(["old"], ["new"], key="command") == ["new"]


def test_simulator_volumes_short_syntax_override_wins_and_moves_tail():
    # vendor L2289-L2297：仅短语法字符串参与去重，覆盖方同 target 获胜，
    # 基方碰撞项删除，覆盖方条目整体落在尾部
    a = ["/h1:/workspace"]
    b = ["/h2:/workspace", "/h3:/data"]
    out = merge_one(a, b, key="volumes")
    assert out == ["/h2:/workspace", "/h3:/data"]


def test_simulator_volumes_long_syntax_dict_not_deduped():
    # 长语法 dict 项永不参与去重（":" in dict 是键判断）：
    # 同 target 的重复挂载条目会全部保留并下发给 podman
    a = [{"type": "bind", "source": "s1", "target": "/workspace"}]
    b = [
        {"type": "bind", "source": "s2", "target": "/workspace"},
        {"type": "bind", "source": "s3", "target": "/data"},
    ]
    out = merge_one(a, b, key="volumes")
    assert [(v["source"], v["target"]) for v in out] == [
        ("s1", "/workspace"), ("s2", "/workspace"), ("s3", "/data"),
    ]


def test_simulator_volumes_anonymous_and_mixed_forms():
    # 匿名卷（无冒号）不参与去重；短语法碰撞只删基方短语法项
    a = ["anonymous-vol", "/h1:/w"]
    b = ["/h2:/w"]
    assert merge_one(a, b, key="volumes") == ["anonymous-vol", "/h2:/w"]


def test_simulator_type_conflict_raises_value_error():
    # 真实 1.6.0 L2283-L2286：跨类型合并硬失败（None+dict 特判除外）
    with pytest.raises(ValueError):
        merge_one(["a"], {"k": "v"}, key="environment")
    # None + dict 按空 dict 合并（L2272-L2273）
    assert merge_one(None, {"k": "v"}, key="labels") == {"k": "v"}


def test_simulator_depends_on_list_dict_normalized():
    # vendor L2276-L2281：depends_on 的 list 等价 {项: {}}，list+dict 不抛冲突
    assert merge_one(["a", "b"], {"b": {"condition": "ok"}, "c": {}},
                     key="depends_on") == {
        "a": {}, "b": {"condition": "ok"}, "c": {},
    }
    assert merge_one({"a": {"restart": True}}, ["b"],
                     key="depends_on") == {"a": {"restart": True}, "b": {}}


# ── 与真实 podman-compose 1.6.0 rec_merge 直接对照（防模拟器漂移）─────────────

def _real_podman_compose():
    """取权威 rec_merge 实现：**vendor 子模块 pin 优先**，安装态仅作 fallback。

    2026-09-21 基准修正：vendor pin ``e3df104`` = ``v1.6.0-97-ge3df104``，即
    **v1.6.0 发布后又走了 97 个 commit 的 main**；而本机安装态是 pip 装的
    **已发布 v1.6.0**（py314 site-packages，2026-09-10 装入）。上游 ``__version__``
    在两次发布之间不 bump，故两份都自称 1.6.0，实际**不是同一快照**——安装态缺
    ``96a2043``（"coerce depends_on list to dict in rec_merge_one when types
    differ"，2026-06-21，未随任何 tag 发布），其 rec_merge_one 对 depends_on
    list↔dict 直接抛 ValueError，vendor 则已归一化。仓库以 gitlink pin vendor
    为权威（vendor/AGENTS.md：third_party 只读依赖以 pin commit 为准），故对照
    基准取 vendor——否则「环境快照的新旧」会单方面决定测试成败，且环境一旦
    升级到含该修复的版本又**反向失败**。

    两份实现对本模拟器覆盖的语义**只在 depends_on 一项分歧**（其余 6/8 探针
    等价）；三栈 compose.yaml 均未使用 depends_on，故该分歧不影响渲染结论。
    """
    vendor_src = _VENDOR_PC / "podman_compose.py"
    if vendor_src.exists():
        if str(_VENDOR_PC) not in sys.path:
            sys.path.insert(0, str(_VENDOR_PC))
        # 安装态副本若已先入 sys.modules，裸 import 会命中它，故先清缓存再导入
        sys.modules.pop("podman_compose", None)
        import podman_compose  # type: ignore
        assert Path(podman_compose.__file__).resolve() == vendor_src.resolve(), (
            f"未加载到 vendor pin 副本，实际为 {podman_compose.__file__}"
        )
        return podman_compose
    try:
        import podman_compose  # type: ignore
        return podman_compose
    except ImportError:
        pytest.skip("vendor 子模块不可用且环境未安装 podman-compose")


_REC_MERGE_PROBES = [
    # dict 深合并 + 标量覆盖
    ({"environment": {"A": "1", "B": "2"}},
     {"environment": {"B": "3", "C": "4"}}),
    # 普通 list 追加（devices 不去重）
    ({"devices": ["/dev/fuse:/dev/fuse"]},
     {"devices": ["/dev/dri:/dev/dri"]}),
    # command 无条件整体替换
    ({"command": ["old"]}, {"command": "/bin/sh -c x"}),
    # volumes 短语法：覆盖方获胜 + 移尾
    ({"volumes": ["/h1:/w"]},
     {"volumes": ["/h2:/w", "/h3:/d"]}),
    # volumes 长语法：dict 不去重
    ({"volumes": [{"type": "bind", "source": "s1", "target": "/w"}]},
     {"volumes": [{"type": "bind", "source": "s2", "target": "/w"}]}),
    # 匿名卷 + 短语法混合
    ({"volumes": ["anon", "/h1:/w"]}, {"volumes": ["/h2:/w"]}),
    # depends_on list↔dict 归一化后取并集（vendor L2276-L2281）
    ({"depends_on": ["a", "b"]},
     {"depends_on": {"b": {"condition": "ok"}, "c": {}}}),
    ({"depends_on": {"a": {"restart": True}}}, {"depends_on": ["b"]}),
]


def test_vs_real_rec_merge_probes():
    pc = _real_podman_compose()
    assert getattr(pc, "__version__", "?") == "1.6.0"
    for base, over in _REC_MERGE_PROBES:
        # 真实 rec_merge 原地修改 target，两侧各喂一份深拷贝
        real = pc.rec_merge(copy.deepcopy(base), copy.deepcopy(over))
        mine = merge(copy.deepcopy(base), copy.deepcopy(over))
        assert mine == real, f"模拟器偏离真实 rec_merge: {base} ◁ {over} → {mine} != {real}"


def test_vs_real_rec_merge_type_conflict():
    pc = _real_podman_compose()
    with pytest.raises(ValueError):
        pc.rec_merge({"environment": ["A=1"]}, {"environment": {"A": "2"}})
    with pytest.raises(ValueError):
        merge({"environment": ["A=1"]}, {"environment": {"A": "2"}})
