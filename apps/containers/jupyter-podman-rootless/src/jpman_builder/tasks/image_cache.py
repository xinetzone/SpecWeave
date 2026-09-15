"""镜像归档任务（podman save 的 invoke 原生实现）。

**为什么需要本模块**：镜像备份此前只有 `bash bin/jpman save`（WSL/bash 路径，
`podman save | pigz`）与一个不含 save 的 `bin/jpman.ps1`（其中 load 分支明确
提示 "Run 'jpman save' first (inside WSL)"）——在本项目的 Windows 原生主工作流
（invoke + podman.exe 远程客户端 + py314）下**没有保存镜像的路径**。本模块以
SDK→CLI 两层实现导出，产物约定（`.image-cache/` 目录、归档命名、manifest.txt
字段、`*-latest.tar.gz` 指针）与 `bin/jpman` 完全对齐，两个生态产出同构、
可互相 `podman load`。

关键环境事实（2026-09-15 真机实证，勿凭推测修改）：
- Windows 上 podman 是**远程客户端**，但 `podman save -o <文件>` 的响应流经
  客户端落盘到**本机文件系统**（实测 112MB ubuntu 归档在 Windows cwd 生成、
  `podman load -i` 回环成功），故归档天然落在 Windows 磁盘，machine/WSL 重置不丢。
- PowerShell 管道是对象管道，二进制重定向会损坏 tar 字节流——**禁止**
  `podman save | ...` 写法，CLI 路径只用 `-o` 文件，压缩在 Python 侧完成。
- 普通用户无创建符号链接权限（WinError 1314），latest 指针用**硬链接**
  （os.link，同卷零额外空间，对 WSL/bash 侧呈现为普通文件），硬链接失败才复制。
- podman-py `Image.save(named=False)` 导出的归档**不带仓库标签**，load 后是
  `<none>:<none>`；必须传 `named=<tag>`（docker-archive 格式，tag 须属于该镜像）。

用法：
    invoke save                          # 保存默认镜像到 .image-cache/（gzip）
    invoke save --no-compress            # 导出未压缩 tar（更快、更大）
    invoke save -t jupyter-podman-rootless:passthrough
    invoke save -o D:\\backups\\img.tar.gz   # 自定义输出文件
"""
from __future__ import annotations

import gzip
import hashlib
import os
import shutil
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values
from invoke import task
from invoke.exceptions import Exit

from .client import APIError, PodmanNotFound, get_client, sdk_available
from .utils import detect_runtime, run_cmd

# ── 产物约定（与 bin/jpman 的 cmd_save 对齐，改动须两处同步）──────────────
CACHE_DIRNAME = ".image-cache"
ARCHIVE_BASENAME = "jupyter-podman-rootless"
LATEST_PREFIX = f"{ARCHIVE_BASENAME}-latest"
MANIFEST_NAME = "manifest.txt"
# podman-py 内部以 2MiB 拉取；本地写盘用 8MiB 聚合块；进度每 100MiB 打点
WRITE_CHUNK = 8 * 1024 * 1024
PROGRESS_STEP = 100 * 1024 ** 2
GZIP_LEVEL = 6  # 与 pigz/gzip 默认级别一致，兼顾速度与压缩率
# 空间预检系数：未压缩 tar ≈ 镜像虚拟大小（实测 112MB 镜像 → 111,569,920B tar）
TAR_BUDGET = 1.05
# CLI 兜底压缩路径存在 tar 与 tar.gz 短暂并存，额外预留 0.5 倍镜像大小
CLI_COMPRESS_EXTRA = 0.5


