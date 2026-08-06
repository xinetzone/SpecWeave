"""知识图谱可视化配置模块。

集中管理知识图谱的所有可视化配置：节点类型标签、关系标签、节点颜色/大小/形状、
边样式、字体、领域颜色映射等。支持从 JSON 文件加载自定义配置。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NodeStyle:
    color: str
    size: int
    shape: str = "dot"
    border_width: int = 2
    border_width_selected: int = 4


@dataclass
class EdgeStyle:
    color: str
    width: int
    dashes: list[int] | bool = False
    arrows: str = ""


@dataclass
class FontConfig:
    color: str = "#333"
    size: int = 14
    face: str = "sans-serif"


DEFAULT_TYPE_LABELS: dict[str, str] = {
    "concept": "概念",
    "person": "人物",
    "event": "事件",
    "document": "文档",
    "period": "时期",
}

DEFAULT_RELATION_LABELS: dict[str, str] = {
    "related_to": "概念相关",
    "influenced": "思想传承",
    "preceded": "时序先后",
    "belongs_to": "时期归属",
    "defined_in": "概念定义",
    "contributed": "人物贡献",
}

DEFAULT_DOMAIN_COLORS: dict[str, str] = {
    "哲学": "#8B4513",
    "物理学": "#1E88E5",
    "方法论": "#43A047",
    "认知科学": "#FB8C00",
    "通用": "#757575",
}

DEFAULT_NODE_STYLES: dict[str, NodeStyle] = {
    "concept": NodeStyle(color="#757575", size=18),
    "person": NodeStyle(color="#E53935", size=22),
    "event": NodeStyle(color="#8E24AA", size=22),
    "document": NodeStyle(color="#00897B", size=18),
    "period": NodeStyle(color="#546E7A", size=35, shape="diamond"),
}

DEFAULT_EDGE_STYLES: dict[str, EdgeStyle] = {
    "related_to": EdgeStyle(color="#999", width=1),
    "influenced": EdgeStyle(color="#1565C0", width=2, arrows="to"),
    "preceded": EdgeStyle(color="#BBB", width=1, arrows="to"),
    "belongs_to": EdgeStyle(color="#CCC", width=1, dashes=[6, 4]),
    "defined_in": EdgeStyle(color="#4CAF50", width=1, dashes=[2, 3]),
    "contributed": EdgeStyle(color="#FF9800", width=2, arrows="to"),
}

DEFAULT_DETAIL_FIELD_LABELS: dict[str, list[dict[str, str]]] = {
    "concept": [
        {"key": "english_name", "label": "英文名"},
        {"key": "definition", "label": "定义摘要"},
        {"key": "rating", "label": "可信度评级", "type": "rating"},
        {"key": "source_url", "label": "查看源文档", "type": "link"},
    ],
    "person": [
        {"key": "period", "label": "时期"},
        {"key": "contribution", "label": "核心贡献"},
        {"key": "source_url", "label": "查看源文档", "type": "link"},
    ],
    "event": [
        {"key": "time", "label": "时间"},
        {"key": "period", "label": "时期"},
        {"key": "importance", "label": "重要程度"},
        {"key": "source_url", "label": "详细说明", "type": "link"},
    ],
    "document": [
        {"key": "description", "label": "简介"},
        {"key": "difficulty", "label": "难度"},
        {"key": "source_url", "label": "打开文档", "type": "link"},
    ],
    "period": [
        {"key": "time_range", "label": "时间范围"},
        {"key": "description", "label": "概述"},
    ],
}

A_RATING_SIZE_BONUS = 2
DEFAULT_FALLBACK_COLOR = "#757575"
DEFAULT_FALLBACK_SIZE = 18
DEFAULT_FALLBACK_SHAPE = "dot"


@dataclass
class KnowledgeGraphConfig:
    type_labels: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_TYPE_LABELS))
    relation_labels: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_RELATION_LABELS))
    domain_colors: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_DOMAIN_COLORS))
    node_styles: dict[str, NodeStyle] = field(default_factory=dict)
    edge_styles: dict[str, EdgeStyle] = field(default_factory=dict)
    font: FontConfig = field(default_factory=FontConfig)
    detail_field_labels: dict[str, list[dict[str, str]]] = field(
        default_factory=lambda: {k: list(v) for k, v in DEFAULT_DETAIL_FIELD_LABELS.items()}
    )
    highlight_border_color: str = "#000"
    enable_editing: bool = True

    def __post_init__(self):
        if not self.node_styles:
            self.node_styles = {k: NodeStyle(color=v.color, size=v.size, shape=v.shape,
                                            border_width=v.border_width,
                                            border_width_selected=v.border_width_selected)
                               for k, v in DEFAULT_NODE_STYLES.items()}
        if not self.edge_styles:
            self.edge_styles = {k: EdgeStyle(color=v.color, width=v.width, dashes=v.dashes, arrows=v.arrows)
                               for k, v in DEFAULT_EDGE_STYLES.items()}

    def get_node_color(self, node_type: str, domain: str | None = None) -> str:
        if node_type == "concept" and domain:
            return self.domain_colors.get(domain, self.domain_colors.get("通用", DEFAULT_FALLBACK_COLOR))
        style = self.node_styles.get(node_type)
        return style.color if style else DEFAULT_FALLBACK_COLOR

    def get_node_size(self, node_type: str, rating: str | None = None) -> int:
        style = self.node_styles.get(node_type)
        size = style.size if style else DEFAULT_FALLBACK_SIZE
        if node_type == "concept" and rating == "A":
            size += A_RATING_SIZE_BONUS
        return size

    def get_node_shape(self, node_type: str) -> str:
        style = self.node_styles.get(node_type)
        return style.shape if style else DEFAULT_FALLBACK_SHAPE

    def get_node_border_width(self, node_type: str) -> int:
        style = self.node_styles.get(node_type)
        return style.border_width if style else 2

    def get_node_border_width_selected(self, node_type: str) -> int:
        style = self.node_styles.get(node_type)
        return style.border_width_selected if style else 4

    def get_edge_style(self, relation: str) -> EdgeStyle:
        return self.edge_styles.get(relation, self.edge_styles.get("related_to", EdgeStyle(
            color=DEFAULT_FALLBACK_COLOR, width=1)))

    def get_type_label(self, node_type: str) -> str:
        return self.type_labels.get(node_type, node_type)

    def get_relation_label(self, relation: str) -> str:
        return self.relation_labels.get(relation, relation)

    def node_type_colors_dict(self) -> dict[str, str]:
        return {k: v.color for k, v in self.node_styles.items()}

    def edge_styles_for_js(self) -> dict[str, dict[str, Any]]:
        return {
            k: {"color": v.color, "dashes": v.dashes if v.dashes else False, "arrows": v.arrows}
            for k, v in self.edge_styles.items()
        }

    def font_dict(self) -> dict[str, Any]:
        return {"color": self.font.color, "size": self.font.size, "face": self.font.face}

    @classmethod
    def from_json(cls, config_path: Path) -> "KnowledgeGraphConfig":
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("无法加载配置文件 %s: %s，使用默认配置", config_path, e)
            return cls()

        config = cls()
        if "type_labels" in data:
            config.type_labels.update(data["type_labels"])
        if "relation_labels" in data:
            config.relation_labels.update(data["relation_labels"])
        if "domain_colors" in data:
            config.domain_colors.update(data["domain_colors"])
        if "font" in data:
            f = data["font"]
            config.font = FontConfig(
                color=f.get("color", config.font.color),
                size=f.get("size", config.font.size),
                face=f.get("face", config.font.face),
            )
        if "node_styles" in data:
            for ntype, ns in data["node_styles"].items():
                base = config.node_styles.get(ntype, NodeStyle(color=DEFAULT_FALLBACK_COLOR, size=DEFAULT_FALLBACK_SIZE))
                config.node_styles[ntype] = NodeStyle(
                    color=ns.get("color", base.color),
                    size=ns.get("size", base.size),
                    shape=ns.get("shape", base.shape),
                )
        if "edge_styles" in data:
            for rel, es in data["edge_styles"].items():
                base = config.edge_styles.get(rel, EdgeStyle(color=DEFAULT_FALLBACK_COLOR, width=1))
                config.edge_styles[rel] = EdgeStyle(
                    color=es.get("color", base.color),
                    width=es.get("width", base.width),
                    dashes=es.get("dashes", base.dashes),
                    arrows=es.get("arrows", base.arrows),
                )
        if "detail_field_labels" in data:
            for ntype, fields in data["detail_field_labels"].items():
                config.detail_field_labels[ntype] = fields
        if "enable_editing" in data:
            config.enable_editing = bool(data["enable_editing"])
        return config


_default_config: KnowledgeGraphConfig | None = None


def get_config() -> KnowledgeGraphConfig:
    global _default_config
    if _default_config is None:
        _default_config = KnowledgeGraphConfig()
    return _default_config


def set_config(config: KnowledgeGraphConfig) -> None:
    global _default_config
    _default_config = config
