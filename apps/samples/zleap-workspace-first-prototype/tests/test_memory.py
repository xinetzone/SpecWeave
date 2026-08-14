"""A-02 行动项单元测试：Agent 记忆三层治理模式。

覆盖 Memory 模块：三分区（人/事/经验）、双线设计（A线/B线）、
经验记忆准入规则（允许 4 类 / 禁止 6 类）。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from memory import (
    MemoryManager,
    MemoryStore,
    PARTITION_PEOPLE,
    PARTITION_TASK,
    PARTITION_EXPERIENCE,
    ALLOWED_EXPERIENCE_KEYS,
    FORBIDDEN_EXPERIENCE_KEYS,
)


class TestMemoryStore(unittest.TestCase):
    """单个记忆分区存储测试。"""

    def setUp(self) -> None:
        self.store = MemoryStore(PARTITION_PEOPLE)

    def test_write_and_read(self):
        self.store.write("语言偏好", "中文")
        self.assertEqual(self.store.read("语言偏好"), "中文")

    def test_read_missing_returns_none(self):
        self.assertIsNone(self.store.read("不存在"))

    def test_read_all_returns_copy(self):
        self.store.write("a", 1)
        data = self.store.read_all()
        data["b"] = 2  # 修改副本不影响原存储
        self.assertEqual(len(self.store), 1)

    def test_len(self):
        self.store.write("a", 1)
        self.store.write("b", 2)
        self.assertEqual(len(self.store), 2)


class TestMemoryPartitions(unittest.TestCase):
    """记忆三分区测试。"""

    def setUp(self) -> None:
        self.mem = MemoryManager()

    def test_three_partitions_exist(self):
        parts = self.mem.all_partitions()
        self.assertIn(PARTITION_PEOPLE, parts)
        self.assertIn(PARTITION_TASK, parts)
        self.assertIn(PARTITION_EXPERIENCE, parts)

    def test_write_people_note_a_line(self):
        self.mem.write_people_note("语言偏好", "中文")
        self.assertEqual(self.mem.read(PARTITION_PEOPLE, "语言偏好"), "中文")

    def test_write_core_record_b_line(self):
        self.mem.write_core_record("项目", "测试")
        self.assertEqual(self.mem.read(PARTITION_TASK, "项目"), "测试")

    def test_write_unknown_partition_raises(self):
        with self.assertRaises(KeyError):
            self.mem.write("unknown", "k", "v")

    def test_partitions_isolated(self):
        # 写入 people 不影响 task
        self.mem.write_people_note("k", "v")
        self.assertIsNone(self.mem.read(PARTITION_TASK, "k"))


class TestExperienceAdmissionRule(unittest.TestCase):
    """经验记忆准入规则测试（允许 4 类 / 禁止 6 类）。"""

    def setUp(self) -> None:
        self.mem = MemoryManager()

    def test_allowed_content_written(self):
        ok = self.mem.write_experience("可复用流程：先切工作区再组装上下文")
        self.assertTrue(ok)
        self.assertEqual(len(self.mem.read_partition(PARTITION_EXPERIENCE)), 1)

    def test_forbidden_customer_name_blocked(self):
        blocked = self.mem.write_experience("客户名：某集团公司")
        self.assertFalse(blocked)

    def test_forbidden_financial_blocked(self):
        blocked = self.mem.write_experience("财务事实：营收 100 万")
        self.assertFalse(blocked)

    def test_forbidden_company_name_blocked(self):
        blocked = self.mem.write_experience("公司名：某某科技")
        self.assertFalse(blocked)

    def test_no_allowed_keyword_blocked(self):
        # 不含任何允许类别关键词
        blocked = self.mem.write_experience("今天天气不错")
        self.assertFalse(blocked)

    def test_admitted_content_not_polluted(self):
        # 合规经验写入后，禁止内容不应进入存储
        self.mem.write_experience("可复用流程：先切工作区")
        self.mem.write_experience("客户名：某公司")
        self.assertEqual(len(self.mem.read_partition(PARTITION_EXPERIENCE)), 1)

    def test_all_allowed_keys_recognized(self):
        for keyword in ALLOWED_EXPERIENCE_KEYS:
            ok = self.mem.write_experience(f"{keyword}：示例内容")
            self.assertTrue(ok, f"允许类别 {keyword} 应被接受")

    def test_all_forbidden_keys_recognized(self):
        for keyword in FORBIDDEN_EXPERIENCE_KEYS:
            blocked = self.mem.write_experience(f"{keyword}：示例内容")
            self.assertFalse(blocked, f"禁止类别 {keyword} 应被拦截")


if __name__ == "__main__":
    unittest.main()