def _project_root() -> Path:
    """定位应用根目录（含 compose.yaml / Containerfile 的目录）。"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "compose.yaml").is_file():
            return current
        current = current.parent
    raise Exit("无法定位应用根目录：从模块路径向上未找到含 compose.yaml 的目录")


def _resolve_tag(c, tag: str | None, project_root: Path) -> str:
    """镜像标签解析：显式参数 > IMAGE_TAG 环境变量 > .env > invoke 配置默认值。"""
    if tag:
        return tag
    if os.environ.get("IMAGE_TAG"):
        return os.environ["IMAGE_TAG"]
    env_path = project_root / ".env"
    if env_path.exists():
        value = (dotenv_values(str(env_path)) or {}).get("IMAGE_TAG")
        if value:
            return value
    return c.container.get("image_tag", f"{ARCHIVE_BASENAME}:latest")


def _short_id(image_id: str) -> str:
    return image_id.removeprefix("sha256:")[:12]


def _human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "K", "M", "G", "T"):
        if size < 1024 or unit == "T":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}B"
        size /= 1024
    return f"{size:.1f}T"


def _preflight_space(target_dir: Path, image_size: int | None, need_extra_tar: bool) -> None:
    """落盘前空间预算预检（防止导出到一半 No space left，见经验 sc-20260915）。"""
    usage = shutil.disk_usage(target_dir)
    if image_size:
        need = int(image_size * TAR_BUDGET)
        if need_extra_tar:
            need += int(image_size * CLI_COMPRESS_EXTRA)
        if usage.free < need:
            raise Exit(
                f"磁盘空间不足：{target_dir} 可用 {_human_size(usage.free)}，"
                f"本次导出峰值约需 {_human_size(need)}（镜像大小 {_human_size(image_size)}）。"
                "请清理空间或用 -o 指定其他磁盘。"
            )


def _write_stream(chunks, tmp_path: Path, compress: bool, total_hint: int | None) -> int:
    """把字节迭代器流式写入临时归档（压缩时边收边 gzip，无中间 tar）。

    返回写入的归档字节数；每 100MiB 打印一次进度（长任务状态可见）。
    """
    written = 0
    next_mark = PROGRESS_STEP
    hint = f"/~{_human_size(total_hint)}" if total_hint else ""
    with open(tmp_path, "wb") as raw:
        sink = gzip.GzipFile(filename="", mode="wb", compresslevel=GZIP_LEVEL, fileobj=raw) if compress else raw
        try:
            for chunk in chunks:
                if not chunk:
                    continue
                sink.write(chunk)
                written += len(chunk)
                if written >= next_mark:
                    print(f"  ... {_human_size(written)}{hint} 已导出")
                    next_mark += PROGRESS_STEP
        finally:
            if compress:
                sink.close()
    return written


def _iter_file(path: Path):
    with open(path, "rb") as handle:
        while True:
            block = handle.read(WRITE_CHUNK)
            if not block:
                break
            yield block


def _verify_and_hash(archive: Path, compress: bool) -> str:
    """归档自证：gzip CRC 通读 / tar 结构遍历，同时返回归档文件自身 SHA256。

    损坏（截断、半成品）在此抛异常，task 层清理 .tmp，latest 指针不会被更新。
    """
    hasher = hashlib.sha256()
    with open(archive, "rb") as handle:
        for block in _iter_file(archive):
            hasher.update(block)
    if compress:
        # gzip 通读触发 CRC32/ISIZE 尾校验，损坏时抛 BadGzipFile/EOFError
        with gzip.open(archive, "rb") as gz:
            while gz.read(WRITE_CHUNK):
                pass
    else:
        with tarfile.open(archive, "r:") as tf:
            for _ in tf:
                pass
    return hasher.hexdigest()


def _point_latest(cache_dir: Path, archive_name: str, compressed: bool) -> bool:
    """更新 latest 指针：硬链接优先（实证 Windows 普通用户无 symlink 权限）。

    旧指针无论是普通文件、硬链接还是 WSL drvfs 留下的 0 字节坏 reparse 点都先移除
    （不能用 exists()/is_symlink() 预判——跨 9p/drvfs 创建的链接 Windows 可能识别
    为不存在）。归档刚落盘的瞬间 Windows Defender/索引服务可能短暂锁定文件，
    os.link/copyfile 偶发 EINVAL——实测无重试时首次切换失败，故带退避重试。
    返回指针是否就绪（调用方据此给出准确的恢复命令）。
    """
    latest = cache_dir / f"{LATEST_PREFIX}.tar.gz" if compressed else cache_dir / f"{LATEST_PREFIX}.tar"
    source = cache_dir / archive_name
    try:
        latest.unlink(missing_ok=True)
    except OSError:
        pass

    delays = (0.5, 1.5, 3.0)
    for attempt, delay in enumerate(delays):
        try:
            os.link(source, latest)
            print(f"[OK] latest 指针（硬链接）: {latest.name} -> {archive_name}")
            return True
        except OSError as exc_link:
            if attempt == len(delays) - 1:
                try:
                    shutil.copyfile(source, latest)
                    print(f"[OK] latest 指针（复制，硬链接失败: {exc_link}）: {latest.name}")
                    return True
                except OSError as exc_copy:
                    print(f"[WARN] latest 指针更新失败（归档本身有效）: {exc_copy}")
                    return False
            time.sleep(delay)
    return False


def _write_manifest(cache_dir: Path, tag: str, image_id: str, archive: Path,
                    sha256: str, started_utc: datetime, took_s: int) -> None:
    """写 manifest.txt（字段与 bin/jpman cmd_save 完全一致）。"""
    fields = [
        "# Jupyter Podman Rootless Image Cache",
        f"IMAGE_NAME={tag}",
        f"IMAGE_ID={image_id}",
        f"IMAGE_FILE={archive.name}",
        f"SIZE={_human_size(archive.stat().st_size)}",
        f"SHA256={sha256}",
        f"SAVED={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"SAVE_TOOK={took_s}s",
    ]
    (cache_dir / MANIFEST_NAME).write_text("\n".join(fields) + "\n", encoding="utf-8")


def _save_via_sdk(client, tag: str, tmp_archive: Path, compress: bool) -> str | bool | None:
    """SDK 路径导出到临时归档。成功返回镜像短 ID；镜像不存在返回 None；其他失败 False。"""
    try:
        image = client.images.get(tag)
    except PodmanNotFound:
        return None
    except APIError as exc:
        if getattr(exc, "response", None) is not None and getattr(exc.response, "status_code", 0) == 404:
            return None
        print(f"[SDK] 查询镜像失败: {exc}")
        return False

    image_id = _short_id(image.id)
    image_size = None
    try:
        image_size = int(image.attrs.get("Size", 0)) or None
    except (AttributeError, TypeError, ValueError):
        pass
    print(f"[SDK] Saving image {tag} ({image_id}, {_human_size(image_size) if image_size else 'size?'})...")
    _preflight_space(tmp_archive.parent, image_size, need_extra_tar=False)
    try:
        # named=tag：归档保留仓库标签，load 后仍是 tag 而非 <none>:<none>
        chunks = image.save(chunk_size=2 * 1024 * 1024, named=tag)
        _write_stream(chunks, tmp_archive, compress, image_size)
    except (APIError, OSError, EOFError) as exc:
        print(f"[SDK] save 失败: {exc}")
        return False
    return image_id


def _save_via_cli(c, runtime: str, tag: str, cache_dir: Path,
                  tmp_archive: Path, compress: bool) -> str | bool | None:
    """CLI 兜底：podman save -o（禁管道）→ Python 压缩。返回同 SDK 约定。"""
    with c.cd(str(_project_root())):
        # Go 模板必须单引号包裹：pwsh 通道下裸 { } 是脚本块定界符（见 manage.py 同纪律）；
        # f-string 中 {{{{ }}}} 转义后输出 {{.Size}}。
        result = run_cmd(
            c, f"{runtime} image inspect {tag} --format '{{{{.Size}}}}'",
            warn=True, hide=True, echo=False,
        )
    image_size = None
    if result is not None and result.ok:
        try:
            image_size = int((result.stdout or "").strip())
        except ValueError:
            image_size = None
    elif result is not None and "image not known" in ((result.stderr or "") + (result.stdout or "")):
        # inspect 已明确镜像不存在——不必再跑 save（秒回中文错误）
        return None

    _preflight_space(cache_dir, image_size, need_extra_tar=compress)

    # 相对项目根路径：podman 远程客户端 -o 已实证落本机 cwd（见模块文档）
    if compress:
        tmp_tar = tmp_archive.with_suffix("")  # .tmp-...tar（gzip 前的未压缩中间产物）
        rel_tar = tmp_tar.relative_to(_project_root()).as_posix()
    else:
        tmp_tar = tmp_archive
        rel_tar = tmp_archive.relative_to(_project_root()).as_posix()

    print(f"[CLI] Saving image {tag} via {runtime} save ...")
    # hide=True 才能拿到 Result.stderr（hide=False 走 TTY 直写分支返回值不可解析）；
    # podman save 自身无进度输出，进度由 Python 压缩阶段打点。
    with c.cd(str(_project_root())):
        result = run_cmd(c, f"{runtime} save -o {rel_tar} {tag}", warn=True, hide=True, echo=True)
    if result is None or not result.ok:
        stderr = (result.stderr if result is not None else "") or ""
        if tmp_tar.exists():
            tmp_tar.unlink()
        if any(token in stderr for token in ("image not known", "not found", "unable to find", "not present")):
            return None
        print(f"[CLI] podman save 失败: {stderr.strip()}")
        return False

    if compress:
        try:
            _write_stream(_iter_file(tmp_tar), tmp_archive, compress=True, total_hint=None)
        except OSError as exc:
            print(f"[CLI] gzip 压缩失败: {exc}")
            return False
        finally:
            if tmp_tar.exists():
                tmp_tar.unlink()

    # 镜像 ID 探针（Go 模板单引号，同 manage.py pwsh 通道纪律）
    with c.cd(str(_project_root())):
        id_result = run_cmd(
            c, f"{runtime} images {tag} --format '{{{{.ID}}}}'", warn=True, hide=True, echo=False
        )
    if id_result is not None and id_result.ok and (id_result.stdout or "").strip():
        return _short_id(id_result.stdout.strip().splitlines()[0].strip())
    print("[CLI] 归档完成，但镜像 ID 读取失败（manifest 将缺少 IMAGE_ID）")
    return False


@task(help={
    "tag": "要保存的镜像标签（默认取 .env/配置中的 IMAGE_TAG）",
    "output": "输出文件路径；缺省保存到 .image-cache/ 并按约定自动命名",
    "no-compress": "导出未压缩 tar（默认 gzip 压缩为 .tar.gz）",
    "force": "输出文件已存在时覆盖",
})
def save(c, tag=None, output=None, no_compress=False, force=False):
    """将镜像保存为归档文件（podman save；默认写入 .image-cache/）。

    Windows 原生可用（SDK→CLI 两层，产物与 bash `bin/jpman save` 同构）。
    恢复：podman load -i <归档文件>。
    """
    runtime = detect_runtime()
    project_root = _project_root()
    tag = _resolve_tag(c, tag, project_root)
    compress = not no_compress
    ext = ".tar.gz" if compress else ".tar"

    if output:
        out_path = Path(output).expanduser().resolve()
        if out_path.is_dir():
            cache_dir = out_path
            auto_name = True
        else:
            cache_dir = out_path.parent
            auto_name = False
    else:
        cache_dir = project_root / CACHE_DIRNAME
        out_path = None
        auto_name = True

    cache_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tmp_archive = cache_dir / f".tmp-save-{os.getpid()}-{timestamp}{ext}"

    started = time.monotonic()
    started_utc = datetime.now(timezone.utc)
    image_id: str | None = None
    used_backend = None

    try:
        # ── Tier 2: podman-py SDK（流式边收边压，无中间 tar）──
        if sdk_available():
            try:
                with get_client() as client:
                    if client is not None:
                        outcome = _save_via_sdk(client, tag, tmp_archive, compress)
                        if outcome is None:
                            raise Exit(f"镜像不存在：{tag}。请先构建：invoke build")
                        if outcome is not False:
                            image_id = outcome
                            used_backend = "SDK"
            except Exit:
                raise
            except Exception as exc:  # SDK 通道整体异常 → 落 CLI 兜底
                print(f"[SDK] 通道异常，降级 CLI: {exc}")
                if tmp_archive.exists():
                    tmp_archive.unlink()

        # ── Tier 3: CLI 兜底 ──
        if not used_backend:
            outcome = _save_via_cli(c, runtime, tag, cache_dir, tmp_archive, compress)
            if outcome is None:
                raise Exit(f"镜像不存在：{tag}。请先构建：invoke build")
            if outcome is False:
                raise Exit(f"镜像保存失败：{tag}（详见上方日志）")
            image_id = outcome
            used_backend = "CLI"

        if not image_id:
            raise Exit("镜像保存失败：未能获取镜像 ID")

        # ── 命名（自动模式与 bin/jpman 约定一致）──
        if auto_name:
            archive = cache_dir / f"{ARCHIVE_BASENAME}-{image_id}-{timestamp}{ext}"
        else:
            archive = out_path
        if archive.exists() and not force:
            raise Exit(f"目标文件已存在：{archive}（加 --force 覆盖）")

        # ── 自证：完整性校验 + 归档 SHA256（通过后才离开临时名）──
        print("[Verify] 校验归档完整性 ...")
        sha256 = _verify_and_hash(tmp_archive, compress)
        os.replace(tmp_archive, archive)
        took = int(time.monotonic() - started)

        size = _human_size(archive.stat().st_size)
        print(f"[OK] 镜像已保存（{used_backend}，{took}s，{size}）: {archive}")

        # ── 仅在默认缓存目录维护 latest 指针与 manifest（自定义输出不污染）──
        if auto_name and cache_dir == project_root / CACHE_DIRNAME:
            latest_ready = _point_latest(cache_dir, archive.name, compress)
            _write_manifest(cache_dir, tag, image_id, archive, sha256, started_utc, took)
            print(f"[OK] manifest 已更新: {cache_dir / MANIFEST_NAME}")
            pointer = cache_dir / (LATEST_PREFIX + ext)
            restore_target = pointer if latest_ready else archive
            restore_hint = f"podman load -i {restore_target}"
        else:
            restore_hint = f"podman load -i {archive}"
        print(f"[OK] SHA256: {sha256}")
        print(f"恢复命令: {restore_hint}")
    finally:
        if tmp_archive.exists():
            tmp_archive.unlink()
        stray_tar = tmp_archive.with_suffix("") if compress else None
        if stray_tar is not None and stray_tar.exists() and stray_tar.name.startswith(".tmp-save-"):
            stray_tar.unlink()
