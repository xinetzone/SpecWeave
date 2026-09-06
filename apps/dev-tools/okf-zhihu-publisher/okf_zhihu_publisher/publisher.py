"""发布编排层。

串联扫描 → 转换 → 对账 → 上传的完整流程。
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .api_client import ZhihuKbApiClient
from .bundle_scanner import BundleFile, BundleScanner, generate_remote_title
from .config import Config
from .state_manager import StateManager
from .transformer import BundleTransformer


# ── 操作类型 ────────────────────────────────────────────


@dataclass
class SyncOperation:
    """一个同步操作。"""

    action: str  # "upload" / "update" / "skip"
    bundle_file: BundleFile
    reason: str = ""


# ── 编排器 ──────────────────────────────────────────────


class Publisher:
    """发布编排器。"""

    def __init__(self, config: Config):
        self.config = config
        self.api: Optional[ZhihuKbApiClient] = None
        self.state: Optional[StateManager] = None
        self.scanner = BundleScanner(config.bundles_dir)
        self.transformer = BundleTransformer()
        self._stats = {"uploaded": 0, "skipped": 0, "failed": 0, "updated": 0}

    def sync(
        self,
        domain_filter: Optional[str] = None,
        top_n: Optional[int] = None,
        bundle_whitelist: Optional[set[str]] = None,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """执行同步。

        Returns:
            统计信息 dict
        """
        if not dry_run:
            self.api = ZhihuKbApiClient(self.config.access_secret, self.config.base_url)
        else:
            self.api = None  # type: ignore

        self.state = StateManager(self.config.state_file)
        self.state.load()

        # 1. 获取默认知识库 ID
        kb_id = self._get_kb_id()
        if not dry_run and not kb_id:
            raise RuntimeError("无法获取默认知识库 ID，请先在知乎创建知识库")

        # 2. 扫描本地文件
        bundle_files = self.scanner.scan(
            domain_filter=domain_filter,
            top_n=top_n,
            bundle_whitelist=bundle_whitelist,
        )
        print(f"📂 扫描到 {len(bundle_files)} 个 Markdown 文件")

        # 3. 生成操作清单
        ops = self._plan_operations(bundle_files)
        upload_ops = [o for o in ops if o.action in ("upload", "update")]
        skip_ops = [o for o in ops if o.action == "skip"]
        print(f"📋 操作计划：上传/更新 {len(upload_ops)} 个，跳过 {len(skip_ops)} 个")

        if dry_run:
            self._print_dry_run(ops)
            return self._stats

        # 4. 检查额度
        assert self.api is not None
        quota = self.api.get_knowledge_quota()
        if quota:
            print(
                f"💰 knowledge 额度：剩余 {quota.remaining_quota} / {quota.total_quota} "
                f"（已用 {quota.total_used}）"
            )
            if quota.remaining_quota < len(upload_ops):
                print(
                    f"⚠️  剩余额度 ({quota.remaining_quota}) 少于待上传数量 "
                    f"({len(upload_ops)})，将只上传 {quota.remaining_quota} 个"
                )
                upload_ops = upload_ops[: quota.remaining_quota]

        # 5. 执行上传
        for i, op in enumerate(upload_ops, 1):
            self._do_upload(op, kb_id, i, len(upload_ops))

        # 6. 保存状态
        self.state.save()
        print(f"\n✅ 同步完成：{self._stats}")

        # 清理
        if self.api:
            self.api.close()
        self.transformer.cleanup()

        return self._stats

    def _get_kb_id(self) -> Optional[str]:
        """获取目标知识库 ID。"""
        if self.config.default_kb_id:
            return self.config.default_kb_id

        # 检查状态文件中是否有记录
        cached = self.state.get_default_kb_id() if self.state else None
        if cached:
            return cached

        if self.api:
            kb_id = self.api.get_default_kb_id()
            if kb_id and self.state:
                self.state.set_default_kb_id(kb_id)
            return kb_id

        return None

    def _plan_operations(self, files: list[BundleFile]) -> list[SyncOperation]:
        """根据本地文件和状态记录生成操作清单。"""
        ops: list[SyncOperation] = []
        assert self.state is not None

        for bf in files:
            current_hash = StateManager.compute_file_hash(bf.abs_path)
            stored = self.state.get(bf.rel_path)

            if stored is None:
                ops.append(
                    SyncOperation(action="upload", bundle_file=bf, reason="新文件")
                )
            elif stored.content_hash != current_hash:
                ops.append(
                    SyncOperation(
                        action="update",
                        bundle_file=bf,
                        reason=f"哈希变化（{stored.content_hash[:8]} → {current_hash[:8]}）",
                    )
                )
            else:
                ops.append(
                    SyncOperation(action="skip", bundle_file=bf, reason="未变化")
                )
                self._stats["skipped"] += 1

        return ops

    def _do_upload(
        self, op: SyncOperation, kb_id: str, index: int, total: int
    ) -> None:
        """执行单个文件上传。"""
        assert self.api is not None
        assert self.state is not None

        bf = op.bundle_file
        remote_title = generate_remote_title(bf)

        print(f"  [{index}/{total}] {op.action.upper():6s} {bf.rel_path}")
        if op.reason:
            print(f"         原因：{op.reason}")

        try:
            # 转换文件
            transformed_path = self.transformer.transform(bf)
            content_hash = StateManager.compute_file_hash(bf.abs_path)

            # 上传
            result = self.api.upload_file(transformed_path, kb_id)

            # 更新状态
            self.state.upsert(
                local_path=bf.rel_path,
                recall_content_id=result.recall_content_id,
                content_hash=content_hash,
                knowledge_base_id=kb_id,
                remote_title=result.title,
                synced_at=int(time.time()),
                file_size=result.file_size,
            )

            self._stats["uploaded" if op.action == "upload" else "updated"] += 1
            print(f"         ✅ 成功 → {result.recall_content_id[:20]}...")

        except Exception as e:
            self._stats["failed"] += 1
            print(f"         ❌ 失败：{e}")

    def _print_dry_run(self, ops: list[SyncOperation]) -> None:
        """打印 dry-run 预览。"""
        print("\n── Dry-Run 预览 ──\n")
        for op in ops:
            icon = {"upload": "➕", "update": "🔄", "skip": "⏭️ "}.get(
                op.action, "❓"
            )
            print(f"  {icon} {op.action:6s} {op.bundle_file.rel_path}")
            if op.reason:
                print(f"         {op.reason}")

        print(f"\n总计：{len(ops)} 个文件")

    def status(self) -> dict:
        """查看当前同步状态。"""
        self.state = StateManager(self.config.state_file)
        self.state.load()
        return {
            "total_tracked": self.state.count(),
            "default_kb_id": self.state.get_default_kb_id(),
            "last_full_scan_at": self.state.state.last_full_scan_at,
        }
