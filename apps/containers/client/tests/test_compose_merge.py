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
- 不支持 ``!reset``/``!override`` YAML 标签（safe_load 遇标签即失败）；
- 不模拟 normalize_service 预处理（build.args dict→list、env/labels list→dict、
  security_opt str→list）；三栈 env/labels 均为 dict 形态故渲染无差异；
- 插值仅支持 ``${NAME}``/``${NAME:-default}``，不支持 ``:?``/``$$``/服务互引；
- 类型冲突（dict↔list 等）真实 1.6.0 抛 ValueError，模拟器同样抛出；
- 环境装有 podman-compose（或 vendor 子模块就位）时，test_vs_real_rec_merge
  会直接调用真实 rec_merge 对照，模拟器一旦偏离上游即失败。

AC-3 正向条款：rootless 三必需不重不漏、env 键并集一致、labels 一致、
privileged 缺失、栈专属字段（image/build/ports/volumes）原样保留。
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import pytest
import yaml

OVERLAYS = Path(__file__).resolve().parents[1] / "overlays"
SHARED = OVERLAYS / "_shared" / "base-rootless.yaml"
# vendor 只读子模块中的权威源码（与本机已安装包同为 1.6.0）
_VENDOR_PC = Path(__file__).resolve().parents[4] / "vendor" / "podman-compose"

_INTERP = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")

# 三栈黄金期望（抽取前逐栈 compose.yaml 的等价清单）
GOLDEN = {
    "quant": {
        "dir": "onnx-quantized", "service": "quant",
        "component": "onnx-quantized",
        "image": "localhost/onnx-quantized:latest",
        "container_name": "onnx-quantized",
        "dockerfile": "Containerfile.quantized",
        "ports": ["2222:22", "8888:8888"],
        "volume_targets": ["/workspace"],
        "env": {
            "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
            "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
        },
    },
    "xmnn": {
        "dir": "xmnn-dev", "service": "xmnn",
        "component": "xmnn-dev",
        "image": "localhost/xmnn-dev:latest",
        "container_name": "xmnn-dev",
        "dockerfile": "Containerfile.xmnn-dev",
        "ports": ["2223:22", "8890:8888"],
        "volume_targets": [
            "/workspace", "/workspace/npu_tvm", "/workspace/npuusertools",
            "/workspace/models", "/root/.ccache",
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
        "volume_targets": ["/workspace", "/workspace/agent-monetize"],
        "env": {
            "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
            "PYTHONPATH", "LD_LIBRARY_PATH",
        },
    },
}

# ── 最小合并模拟器（语义对齐 podman-compose 1.6.0 rec_merge_one）──────────────

_REPLACE_KEYS = {"command", "entrypoint"}
_MISSING = object()


def _interpolate(node, env):
    if isinstance(node, dict):
        return {k: _interpolate(v, env) for k, v in node.items()}
    if isinstance(node, list):
        return [_interpolate(v, env) for v in node]
    if isinstance(node, str):
        def sub(m):
            name, default = m.group(1), m.group(2)
            if name in env and env[name] != "":
                return env[name]
            return default if default is not None else ""
        return _INTERP.sub(sub, node)
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
    不含 !reset/!override 标签语义（三栈 YAML 未使用）。
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
            out[k] = merge_one(out[k], v, k) if k in out else copy.deepcopy(v)
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


def render_stack(stack: str, env=None, *, gpu=False):
    """模拟 resolve_extends + 多文件 rec_merge 后的服务 dict。"""
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
    if gpu:
        # 真实管线：文件循环先逐文件 rec_merge（compose ◁ gpu，L2851），
        # 循环后才 resolve_extends（rec_merge({}, base, merged)，L2919）
        ov = _interpolate(_load(odir / "compose.gpu.yaml"), env or {})
        stacked = merge(svc, ov["services"][g["service"]])
    else:
        stacked = svc
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
    assert gpu["devices"] == ["/dev/fuse:/dev/fuse", "/dev/dri:/dev/dri"]
    # 其余字段不被 override 影响
    assert gpu["environment"] == plain["environment"]
    assert gpu["ports"] == plain["ports"]


def test_env_override_flows_through_interpolation():
    svc = render_stack("xmnn", env={
        "XMNN_IMAGE_TAG": "registry.example/x:9", "XMNN_SSH_PORT": "2300",
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
    """优先已安装的 podman-compose，回退 vendor 只读子模块；都没有则 skip。"""
    try:
        import podman_compose  # type: ignore
        return podman_compose
    except ImportError:
        if (_VENDOR_PC / "podman_compose.py").exists():
            sys.path.insert(0, str(_VENDOR_PC))
            import podman_compose  # type: ignore
            return podman_compose
    pytest.skip("环境未安装 podman-compose 且 vendor 子模块不可用")


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
