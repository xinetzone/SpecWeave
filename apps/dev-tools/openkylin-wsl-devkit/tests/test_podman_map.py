"""podman 映射区间纯函数测试：ranges_overlap 12 类 off-by-one + parse_subordinate_file 边角。

强制门禁（I-2 洞察要求）：ranges_overlap 12 类全不通过不允许合并。
所有函数无副作用，无需 WSL mock。
"""

import pytest

from okw.podman import (
    STANDARD_SUBUID_COUNT,
    SubordinateMapEntry,
    has_valid_mapping_for,
    parse_subordinate_file,
    range_conflicts_with_standard,
    ranges_overlap,
)


def _e(name, start, count):
    return SubordinateMapEntry(name=name, start=start, count=count)


# ---------------------------------------------------------------------------
# ranges_overlap：12 类 off-by-one 覆盖
#   判定规则：左闭右开 [start, end)，重叠 iff a.start < b.end AND b.start < a.end
# ---------------------------------------------------------------------------

class TestRangesOverlap:
    # ——— 明确重叠 4 类 ———
    def test_identical(self):
        a, b = _e("a", 100000, 65536), _e("b", 100000, 65536)
        assert ranges_overlap(a, b)

    def test_contained(self):
        outer = _e("x", 100000, 100000)
        inner = _e("y", 100100, 1000)
        assert ranges_overlap(outer, inner)

    def test_a_starts_inside_b(self):
        a = _e("a", 150000, 20000)      # [150000, 170000)
        b = _e("b", 100000, 65536)       # [100000, 165536)
        assert ranges_overlap(a, b)

    def test_a_overlap_one(self):
        # 恰重叠 1 个值：A=[100,200) B=[199,250) => 199 同时属于 A 的 end 前、B 的 start，有重叠
        a = _e("a", 100, 100)             # end=200
        b = _e("b", 199, 51)              # start=199 < 200 且 b.start=199 < a.end=200，a.start=100 < b.end=250
        assert ranges_overlap(a, b)

    # ——— 明确不重叠 4 类 ———
    def test_disjoint_far_left(self):
        a = _e("a", 0, 100)
        b = _e("b", 100000, 65536)
        assert not ranges_overlap(a, b)

    def test_disjoint_far_right(self):
        a = _e("a", 200000, 1)
        b = _e("b", 100000, 65536)
        assert not ranges_overlap(a, b)

    def test_touching_endpoints_not_overlap(self):
        # 端点恰好相等 A.end == B.start：按左闭右开，100 不属于 A、100 属于 B 的起点 -> 不重叠
        a = _e("a", 0, 100)               # [0, 100)
        b = _e("b", 100, 100)             # [100, 200)
        assert a.end == b.start == 100
        assert not ranges_overlap(a, b)

    def test_single_element_not_touching(self):
        # A 长度 1: [5,6)；B=[7,8) -> 不重叠
        a = _e("a", 5, 1)
        b = _e("b", 7, 1)
        assert not ranges_overlap(a, b)

    # ——— 交换律 2 类（确保 a,b 调换结果一致）———
    def test_commutative_overlap(self):
        a = _e("a", 100, 1000)
        b = _e("b", 500, 1000)
        assert ranges_overlap(a, b) == ranges_overlap(b, a) is True

    def test_commutative_disjoint(self):
        a = _e("a", 0, 5)
        b = _e("b", 10, 5)
        assert ranges_overlap(a, b) == ranges_overlap(b, a) is False

    # ——— 单元素 / 边界 2 类 ———
    def test_single_element_overlap_itself(self):
        a = _e("a", 42, 1)
        assert ranges_overlap(a, a)

    def test_zero_or_negative_count_not_overlap(self):
        # 语义上 count<=0 是非法条目；parse_subordinate_file 已过滤；但函数端不应报错
        x = _e("x", 100000, 0)            # end == start，区间空
        y = _e("y", 100000, 65536)
        # 空区间与任何区间都不重叠（start == end 使不等式 a.start < b.end 成立但 b.start < a.end -> 100000 < 100000 不成立）
        assert not ranges_overlap(x, y)


# ---------------------------------------------------------------------------
# range_conflicts_with_standard（固定与 [100000, 165536) 比较）
# ---------------------------------------------------------------------------

