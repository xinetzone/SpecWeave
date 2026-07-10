#!/usr/bin/env python3
"""
extract-key-entities.py - 从子代理报告中提取关键实体汇总表

功能：
- 遍历所有子代理报告，提取关键实体汇总表
- 按实体名称分组，识别术语冲突
- 基于预探索的依赖关系，建议跨模块关联
- 输出JSON格式结果，便于主控代理消费

使用方式：
    python .agents/scripts/extract-key-entities.py --input ./subagent-outputs/ --output entities.json

输出格式：
{
    "entities": [
        {
            "type": "API",
            "name": "POST /api/v1/test/run",
            "description": "执行测试任务接口",
            "sources": ["task1.md", "task3.md"]
        }
    ],
    "term_conflicts": [
        {
            "names": ["测试任务接口", "RunTest"],
            "common_entity": "POST /api/v1/test/run",
            "suggested_unified_term": "执行测试任务接口"
        }
    ],
    "cross_module_suggestions": [
        {
            "entity": "MINITEST_API_KEY",
            "modules": ["minitest-cli", "minitest-trigger"],
            "suggestion": "可能存在跨模块配置共享"
        }
    ]
}
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


class EntityExtractor:
    """关键实体提取器"""

    def __init__(self, input_dir: str, preflight_file: str | None = None):
        self.input_dir = Path(input_dir)
        self.preflight_file = Path(preflight_file) if preflight_file else None
        self.entities: list[dict[str, Any]] = []
        self.term_conflicts: list[dict[str, Any]] = []
        self.cross_module_suggestions: list[dict[str, Any]] = []
        self.supported_types = {"API", "CONFIG", "MODULE"}

    def extract_from_file(self, filepath: Path) -> None:
        """从单个文件中提取关键实体"""
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[WARN] 无法读取文件: {filepath} - {e}")
            return

        table_start = content.find("## 关键实体")
        if table_start == -1:
            return

        table_end = content.find("## ", table_start + 10)
        if table_end == -1:
            table_end = len(content)

        table_content = content[table_start:table_end]

        rows = self._parse_markdown_table(table_content)
        for row in rows:
            if len(row) >= 3 and row[0] in self.supported_types:
                entity = {
                    "type": row[0].strip(),
                    "name": row[1].strip(),
                    "description": row[2].strip(),
                    "sources": [filepath.name],
                }
                self.entities.append(entity)

    def _parse_markdown_table(self, content: str) -> list[list[str]]:
        """解析Markdown表格"""
        rows = []
        lines = content.split("\n")
        in_table = False
        for line in lines:
            if "|" in line and "-|" not in line and not line.strip().startswith("|--"):
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 3 and cells[0] != "类型":
                    rows.append(cells)
        return rows

    def merge_entities(self) -> None:
        """合并相同实体"""
        merged: dict[str, dict[str, Any]] = {}
        for entity in self.entities:
            key = f"{entity['type']}|{entity['name']}"
            if key in merged:
                if entity["description"] != merged[key]["description"]:
                    merged[key]["descriptions"].append(entity["description"])
                if entity["sources"][0] not in merged[key]["sources"]:
                    merged[key]["sources"].append(entity["sources"][0])
            else:
                merged[key] = {
                    "type": entity["type"],
                    "name": entity["name"],
                    "description": entity["description"],
                    "descriptions": [entity["description"]],
                    "sources": entity["sources"],
                }
        self.entities = list(merged.values())

    def detect_term_conflicts(self) -> None:
        """检测术语冲突（相同实体不同命名）"""
        name_groups: dict[str, list[dict[str, Any]]] = {}
        for entity in self.entities:
            base_name = self._normalize_name(entity["name"])
            if base_name not in name_groups:
                name_groups[base_name] = []
            name_groups[base_name].append(entity)

        for base_name, entities in name_groups.items():
            if len(entities) > 1:
                descriptions = set()
                names = set()
                for e in entities:
                    names.add(e["name"])
                    descriptions.update(e["descriptions"])

                if len(names) > 1:
                    self.term_conflicts.append({
                        "names": list(names),
                        "common_entity": base_name,
                        "descriptions": list(descriptions),
                        "suggested_unified_term": max(names, key=len),
                    })

    def _normalize_name(self, name: str) -> str:
        """标准化实体名称用于匹配"""
        return re.sub(r"[^a-zA-Z0-9/_-]", "", name).lower()

    def suggest_cross_module(self) -> None:
        """建议跨模块关联"""
        name_to_modules: dict[str, list[str]] = {}
        for entity in self.entities:
            for source in entity["sources"]:
                module_name = self._extract_module_from_source(source)
                key = f"{entity['type']}|{entity['name']}"
                if key not in name_to_modules:
                    name_to_modules[key] = []
                if module_name not in name_to_modules[key]:
                    name_to_modules[key].append(module_name)

        for key, modules in name_to_modules.items():
            if len(modules) >= 2:
                entity_type, entity_name = key.split("|", 1)
                self.cross_module_suggestions.append({
                    "entity_type": entity_type,
                    "entity_name": entity_name,
                    "modules": modules,
                    "suggestion": f"{entity_type} {entity_name} 在多个模块中出现，可能存在跨模块共享或依赖关系",
                })

    def _extract_module_from_source(self, source: str) -> str:
        """从源文件名提取模块名"""
        patterns = [
            r"task(\d+)",
            r"(\w+)-analysis",
            r"(\w+)-report",
        ]
        for pattern in patterns:
            match = re.search(pattern, source, re.IGNORECASE)
            if match:
                return match.group(1)
        return source.replace(".md", "")

    def run(self) -> dict[str, Any]:
        """执行完整提取流程"""
        if not self.input_dir.exists():
            raise ValueError(f"输入目录不存在: {self.input_dir}")

        for filepath in sorted(self.input_dir.glob("*.md")):
            self.extract_from_file(filepath)

        self.merge_entities()
        self.detect_term_conflicts()
        self.suggest_cross_module()

        return {
            "entities": self.entities,
            "term_conflicts": self.term_conflicts,
            "cross_module_suggestions": self.cross_module_suggestions,
            "summary": {
                "total_entities": len(self.entities),
                "total_conflicts": len(self.term_conflicts),
                "total_cross_module": len(self.cross_module_suggestions),
                "source_files": [f.name for f in self.input_dir.glob("*.md")],
            },
        }


def main():
    parser = argparse.ArgumentParser(description="从子代理报告中提取关键实体汇总表")
    parser.add_argument("--input", required=True, help="子代理报告目录路径")
    parser.add_argument("--output", default="entities.json", help="输出JSON文件路径")
    parser.add_argument("--preflight", help="预探索报告文件路径（可选）")
    args = parser.parse_args()

    extractor = EntityExtractor(args.input, args.preflight)
    result = extractor.run()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[INFO] 提取完成，输出到: {output_path}")
    print(f"[INFO] 提取实体: {result['summary']['total_entities']}")
    print(f"[INFO] 术语冲突: {result['summary']['total_conflicts']}")
    print(f"[INFO] 跨模块关联建议: {result['summary']['total_cross_module']}")


if __name__ == "__main__":
    main()
