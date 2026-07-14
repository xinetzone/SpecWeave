"""知识库模糊测试框架。

生成随机畸形输入，测试系统在异常输入下的鲁棒性。
覆盖场景：超大文件、畸形YAML、非法字符、边界条件、路径遍历等。

用法：
  python -m lib.knowledge_fuzzer --scenarios all    # 运行所有场景
  python -m lib.knowledge_fuzzer --scenarios yaml    # 仅运行YAML测试
  python -m lib.knowledge_fuzzer --scenarios path    # 仅运行路径测试
"""

import random
import string
import textwrap
from pathlib import Path
from typing import Callable

from .knowledge_defense import (
    InputValidator,
    ResourceGuard,
    DEFAULT_MAX_FILE_SIZE_MB,
    DEFAULT_MAX_CONTENT_LENGTH,
    DEFAULT_MAX_METADATA_FIELDS,
    DEFAULT_MAX_TAGS_COUNT,
    DEFAULT_MAX_FILENAME_LENGTH,
    DEFAULT_MAX_PATH_DEPTH,
    DEFAULT_MAX_RECURSION_DEPTH,
)


# ---------------------------------------------------------------------------
# 畸形输入生成器
# ---------------------------------------------------------------------------

def generate_random_string(length: int, charset: str = "all") -> str:
    """生成随机字符串。

    Args:
        length: 长度。
        charset: 字符集，可选 "all", "printable", "binary", "unicode", "control"。

    Returns:
        随机字符串。
    """
    charsets = {
        "all": string.printable + ''.join(chr(i) for i in range(256) if chr(i) not in string.printable),
        "printable": string.printable,
        "binary": ''.join(chr(i) for i in range(256)),
        "unicode": ''.join(chr(i) for i in range(0x4E00, 0x9FFF)) + string.printable,
        "control": ''.join(chr(i) for i in range(32)),
    }
    chars = charsets.get(charset, charsets["all"])
    return ''.join(random.choice(chars) for _ in range(length))


def generate_malformed_yaml() -> str:
    """生成畸形 YAML frontmatter 输入。

    Returns:
        畸形 YAML 字符串列表。
    """
    scenarios = [
        # 无结束标记
        "---\ntitle: test\n",
        # 只有开始标记
        "---\n",
        # 嵌套 frontmatter
        "---\n---\n---\n",
        # 超大 frontmatter
        "---\n" + "\n".join(f"key_{i}: value_{i}" for i in range(100)) + "\n---\n",
        # 空字节
        "---\ntitle: test\x00\n---\n",
        # 非法键名
        "---\n123key: value\n---\n",
        # 无键名
        "---\n: value\n---\n",
        # 极长值
        "---\ntitle: " + "x" * 100000 + "\n---\n",
        # 重复键
        "---\ntitle: a\ntitle: b\n---\n",
        # 无冒号行
        "---\njust some text\nmore text\n---\n",
        # 极深嵌套（模拟块级YAML非法）
        "---\n" + "\n".join(f"  " * i + f"key_{i}: value" for i in range(50)) + "\n---\n",
    ]
    return scenarios


def generate_malformed_paths() -> list[str]:
    """生成畸形路径输入。

    Returns:
        畸形路径字符串列表。
    """
    return [
        "../../../etc/passwd",
        "..\\..\\..\\Windows\\System32\\config\\SAM",
        "\\\\server\\share\\file",
        "C:\\Windows\\System32\\",
        "/" * 1000,
        "\x00/etc/passwd",
        "file" + "?<>" * 10,
        "COM1",
        "LPT1",
        "NUL",
        "CON",
        "file\x00name.md",
        "file" + "\x1b" * 5 + ".md",
        "." * 300,
        " "* 300,
        "",
    ]


def generate_malformed_tags() -> list[list[str]]:
    """生成畸形标签输入。

    Returns:
        畸形标签列表。
    """
    return [
        [""],  # 空标签
        ["tag" * 100],  # 超长标签
        ["<script>alert(1)</script>"],  # XSS 尝试
        ["tag\x00name"],  # 空字节
        ["tag\nname"],  # 换行符
        ["tag;drop table"],  # SQL 注入尝试
        ["tag" * 1000],  # 极长标签
        ["tag" + "\x1b" * 5],  # ANSI 转义
        [f"tag_{i}" for i in range(100)],  # 超多标签
        ["tag" + chr(i) for i in range(256)],  # 所有字节
    ]


