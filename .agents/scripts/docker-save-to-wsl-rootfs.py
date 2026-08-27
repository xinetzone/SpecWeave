#!/usr/bin/env python3
"""
⚠️  **仅供学习参考 — 不推荐生产使用** ⚠️

将 docker save 格式的 tar.gz 转换为 WSL --import 所需的 flat rootfs tar。

**强烈建议使用OCI运行时（Podman/Docker）进行转换**，详见模式库：
  patterns/code-patterns/oci-image-wsl-rootfs-bridge.md

验证状态（2026-08-18，devcontainer-base:latest，26层/1.4GB镜像）：
  ✅ Bug修复后可正确产出可启动WSL rootfs（Python 3.14.6 free-threading验证通过）
  ⚠️ whiteout处理不完整：输出多~9899个文件（~65MB系统缓存/locale残留），不影响功能
  ⏱️ 耗时5分20秒（类似规模镜像与podman export相当，但为三次IO传递）
  ❌ 不处理xattr扩展属性、可能遗漏某些特殊文件语义

已知问题：
  - 叠层whiteout删除处理在复杂镜像上不完整（残留.pyc/.ftl等本应被上层删除的文件）
  - 纯Python单线程，大规模镜像（>5GB）性能可能不可接受
  - filter='data'模式下setuid/setgid位和设备文件被过滤（WSL会自动创建/dev，影响不大）

Docker save 格式:
  - 外层 tar 包含: manifest.json, config.json, 多个 <layer-hash>/ 目录
  - 每个 <layer-hash>/layer.tar 是一层文件系统增量
  - 需要按顺序叠层, 处理 whiteout 文件 (.wh.*)

WSL --import 需要:
  - 一个 flat tar (可 gzip), 根目录直接包含 /bin, /etc, /usr 等
  - 保留 Unix 权限、符号链接等元数据

用法:
  python docker-save-to-wsl-rootfs.py <input.tar.gz> <output.tar> [--compress] [--verbose]
"""

import argparse
import copy
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Optional


# Whiteout 前缀
WHITEOUT_PREFIX = ".wh."
OPAQUE_WHITEOUT = ".wh..wh..opq"

# 要跳过的文件类型 (设备文件、FIFO等, WSL 会自动创建 /dev)
SKIP_TYPES = {tarfile.CHRTYPE, tarfile.BLKTYPE, tarfile.FIFOTYPE}