class TestRangeConflictsWithStandard:
    def test_standard_itself_conflicts(self):
        assert range_conflicts_with_standard(
            SubordinateMapEntry("x", 100000, STANDARD_SUBUID_COUNT)
        )

    def test_touching_standard_left_no_conflict(self):
        # [94464, 100000) end=100000 == 标准 start -> 不重叠
        assert not range_conflicts_with_standard(_e("u", 94464, 5536))

    def test_touching_standard_right_no_conflict(self):
        # [165536, 231072) start=165536 == 标准 end -> 不重叠
        assert not range_conflicts_with_standard(_e("u", 165536, 65536))

    def test_partial_overlap_conflicts(self):
        # 左溢出一点
        assert range_conflicts_with_standard(_e("u", 160000, 10000))


# ---------------------------------------------------------------------------
# parse_subordinate_file：三列格式 + 边角过滤
# ---------------------------------------------------------------------------

class TestParseSubordinateFile:
    def test_clean_file(self):
        text = (
            "root:100000:65536\n"
            "openkylin:165536:65536\n"
        )
        entries = parse_subordinate_file(text)
        assert len(entries) == 2
        assert entries[0].name == "root" and entries[0].start == 100000 and entries[0].count == 65536
        assert entries[1].name == "openkylin" and entries[1].start == 165536

    def test_comments_and_blank_lines_ignored(self):
        text = (
            "# 由 shadow-utils 管理，勿手动编辑\n"
            "\n"
            "root:100000:65536\n"
            "  \n"
            "# trailing\n"
        )
        assert len(parse_subordinate_file(text)) == 1

    def test_malformed_rows_reject_entire_file(self):
        # 畸形行不能被跳过，否则冲突信息会丢失并可能误写映射。
        text = (
            "good:100000:65536\n"
            "bad-columns-only-two:100000\n"
            "bad-columns-four:100:200:300:400\n"
            "non-int-start:abc:65536\n"
            "non-int-count:100000:xyz\n"
            "zero-start:0:65536\n"
            "neg-count:100000:-100\n"
            "zero-count:100000:0\n"
            "has space in name:100000:65536\n"
        )
        with pytest.raises(ValueError, match="映射"):
            parse_subordinate_file(text)

    def test_surrounding_whitespace_is_normalized(self):
        entries = parse_subordinate_file("  whitespace-ok  :  100000 : 65536 \n")
        assert entries == [_e("whitespace-ok", 100000, 65536)]

    def test_empty_file(self):
        assert parse_subordinate_file("") == []
        assert parse_subordinate_file("\n\n") == []


# ---------------------------------------------------------------------------
# has_valid_mapping_for：同用户不冲突、单区间>=65536、与其它用户不冲突
# ---------------------------------------------------------------------------

class TestHasValidMappingFor:
    def test_single_entry_at_standard(self):
        entries = [_e("openkylin", 100000, 65536)]
        assert has_valid_mapping_for(entries, "openkylin")

    def test_count_below_65536_invalid(self):
        entries = [_e("openkylin", 100000, 1000)]
        assert not has_valid_mapping_for(entries, "openkylin")

    def test_two_adjacent_entries_sum_not_allowed(self):
        # 同用户两个相邻短区间：单条各自 < 65536 且不重叠 -> 无效
        entries = [_e("o", 100000, 30000), _e("o", 130000, 40000)]
        assert not has_valid_mapping_for(entries, "o")

    def test_same_user_two_overlapping_entries_invalid(self):
        # 同名用户内部重叠 -> 直接 False
        entries = [_e("o", 100000, 65536), _e("o", 150000, 1000)]
        assert not has_valid_mapping_for(entries, "o")

    def test_conflict_with_other_user(self):
        # openkylin 有一条>=65536，但其它用户区间与之重叠 -> 无效
        entries = [
            _e("openkylin", 100000, 65536),
            _e("other", 120000, 100000),
        ]
        assert not has_valid_mapping_for(entries, "openkylin")

    def test_other_user_touching_not_conflict(self):
        # 其他用户区间恰好相接（端点相等）-> 不冲突 -> 有效
        entries = [
            _e("openkylin", 100000, 65536),   # end=165536
            _e("other", 165536, 65536),       # start=165536
        ]
        assert has_valid_mapping_for(entries, "openkylin")

    def test_user_not_in_entries(self):
        entries = [_e("other", 100000, 65536)]
        assert not has_valid_mapping_for(entries, "openkylin")

    def test_multiple_entries_pick_valid_one(self):
        # 用户有一条短的（无效）+ 一条长的且不重叠 -> 有效
        entries = [
            _e("openkylin", 100000, 1000),
            _e("openkylin", 1000000, 65536),
            _e("other", 100000, 65536),
        ]
        assert has_valid_mapping_for(entries, "openkylin")