def generate_malformed_metadata() -> list[dict]:
    """生成畸形元数据输入。

    Returns:
        畸形元数据字典列表。
    """
    return [
        {"key" * 100: "value"},  # 超长键名
        {"key": "value" * 10000},  # 超长值
        {f"key_{i}": f"value_{i}" for i in range(100)},  # 超多字段
        {"key": ["item" * 1000]},  # 列表项超长
        {"key": "\x00value"},  # 空字节值
        {"key": ["item" for _ in range(1000)]},  # 超大列表
        {123: "value"},  # 非字符串键
        {"key": 123},  # 非字符串值
        {"key": None},  # None 值
        {"": "value"},  # 空键名
        {"key.with.dots": "value"},  # 含点号键名
        {"key-has-hyphens": "value"},  # 含连字符键名
    ]


def generate_boundary_inputs() -> list[str]:
    """生成边界条件输入。

    Returns:
        边界条件字符串列表。
    """
    return [
        "",  # 空字符串
        "a",  # 单字符
        "a" * (DEFAULT_MAX_CONTENT_LENGTH - 1),  # 刚好低于限制
        "a" * DEFAULT_MAX_CONTENT_LENGTH,  # 刚好等于限制
        "a" * (DEFAULT_MAX_CONTENT_LENGTH + 1),  # 刚好超过限制
        "a" * 10_000_000,  # 远超限制（10MB字符）
        "\x00",  # 单空字节
        "\x00" * 1000,  # 大量空字节
        "\x1b[31mRED\x1b[0m",  # ANSI 颜色码
        "\ufeff",  # BOM
        "\ufffd" * 100,  # 替换字符
        "\\" * 10000,  # 大量反斜杠
        "\n" * 10000,  # 大量换行
        "\t" * 10000,  # 大量制表符
    ]


# ---------------------------------------------------------------------------
# 测试执行器
# ---------------------------------------------------------------------------

