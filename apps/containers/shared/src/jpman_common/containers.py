"""容器只读探测（CLI 路径，jpman-builder / jpman-client 共享）。

通过 ``<runtime> ps --filter`` 判断容器存在性/运行态；与 SDK 路径互补。

相位模型（:func:`container_phase`）：
- ``running``      容器存在且正在运行
- ``stopped``      容器存在但非运行（created / exited / paused 等）
- ``absent``       容器不存在
- ``unknown``      探测命令本身失败（daemon 瞬断 / 机器预热 / 编码异常）

``unknown`` 与 ``absent`` 必须区分：旧版 ``container_exists`` 把两者合并为
False，调用方在残留容器存在时裸跑 ``podman run`` 必撞 name already in use
（exit 125，2026-09-15 builder 实证）。

Windows invoke 通道铁律：探针命令**不得包含双引号**。invoke 在 Windows 把
命令包装为 ``pwsh /c "<cmd>"``，内嵌双引号会提前截断外层引用，残片被 pwsh
当成自身参数（实证报错 ``unknown shorthand flag: 'i' in -inputFormat``），
命令必然失败且被 ``warn=True`` 静默吞掉。故使用 ``-q`` 输出容器 ID（非空即
命中），不用 ``--format "{{.Names}}"`` 做名称比对；name regex 锚定
``^name$`` 已保证结果唯一属于目标容器。
"""
from typing import Optional

from invoke import Context, Result

from .proc import run_cmd

__all__ = ["container_exists", "container_running", "container_phase"]

PHASE_RUNNING = "running"
PHASE_STOPPED = "stopped"
PHASE_ABSENT = "absent"
PHASE_UNKNOWN = "unknown"


def _ps_ids(c: Context, runtime: str, name: str, all_containers: bool) -> Optional[bool]:
    """单次 ``ps -q --filter`` 探测，返回三态。

    True=精确匹配到目标容器（有 ID 输出）；False=未匹配（空输出且 exit 0）；
    None=探测命令失败（unknown）。``all_containers=False`` 仅查运行态，
    True 用 ``ps -aq`` 查全部状态。
    """
    ps_flag = "-aq" if all_containers else "-q"
    cmd = runtime + " ps " + ps_flag + " --filter name=^" + name + "$"
    if not all_containers:
        cmd += " --filter status=running"
    result: Optional[Result] = run_cmd(
        c, cmd, hide=True, warn=True, echo=False,
    )
    if result is None or not getattr(result, "ok", False):
        return None
    return bool((result.stdout or "").strip())


def container_exists(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否存在（包括停止态）。探测失败按 False 处理（保守兼容旧契约）。"""
    return _ps_ids(c, runtime, name, all_containers=True) is True


def container_running(c: Context, runtime: str, name: str) -> bool:
    """检查容器是否正在运行。探测失败按 False 处理（保守兼容旧契约）。"""
    return _ps_ids(c, runtime, name, all_containers=False) is True


def container_phase(c: Context, runtime: str, name: str) -> str:
    """返回容器当前相位（running / stopped / absent / unknown）。

    两次窄查询：运行态命中立即短路；未命中再查全部状态，存在即 stopped，
    不存在即 absent；任一探测命令失败归 unknown（不得与 absent 混淆）。
    """
    running = _ps_ids(c, runtime, name, all_containers=False)
    if running is None:
        return PHASE_UNKNOWN
    if running:
        return PHASE_RUNNING

    exists = _ps_ids(c, runtime, name, all_containers=True)
    if exists is None:
        return PHASE_UNKNOWN
    return PHASE_STOPPED if exists else PHASE_ABSENT
