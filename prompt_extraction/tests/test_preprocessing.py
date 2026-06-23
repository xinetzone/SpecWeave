"""文本预处理模块单元测试"""

import pytest

from prompt_extraction.preprocessing.cleaner import (
    clean_text,
    extract_markdown_structure,
    identify_metadata,
    normalize_whitespace,
    strip_markup,
)
from prompt_extraction.preprocessing.normalizer import (
    normalize_fullwidth,
    normalize_punctuation,
    normalize_text,
)


# ============================================================================
# normalize_whitespace 测试
# ============================================================================


class TestNormalizeWhitespace:
    """测试空白规范化功能"""

    def test_多余空白规范化(self):
        """连续多个空格应规范化为单个空格"""
        result = normalize_whitespace("hello    world")
        assert result == "hello world"

    def test_制表符规范化(self):
        """制表符应规范化为空格"""
        result = normalize_whitespace("hello\t\tworld")
        assert result == "hello world"

    def test_换行符规范化(self):
        """换行符应规范化为空格"""
        result = normalize_whitespace("hello\n\nworld")
        assert result == "hello world"

    def test_混合空白规范化(self):
        """混合多种空白字符应规范化为单个空格"""
        result = normalize_whitespace("hello \t\n\r world \t test")
        assert result == "hello world test"

    def test_首尾空白去除(self):
        """首尾空白应被去除"""
        result = normalize_whitespace("  hello world  ")
        assert result == "hello world"

    def test_首尾换行去除(self):
        """首尾换行应被去除"""
        result = normalize_whitespace("\n\nhello world\n\n")
        assert result == "hello world"

    def test_空字符串(self):
        """空字符串应返回空字符串"""
        result = normalize_whitespace("")
        assert result == ""

    def test_纯空白字符串(self):
        """纯空白字符串应返回空字符串"""
        result = normalize_whitespace("   \t\n  ")
        assert result == ""

    def test_纯文本不变性(self):
        """纯文本（无多余空白）应保持不变"""
        result = normalize_whitespace("hello world")
        assert result == "hello world"


# ============================================================================
# strip_markup 测试
# ============================================================================


class TestStripMarkup:
    """测试 Markdown/HTML 格式标记去除功能"""

    def test_粗体去除(self):
        """**粗体标记**应被去除，保留文本内容"""
        result = strip_markup("这是 **粗体** 文本")
        assert result == "这是 粗体 文本"

    def test_双下划线粗体去除(self):
        """__粗体标记__应被去除，保留文本内容"""
        result = strip_markup("这是 __粗体__ 文本")
        assert result == "这是 粗体 文本"

    def test_斜体去除(self):
        """*斜体标记*应被去除，保留文本内容"""
        result = strip_markup("这是 *斜体* 文本")
        assert result == "这是 斜体 文本"

    def test_下划线斜体去除(self):
        """_斜体标记_应被去除，保留文本内容"""
        result = strip_markup("这是 _斜体_ 文本")
        assert result == "这是 斜体 文本"

    def test_删除线去除(self):
        """~~删除线~~应被去除，保留文本内容"""
        result = strip_markup("这是 ~~删除线~~ 文本")
        assert result == "这是 删除线 文本"

    def test_行内代码去除(self):
        """`行内代码`应被去除，保留文本内容"""
        result = strip_markup("这是 `code` 文本")
        assert result == "这是 code 文本"

    def test_代码块去除(self):
        """```代码块```应被去除"""
        result = strip_markup("文本\n```\ncode block\n```\n更多文本")
        assert "code block" not in result
        assert "文本" in result
        assert "更多文本" in result

    def test_链接去除保留文本(self):
        """[text](url) 应去除标记，保留链接文本"""
        result = strip_markup("请访问 [示例](https://example.com) 网站")
        assert result == "请访问 示例 网站"

    def test_图片去除保留alt文本(self):
        """![alt](url) 应去除标记，保留 alt 文本"""
        result = strip_markup("这是一张 ![图片](image.png) 截图")
        assert result == "这是一张 图片 截图"

    def test_HTML标签去除(self):
        """HTML 标签应被去除"""
        result = strip_markup("这是 <b>加粗</b> 和 <i>斜体</i> 文本")
        assert result == "这是 加粗 和 斜体 文本"

    def test_标题标记去除(self):
        """标题标记 # 应被去除，保留标题文本"""
        result = strip_markup("# 一级标题\n## 二级标题\n普通文本")
        assert "一级标题" in result
        assert "二级标题" in result
        assert "普通文本" in result
        assert "#" not in result

    def test_列表标记去除(self):
        """列表标记 - 应被去除，保留列表项文本"""
        result = strip_markup("- 列表项1\n- 列表项2\n- 列表项3")
        assert "列表项1" in result
        assert "列表项2" in result
        assert "列表项3" in result

    def test_有序列表标记去除(self):
        """有序列表标记应被去除，保留列表项文本"""
        result = strip_markup("1. 第一项\n2. 第二项\n3. 第三项")
        assert "第一项" in result
        assert "第二项" in result
        assert "第三项" in result

    def test_引用标记去除(self):
        """引用标记 > 应被去除"""
        result = strip_markup("> 这是一段引用文本")
        assert result == "这是一段引用文本"

    def test_空字符串(self):
        """空字符串应返回空字符串"""
        result = strip_markup("")
        assert result == ""

    def test_纯文本不变性(self):
        """纯文本（无任何标记）应保持不变"""
        result = strip_markup("这是一段纯文本，没有任何标记。")
        assert result == "这是一段纯文本，没有任何标记。"


