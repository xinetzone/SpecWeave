"""L2 渐进式披露运行时规范加载器。

实现 L0/L1a/L1b/L2 四层规范按需加载：
  - L0: ONBOARDING.md (入口速查, <100行, <30秒读完)
  - L1a: global-core-rules.md + capability-boundaries.md (核心规则，始终加载)
  - L1b: capability-registry.md + context-routing.md + skills/ (索引文档，按需/规划阶段加载)
  - L2: commands/、protocols/、rules/ 等详细规范 (执行阶段按需加载)

核心能力：
  - 根据任务类型关键词自动路由到对应 L2 规范
  - 内存缓存 + mtime磁盘持久缓存：避免跨会话重复读取
  - L1分层：执行阶段仅加载核心规则，索引文档延迟加载
  - 详细耗时日志：记录触发时间、各步骤耗时、缓存命中率

用法：
  from lib.spec_loader import SpecLoader
  loader = SpecLoader(project_root)
  specs = loader.load_for_task("code review")
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
import time
import tomllib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from lib.atomic_write import (
    _atomic_replace_with_retry as _shared_atomic_replace,
    atomic_write_json,
)
from lib.project import resolve_project_root, resolve_agents_dir

_log = logging.getLogger("spec_loader")

CACHE_DIRNAME = ".cache"
CACHE_FILENAME = "spec-loader.json"
CACHE_PATH = f"{CACHE_DIRNAME}/{CACHE_FILENAME}"
CACHE_VERSION = 2
CACHE_MAX_ENTRIES = 200
CONFIG_FILENAME = "config/spec-loader.toml"


def _atomic_replace_with_retry(src: Path, dst: Path,
                                max_retries: int = 3,
                                interval_ms: int = 10):
    """向后兼容包装：委托到lib.atomic_write共享实现。"""
    return _shared_atomic_replace(src, dst, max_retries=max_retries, interval_ms=interval_ms)


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.WARNING
    if not _log.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        _log.addHandler(handler)
    _log.setLevel(level)
    return _log


LAYER_DESCRIPTIONS = {
    "L0": "入口速查（ONBOARDING.md）",
    "L1a": "核心规则（global-core-rules + capability-boundaries，始终加载）",
    "L1b": "索引文档（capability-registry + context-routing + skills/，按需加载）",
    "L2": "详细规范（commands/protocols/rules/workflows等按需加载）",
}


TASK_ROUTING = {
    "retrospective": {
        "keywords": ["复盘", "retrospective", "回顾", "总结经验", "项目总结", "阶段回顾", "postmortem"],
        "l2_specs": [
            "commands/retrospective.md",
            "skills/retrospective-cmd/SKILL.md",
        ],
        "description": "复盘任务",
    },
    "insight": {
        "keywords": ["洞察", "insight", "分析问题", "萃取洞察", "根因分析", "诊断", "找原因"],
        "l2_specs": [
            "commands/insight.md",
            "skills/insight-cmd/SKILL.md",
        ],
        "description": "洞察分析任务",
    },
    "first_principles": {
        "keywords": ["第一性原理", "first principles", "first-principles", "本质分析", "根因本质"],
        "l2_specs": [
            "commands/first-principles.md",
        ],
        "description": "第一性原理分析任务",
    },
    "mermaid": {
        "keywords": ["mermaid", "流程图", "时序图", "状态图", "画个图", "图表", "架构图", "思维导图"],
        "l2_specs": [
            "commands/mermaid.md",
            "skills/mermaid-cmd/SKILL.md",
        ],
        "description": "Mermaid图表任务",
    },
    "atomization": {
        "keywords": ["原子化", "拆分文件", "atomize", "拆分大文档", "文档拆分", "原子化收尾"],
        "l2_specs": [
            "commands/atomization.md",
            "skills/atomization-cmd/SKILL.md",
            "skills/atomization-finalize-cmd/SKILL.md",
        ],
        "description": "文档原子化任务",
    },
    "commit": {
        "keywords": ["提交", "commit", "原子提交", "提交代码", "保存更改", "git commit"],
        "l2_specs": [
            "commands/atomic-commit.md",
            "skills/atomic-commit-cmd/SKILL.md",
            "skills/git-commit-helper/SKILL.md",
        ],
        "description": "代码提交任务",
    },
    "export_report": {
        "keywords": ["导出报告", "export", "生成报告", "导出文档", "归档"],
        "l2_specs": [
            "commands/export-report.md",
            "skills/export-report-cmd/SKILL.md",
        ],
        "description": "报告导出任务",
    },
    "file_creation": {
        "keywords": ["创建文件", "新建文件", "file creation", "新文件"],
        "l2_specs": [
            "commands/file-creation.md",
        ],
        "description": "文件创建任务",
    },
    "home_assistant": {
        "keywords": ["智能家居", "home assistant", "ha_api", "控制设备"],
        "l2_specs": [
            "commands/home-assistant.md",
            "skills/home-assistant/SKILL.md",
        ],
        "description": "Home Assistant任务",
    },
    "adversarial_review": {
        "keywords": ["对抗性评审", "adversarial review", "对抗评审", "红队审查"],
        "l2_specs": [
            "commands/adversarial-review.md",
        ],
        "description": "对抗性评审任务",
    },
    "code_review": {
        "keywords": ["代码审查", "code review", "review", "审查代码", "CR"],
        "l2_specs": [
            "workflows/code-review.md",
            "roles/reviewer.md",
        ],
        "description": "代码审查任务",
    },
    "development": {
        "keywords": ["开发", "写代码", "实现功能", "develop", "coding", "写功能", "bug修复", "修复"],
        "l2_specs": [
            "workflows/feature-development.md",
            "roles/developer.md",
            "rules/ai-coding-guidelines.md",
        ],
        "description": "功能开发任务",
    },
    "testing": {
        "keywords": ["测试", "test", "单元测试", "运行测试", "验证"],
        "l2_specs": [
            "workflows/testing.md",
            "roles/tester.md",
        ],
        "description": "测试任务",
    },
    "link_check": {
        "keywords": ["链接检查", "断链", "链接修复", "fix links", "check links"],
        "l2_specs": [
            "skills/link-check-cmd/SKILL.md",
        ],
        "description": "链接检查任务",
    },
    "ci_check": {
        "keywords": ["CI检查", "提交前检查", "综合检查", "流水线检查", "pre-commit", "预检"],
        "l2_specs": [
            "skills/ci-check-cmd/SKILL.md",
        ],
        "description": "CI质量检查任务",
    },
    "docgen": {
        "keywords": ["更新导航", "docgen", "刷新看板", "生成文档索引", "更新README"],
        "l2_specs": [
            "skills/docgen-cmd/SKILL.md",
        ],
        "description": "文档生成任务",
    },
    "knowledge_graph": {
        "keywords": ["知识图谱", "knowledge graph", "概念关系可视化"],
        "l2_specs": [
            "skills/knowledge-graph-generator/SKILL.md",
        ],
        "description": "知识图谱任务",
    },
    "duplication_check": {
        "keywords": ["重复代码", "重复检查", "check-duplication", "提取共享库", "DRY检查"],
        "l2_specs": [
            "skills/check-duplication-cmd/SKILL.md",
        ],
        "description": "重复代码检查任务",
    },
    "pattern_extraction": {
        "keywords": ["模式沉淀", "萃取模式", "模式入库", "可复用模式", "pattern extraction"],
        "l2_specs": [
            "skills/pattern-extraction-cmd/SKILL.md",
        ],
        "description": "模式萃取任务",
    },
    "forum": {
        "keywords": ["发帖", "编辑帖子", "回复帖子", "forum", "论坛"],
        "l2_specs": [
            "skills/forum-posting/SKILL.md",
        ],
        "description": "论坛操作任务",
    },
}

STAGE_REQUIREMENTS = {
    "startup": {
        "required_layers": ["L0", "L1a"],
        "description": "会话启动阶段",
    },
    "planning": {
        "required_layers": ["L0", "L1a", "L1b"],
        "required_l2": ["context-routing.md"],
        "description": "任务规划阶段",
    },
    "execution": {
        "required_layers": ["L0", "L1a"],
        "description": "任务执行阶段（L1b索引延迟加载，L2按任务类型按需加载）",
    },
    "verification": {
        "required_layers": ["L0", "L1a"],
        "required_l2": [],
        "description": "验证阶段",
    },
}


@dataclass
class LoadedSpec:
    path: str
    layer: str
    content: str
    char_count: int
    loaded_from: str


@dataclass
class LoadResult:
    loaded_specs: list[LoadedSpec] = field(default_factory=list)
    already_loaded: set[str] = field(default_factory=set)
    missing_specs: list[str] = field(default_factory=list)
    total_chars: int = 0
    layer_summary: dict[str, int] = field(
        default_factory=lambda: {"L0": 0, "L1a": 0, "L1b": 0, "L2": 0}
    )

    @property
    def spec_count(self) -> int:
        return len(self.loaded_specs)

    @property
    def l1_count(self) -> int:
        return self.layer_summary.get("L1a", 0) + self.layer_summary.get("L1b", 0)

    def summary(self) -> str:
        lines = [
            f"规范加载结果：{self.spec_count} 个文件，{self.total_chars} 字符",
            f"  L0（入口速查）: {self.layer_summary.get('L0', 0)} 个",
            f"  L1a（核心规则）: {self.layer_summary.get('L1a', 0)} 个",
            f"  L1b（索引文档）: {self.layer_summary.get('L1b', 0)} 个",
            f"  L2（详细规范）: {self.layer_summary.get('L2', 0)} 个",
        ]
        if self.missing_specs:
            lines.append(f"  ⚠️ 未找到: {', '.join(self.missing_specs)}")
        return "\n".join(lines)


class SpecLoader:
    """L2 渐进式披露运行时规范加载器。

    四层架构：
      - L0: ONBOARDING.md（始终加载）
      - L1a: 核心规则（始终加载，执行阶段基线）
      - L1b: 索引文档（planning阶段/需要时加载）
      - L2: 具体规范（执行阶段按任务类型按需加载）

    缓存机制：
      - 内存缓存：self._loaded dict，实例生命周期内有效
      - 磁盘缓存：.agents/.cache/spec-loader.json，基于mtime失效，跨会话有效

    用法：
      >>> loader = SpecLoader()  # 自动解析项目根目录+加载磁盘缓存
      >>> result = loader.load_for_task("code review")
      >>> print(result.summary())
      >>> for spec in result.loaded_specs:
      ...     print(f"[{spec.layer}] {spec.path} ({spec.char_count} chars)")
    """

    L0_SPECS = [
        "ONBOARDING.md",
    ]

    L1A_CORE_SPECS = [
        "global-core-rules.md",
        "capability-boundaries.md",
    ]

    L1B_INDEX_SPECS = [
        "capability-registry.md",
        "context-routing.md",
        "skills/README.md",
    ]

    L1_SPECS = L1A_CORE_SPECS + L1B_INDEX_SPECS

    def __init__(self, project_root: Optional[Path | str] = None, verbose: bool = False,
                 use_disk_cache: bool = True):
        _t_init_start = time.perf_counter()
        if project_root is None:
            self.root = resolve_project_root(__file__)
        else:
            self.root = Path(project_root).resolve()
        self.agents_dir = self.root / ".agents"
        self._loaded: dict[str, LoadedSpec] = {}
        self._verbose = verbose
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_dirty = False

        self._config = self._load_config()
        self._use_disk_cache = self._config.get("_cache_enabled", True) and use_disk_cache
        self._cache_dirname = self._config.get("cache_dir_name", CACHE_DIRNAME)
        self._cache_filename = self._config.get("cache_filename", CACHE_FILENAME)
        self._cache_version = self._config.get("cache_version", CACHE_VERSION)
        self._cache_max_entries = self._config.get("cache_max_entries", CACHE_MAX_ENTRIES)
        self._mtime_precision = self._config.get("mtime_precision", 0.001)
        self._atomic_write = self._config.get("atomic_write", True)
        self._auto_save = self._config.get("auto_save_cache", True)

        self._cache_dir = self.agents_dir / self._cache_dirname
        self._cache_path = self._cache_dir / self._cache_filename
        self._disk_cache: dict[str, dict] = {}

        if self._use_disk_cache:
            self._load_disk_cache()

        _init_elapsed = (time.perf_counter() - _t_init_start) * 1000
        if verbose:
            _log.debug("SpecLoader 初始化完成 | project_root=%s | agents_dir=%s | 磁盘缓存=%d条目 | 初始化耗时=%.2fms",
                       self.root, self.agents_dir, len(self._disk_cache), _init_elapsed)

    def _load_config(self) -> dict:
        config_path = self.agents_dir / CONFIG_FILENAME
        defaults = {
            "_cache_enabled": True,
            "cache_dir_name": CACHE_DIRNAME,
            "cache_filename": CACHE_FILENAME,
            "cache_version": CACHE_VERSION,
            "cache_max_entries": CACHE_MAX_ENTRIES,
            "mtime_precision": 0.001,
            "atomic_write": True,
            "auto_save_cache": True,
            "enable_timing_breakdown": True,
        }
        if not config_path.exists():
            _log.debug("配置文件不存在，使用默认配置 | path=%s", config_path)
            return defaults
        try:
            with open(config_path, "rb") as f:
                raw = tomllib.load(f)
            cache_cfg = raw.get("cache", {})
            logging_cfg = raw.get("logging", {})
            perf_cfg = raw.get("performance", {})
            merged = dict(defaults)
            if "enabled" in cache_cfg:
                merged["_cache_enabled"] = bool(cache_cfg["enabled"])
            if "dir_name" in cache_cfg:
                merged["cache_dir_name"] = str(cache_cfg["dir_name"])
            if "filename" in cache_cfg:
                merged["cache_filename"] = str(cache_cfg["filename"])
            if "max_entries" in cache_cfg:
                merged["cache_max_entries"] = int(cache_cfg["max_entries"])
            if "version" in cache_cfg:
                merged["cache_version"] = int(cache_cfg["version"])
            if "atomic_write" in cache_cfg:
                merged["atomic_write"] = bool(cache_cfg["atomic_write"])
            if "mtime_precision" in cache_cfg:
                merged["mtime_precision"] = float(cache_cfg["mtime_precision"])
            if "enable_timing_breakdown" in logging_cfg:
                merged["enable_timing_breakdown"] = bool(logging_cfg["enable_timing_breakdown"])
            if "auto_save_cache" in perf_cfg:
                merged["auto_save_cache"] = bool(perf_cfg["auto_save_cache"])
            _log.debug("配置文件加载成功 | path=%s | cache_enabled=%s | version=%d | max_entries=%d",
                       config_path, merged["_cache_enabled"], merged["cache_version"], merged["cache_max_entries"])
            return merged
        except (tomllib.TOMLDecodeError, OSError, KeyError, ValueError) as e:
            _log.warning("配置文件加载失败，使用默认配置 | path=%s | error=%s", config_path, e)
            return defaults

    def _cache_key(self, rel_path: str) -> str:
        return hashlib.sha1(rel_path.encode("utf-8")).hexdigest()[:16]

    def _resolve_path(self, rel_path: str) -> Optional[Path]:
        full_path = self.agents_dir / rel_path
        if full_path.exists():
            return full_path
        root_path = self.root / rel_path
        if root_path.exists():
            return root_path
        return None

    def _get_mtime(self, path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    def _load_disk_cache(self):
        _t_cache_start = time.perf_counter()
        try:
            if not self._cache_path.exists():
                _log.debug("磁盘缓存不存在 | path=%s", self._cache_path)
                return
            with open(self._cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("version") != self._cache_version:
                _log.debug("磁盘缓存版本不匹配 | expected=%d | got=%s | 将重新创建",
                           self._cache_version, data.get("version"))
                return
            entries = data.get("entries", {})
            valid_count = 0
            for key, entry in entries.items():
                rel_path = entry.get("path", "")
                full_path = self._resolve_path(rel_path)
                if not full_path:
                    continue
                cached_mtime = entry.get("mtime", 0)
                actual_mtime = self._get_mtime(full_path)
                if abs(cached_mtime - actual_mtime) < self._mtime_precision:
                    self._disk_cache[key] = entry
                    valid_count += 1
            _cache_elapsed = (time.perf_counter() - _t_cache_start) * 1000
            _log.debug("磁盘缓存加载完成 | 有效条目=%d/%d | 耗时=%.2fms",
                       valid_count, len(entries), _cache_elapsed)
        except (json.JSONDecodeError, OSError, KeyError) as e:
            _log.warning("磁盘缓存加载失败 | error=%s | 将在下次保存时重建", e)
            self._disk_cache = {}

    def _save_disk_cache(self):
        _t_save_start = time.perf_counter()
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            entries = {}
            for key, entry in self._disk_cache.items():
                entries[key] = entry
            for rel_path, spec in self._loaded.items():
                key = self._cache_key(rel_path)
                full_path = self._resolve_path(rel_path)
                mtime = self._get_mtime(full_path) if full_path else 0
                entries[key] = {
                    "path": rel_path,
                    "layer": spec.layer,
                    "content": spec.content,
                    "char_count": spec.char_count,
                    "mtime": mtime,
                    "cached_at": time.time(),
                }
            if len(entries) > self._cache_max_entries:
                sorted_entries = sorted(
                    entries.items(),
                    key=lambda x: x[1].get("cached_at", 0),
                    reverse=True,
                )[:self._cache_max_entries]
                entries = dict(sorted_entries)
            data = {
                "version": self._cache_version,
                "saved_at": time.time(),
                "project_root": str(self.root),
                "entries": entries,
            }
            _t_write_start = time.perf_counter()
            if self._atomic_write:
                atomic_write_json(self._cache_path, data, ensure_ascii=False, indent=None)
            else:
                with open(self._cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            _t_write_ms = (time.perf_counter() - _t_write_start) * 1000
            self._cache_dirty = False
            _save_elapsed = (time.perf_counter() - _t_save_start) * 1000
            _log.debug("磁盘缓存保存完成 | 条目=%d | write=%.2fms | 总耗时=%.2fms | path=%s",
                       len(entries), _t_write_ms, _save_elapsed, self._cache_path)
        except OSError as e:
            _log.warning("磁盘缓存保存失败 | error=%s", e)

    def _read_spec(self, rel_path: str, layer: str, loaded_from: str) -> Optional[LoadedSpec]:
        _t_read_start = time.perf_counter()
        _t_resolve_start = time.perf_counter()
        full_path = self._resolve_path(rel_path)
        _t_resolve_ms = (time.perf_counter() - _t_resolve_start) * 1000
        if full_path is None:
            _log.warning("规范文件未找到 | layer=%s | path=%s (从 %s 加载请求) | resolve=%.2fms",
                         layer, rel_path, loaded_from, _t_resolve_ms)
            return None
        if str(full_path).startswith(str(self.root)) and ".agents" not in str(full_path.relative_to(self.root)).split(os.sep)[0:1]:
            path_source = "root/"
        else:
            path_source = ".agents/"

        _t_memcheck_start = time.perf_counter()
        if rel_path in self._loaded:
            cached = self._loaded[rel_path]
            _t_total_ms = (time.perf_counter() - _t_read_start) * 1000
            _t_memcheck_ms = (time.perf_counter() - _t_memcheck_start) * 1000
            _log.debug("内存缓存命中 | layer=%s | path=%s%s | chars=%d | 来源=%s | "
                       "resolve=%.2fms | memcheck=%.2fms | 总耗时=%.3fms",
                       layer, path_source, rel_path, cached.char_count, loaded_from,
                       _t_resolve_ms, _t_memcheck_ms, _t_total_ms)
            return cached
        _t_memcheck_ms = (time.perf_counter() - _t_memcheck_start) * 1000

        _t_cache_lookup_start = time.perf_counter()
        cache_key = self._cache_key(rel_path)
        disk_hit = False
        cache_stale = False
        if cache_key in self._disk_cache:
            _t_cache_lookup_ms = (time.perf_counter() - _t_cache_lookup_start) * 1000
            entry = self._disk_cache[cache_key]
            cached_mtime = entry.get("mtime", 0)
            _t_mtime_start = time.perf_counter()
            actual_mtime = self._get_mtime(full_path)
            _t_mtime_ms = (time.perf_counter() - _t_mtime_start) * 1000
            if abs(cached_mtime - actual_mtime) < self._mtime_precision:
                _t_construct_start = time.perf_counter()
                spec = LoadedSpec(
                    path=rel_path,
                    layer=entry.get("layer", layer),
                    content=entry["content"],
                    char_count=entry["char_count"],
                    loaded_from=f"{loaded_from}+disk-cache",
                )
                self._loaded[rel_path] = spec
                self._cache_hits += 1
                _t_construct_ms = (time.perf_counter() - _t_construct_start) * 1000
                _t_total_ms = (time.perf_counter() - _t_read_start) * 1000
                disk_hit = True
                _log.info("磁盘缓存命中(HIT) | layer=%s | path=%s%s | chars=%d | 来源=%s | "
                          "resolve=%.2fms | memcheck=%.2fms | lookup=%.2fms | mtime-stat=%.2fms | "
                          "construct=%.2fms | 总耗时=%.3fms",
                          layer, path_source, rel_path, spec.char_count, loaded_from,
                          _t_resolve_ms, _t_memcheck_ms, _t_cache_lookup_ms, _t_mtime_ms,
                          _t_construct_ms, _t_total_ms)
                return spec
            else:
                cache_stale = True
                _log.debug("磁盘缓存过期(STALE) | layer=%s | path=%s | cached_mtime=%.3f | actual_mtime=%.3f | "
                           "mtime-stat=%.2fms",
                           layer, rel_path, cached_mtime, actual_mtime, _t_mtime_ms)
        else:
            _t_cache_lookup_ms = (time.perf_counter() - _t_cache_lookup_start) * 1000

        self._cache_misses += 1
        _t_io_start = time.perf_counter()
        content = full_path.read_text(encoding="utf-8")
        _t_io_ms = (time.perf_counter() - _t_io_start) * 1000
        _t_construct_start = time.perf_counter()
        spec = LoadedSpec(
            path=rel_path,
            layer=layer,
            content=content,
            char_count=len(content),
            loaded_from=loaded_from,
        )
        self._loaded[rel_path] = spec
        _t_cache_write_start = time.perf_counter()
        _t_get_mtime_for_write_start = time.perf_counter()
        write_mtime = self._get_mtime(full_path)
        _t_get_mtime_for_write_ms = (time.perf_counter() - _t_get_mtime_for_write_start) * 1000
        self._disk_cache[cache_key] = {
            "path": rel_path,
            "layer": layer,
            "content": content,
            "char_count": spec.char_count,
            "mtime": write_mtime,
            "cached_at": time.time(),
        }
        self._cache_dirty = True
        _t_cache_write_ms = (time.perf_counter() - _t_cache_write_start) * 1000
        _t_construct_ms = (time.perf_counter() - _t_construct_start) * 1000
        _t_total_ms = (time.perf_counter() - _t_read_start) * 1000
        miss_reason = "stale" if cache_stale else "missing"
        _log.info("磁盘缓存未命中(MISS:%s) | layer=%s | path=%s%s | chars=%d | 来源=%s | "
                  "resolve=%.2fms | memcheck=%.2fms | lookup=%.2fms | read-io=%.2fms | "
                  "construct+write=%.2fms(mtime-stat=%.2fms) | 总耗时=%.3fms",
                  miss_reason, layer, path_source, rel_path, spec.char_count, loaded_from,
                  _t_resolve_ms, _t_memcheck_ms, _t_cache_lookup_ms, _t_io_ms,
                  _t_construct_ms, _t_get_mtime_for_write_ms, _t_total_ms)
        return spec

    def load_layer(self, layer: str, force: bool = False) -> LoadResult:
        _t_layer_start = time.perf_counter()
        result = LoadResult()

        if layer == "L0":
            specs_to_load = self.L0_SPECS
            summary_key = "L0"
        elif layer == "L1a":
            specs_to_load = self.L1A_CORE_SPECS
            summary_key = "L1a"
        elif layer == "L1b":
            specs_to_load = self.L1B_INDEX_SPECS
            summary_key = "L1b"
        elif layer == "L1":
            specs_to_load = self.L1_SPECS
            summary_key = "_L1"
        else:
            _log.error("不支持的层: %s", layer)
            return result

        _log.info("开始加载层 | layer=%s | 文件数=%d | force=%s", layer, len(specs_to_load), force)

        for rel_path in specs_to_load:
            if not force and rel_path in self._loaded:
                result.already_loaded.add(rel_path)
                _log.debug("跳过已加载 | layer=%s | path=%s", layer, rel_path)
                continue
            target_layer = layer
            if layer == "L1":
                if rel_path in self.L1A_CORE_SPECS:
                    target_layer = "L1a"
                else:
                    target_layer = "L1b"
            spec = self._read_spec(rel_path, target_layer, f"layer:{layer}")
            if spec:
                result.loaded_specs.append(spec)
                result.total_chars += spec.char_count
                result.layer_summary[target_layer] += 1
            else:
                result.missing_specs.append(rel_path)

        _layer_elapsed = (time.perf_counter() - _t_layer_start) * 1000
        _log.info("层加载完成 | layer=%s | 新加载=%d | 已缓存=%d | 缺失=%d | 累计字符=%d | 层耗时=%.2fms",
                  layer, len(result.loaded_specs), len(result.already_loaded),
                  len(result.missing_specs), result.total_chars, _layer_elapsed)

        if self._auto_save and self._use_disk_cache and self._cache_dirty and result.loaded_specs:
            self._save_disk_cache()

        return result

    def ensure_l1b(self) -> LoadResult:
        if all(p in self._loaded for p in self.L1B_INDEX_SPECS):
            result = LoadResult()
            for p in self.L1B_INDEX_SPECS:
                result.already_loaded.add(p)
            return result
        return self.load_layer("L1b")

    def match_task_type(self, task_description: str) -> list[str]:
        _t_match_start = time.perf_counter()
        task_lower = task_description.lower()
        matched = []
        match_details = []
        for task_type, config in TASK_ROUTING.items():
            for kw in config["keywords"]:
                if kw.lower() in task_lower:
                    matched.append(task_type)
                    match_details.append((task_type, kw))
                    break
        _match_elapsed = (time.perf_counter() - _t_match_start) * 1000
        if match_details:
            _log.info("任务类型匹配成功 | 输入=\"%s\" | 匹配=%s (关键词: %s) | 路由数=%d | 耗时=%.2fms",
                      task_description[:60],
                      [m[0] for m in match_details],
                      [m[1] for m in match_details],
                      len(TASK_ROUTING), _match_elapsed)
        else:
            _log.warning("任务类型无匹配 | 输入=\"%s\" | 路由数=%d | 耗时=%.2fms | 将仅加载L0+L1a层",
                         task_description[:60], len(TASK_ROUTING), _match_elapsed)
        return matched

    def load_for_task(
        self,
        task_description: str,
        stage: str = "execution",
        include_l1b: Optional[bool] = None,
        max_chars: Optional[int] = None,
    ) -> LoadResult:
        _t_total_start = time.perf_counter()
        _trigger_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        _log.info("===== 开始任务加载 =====")
        _log.info("触发时间: %s | 任务描述: \"%s\" | 阶段=%s | max_chars=%s",
                  _trigger_ts, task_description[:80], stage, max_chars)

        if include_l1b is None:
            include_l1b = stage in ("planning", "startup")

        result = LoadResult()
        _step_times = {}

        _t_step = time.perf_counter()
        _log.debug("步骤1/5: 加载 L0 层（入口速查）")
        l0_result = self.load_layer("L0")
        self._merge_result(result, l0_result, "L0")
        _step_times["L0加载"] = (time.perf_counter() - _t_step) * 1000
        _log.debug("[TIMER] 步骤1/5 L0加载完成 | 耗时=%.2fms | 文件=%d个 | 字符=%d",
                   _step_times["L0加载"], l0_result.layer_summary.get("L0", 0), l0_result.total_chars)

        _t_step = time.perf_counter()
        _log.debug("步骤2/5: 加载 L1a 层（核心规则，始终加载）")
        l1a_result = self.load_layer("L1a")
        self._merge_result(result, l1a_result, "L1a")
        _step_times["L1a加载"] = (time.perf_counter() - _t_step) * 1000
        _log.debug("[TIMER] 步骤2/5 L1a加载完成 | 耗时=%.2fms | 文件=%d个 | 字符=%d",
                   _step_times["L1a加载"], l1a_result.layer_summary.get("L1a", 0), l1a_result.total_chars)

        _t_step = time.perf_counter()
        _l1b_result = None
        if include_l1b:
            _log.debug("步骤3/5: 加载 L1b 层（索引文档，按需）")
            _l1b_result = self.load_layer("L1b")
            self._merge_result(result, _l1b_result, "L1b")
            _step_times["L1b加载"] = (time.perf_counter() - _t_step) * 1000
            _log.debug("[TIMER] 步骤3/5 L1b加载完成 | 耗时=%.2fms | 文件=%d个 | 字符=%d",
                       _step_times["L1b加载"], _l1b_result.layer_summary.get("L1b", 0), _l1b_result.total_chars)
        else:
            _log.debug("步骤3/5: 跳过 L1b 层（执行阶段延迟加载）")
            _step_times["L1b加载"] = 0.0

        _t_step = time.perf_counter()
        _log.debug("步骤4/5: 匹配任务类型")
        matched_types = self.match_task_type(task_description)
        l2_specs = []
        for task_type in matched_types:
            config = TASK_ROUTING[task_type]
            for spec_path in config["l2_specs"]:
                if spec_path not in l2_specs:
                    l2_specs.append(spec_path)
        _step_times["类型匹配"] = (time.perf_counter() - _t_step) * 1000
        _log.info("L2 待加载清单 | 数量=%d | 文件=%s", len(l2_specs), l2_specs)
        _log.debug("[TIMER] 步骤4/5 任务类型匹配完成 | 耗时=%.2fms | 匹配类型=%s | L2文件数=%d",
                   _step_times["类型匹配"], matched_types, len(l2_specs))

        _t_step = time.perf_counter()
        _log.debug("步骤5/5: 加载 L2 层（按需规范）")
        skipped_due_to_limit = 0
        _l2_chars_before = result.total_chars
        for rel_path in l2_specs:
            if rel_path in self._loaded:
                result.already_loaded.add(rel_path)
                _log.debug("L2 缓存命中 | path=%s", rel_path)
                continue
            if max_chars and result.total_chars >= max_chars:
                _log.warning("达到字符上限，停止加载 | max_chars=%d | 当前=%d | 跳过=%s",
                             max_chars, result.total_chars, rel_path)
                skipped_due_to_limit += 1
                break
            spec = self._read_spec(rel_path, "L2", f"task:{task_description[:30]}")
            if spec:
                result.loaded_specs.append(spec)
                result.total_chars += spec.char_count
                result.layer_summary["L2"] += 1
            else:
                result.missing_specs.append(rel_path)
        _l2_chars_added = result.total_chars - _l2_chars_before
        _step_times["L2加载"] = (time.perf_counter() - _t_step) * 1000
        _log.debug("[TIMER] 步骤5/5 L2按需加载完成 | 耗时=%.2fms | 文件=%d个 | 新增字符=%d | 限载跳过=%d",
                   _step_times["L2加载"], result.layer_summary.get("L2", 0), _l2_chars_added, skipped_due_to_limit)

        _total_elapsed = (time.perf_counter() - _t_total_start) * 1000
        _log.info("===== 任务加载完成 =====")
        _log.info("汇总: L0=%d | L1a=%d | L1b=%d | L2=%d | 总文件=%d | 总字符=%d | 缓存命中(磁盘)=%d | 缓存未命中=%d | 缺失=%d | 限载跳过=%d",
                  result.layer_summary.get("L0", 0), result.layer_summary.get("L1a", 0),
                  result.layer_summary.get("L1b", 0), result.layer_summary.get("L2", 0),
                  result.spec_count, result.total_chars,
                  self._cache_hits, self._cache_misses,
                  len(result.missing_specs), skipped_due_to_limit)
        _log.info("[TIMER] 性能统计 | 触发时间=%s | 总耗时=%.2fms | L0=%.2fms | L1a=%.2fms | L1b=%.2fms | 匹配=%.2fms | L2=%.2fms",
                  _trigger_ts, _total_elapsed,
                  _step_times.get("L0加载", 0), _step_times.get("L1a加载", 0),
                  _step_times.get("L1b加载", 0),
                  _step_times.get("类型匹配", 0), _step_times.get("L2加载", 0))

        if self._auto_save and self._use_disk_cache and self._cache_dirty:
            self._save_disk_cache()

        return result

    def _merge_result(self, target: LoadResult, source: LoadResult, layer_key: str):
        target.loaded_specs.extend(source.loaded_specs)
        target.total_chars += source.total_chars
        for k, v in source.layer_summary.items():
            if k in target.layer_summary:
                target.layer_summary[k] += v
            else:
                target.layer_summary[k] = v
        target.missing_specs.extend(source.missing_specs)
        target.already_loaded.update(source.already_loaded)

    def load_specific(self, rel_paths: list[str], layer: str = "L2") -> LoadResult:
        result = LoadResult()
        for rel_path in rel_paths:
            if rel_path in self._loaded:
                result.already_loaded.add(rel_path)
                continue
            spec = self._read_spec(rel_path, layer, "explicit")
            if spec:
                result.loaded_specs.append(spec)
                result.total_chars += spec.char_count
                result.layer_summary[layer] = result.layer_summary.get(layer, 0) + 1
            else:
                result.missing_specs.append(rel_path)
        return result

    def save_cache(self):
        self._save_disk_cache()

    def get_cache_stats(self) -> dict:
        total = self._cache_hits + self._cache_misses
        return {
            "memory_loaded": len(self._loaded),
            "disk_entries": len(self._disk_cache),
            "disk_cache_hits": self._cache_hits,
            "disk_cache_misses": self._cache_misses,
            "hit_rate": (
                self._cache_hits / total * 100
                if total > 0
                else 0.0
            ),
            "config": {
                "cache_enabled": self._use_disk_cache,
                "cache_version": self._cache_version,
                "max_entries": self._cache_max_entries,
                "mtime_precision": self._mtime_precision,
                "atomic_write": self._atomic_write,
                "auto_save": self._auto_save,
                "cache_path": str(self._cache_path),
            },
        }

    def get_loaded_paths(self) -> set[str]:
        return set(self._loaded.keys())

    def format_for_prompt(self, result: LoadResult, include_content: bool = False) -> str:
        lines = ["## 已加载规范（渐进式披露）", ""]
        lines.append(result.summary())
        lines.append("")

        if include_content:
            for spec in result.loaded_specs:
                lines.append(f"### [{spec.layer}] {spec.path}")
                lines.append("")
                lines.append(spec.content)
                lines.append("")
        else:
            lines.append("### 规范文件清单")
            lines.append("")
            for spec in result.loaded_specs:
                lines.append(f"- [{spec.layer}] `{spec.path}` ({spec.char_count} 字符)")

        return "\n".join(lines)

    def invalidate_cache(self):
        self._disk_cache = {}
        self._loaded = {}
        self._cache_dirty = False
        self._cache_hits = 0
        self._cache_misses = 0
        try:
            if self._cache_path.exists():
                self._cache_path.unlink()
                _log.info("磁盘缓存已清除 | path=%s", self._cache_path)
        except OSError as e:
            _log.warning("清除磁盘缓存失败 | error=%s", e)


def quick_load(task: str, project_root: Optional[Path | str] = None, **kwargs) -> LoadResult:
    loader = SpecLoader(project_root)
    result = loader.load_for_task(task, **kwargs)
    if not loader._auto_save:
        loader.save_cache()
    return result