class VirtualFS:
    """虚拟文件系统, 跟踪叠层后的最终文件状态。"""

    def __init__(self, tmpdir: Path):
        self.tmpdir = tmpdir
        # path -> (TarInfo, content_file_path | None)
        # content_file_path 仅对 regular files 有值
        self.entries: dict[str, tuple[tarfile.TarInfo, Optional[Path]]] = {}
        self._content_counter = 0

    def _content_path(self) -> Path:
        """生成临时内容文件路径。"""
        self._content_counter += 1
        return self.tmpdir / f"content_{self._content_counter:08d}"

    def _normalize_path(self, name: str) -> str:
        """规范化 tar 中的路径: 去除前导 ./ 和 /, 使用正斜杠。"""
        # 去除前导的 ./ 或 /
        name = name.lstrip("/")
        while name.startswith("./"):
            name = name[2:]
        # tar 中目录条目可能以 / 结尾, 保留
        return name

    def apply_layer(self, layer_tar: tarfile.TarFile):
        """应用一层 layer.tar 到虚拟文件系统。"""
        # 先收集 opaque whiteout 标记的目录, 需要先清空再处理其他条目
        opaque_dirs: set[str] = set()
        # 收集本层的 whiteout 删除和正常条目
        whiteouts: list[tuple[str, str]] = []  # (dirname, basename_to_delete)
        regular_entries: list[tarfile.TarInfo] = []

        for member in layer_tar:
            # 规范化路径
            mname = self._normalize_path(member.name)
            if not mname:
                continue

            member.name = mname
            dirname = os.path.dirname(mname)
            basename = os.path.basename(mname)

            # 处理 opaque whiteout: .wh..wh..opq
            if basename == OPAQUE_WHITEOUT:
                opaque_dirs.add(dirname)
                continue

            # 处理 whiteout: .wh.<filename>
            if basename.startswith(WHITEOUT_PREFIX):
                deleted_name = basename[len(WHITEOUT_PREFIX):]
                if deleted_name:
                    whiteouts.append((dirname, deleted_name))
                continue

            regular_entries.append(member)

        # 1. 处理 opaque whiteout: 清空标记目录下所有子条目
        for odir in opaque_dirs:
            self._clear_directory(odir)

        # 2. 处理 whiteout 删除
        for dirname, del_name in whiteouts:
            full_path = os.path.join(dirname, del_name) if dirname else del_name
            self._remove_entry(full_path)

        # 3. 处理正常条目
        for member in regular_entries:
            self._add_entry(layer_tar, member)

    def _clear_directory(self, dirpath: str):
        """清空目录下所有子条目 (opaque whiteout 处理)。"""
        # 构建要删除的路径列表
        prefix = dirpath + "/" if dirpath else ""
        to_remove = [p for p in self.entries if p.startswith(prefix) or p == dirpath]
        for p in to_remove:
            self._remove_entry(p)

    def _remove_entry(self, path: str):
        """删除条目及其子条目。"""
        if path in self.entries:
            tarinfo, content_path = self.entries.pop(path)
            if content_path and content_path.exists():
                content_path.unlink()

        # 如果是目录, 删除所有子条目
        prefix = path + "/"
        children = [p for p in self.entries if p.startswith(prefix)]
        for p in children:
            tarinfo, content_path = self.entries.pop(p)
            if content_path and content_path.exists():
                content_path.unlink()

    def _add_entry(self, src_tar: tarfile.TarFile, member: tarfile.TarInfo):
        """添加/覆盖一个条目。"""
        path = member.name

        # 跳过设备文件和FIFO
        if member.type in SKIP_TYPES:
            return

        # 如果该路径已存在, 先删除旧内容
        if path in self.entries:
            old_info, old_content = self.entries[path]
            if old_content and old_content.exists():
                old_content.unlink()

        # 处理不同类型
        if member.isreg() or member.type == tarfile.AREGTYPE or member.type == tarfile.CONTTYPE:
            # 普通文件: 提取内容到临时文件
            content_path = self._content_path()
            with src_tar.extractfile(member) as src_f:
                if src_f is not None:
                    with open(content_path, "wb") as dst_f:
                        shutil.copyfileobj(src_f, dst_f, length=1024 * 1024)
            self.entries[path] = (member, content_path)
        elif member.issym() or member.islnk():
            # 符号链接/硬链接: 不需要内容文件
            self.entries[path] = (member, None)
        elif member.isdir():
            # 目录
            self.entries[path] = (member, None)
        else:
            # 其他类型 (如稀疏文件等): 尝试作为普通文件处理
            try:
                content_path = self._content_path()
                with src_tar.extractfile(member) as src_f:
                    if src_f is not None:
                        with open(content_path, "wb") as dst_f:
                            shutil.copyfileobj(src_f, dst_f, length=1024 * 1024)
                    else:
                        content_path = None
                self.entries[path] = (member, content_path)
            except Exception:
                # 无法提取的类型, 跳过
                pass

    def write_to_tar(self, out_tar: tarfile.TarFile):
        """将虚拟文件系统写入输出 tar。"""
        # 确保先写入目录条目 (排序保证父目录在子条目之前)
        sorted_paths = sorted(self.entries.keys())

        for path in sorted_paths:
            tarinfo, content_path = self.entries[path]

            # 确保 tarinfo 名称正确（浅拷贝避免修改VFS中存储的原始TarInfo）
            tarinfo = copy.copy(tarinfo)
            tarinfo.name = path

            if content_path and tarinfo.isreg():
                # 普通文件: 从临时文件流式写入
                with open(content_path, "rb") as f:
                    out_tar.addfile(tarinfo, f)
            else:
                # 目录、符号链接等: 无内容
                out_tar.addfile(tarinfo)

    def cleanup(self):
        """清理所有临时内容文件。"""
        for _path, (_info, content_path) in self.entries.items():
            if content_path and content_path.exists():
                try:
                    content_path.unlink()
                except OSError:
                    pass