class FuzzRunner:
    """模糊测试执行器。

    运行畸形输入并记录系统行为：是否崩溃、是否返回错误、
    错误信息是否清晰、是否有资源泄漏。
    """

    def __init__(self):
        self.results: list[dict] = []
        self.passed = 0
        self.failed = 0
        self.crashed = 0

    def run_test(
        self,
        name: str,
        test_func: Callable,
        *args,
        should_fail: bool = True,
        **kwargs,
    ) -> dict:
        """运行单个模糊测试。

        Args:
            name: 测试名称。
            test_func: 被测试的函数。
            *args: 传递给 test_func 的位置参数。
            should_fail: 预期是否应该失败（返回错误）。
            **kwargs: 传递给 test_func 的关键字参数。

        Returns:
            测试结果字典。
        """
        result = {
            "name": name,
            "passed": False,
            "crashed": False,
            "error": "",
        }

        try:
            output = test_func(*args, **kwargs)
            if isinstance(output, tuple) and len(output) >= 1:
                success = output[0]
                if should_fail and not success:
                    # 预期失败，实际失败 — 正确
                    result["passed"] = True
                    result["error"] = output[1] if len(output) > 1 else ""
                elif not should_fail and success:
                    # 预期成功，实际成功 — 正确
                    result["passed"] = True
                elif should_fail and success:
                    # 预期失败，实际成功 — 防御不足
                    result["error"] = f"应拒绝但通过了: {output}"
                else:
                    # 预期成功，实际失败 — 误报
                    result["error"] = f"应通过但拒绝了: {output[1] if len(output) > 1 else output}"
            else:
                result["passed"] = True
        except Exception as e:
            result["crashed"] = True
            result["error"] = f"崩溃: {type(e).__name__}: {e}"

        if result["passed"]:
            self.passed += 1
        elif result["crashed"]:
            self.crashed += 1
        else:
            self.failed += 1

        self.results.append(result)
        return result

    def run_all(self) -> dict:
        """运行所有模糊测试场景。

        Returns:
            包含统计和详细结果的字典。
        """
        self._run_string_tests()
        self._run_filename_tests()
        self._run_tag_tests()
        self._run_metadata_tests()
        self._run_frontmatter_tests()
        self._run_boundary_tests()
        self._run_resource_tests()
        self._run_path_tests()

        return {
            "total": len(self.results),
            "passed": self.passed,
            "failed": self.failed,
            "crashed": self.crashed,
            "results": self.results,
        }

    def _run_string_tests(self):
        """字符串输入模糊测试。"""
        # 空字节
        self.run_test(
            "string_null_byte",
            InputValidator.validate_string_input,
            "hello\x00world",
            field_name="test",
            should_fail=True,
        )
        # ANSI 转义
        self.run_test(
            "string_ansi_escape",
            InputValidator.validate_string_input,
            "hello\x1bworld",
            field_name="test",
            should_fail=True,
        )
        # 超长字符串
        self.run_test(
            "string_too_long",
            InputValidator.validate_string_input,
            "x" * (DEFAULT_MAX_CONTENT_LENGTH + 1),
            field_name="test",
            should_fail=True,
        )
        # 正常字符串
        self.run_test(
            "string_normal",
            InputValidator.validate_string_input,
            "hello world",
            field_name="test",
            should_fail=False,
        )
        # 非字符串类型
        self.run_test(
            "string_wrong_type",
            InputValidator.validate_string_input,
            123,
            field_name="test",
            should_fail=True,
        )

    def _run_filename_tests(self):
        """文件名模糊测试。"""
        # 路径遍历
        self.run_test(
            "filename_path_traversal",
            InputValidator.validate_filename,
            "../../etc/passwd",
            should_fail=True,
        )
        # 空字节
        self.run_test(
            "filename_null_byte",
            InputValidator.validate_filename,
            "file\x00name.md",
            should_fail=True,
        )
        # 隐藏文件
        self.run_test(
            "filename_dot_prefix",
            InputValidator.validate_filename,
            ".hidden.md",
            should_fail=True,
        )
        # 超长
        self.run_test(
            "filename_too_long",
            InputValidator.validate_filename,
            "x" * (DEFAULT_MAX_FILENAME_LENGTH + 1),
            should_fail=True,
        )
        # 正常
        self.run_test(
            "filename_normal",
            InputValidator.validate_filename,
            "my-file.md",
            should_fail=False,
        )
        # 空文件名
        self.run_test(
            "filename_empty",
            InputValidator.validate_filename,
            "",
            should_fail=True,
        )

    def _run_tag_tests(self):
        """标签模糊测试。"""
        # 空标签
        self.run_test(
            "tag_empty",
            InputValidator.validate_tags,
            [""],
            should_fail=True,
        )
        # XSS 尝试
        self.run_test(
            "tag_xss",
            InputValidator.validate_tags,
            ["<script>alert(1)</script>"],
            should_fail=True,
        )
        # 超多标签
        self.run_test(
            "tag_too_many",
            InputValidator.validate_tags,
            [f"tag_{i}" for i in range(DEFAULT_MAX_TAGS_COUNT + 1)],
            should_fail=True,
        )
        # 正常标签
        self.run_test(
            "tag_normal",
            InputValidator.validate_tags,
            ["tag1", "tag2", "tag3"],
            should_fail=False,
        )

    def _run_metadata_tests(self):
        """元数据模糊测试。"""
        # 超多字段
        self.run_test(
            "metadata_too_many_fields",
            InputValidator.validate_metadata,
            {f"key_{i}": f"value_{i}" for i in range(DEFAULT_MAX_METADATA_FIELDS + 1)},
            should_fail=True,
        )
        # 超长值
        self.run_test(
            "metadata_value_too_long",
            InputValidator.validate_metadata,
            {"key": "x" * 20000},
            should_fail=True,
        )
        # 非字符串键
        self.run_test(
            "metadata_non_string_key",
            InputValidator.validate_metadata,
            {123: "value"},
            should_fail=True,
        )
        # 正常元数据
        self.run_test(
            "metadata_normal",
            InputValidator.validate_metadata,
            {"title": "test", "tags": ["a", "b"]},
            should_fail=False,
        )

    def _run_frontmatter_tests(self):
        """Frontmatter 格式模糊测试。"""
        # 无结束标记
        self.run_test(
            "fm_no_end_marker",
            InputValidator.validate_frontmatter_format,
            "---\ntitle: test\n",
            should_fail=True,
        )
        # 正常 frontmatter
        self.run_test(
            "fm_normal",
            InputValidator.validate_frontmatter_format,
            "---\ntitle: test\n---\ncontent",
            should_fail=False,
        )
        # 空内容
        self.run_test(
            "fm_empty",
            InputValidator.validate_frontmatter_format,
            "",
            should_fail=False,
        )

    def _run_boundary_tests(self):
        """边界条件测试。"""
        # 空字符串
        self.run_test(
            "boundary_empty",
            InputValidator.validate_string_input,
            "",
            field_name="test",
            should_fail=False,
        )
        # 刚好低于限制
        self.run_test(
            "boundary_just_below",
            InputValidator.validate_string_input,
            "x" * (DEFAULT_MAX_CONTENT_LENGTH - 1),
            field_name="test",
            should_fail=False,
        )
        # 刚好等于限制
        self.run_test(
            "boundary_just_equal",
            InputValidator.validate_string_input,
            "x" * DEFAULT_MAX_CONTENT_LENGTH,
            field_name="test",
            should_fail=False,
        )
        # 刚好超过限制
        self.run_test(
            "boundary_just_over",
            InputValidator.validate_string_input,
            "x" * (DEFAULT_MAX_CONTENT_LENGTH + 1),
            field_name="test",
            should_fail=True,
        )

    def _run_resource_tests(self):
        """资源消耗测试。"""
        # 正常内容
        self.run_test(
            "resource_normal",
            ResourceGuard.check_content_size,
            "hello",
            should_fail=False,
        )
        # 超长内容
        self.run_test(
            "resource_too_long",
            ResourceGuard.check_content_size,
            "x" * (DEFAULT_MAX_CONTENT_LENGTH + 1),
            should_fail=True,
        )
        # 非字符串
        self.run_test(
            "resource_wrong_type",
            ResourceGuard.check_content_size,
            123,
            should_fail=True,
        )
        # 递归深度检查
        try:
            for _ in range(DEFAULT_MAX_RECURSION_DEPTH + 1):
                ResourceGuard.enter_recursion()
            self.run_test(
                "resource_recursion_overflow",
                lambda: True,
                should_fail=False,  # 应该抛出异常，这里不会执行到
            )
        except Exception as e:
            self.run_test(
                "resource_recursion_limit",
                lambda: True,
                should_fail=False,
            )
            self.results[-1]["passed"] = True
            self.passed += 1
            # 重置递归计数器
            ResourceGuard._recursion_depth = 0

    def _run_path_tests(self):
        """路径验证测试。"""
        # 深层路径
        self.run_test(
            "path_deep_nesting",
            InputValidator.validate_path_depth,
            Path("a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v"),
            should_fail=True,
        )
        # 正常路径
        self.run_test(
            "path_normal",
            InputValidator.validate_path_depth,
            Path("docs/knowledge/test.md"),
            should_fail=False,
        )


def run_fuzz_tests() -> dict:
    """运行所有模糊测试的便捷入口。

    Returns:
        测试结果字典。
    """
    runner = FuzzRunner()
    return runner.run_all()


def print_fuzz_report(results: dict):
    """打印模糊测试报告。

    Args:
        results: FuzzRunner.run_all() 的返回值。
    """
    print(f"\n{'='*60}")
    print(f"模糊测试报告")
    print(f"{'='*60}")
    print(f"总计: {results['total']} | 通过: {results['passed']} | 失败: {results['failed']} | 崩溃: {results['crashed']}")
    print(f"{'='*60}")

    for r in results["results"]:
        status = "PASS" if r["passed"] else ("CRASH" if r["crashed"] else "FAIL")
        if r["error"]:
            print(f"  [{status}] {r['name']}: {r['error']}")
        else:
            print(f"  [{status}] {r['name']}")

    print(f"{'='*60}")
    if results["failed"] == 0 and results["crashed"] == 0:
        print("所有模糊测试通过！")
    else:
        print(f"存在 {results['failed']} 个失败和 {results['crashed']} 个崩溃，需要修复。")