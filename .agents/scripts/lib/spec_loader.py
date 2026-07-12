"""L2 渐进式披露运行时规范加载器。

实现 L0/L1/L2 三层规范按需加载：
  - L0: ONBOARDING.md (入口速查, <100行, <30秒读完)
  - L1: capability-registry.md + context-routing.md + skills/ (全量索引, 1-3分钟)
  - L2: commands/、protocols/、rules/ 等详细规范 (按需加载)

核心能力：
  - 根据任务类型关键词自动路由到对应 L2 规范
  - 加载追踪：记录已加载的规范避免重复读取
  - 依赖解析：自动加载规范声明的前置依赖
  - 阶段守卫集成：支持按任务阶段加载所需规范

用法：
  from lib.spec_loader import SpecLoader
  loader = SpecLoader(project_root)
  specs = loader.load_for_task("code review")
"""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root, resolve_agents_dir

_log = logging.getLogger("spec_loader")


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.WARNING
    if not _log.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        _log.addHandler(handler)
    _log.setLevel(level)
    return _log


LAYER_DESCRIPTIONS = {
    "L0": "入口速查（ONBOARDING.md）",
    "L1": "全量索引（capability-registry + context-routing + skills/）",
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
        "required_layers": ["L0"],
        "description": "会话启动阶段",
    },
    "planning": {
        "required_layers": ["L0", "L1"],
        "required_l2": ["context-routing.md"],
        "description": "任务规划阶段",
    },
    "execution": {
        "required_layers": ["L0", "L1"],
        "description": "任务执行阶段（按任务类型加载L2）",
    },
    "verification": {
        "required_layers": ["L0", "L1"],
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
    layer_summary: dict[str, int] = field(default_factory=lambda: {"L0": 0, "L1": 0, "L2": 0})

    @property
    def spec_count(self) -> int:
        return len(self.loaded_specs)

    def summary(self) -> str:
        lines = [
            f"规范加载结果：{self.spec_count} 个文件，{self.total_chars} 字符",
            f"  L0（入口速查）: {self.layer_summary['L0']} 个",
            f"  L1（全量索引）: {self.layer_summary['L1']} 个",
            f"  L2（详细规范）: {self.layer_summary['L2']} 个",
        ]
        if self.missing_specs:
            lines.append(f"  ⚠️ 未找到: {', '.join(self.missing_specs)}")
        return "\n".join(lines)


class SpecLoader:
    """L2 渐进式披露运行时规范加载器。

    三层架构：
      - L0: ONBOARDING.md（始终加载）
      - L1: capability-registry.md + context-routing.md + skills索引（规划阶段加载）
      - L2: 具体规范（执行阶段按任务类型按需加载）

    用法：
      >>> loader = SpecLoader()  # 自动解析项目根目录
      >>> result = loader.load_for_task("code review")
      >>> print(result.summary())
      >>> for spec in result.loaded_specs:
      ...     print(f"[{spec.layer}] {spec.path} ({spec.char_count} chars)")
    """

    L0_SPECS = [
        "ONBOARDING.md",
    ]

    L1_SPECS = [
        "capability-registry.md",
        "context-routing.md",
        "global-core-rules.md",
        "capability-boundaries.md",
        "skills/README.md",
    ]

    def __init__(self, project_root: Optional[Path | str] = None, verbose: bool = False):
        if project_root is None:
            self.root = resolve_project_root(__file__)
        else:
            self.root = Path(project_root).resolve()
        self.agents_dir = self.root / ".agents"
        self._loaded: dict[str, LoadedSpec] = {}
        self._verbose = verbose
        if verbose:
            _log.debug("SpecLoader 初始化完成 | project_root=%s | agents_dir=%s", self.root, self.agents_dir)

    def _read_spec(self, rel_path: str, layer: str, loaded_from: str) -> Optional[LoadedSpec]:
        full_path = self.agents_dir / rel_path
        path_source = ".agents/"
        if not full_path.exists():
            root_path = self.root / rel_path
            if root_path.exists():
                full_path = root_path
                path_source = "root/"
            else:
                _log.warning("规范文件未找到 | layer=%s | path=%s (从 %s 加载请求)", layer, rel_path, loaded_from)
                return None

        if rel_path in self._loaded:
            cached = self._loaded[rel_path]
            _log.debug("缓存命中 | layer=%s | path=%s | chars=%d", layer, rel_path, cached.char_count)
            return cached

        content = full_path.read_text(encoding="utf-8")
        spec = LoadedSpec(
            path=rel_path,
            layer=layer,
            content=content,
            char_count=len(content),
            loaded_from=loaded_from,
        )
        self._loaded[rel_path] = spec
        _log.info("已加载规范 | layer=%s | path=%s%s | chars=%d | 来源=%s",
                  layer, path_source, rel_path, spec.char_count, loaded_from)
        return spec

    def load_layer(self, layer: str, force: bool = False) -> LoadResult:
        result = LoadResult()

        if layer == "L0":
            specs_to_load = self.L0_SPECS
        elif layer == "L1":
            specs_to_load = self.L1_SPECS
        else:
            _log.error("不支持的层: %s", layer)
            return result

        _log.info("开始加载层 | layer=%s | 文件数=%d | force=%s", layer, len(specs_to_load), force)

        for rel_path in specs_to_load:
            if not force and rel_path in self._loaded:
                result.already_loaded.add(rel_path)
                _log.debug("跳过已加载 | layer=%s | path=%s", layer, rel_path)
                continue
            spec = self._read_spec(rel_path, layer, f"layer:{layer}")
            if spec:
                result.loaded_specs.append(spec)
                result.total_chars += spec.char_count
                result.layer_summary[layer] += 1
            else:
                result.missing_specs.append(rel_path)

        _log.info("层加载完成 | layer=%s | 新加载=%d | 已缓存=%d | 缺失=%d | 累计字符=%d",
                  layer, len(result.loaded_specs), len(result.already_loaded),
                  len(result.missing_specs), result.total_chars)
        return result

    def match_task_type(self, task_description: str) -> list[str]:
        task_lower = task_description.lower()
        matched = []
        match_details = []
        for task_type, config in TASK_ROUTING.items():
            for kw in config["keywords"]:
                if kw.lower() in task_lower:
                    matched.append(task_type)
                    match_details.append((task_type, kw))
                    break
        if match_details:
            _log.info("任务类型匹配成功 | 输入=\"%s\" | 匹配=%s (关键词: %s)",
                      task_description[:60],
                      [m[0] for m in match_details],
                      [m[1] for m in match_details])
        else:
            _log.warning("任务类型无匹配 | 输入=\"%s\" | 将仅加载L0+L1层", task_description[:60])
        return matched

    def load_for_task(
        self,
        task_description: str,
        stage: str = "execution",
        include_l1: bool = True,
        max_chars: Optional[int] = None,
    ) -> LoadResult:
        _log.info("===== 开始任务加载 =====")
        _log.info("任务描述: \"%s\" | 阶段=%s | include_l1=%s | max_chars=%s",
                  task_description[:80], stage, include_l1, max_chars)

        result = LoadResult()

        _log.debug("步骤1/4: 加载 L0 层（入口速查）")
        l0_result = self.load_layer("L0")
        result.loaded_specs.extend(l0_result.loaded_specs)
        result.total_chars += l0_result.total_chars
        result.layer_summary["L0"] += l0_result.layer_summary["L0"]
        result.missing_specs.extend(l0_result.missing_specs)
        result.already_loaded.update(l0_result.already_loaded)

        if include_l1 or stage in ("planning", "startup"):
            _log.debug("步骤2/4: 加载 L1 层（全量索引）")
            l1_result = self.load_layer("L1")
            result.loaded_specs.extend(l1_result.loaded_specs)
            result.total_chars += l1_result.total_chars
            result.layer_summary["L1"] += l1_result.layer_summary["L1"]
            result.missing_specs.extend(l1_result.missing_specs)
            result.already_loaded.update(l1_result.already_loaded)
        else:
            _log.debug("步骤2/4: 跳过 L1 层（include_l1=False 且阶段非 planning/startup）")

        _log.debug("步骤3/4: 匹配任务类型")
        matched_types = self.match_task_type(task_description)
        l2_specs = []
        for task_type in matched_types:
            config = TASK_ROUTING[task_type]
            for spec_path in config["l2_specs"]:
                if spec_path not in l2_specs:
                    l2_specs.append(spec_path)
        _log.info("L2 待加载清单 | 数量=%d | 文件=%s", len(l2_specs), l2_specs)

        _log.debug("步骤4/4: 加载 L2 层（按需规范）")
        skipped_due_to_limit = 0
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

        _log.info("===== 任务加载完成 =====")
        _log.info("汇总: L0=%d个 | L1=%d个 | L2=%d个 | 总文件=%d | 总字符=%d | 已缓存=%d | 缺失=%d | 限载跳过=%d",
                  result.layer_summary["L0"], result.layer_summary["L1"], result.layer_summary["L2"],
                  result.spec_count, result.total_chars,
                  len(result.already_loaded), len(result.missing_specs), skipped_due_to_limit)
        return result

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
                result.layer_summary[layer] += 1
            else:
                result.missing_specs.append(rel_path)
        return result

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


def quick_load(task: str, project_root: Optional[Path | str] = None, **kwargs) -> LoadResult:
    loader = SpecLoader(project_root)
    return loader.load_for_task(task, **kwargs)