# ============================================================================
# extract_markdown_structure 测试
# ============================================================================


class TestExtractMarkdownStructure:
    """测试 Markdown 结构提取功能"""

    def test_标题提取(self):
        """应正确提取各级标题及其层级"""
        text = "# 一级标题\n## 二级标题\n### 三级标题"
        structure = extract_markdown_structure(text)
        assert len(structure["headings"]) == 3
        assert structure["headings"][0] == {"level": 1, "text": "一级标题"}
        assert structure["headings"][1] == {"level": 2, "text": "二级标题"}
        assert structure["headings"][2] == {"level": 3, "text": "三级标题"}

    def test_无序列表提取(self):
        """应正确提取无序列表项"""
        text = "- 第一项\n- 第二项\n- 第三项"
        structure = extract_markdown_structure(text)
        assert len(structure["list_items"]) == 3
        assert structure["list_items"][0] == "第一项"
        assert structure["list_items"][1] == "第二项"
        assert structure["list_items"][2] == "第三项"

    def test_有序列表提取(self):
        """应正确提取有序列表项"""
        text = "1. 步骤一\n2. 步骤二\n3. 步骤三"
        structure = extract_markdown_structure(text)
        assert len(structure["list_items"]) == 3
        assert structure["list_items"][0] == "步骤一"
        assert structure["list_items"][1] == "步骤二"
        assert structure["list_items"][2] == "步骤三"

    def test_代码块提取(self):
        """应正确提取代码块内容"""
        text = "```python\nprint('hello')\nprint('world')\n```"
        structure = extract_markdown_structure(text)
        assert len(structure["code_blocks"]) == 1
        assert "print('hello')" in structure["code_blocks"][0]

    def test_无结构的纯文本(self):
        """纯文本应返回空结构"""
        text = "这是一段纯文本，没有任何结构。"
        structure = extract_markdown_structure(text)
        assert structure["headings"] == []
        assert structure["list_items"] == []
        assert structure["code_blocks"] == []

    def test_空字符串(self):
        """空字符串应返回空结构"""
        structure = extract_markdown_structure("")
        assert structure["headings"] == []
        assert structure["list_items"] == []
        assert structure["code_blocks"] == []

    def test_星号列表提取(self):
        """使用 * 标记的无序列表应被正确提取"""
        text = "* 项目A\n* 项目B\n* 项目C"
        structure = extract_markdown_structure(text)
        assert len(structure["list_items"]) == 3
        assert structure["list_items"][0] == "项目A"

    def test_加号列表提取(self):
        """使用 + 标记的无序列表应被正确提取"""
        text = "+ 任务一\n+ 任务二"
        structure = extract_markdown_structure(text)
        assert len(structure["list_items"]) == 2
        assert structure["list_items"][0] == "任务一"


# ============================================================================
# identify_metadata 测试
# ============================================================================


