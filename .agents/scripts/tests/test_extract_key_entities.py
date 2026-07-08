#!/usr/bin/env python3
"""
测试 extract-key-entities.py 脚本
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

import sys
import importlib.util

script_path = Path(__file__).resolve().parent.parent / "extract-key-entities.py"
spec = importlib.util.spec_from_file_location("extract_key_entities", str(script_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

EntityExtractor = module.EntityExtractor


def test_extract_from_file():
    """测试从文件中提取关键实体"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """## 其他内容

## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
| MODULE | minitest.cli.commands | CLI命令模块 |

## 后续内容
"""
        filepath = Path(tmpdir) / "task1.md"
        filepath.write_text(content, encoding="utf-8")

        extractor = EntityExtractor(tmpdir)
        extractor.extract_from_file(filepath)

        assert len(extractor.entities) == 3
        types = {e["type"] for e in extractor.entities}
        assert types == {"API", "CONFIG", "MODULE"}
        names = {e["name"] for e in extractor.entities}
        assert names == {"POST /api/v1/test/run", "MINITEST_API_KEY", "minitest.cli.commands"}


def test_merge_entities():
    """测试合并相同实体"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content1 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
"""
        content2 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | Run test task |
"""
        Path(tmpdir, "task1.md").write_text(content1, encoding="utf-8")
        Path(tmpdir, "task2.md").write_text(content2, encoding="utf-8")

        extractor = EntityExtractor(tmpdir)
        extractor.extract_from_file(Path(tmpdir) / "task1.md")
        extractor.extract_from_file(Path(tmpdir) / "task2.md")
        extractor.merge_entities()

        assert len(extractor.entities) == 1
        entity = extractor.entities[0]
        assert entity["name"] == "POST /api/v1/test/run"
        assert len(entity["sources"]) == 2
        assert len(entity["descriptions"]) == 2


def test_detect_term_conflicts():
    """测试检测术语冲突"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content1 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务 |
"""
        content2 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | post /api/v1/test/run | RunTest |
"""
        Path(tmpdir, "task1.md").write_text(content1, encoding="utf-8")
        Path(tmpdir, "task2.md").write_text(content2, encoding="utf-8")

        extractor = EntityExtractor(tmpdir)
        extractor.extract_from_file(Path(tmpdir) / "task1.md")
        extractor.extract_from_file(Path(tmpdir) / "task2.md")
        extractor.merge_entities()
        extractor.detect_term_conflicts()

        assert len(extractor.term_conflicts) >= 1


def test_suggest_cross_module():
    """测试跨模块关联建议"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content1 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| CONFIG | MINITEST_API_KEY | API密钥 |
"""
        content2 = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| CONFIG | MINITEST_API_KEY | API密钥配置 |
"""
        Path(tmpdir, "task1-cli.md").write_text(content1, encoding="utf-8")
        Path(tmpdir, "task2-trigger.md").write_text(content2, encoding="utf-8")

        extractor = EntityExtractor(tmpdir)
        extractor.extract_from_file(Path(tmpdir) / "task1-cli.md")
        extractor.extract_from_file(Path(tmpdir) / "task2-trigger.md")
        extractor.merge_entities()
        extractor.suggest_cross_module()

        assert len(extractor.cross_module_suggestions) >= 1


def test_table_parser_with_separator():
    """测试表格解析器处理分隔行"""
    content = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
"""
    extractor = EntityExtractor(".")
    rows = extractor._parse_markdown_table(content)
    assert len(rows) == 2


def test_main():
    """测试主函数"""
    with tempfile.TemporaryDirectory() as tmpdir:
        content = """## 关键实体

| 类型 | 名称 | 说明 |
|------|------|------|
| API | POST /api/v1/test/run | 执行测试任务接口 |
| CONFIG | MINITEST_API_KEY | API密钥配置 |
"""
        Path(tmpdir, "task1.md").write_text(content, encoding="utf-8")
        
        output_path = Path(tmpdir) / "entities.json"
        
        import subprocess
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent / "extract-key-entities.py"),
             "--input", tmpdir, "--output", str(output_path)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        
        assert result.returncode == 0
        assert output_path.exists()
        
        data = json.loads(output_path.read_text(encoding="utf-8"))
        assert data["summary"]["total_entities"] == 2


if __name__ == "__main__":
    test_extract_from_file()
    print("✓ test_extract_from_file")
    
    test_merge_entities()
    print("✓ test_merge_entities")
    
    test_detect_term_conflicts()
    print("✓ test_detect_term_conflicts")
    
    test_suggest_cross_module()
    print("✓ test_suggest_cross_module")
    
    test_table_parser_with_separator()
    print("✓ test_table_parser_with_separator")
    
    test_main()
    print("✓ test_main")
    
    print("\n所有测试通过！")
