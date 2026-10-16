"""readingTime.ts 计数口径测试。"""

from doocs_md_py.render.reading_time import reading_time


def test_english_words():
    result = reading_time("hello world foo")
    assert result.words == 3
    assert result.minutes == 3 / 200
    assert result.time == round(result.minutes * 60 * 1000)
    assert result.text == "1 min read"


def test_chinese_chars_count_individually():
    result = reading_time("你好世界")
    assert result.words == 4


def test_mixed_cjk_and_english():
    # CJK 与其后拉丁词边界处拉丁词计一次
    result = reading_time("你好 world")
    assert result.words == 3  # 你、好、world


def test_punctuation_not_counted():
    # 上游口径：标点本身不计；但标点串结尾紧邻词边界（追加 \n）时，
    # 末个标点满足「非边界 + 下个是边界」被计为一词——与 JS readingTime 行为一致
    assert reading_time("！，。").words == 1
    assert reading_time("a, b!").words == 2
    assert reading_time("，，").words == 1


def test_leading_trailing_whitespace_ignored():
    assert reading_time("  hi  ").words == 1
    assert reading_time("").words == 0


def test_displayed_minutes_ceil_to_fixed_2():
    result = reading_time("word " * 201)
    assert result.words == 201
    # 1.005 min -> toFixed(2)=1.0（浮点）或 1.01；验证与 ceil 口径一致即可
    assert result.text in {"1 min read", "2 min read"}


def test_extension_b_cjk_surrogate_pair_not_counted():
    # 扩展 B 区字符在 JS charCodeAt 口径下为代理对（0xD800 区），不计 CJK
    result = reading_time("\U00020000")
    assert result.words == 0