def main():
    parser = argparse.ArgumentParser(
        description="将 docker save tar.gz 转换为 WSL rootfs tar"
    )
    parser.add_argument("input", help="输入文件: docker save 生成的 .tar 或 .tar.gz")
    parser.add_argument("output", help="输出文件: WSL rootfs .tar 或 .tar.gz")
    parser.add_argument(
        "--compress", "-z", action="store_true", help="输出使用 gzip 压缩 (.tar.gz)"
    )
    parser.add_argument(
        "--tmpdir", "-t", default=None, help="临时文件目录 (默认使用系统临时目录)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="详细输出"
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 创建临时工作目录
    tmp_base = Path(args.tmpdir) if args.tmpdir else None
    workdir = Path(tempfile.mkdtemp(prefix="docker2wsl_", dir=tmp_base))
    if args.verbose:
        print(f"[INFO] 临时工作目录: {workdir}", file=sys.stderr)

    vfs = VirtualFS(workdir)
    tar_path = None  # 解压后的外层 tar

    try:
        # 步骤 1: 如果输入是 .gz, 先解压
        open_mode = "r:gz" if str(input_path).endswith(".gz") else "r:"
        if args.verbose:
            print(f"[INFO] 打开 docker save 归档: {input_path} ({open_mode})", file=sys.stderr)

        with tarfile.open(input_path, open_mode) as outer_tar:
            # 步骤 2: 读取 manifest.json 获取层顺序
            manifest_member = None
            for member in outer_tar.getmembers():
                if member.name == "manifest.json" or member.name.endswith("/manifest.json"):
                    manifest_member = member
                    break

            if manifest_member is None:
                print("错误: 未找到 manifest.json, 不是有效的 docker save 归档", file=sys.stderr)
                sys.exit(1)

            manifest_f = outer_tar.extractfile(manifest_member)
            manifest_data = json.loads(manifest_f.read().decode("utf-8"))
            manifest_f.close()

            if not manifest_data:
                print("错误: manifest.json 为空", file=sys.stderr)
                sys.exit(1)

            # docker save 可能包含多个镜像, 取第一个
            image_manifest = manifest_data[0]
            layer_paths = image_manifest.get("Layers", [])
            if args.verbose:
                print(f"[INFO] 找到 {len(layer_paths)} 个层:", file=sys.stderr)
                for i, lp in enumerate(layer_paths):
                    print(f"  [{i+1}] {lp}", file=sys.stderr)

            # 步骤 3: 解压外层 tar 到临时文件 (需要随机访问各层)
            # tarfile 对 gzip 流不支持随机访问, 所以先解压整个外层 tar
            tar_path = workdir / "outer.tar"
            if args.verbose:
                print(f"[INFO] 解压外层 tar 到临时文件...", file=sys.stderr)

            # 流式解压: 由于外层 tar 是 gzip 压缩的, 我们已经打开了它
            # 需要解压到临时文件以支持随机访问各 layer.tar
            # 直接从 outer_tar 提取所有成员到临时目录
            extract_dir = workdir / "extracted"
            extract_dir.mkdir(exist_ok=True)

            # 重新打开输入文件来解压
            outer_tar.close()

        # 重新打开并解压所有内容到临时目录
        with tarfile.open(input_path, open_mode) as outer_tar:
            # filter='data' 在 Python 3.12+ 中消除安全警告，同时保留必要的文件元数据
            outer_tar.extractall(extract_dir, filter='data')

        # 找到解压后的 manifest.json 和层目录
        manifest_file = extract_dir / "manifest.json"
        if not manifest_file.exists():
            # 可能在子目录? 搜索一下
            for f in extract_dir.rglob("manifest.json"):
                manifest_file = f
                break

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        image_manifest = manifest_data[0]
        layer_paths = image_manifest.get("Layers", [])

        # 确定层文件的基础目录
        layer_base = manifest_file.parent

        if args.verbose:
            print(f"[INFO] 层基础目录: {layer_base}", file=sys.stderr)

        # 步骤 4: 按顺序应用每一层
        for i, layer_rel_path in enumerate(layer_paths):
            layer_file = layer_base / layer_rel_path
            if not layer_file.exists():
                print(f"警告: 层文件不存在, 跳过: {layer_file}", file=sys.stderr)
                continue

            if args.verbose:
                print(f"[INFO] 处理层 [{i+1}/{len(layer_paths)}]: {layer_rel_path}", file=sys.stderr)

            with tarfile.open(layer_file, "r:") as layer_tar:
                vfs.apply_layer(layer_tar)

        if args.verbose:
            print(f"[INFO] 虚拟文件系统条目数: {len(vfs.entries)}", file=sys.stderr)

        # 步骤 5: 写入输出 tar
        out_mode = "w:gz" if args.compress else "w:"
        if args.verbose:
            print(f"[INFO] 写入 WSL rootfs tar: {output_path} ({out_mode})", file=sys.stderr)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(output_path, out_mode) as out_tar:
            vfs.write_to_tar(out_tar)

        out_size = output_path.stat().st_size
        if args.verbose:
            print(f"[INFO] 输出大小: {out_size / (1024*1024):.1f} MB", file=sys.stderr)
            print(f"[INFO] 转换完成!", file=sys.stderr)

    finally:
        # 清理
        vfs.cleanup()
        if workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