class TestIdentifyMetadata:
    """测试元数据识别功能"""

    def test_URL识别(self):
        """应正确识别文本中的 URL"""
        text = "请访问 https://example.com 了解更多信息"
        metadata = identify_metadata(text)
        assert "https://example.com" in metadata["urls"]

    def test_多个URL识别(self):
        """应正确识别多个 URL"""
        text = "参考 https://a.com 和 https://b.com/page"
        metadata = identify_metadata(text)
        assert len(metadata["urls"]) == 2
        assert "https://a.com" in metadata["urls"]
        assert "https://b.com/page" in metadata["urls"]

    def test_email识别(self):
        """应正确识别 email 地址"""
        text = "请联系 admin@example.com 获取帮助"
        metadata = identify_metadata(text)
        assert "admin@example.com" in metadata["emails"]

    def test_多个email识别(self):
        """应正确识别多个 email 地址"""
        text = "发送至 a@test.com 和 b@test.org"
        metadata = identify_metadata(text)
        assert len(metadata["emails"]) == 2

    def test_代码块识别(self):
        """应正确识别代码块"""
        text = "代码如下：\n```\nprint('hello')\n```\n结束"
        metadata = identify_metadata(text)
        assert len(metadata["code_blocks"]) == 1

    def test_core_text生成(self):
        """core_text 应去除 URL、email 和代码块"""
        text = "正文内容 https://example.com 更多 admin@test.com 文本"
        metadata = identify_metadata(text)
        core = metadata["core_text"]
        assert "https://example.com" not in core
        assert "admin@test.com" not in core
        assert "正文内容" in core
        assert "更多" in core
        assert "文本" in core

    def test_空字符串(self):
        """空字符串应返回空元数据"""
        metadata = identify_metadata("")
        assert metadata["urls"] == []
        assert metadata["emails"] == []
        assert metadata["code_blocks"] == []
        assert metadata["core_text"] == ""

    def test_纯文本无元数据(self):
        """纯文本（无 URL/email/代码块）应返回空的元数据列表"""
        text = "这是一段纯文本，没有任何元数据。"
        metadata = identify_metadata(text)
        assert metadata["urls"] == []
        assert metadata["emails"] == []
        assert metadata["code_blocks"] == []
        assert metadata["core_text"] == text


# ============================================================================
# clean_text 测试
# ============================================================================

class TestCleanText:
    """测试 clean_text 统一入口"""

    def test_返回三元组(self):
        """应返回 (清洗文本, 结构, 元数据) 三元组"""
        result = clean_text("hello world")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_清洗后文本(self):
        """清洗后的文本应去除 Markdown 标记并规范化空白"""
        cleaned, structure, metadata = clean_text("**hello**   *world*")
        assert cleaned == "hello world"

    def test_结构提取(self):
        """应正确提取 Markdown 结构"""
        text = "# 标题\n## 子标题\n- 项目1\n- 项目2"
        _, structure, _ = clean_text(text)
        assert len(structure["headings"]) == 2
        assert len(structure["list_items"]) == 2

    def test_元数据提取(self):
        """应正确提取元数据"""
        text = "访问 https://example.com 或联系 admin@test.com"
        _, _, metadata = clean_text(text)
        assert len(metadata["urls"]) == 1
        assert len(metadata["emails"]) == 1

    def test_空字符串(self):
        """空字符串应返回空三元组"""
        result = clean_text("")
        assert result[0] == ""
        assert result[1]["headings"] == []
        assert result[1]["list_items"] == []
        assert result[1]["code_blocks"] == []
        assert result[2]["urls"] == []
        assert result[2]["emails"] == []
        assert result[2]["code_blocks"] == []
        assert result[2]["core_text"] == ""


# ============================================================================
# normalize_fullwidth 测试
# ============================================================================


class TestNormalizeFullwidth:
    """测试全角字符转半角功能"""

    def test_全角字母转半角(self):
        """全角英文字母应转换为半角"""
        result = normalize_fullwidth("Ｈｅｌｌｏ")
        assert result == "Hello"

    def test_全角数字转半角(self):
        """全角数字应转换为半角"""
        result = normalize_fullwidth("１２３４５")
        assert result == "12345"

    def test_全角标点转半角(self):
        """全角标点符号应转换为半角"""
        result = normalize_fullwidth("！＠＃＄％")
        assert result == "!@#$%"

    def test_全角空格转半角(self):
        """全角空格应转换为半角空格"""
        result = normalize_fullwidth("hello\u3000world")
        assert result == "hello world"

    def test_混合全角半角(self):
        """混合文本中的全角部分应正确转换"""
        result = normalize_fullwidth("Hello　Ｗｏｒｌｄ　１２３")
        assert result == "Hello World 123"

    def test_空字符串(self):
        """空字符串应返回空字符串"""
        result = normalize_fullwidth("")
        assert result == ""

    def test_纯半角不变性(self):
        """纯半角文本应保持不变"""
        result = normalize_fullwidth("Hello World 123")
        assert result == "Hello World 123"


