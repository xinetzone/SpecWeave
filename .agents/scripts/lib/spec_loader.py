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
  - L0/L1a 批量读取：预分类缓存命中状态，减少逐文件固定开销
  - 详细耗时日志：记录触发时间、各步骤耗时、缓存命中率、批量分类/IO分阶段统计

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

from lib.atomic_write import atomic_write_bytes
from lib.project import resolve_project_root, resolve_agents_dir

_log = logging.getLogger("spec_loader")

CACHE_DIRNAME = ".cache"
CACHE_FILENAME = "spec-loader.json"
CACHE_PATH = f"{CACHE_DIRNAME}/{CACHE_FILENAME}"
CACHE_VERSION = 2
CACHE_MAX_ENTRIES = 200
CONFIG_FILENAME = "config/spec-loader.toml"


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

L2_PRIORITY_ORDER = [
    "commands/",
    "skills/",
    "protocols/",
    "workflows/",
    "roles/",
    "rules/",
]

FALLBACK_L2_SPECS = [
    "rules/ai-coding-guidelines.md",
]


def _l2_priority_key(rel_path: str) -> tuple:
    for idx, prefix in enumerate(L2_PRIORITY_ORDER):
        if rel_path.startswith(prefix):
            return (idx, rel_path)
    return (len(L2_PRIORITY_ORDER), rel_path)


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
            "rules/ai-coding-guidelines.md",
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
            "rules/ai-coding-guidelines.md",
        ],
        "description": "对抗性评审任务",
    },
    "first_principles": {
        "keywords": ["第一性原理", "first principles", "根本原因", "本质思考", "底层原理"],
        "l2_specs": [
            "commands/first-principles.md",
        ],
        "description": "第一性原理分析任务",
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
    "extraction": {
        "keywords": ["萃取", "extraction", "萃取模式", "模式入库", "沉淀为模式", "生成模式文档"],
        "l2_specs": [
            "commands/extraction.md",
            "skills/extraction-cmd/SKILL.md",
        ],
        "description": "模式萃取任务",
    },
    "knowledge_sedimentation": {
        "keywords": ["知识沉淀", "沉淀知识", "总结方法论", "生成Wiki", "知识库建设", "最佳实践库"],
        "l2_specs": [
            "commands/knowledge-sedimentation.md",
        ],
        "description": "知识沉淀任务",
    },
    "seven_concepts": {
        "keywords": ["七概念", "方法论编排", "R-I-E-C-A-F-V", "元编排", "概念组合", "seven concepts"],
        "l2_specs": [
            "commands/seven-concepts.md",
            "skills/seven-concepts-cmd/SKILL.md",
        ],
        "description": "七概念方法论编排任务",
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
    matched_types: list[str] = field(default_factory=list)
    primary_type: Optional[str] = None
    pending_l2: list[str] = field(default_factory=list)
    lightweight: bool = False

    @property
    def spec_count(self) -> int:
        return len(self.loaded_specs)

    @property
    def l1_count(self) -> int:
        return self.layer_summary.get("L1a", 0) + self.layer_summary.get("L1b", 0)

    def summary(self) -> str:
        mode = "（轻量模式·L2待加载）" if self.lightweight else ""
        lines = [
            f"规范加载结果{mode}：{self.spec_count} 个文件，{self.total_chars} 字符",
            f"  L0（入口速查）: {self.layer_summary.get('L0', 0)} 个",
            f"  L1a（核心规则）: {self.layer_summary.get('L1a', 0)} 个",
            f"  L1b（索引文档）: {self.layer_summary.get('L1b', 0)} 个",
            f"  L2（详细规范）: {self.layer_summary.get('L2', 0)} 个",
        ]
        if self.primary_type:
            lines.append(f"  主任务类型: {self.primary_type}")
        if self.matched_types and len(self.matched_types) > 1:
            aux = [t for t in self.matched_types if t != self.primary_type]
            lines.append(f"  辅助类型(跳过roles): {', '.join(aux)}")
        if self.pending_l2:
            lines.append(f"  📋 待加载L2清单: {len(self.pending_l2)} 个文件（轻量模式）")
            for p in self.pending_l2[:5]:
                lines.append(f"    - {p}")
            if len(self.pending_l2) > 5:
                lines.append(f"    ... 还有 {len(self.pending_l2) - 5} 个")
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
        self._last_match_weighted: list[tuple] = []

        if verbose:
            _log.setLevel(logging.DEBUG)
            if not _log.handlers and not logging.getLogger().handlers:
                setup_logging(verbose=True)

        _t_config_start = time.perf_counter()
        self._config = self._load_config()
        _t_config_ms = (time.perf_counter() - _t_config_start) * 1000
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

        _t_disk_load_ms = 0.0
        if self._use_disk_cache:
            _t_disk_start = time.perf_counter()
            self._load_disk_cache()
            _t_disk_load_ms = (time.perf_counter() - _t_disk_start) * 1000

        _init_elapsed = (time.perf_counter() - _t_init_start) * 1000
        _log.debug("SpecLoader 初始化完成 | project_root=%s | agents_dir=%s | "
                   "磁盘缓存=%d条目 | config=%.2fms | disk-load=%.2fms | 总耗时=%.2fms",
                   self.root, self.agents_dir, len(self._disk_cache),
                   _t_config_ms, _t_disk_load_ms, _init_elapsed)

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

            _t_build_start = time.perf_counter()
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
            _t_build_ms = (time.perf_counter() - _t_build_start) * 1000

            _t_evict_start = time.perf_counter()
            evicted = 0
            if len(entries) > self._cache_max_entries:
                sorted_entries = sorted(
                    entries.items(),
                    key=lambda x: x[1].get("cached_at", 0),
                    reverse=True,
                )[:self._cache_max_entries]
                evicted = len(entries) - len(sorted_entries)
                entries = dict(sorted_entries)
            _t_evict_ms = (time.perf_counter() - _t_evict_start) * 1000

            _t_serialize_start = time.perf_counter()
            data = {
                "version": self._cache_version,
                "saved_at": time.time(),
                "project_root": str(self.root),
                "entries": entries,
            }
            serialized = json.dumps(data, ensure_ascii=False).encode("utf-8")
            _t_serialize_ms = (time.perf_counter() - _t_serialize_start) * 1000

            _t_write_start = time.perf_counter()
            if self._atomic_write:
                atomic_write_bytes(self._cache_path, serialized)
            else:
                with open(self._cache_path, "wb") as f:
                    f.write(serialized)
            _t_write_ms = (time.perf_counter() - _t_write_start) * 1000
            self._cache_dirty = False
            _save_elapsed = (time.perf_counter() - _t_save_start) * 1000
            _log.debug("磁盘缓存保存完成 | 条目=%d(evict=%d) | build=%.2fms | evict=%.2fms | "
                       "serialize=%d bytes/%.2fms | atomic-write=%.2fms | 总耗时=%.2fms | path=%s",
                       len(entries), evicted, _t_build_ms, _t_evict_ms,
                       len(serialized), _t_serialize_ms, _t_write_ms, _save_elapsed, self._cache_path.name)
        except OSError as e:
            _log.warning("磁盘缓存保存失败 | error=%s | elapsed=%.2fms", e,
                         (time.perf_counter() - _t_save_start) * 1000)

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

    def _read_specs_batch(
        self,
        rel_paths: list[str],
        layer: str,
        loaded_from: str,
    ) -> tuple[list[LoadedSpec], list[str], list[str]]:
        _t_batch_start = time.perf_counter()
        _log.debug("===== 批量读取开始 | layer=%s | 文件数=%d | loaded_from=%s =====",
                   layer, len(rel_paths), loaded_from)

        loaded: list[LoadedSpec] = []
        mem_hits: list[str] = []
        missing: list[str] = []
        disk_hits: list[tuple[str, int]] = []
        disk_stale: list[str] = []
        disk_misses: list[str] = []
        need_io: list[str] = []

        _t_classify_start = time.perf_counter()
        for rel_path in rel_paths:
            _t_item_start = time.perf_counter()

            if rel_path in self._loaded:
                mem_hits.append(rel_path)
                _t_item_ms = (time.perf_counter() - _t_item_start) * 1000
                _log.debug("  [MEM-HIT]  path=%s | 耗时=%.3fms", rel_path, _t_item_ms)
                continue

            full_path = self._resolve_path(rel_path)
            if full_path is None:
                missing.append(rel_path)
                _log.warning("  [MISSING]  path=%s | resolve失败 | 耗时=%.3fms",
                             rel_path, (time.perf_counter() - _t_item_start) * 1000)
                continue

            cache_key = self._cache_key(rel_path)
            if cache_key in self._disk_cache:
                entry = self._disk_cache[cache_key]
                actual_mtime = self._get_mtime(full_path)
                cached_mtime = entry.get("mtime", 0)
                if abs(cached_mtime - actual_mtime) < self._mtime_precision:
                    _t_construct_start = time.perf_counter()
                    spec = LoadedSpec(
                        path=rel_path,
                        layer=entry.get("layer", layer),
                        content=entry["content"],
                        char_count=entry["char_count"],
                        loaded_from=f"{loaded_from}+disk-cache(batch)",
                    )
                    self._loaded[rel_path] = spec
                    self._cache_hits += 1
                    loaded.append(spec)
                    disk_hits.append((rel_path, spec.char_count))
                    _t_construct_ms = (time.perf_counter() - _t_construct_start) * 1000
                    _t_item_ms = (time.perf_counter() - _t_item_start) * 1000
                    _log.debug("  [DISK-HIT] path=%s | chars=%d | construct=%.3fms | 总耗时=%.3fms",
                               rel_path, spec.char_count, _t_construct_ms, _t_item_ms)
                    continue
                else:
                    disk_stale.append(rel_path)
                    _log.debug("  [STALE]    path=%s | cached_mtime=%.3f | actual_mtime=%.3f | 需要重新IO",
                               rel_path, cached_mtime, actual_mtime)
                    need_io.append(rel_path)
            else:
                disk_misses.append(rel_path)
                _log.debug("  [DISK-MISS] path=%s | 无磁盘缓存 | 需要IO", rel_path)
                need_io.append(rel_path)

        _t_classify_ms = (time.perf_counter() - _t_classify_start) * 1000

        _log.debug("----- 批量分类完成 | layer=%s | 分类耗时=%.2fms -----", layer, _t_classify_ms)
        _log.debug("  MEM-HIT:  %d 个 %s", len(mem_hits), mem_hits)
        _log.debug("  DISK-HIT: %d 个 %s", len(disk_hits), [f"{p}({c}c)" for p, c in disk_hits])
        _log.debug("  STALE:    %d 个 %s", len(disk_stale), disk_stale)
        _log.debug("  MISS:     %d 个 %s", len(disk_misses), disk_misses)
        _log.debug("  MISSING:  %d 个 %s", len(missing), missing)
        _log.debug("  需IO:     %d 个 %s", len(need_io), need_io)

        _t_io_start = time.perf_counter()
        io_hits = 0
        io_misses = 0
        io_chars = 0
        for rel_path in need_io:
            _t_io_item_start = time.perf_counter()
            spec = self._read_spec(rel_path, layer, f"{loaded_from}+batch-io")
            _t_io_item_ms = (time.perf_counter() - _t_io_item_start) * 1000
            if spec:
                loaded.append(spec)
                io_hits += 1
                io_chars += spec.char_count
                _log.debug("  [IO-OK]    path=%s | chars=%d | _read_spec耗时=%.2fms",
                           rel_path, spec.char_count, _t_io_item_ms)
            else:
                io_misses += 1
                missing.append(rel_path)
                _log.warning("  [IO-FAIL]  path=%s | _read_spec返回None | 耗时=%.2fms",
                             rel_path, _t_io_item_ms)
        _t_io_ms = (time.perf_counter() - _t_io_start) * 1000

        _t_batch_ms = (time.perf_counter() - _t_batch_start) * 1000

        total_loaded = len(loaded)
        total_chars = sum(s.char_count for s in loaded)
        mem_hit_chars = sum(self._loaded[p].char_count for p in mem_hits if p in self._loaded)
        disk_hit_chars = sum(c for _, c in disk_hits)

        _log.debug("===== 批量读取完成 | layer=%s =====", layer)
        _log.debug("  结果汇总: 总请求=%d | 新加载=%d(%d字符) | 内存命中=%d(%d字符) | "
                   "磁盘命中=%d(%d字符) | IO读取=%d(%d字符) | IO失败=%d | 缺失=%d",
                   len(rel_paths), total_loaded, total_chars,
                   len(mem_hits), mem_hit_chars,
                   len(disk_hits), disk_hit_chars,
                   io_hits, io_chars, io_misses, len(missing))
        _log.debug("  阶段耗时: 分类=%.2fms | IO=%.2fms | 总耗时=%.2fms",
                   _t_classify_ms, _t_io_ms, _t_batch_ms)
        if len(need_io) > 0:
            _log.debug("  IO平均:   %.2fms/文件 (共%d个)",
                       _t_io_ms / len(need_io) if need_io else 0, len(need_io))
        _log.debug("  效率:      快速路径(内存+磁盘命中)=%d/%d (%.0f%%) | 需IO=%d/%d (%.0f%%)",
                   len(mem_hits) + len(disk_hits), len(rel_paths),
                   (len(mem_hits) + len(disk_hits)) / len(rel_paths) * 100 if rel_paths else 0,
                   len(need_io), len(rel_paths),
                   len(need_io) / len(rel_paths) * 100 if rel_paths else 0)

        return loaded, mem_hits, missing

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

        if layer in ("L0", "L1a") and not force:
            batch_loaded, batch_mem_hits, batch_missing = self._read_specs_batch(
                list(specs_to_load), layer, f"layer:{layer}"
            )
            for spec in batch_loaded:
                result.loaded_specs.append(spec)
                result.total_chars += spec.char_count
                result.layer_summary[layer] += 1
            for p in batch_mem_hits:
                result.already_loaded.add(p)
            for p in batch_missing:
                result.missing_specs.append(p)
        else:
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
            _t_layer_save = time.perf_counter()
            self._save_disk_cache()
            _log.debug("层加载后自动保存缓存 | layer=%s | save耗时=%.2fms",
                       layer, (time.perf_counter() - _t_layer_save) * 1000)

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
        task_len = len(task_lower)
        matched = []
        match_details = []
        weighted = []
        _scan_start = time.perf_counter()
        _total_keywords = 0
        for task_type, config in TASK_ROUTING.items():
            _type_kw_start = time.perf_counter()
            _type_hit = False
            for kw in config["keywords"]:
                _total_keywords += 1
                kw_lower = kw.lower()
                pos = task_lower.find(kw_lower)
                if pos >= 0:
                    matched.append(task_type)
                    match_details.append((task_type, kw))
                    position_weight = max(0, 1.0 - pos / max(task_len, 1))
                    length_weight = len(kw_lower) / max(len(kw_lower), 1)
                    exact_bonus = 5.0 if kw_lower == task_lower.strip() else 0.0
                    weight = position_weight * 2.0 + length_weight * 0.5 + exact_bonus
                    weighted.append((weight, task_type, kw, pos))
                    _log.debug("[路由匹配] 命中 | type=%s | keyword=\"%s\" | pos=%d | position_weight=%.3f | exact_bonus=%.1f | total_weight=%.3f | 扫描耗时=%.3fms",
                               task_type, kw, pos, position_weight, exact_bonus, weight,
                               (time.perf_counter() - _type_kw_start) * 1000)
                    _type_hit = True
                    break
            if not _type_hit:
                _log.debug("[路由匹配] 未命中 | type=%s | keywords=%s | 扫描耗时=%.3fms",
                           task_type, [k for k in config["keywords"]],
                           (time.perf_counter() - _type_kw_start) * 1000)
        _scan_elapsed = (time.perf_counter() - _scan_start) * 1000
        _match_elapsed = (time.perf_counter() - _t_match_start) * 1000
        if match_details:
            weighted.sort(key=lambda x: (-x[0], x[3]))
            sorted_types = [w[1] for w in weighted]
            _log.debug("[路由匹配] 权重排序详情:")
            for rank, (w, t, kw, pos) in enumerate(weighted, 1):
                _log.debug("  #%d: type=%s | kw=\"%s\" | pos=%d | weight=%.3f", rank, t, kw, pos, w)
            _log.info("任务类型匹配成功 | 输入=\"%s\" | 匹配=%s (关键词: %s) | 主类型=%s | 路由数=%d | 总关键词=%d | 扫描耗时=%.2fms | 总耗时=%.2fms",
                      task_description[:60],
                      [m[0] for m in match_details],
                      [m[1] for m in match_details],
                      sorted_types[0] if sorted_types else None,
                      len(TASK_ROUTING), _total_keywords, _scan_elapsed, _match_elapsed)
            self._last_match_weighted = weighted
            return sorted_types
        else:
            _log.warning("任务类型无匹配 | 输入=\"%s\" | 路由数=%d | 总关键词=%d | 扫描耗时=%.2fms | 总耗时=%.2fms | 将加载通用兜底规范: %s",
                         task_description[:60], len(TASK_ROUTING), _total_keywords, _scan_elapsed, _match_elapsed, FALLBACK_L2_SPECS)
            self._last_match_weighted = []
            return matched

    def _is_role_spec(self, rel_path: str) -> bool:
        return rel_path.startswith("roles/")

    def _resolve_l2_specs(self, matched_types: list[str], primary_only: bool = False) -> tuple[list[str], Optional[str], list[str]]:
        _t_resolve = time.perf_counter()
        if not matched_types:
            _log.debug("[L2解析] 无匹配类型，返回兜底规范 | fallback=%s", FALLBACK_L2_SPECS)
            return list(FALLBACK_L2_SPECS), None, []
        primary_type = matched_types[0]
        l2_specs = []
        seen = set()
        dedup_skipped = 0
        role_skipped = 0
        for idx, task_type in enumerate(matched_types):
            _type_start = time.perf_counter()
            if primary_only and idx > 0:
                _log.debug("[L2解析] primary_only模式，跳过辅助类型 | type=%s | idx=%d", task_type, idx)
                break
            config = TASK_ROUTING[task_type]
            type_specs_added = 0
            for spec_path in config["l2_specs"]:
                if spec_path in seen:
                    dedup_skipped += 1
                    _log.debug("[L2解析] 去重跳过（已被其他类型加载）| type=%s | path=%s", task_type, spec_path)
                    continue
                if idx > 0 and self._is_role_spec(spec_path):
                    role_skipped += 1
                    _log.debug("[L2解析] 辅助类型跳过角色文件 | type=%s | path=%s | 原因=%s",
                               task_type, spec_path, "角色互斥：辅助类型不加载角色定义")
                    continue
                seen.add(spec_path)
                l2_specs.append(spec_path)
                type_specs_added += 1
            _log.debug("[L2解析] 类型处理完成 | type=%s | role=%s | 新增文件=%d | 耗时=%.3fms",
                       task_type, "主类型" if idx == 0 else "辅助类型",
                       type_specs_added, (time.perf_counter() - _type_start) * 1000)
        _before_sort = list(l2_specs)
        l2_specs.sort(key=_l2_priority_key)
        if _before_sort != l2_specs:
            _log.debug("[L2解析] 优先级重排 | 排序前=%s | 排序后=%s", _before_sort, l2_specs)
        aux_types = [t for t in matched_types if t != primary_type]
        _elapsed = (time.perf_counter() - _t_resolve) * 1000
        _log.debug("[L2解析] 解析完成 | primary=%s | aux=%s | 总文件=%d | 去重跳过=%d | 角色跳过=%d | 耗时=%.3fms",
                   primary_type, aux_types, len(l2_specs), dedup_skipped, role_skipped, _elapsed)
        return l2_specs, primary_type, aux_types

    def load_spec_content(self, rel_path: str) -> Optional[LoadedSpec]:
        if rel_path in self._loaded:
            return self._loaded[rel_path]
        spec = self._read_spec(rel_path, "L2", "explicit:load_spec_content")
        if spec and self._auto_save and self._use_disk_cache and self._cache_dirty:
            self._save_disk_cache()
        return spec

    def load_for_task_lightweight(
        self,
        task_description: str,
        stage: str = "execution",
    ) -> LoadResult:
        return self.load_for_task(
            task_description,
            stage=stage,
            include_l1b=False,
            lightweight=True,
        )

    def load_for_task(
        self,
        task_description: str,
        stage: str = "execution",
        include_l1b: Optional[bool] = None,
        max_chars: Optional[int] = None,
        lightweight: bool = False,
        primary_only: bool = False,
    ) -> LoadResult:
        _t_total_start = time.perf_counter()
        _trigger_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        _log.info("===== 开始任务加载 =====")
        _log.info("触发时间: %s | 任务描述: \"%s\" | 阶段=%s | lightweight=%s | primary_only=%s | max_chars=%s",
                  _trigger_ts, task_description[:80], stage, lightweight, primary_only, max_chars)

        if include_l1b is None:
            include_l1b = stage in ("planning", "startup")
        if lightweight:
            include_l1b = False

        result = LoadResult(lightweight=lightweight)
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
            _log.debug("步骤3/5: 跳过 L1b 层（执行阶段/轻量模式延迟加载）")
            _step_times["L1b加载"] = 0.0

        _t_step = time.perf_counter()
        _log.debug("步骤4/5: 匹配任务类型（带权重排序）")
        matched_types = self.match_task_type(task_description)
        l2_specs, primary_type, aux_types = self._resolve_l2_specs(matched_types, primary_only=primary_only)
        result.matched_types = matched_types
        result.primary_type = primary_type
        _step_times["类型匹配"] = (time.perf_counter() - _t_step) * 1000
        _log.info("L2 待加载清单 | 主类型=%s | 辅助类型=%s | 数量=%d | 文件=%s",
                  primary_type, aux_types, len(l2_specs), l2_specs)
        _log.debug("[TIMER] 步骤4/5 任务类型匹配完成 | 耗时=%.2fms | 匹配类型=%s | 主类型=%s | L2文件数=%d",
                   _step_times["类型匹配"], matched_types, primary_type, len(l2_specs))

        _t_step = time.perf_counter()
        skipped_due_to_limit = 0
        _l2_chars_before = result.total_chars

        if lightweight:
            _log.debug("步骤5/5: 轻量模式——不加载L2内容，仅返回路径清单")
            result.pending_l2 = list(l2_specs)
            for p in l2_specs:
                result.already_loaded.add(p) if p in self._loaded else None
            _step_times["L2加载"] = (time.perf_counter() - _t_step) * 1000
        else:
            if not matched_types:
                _log.info("无匹配任务类型，加载通用兜底规范 | fallback=%s", FALLBACK_L2_SPECS)
            _warned_80 = False
            _log.debug("步骤5/5: 加载 L2 层（按优先级排序: commands>skills>protocols>workflows>roles>rules）")
            if max_chars:
                _log.debug("[预算] max_chars=%d | L0+L1基线=%d字符 | L2可用预算=%d字符",
                           max_chars, result.total_chars, max_chars - result.total_chars)
            for file_idx, rel_path in enumerate(l2_specs, 1):
                _file_t_start = time.perf_counter()
                if rel_path in self._loaded:
                    result.already_loaded.add(rel_path)
                    _log.debug("[L2#%d] 缓存命中 | path=%s | 耗时=%.3fms",
                               file_idx, rel_path, (time.perf_counter() - _file_t_start) * 1000)
                    continue
                if max_chars and result.total_chars >= max_chars:
                    _log.warning("[L2#%d] 达到字符上限，停止加载 | max_chars=%d | 当前=%d (%.0f%%) | 跳过=%s | 剩余文件=%d",
                                 file_idx, max_chars, result.total_chars,
                                 result.total_chars / max_chars * 100,
                                 rel_path, len(l2_specs) - file_idx)
                    skipped_due_to_limit += 1
                    break
                _pre_chars = result.total_chars
                _budget_check = "无限制"
                _est_size = 0
                if max_chars:
                    full_path = self._resolve_path(rel_path)
                    _est_source = "N/A"
                    if full_path:
                        try:
                            _est_size = full_path.stat().st_size
                            _est_source = f"stat({full_path.name})"
                        except OSError as e:
                            _est_size = 0
                            _est_source = f"stat失败({e.errno})"
                    _remaining = max_chars - result.total_chars
                    _pct = result.total_chars / max_chars * 100
                    _will_exceed = _est_size > 0 and _est_size > _remaining
                    _at_80 = result.total_chars >= max_chars * 0.8
                    _budget_check = (f"当前={_pre_chars}c ({_pct:.0f}%) | 剩余={_remaining}c | "
                                     f"预估={_est_size}c({_est_source}) | "
                                     f"加载后预估={_pre_chars + _est_size}c")
                    _log.debug("[L2#%d] 预算检查 | path=%s | %s | 将超限=%s",
                               file_idx, rel_path, _budget_check, _will_exceed)
                    if not _warned_80 and (_at_80 or _will_exceed):
                        _log.warning("字符预算使用达80%% | max_chars=%d | 当前=%d (%.0f%%) | 剩余=%d | 下一个文件=%s(预估%d字符)%s",
                                     max_chars, result.total_chars, _pct,
                                     _remaining, rel_path, _est_size,
                                     "（将跳过）" if _will_exceed else "")
                        _warned_80 = True
                    if _est_size > 0 and _will_exceed and result.total_chars >= max_chars * 0.5:
                        _log.warning("[L2#%d] 文件超出剩余预算，跳过 | path=%s | 预估=%d字符 | 剩余=%d | 超限比=%.0f%% | 决策=SKIP",
                                     file_idx, rel_path, _est_size, _remaining,
                                     (_est_size - _remaining) / _remaining * 100 if _remaining > 0 else 999)
                        skipped_due_to_limit += 1
                        continue
                else:
                    _log.debug("[L2#%d] 开始加载 | path=%s | 基线=%d字符", file_idx, rel_path, _pre_chars)
                spec = self._read_spec(rel_path, "L2", f"task:{task_description[:30]}")
                _file_elapsed = (time.perf_counter() - _file_t_start) * 1000
                if spec:
                    result.loaded_specs.append(spec)
                    result.total_chars += spec.char_count
                    result.layer_summary["L2"] += 1
                    _after_pct = (result.total_chars / max_chars * 100) if max_chars else 0
                    _log.debug("[L2#%d] 加载成功 | path=%s | 实际=%d字符(预估偏差=%+d) | 累计=%d字符%s | 耗时=%.2fms",
                               file_idx, rel_path, spec.char_count,
                               spec.char_count - _est_size if max_chars else 0,
                               result.total_chars,
                               f"({_after_pct:.0f}%)" if max_chars else "",
                               _file_elapsed)
                    if max_chars and not _warned_80 and result.total_chars >= max_chars * 0.8:
                        _log.warning("字符预算使用达80%% | max_chars=%d | 当前=%d (%.0f%%) | 刚加载=%s(%d字符) | 预估偏差=%+d",
                                     max_chars, result.total_chars,
                                     result.total_chars / max_chars * 100,
                                     rel_path, spec.char_count,
                                     spec.char_count - _est_size)
                        _warned_80 = True
                else:
                    result.missing_specs.append(rel_path)
                    _log.debug("[L2#%d] 文件未找到 | path=%s | 耗时=%.2fms", file_idx, rel_path, _file_elapsed)
            _step_times["L2加载"] = (time.perf_counter() - _t_step) * 1000

        _l2_chars_added = result.total_chars - _l2_chars_before
        _log.debug("[TIMER] 步骤5/5 L2按需加载完成 | 耗时=%.2fms | 文件=%d个 | 新增字符=%d | 限载跳过=%d | lightweight=%s",
                   _step_times["L2加载"], result.layer_summary.get("L2", 0), _l2_chars_added, skipped_due_to_limit, lightweight)

        _total_elapsed = (time.perf_counter() - _t_total_start) * 1000
        _log.info("===== 任务加载完成 =====")
        _log.info("汇总: L0=%d | L1a=%d | L1b=%d | L2=%d | 总文件=%d | 总字符=%d | 主类型=%s | "
                  "缓存命中(磁盘)=%d | 缓存未命中=%d | 缺失=%d | 限载跳过=%d | lightweight=%s | pending_L2=%d",
                  result.layer_summary.get("L0", 0), result.layer_summary.get("L1a", 0),
                  result.layer_summary.get("L1b", 0), result.layer_summary.get("L2", 0),
                  result.spec_count, result.total_chars, primary_type,
                  self._cache_hits, self._cache_misses,
                  len(result.missing_specs), skipped_due_to_limit, lightweight, len(result.pending_l2))

        _t_save_start = time.perf_counter()
        _save_triggered = False
        if self._auto_save and self._use_disk_cache and self._cache_dirty:
            _save_triggered = True
            self._save_disk_cache()
        _t_save_ms = (time.perf_counter() - _t_save_start) * 1000
        _total_with_save = (time.perf_counter() - _t_total_start) * 1000

        _log.info("[TIMER] 性能统计 | 触发时间=%s | 加载耗时=%.2fms | save=%.2fms(%s) | 总耗时=%.2fms | "
                  "L0=%.2fms | L1a=%.2fms | L1b=%.2fms | 匹配=%.2fms | L2=%.2fms",
                  _trigger_ts, _total_elapsed,
                  _t_save_ms, "yes" if _save_triggered else "no",
                  _total_with_save,
                  _step_times.get("L0加载", 0), _step_times.get("L1a加载", 0),
                  _step_times.get("L1b加载", 0),
                  _step_times.get("类型匹配", 0), _step_times.get("L2加载", 0))

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
        mode_tag = "lightweight" if result.lightweight else "full"
        lines = [f"## 已加载规范（渐进式披露·{mode_tag}）", ""]
        lines.append(result.summary())
        lines.append("")

        if result.lightweight and not include_content:
            lines.append("### 已加载规范（L0+L1a 核心层）")
            lines.append("")
            for spec in result.loaded_specs:
                lines.append(f"- [{spec.layer}] `{spec.path}` ({spec.char_count} 字符)")
            lines.append("")
            lines.append("### 📋 L2 待加载清单（按需调用 load_spec_content）")
            lines.append("")
            for p in result.pending_l2:
                loaded_mark = " ✅(已缓存)" if p in self._loaded else ""
                lines.append(f"- `{p}`{loaded_mark}")
        elif include_content:
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
        _t_inval_start = time.perf_counter()
        self._disk_cache = {}
        self._loaded = {}
        self._cache_dirty = False
        self._cache_hits = 0
        self._cache_misses = 0
        unlinked = False
        try:
            if self._cache_path.exists():
                self._cache_path.unlink()
                unlinked = True
                _log.info("磁盘缓存已清除 | path=%s | elapsed=%.2fms", self._cache_path,
                          (time.perf_counter() - _t_inval_start) * 1000)
        except OSError as e:
            _log.warning("清除磁盘缓存失败 | error=%s | elapsed=%.2fms", e,
                         (time.perf_counter() - _t_inval_start) * 1000)
        if not unlinked:
            _log.debug("内存缓存已重置（磁盘文件不存在或已删除） | elapsed=%.2fms",
                       (time.perf_counter() - _t_inval_start) * 1000)


def quick_load(task: str, project_root: Optional[Path | str] = None, **kwargs) -> LoadResult:
    loader = SpecLoader(project_root)
    result = loader.load_for_task(task, **kwargs)
    if not loader._auto_save:
        loader.save_cache()
    return result