# ============================================================================
# normalize_punctuation 测试
# ============================================================================


class TestNormalizePunctuation:
    """测试标点符号规范化功能"""

    def test_中文逗号转英文(self):
        """中文逗号应转换为英文逗号"""
        result = normalize_punctuation("苹果，香蕉，橘子")
        assert result == "苹果,香蕉,橘子"

    def test_中文句号转英文(self):
        """中文句号应转换为英文句号"""
        result = normalize_punctuation("今天天气很好。")
        assert result == "今天天气很好."

    def test_中文问号感叹号转换(self):
        """中文问号和感叹号应转换为英文标点"""
        result = normalize_punctuation("你好！今天怎么样？")
        assert result == "你好!今天怎么样?"

    def test_中文冒号分号转换(self):
        """中文冒号和分号应转换为英文标点"""
        result = normalize_punctuation("注意：以下内容；请查看")
        assert result == "注意:以下内容;请查看"

    def test_中文括号转换(self):
        """中文括号应转换为英文括号"""
        result = normalize_punctuation("（这是括号）【这是方括号】")
        assert result == "(这是括号)[这是方括号]"

    def test_中文书名号转换(self):
        """中文书名号应转换为英文尖括号"""
        result = normalize_punctuation("《书名》")
        assert result == "<书名>"

    def test_中文引号转换(self):
        """中文引号应转换为英文引号"""
        result = normalize_punctuation("他说：\u201c你好\u201d")
        assert result == "他说:\"你好\""

    def test_省略号转换(self):
        """省略号应转换为英文句点"""
        result = normalize_punctuation("等等……")
        assert result == "等等..."

    def test_破折号转换(self):
        """破折号应转换为英文连字符"""
        result = normalize_punctuation("这是——一个例子")
        assert result == "这是--一个例子"

    def test_空字符串(self):
        """空字符串应返回空字符串"""
        result = normalize_punctuation("")
        assert result == ""

    def test_纯英文标点不变性(self):
        """纯英文标点文本应保持不变"""
        result = normalize_punctuation("Hello, world! How are you?")
        assert result == "Hello, world! How are you?"


# ============================================================================
# normalize_text 测试
# ============================================================================


class TestNormalizeText:
    """测试 normalize_text 统一入口"""

    def test_全角转半角加标点规范化(self):
        """应依次执行全角转换和标点规范化"""
        result = normalize_text("Ｈｅｌｌｏ，Ｗｏｒｌｄ！")
        assert result == "Hello,World!"

    def test_中文文本标准化(self):
        """中文文本应正确标准化"""
        result = normalize_text("你好，世界！欢迎访问：https://example.com")
        assert result == "你好,世界!欢迎访问:https://example.com"

    def test_空字符串(self):
        """空字符串应返回空字符串"""
        result = normalize_text("")
        assert result == ""

    def test_纯文本不变性(self):
        """纯英文半角文本应保持不变"""
        result = normalize_text("Hello World 123")
        assert result == "Hello World 123"


# ============================================================================
# 综合场景测试
# ============================================================================


class TestIntegration:
    """综合场景测试"""

    def test_cleaner加normalizer串联(self):
        """清洗后标准化应正常工作"""
        from prompt_extraction.preprocessing.cleaner import normalize_whitespace as nw
        from prompt_extraction.preprocessing.normalizer import normalize_text as nt

        raw = "**Ｈｅｌｌｏ**\t　**Ｗｏｒｌｄ**"
        cleaned = nw(raw)
        normalized = nt(cleaned)
        # 清洗后：**Ｈｅｌｌｏ** **Ｗｏｒｌｄ**（空白规范化）
        # 标准化后：半角 + 标点统一
        assert "Hello" in normalized
        assert "World" in normalized

    def test_PromptRecord字段映射(self):
        """验证 clean_text 返回的结构与 PromptRecord 字段兼容"""
        from prompt_extraction.models import PromptRecord

        text = "# 任务\n请完成以下任务：\n- 步骤1\n- 步骤2\n\n```python\nprint('hello')\n```"
        cleaned, structure, metadata = clean_text(text)

        record = PromptRecord(
            id="test-001",
            original_text=text,
            cleaned_text=cleaned,
            markdown_structure=structure,
        )
        assert record.cleaned_text == cleaned
        assert record.markdown_structure is not None
        assert len(record.markdown_structure["headings"]) == 1
        assert len(record.markdown_structure["list_items"]) == 2
        assert len(record.markdown_structure["code_blocks"]) == 1