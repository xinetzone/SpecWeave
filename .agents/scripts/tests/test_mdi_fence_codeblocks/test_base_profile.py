from .helpers import _parse_doc, _make_graphql_doc_md

class TestBaseProfileFenceReconstruction:
    """测试BaseProfile的fence重建和code block遍历功能。"""

    def test_get_full_text_includes_directive_fence_header(self, parser, graphql_profile):
        """get_full_text()应包含directive fence的header行，如`{query} getUser`。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        assert "{query} getUser" in full_text, "directive fence header {query} getUser 应出现在full_text中"
        assert "{query} listPosts" in full_text, "directive fence header {query} listPosts 应出现在full_text中"
        assert "{mutation} createPost" in full_text, "directive fence header {mutation} createPost 应出现在full_text中"
        assert "{subscription} onNewPost" in full_text, "directive fence header {subscription} onNewPost 应出现在full_text中"

    def test_get_full_text_includes_graphql_code_block(self, parser, graphql_profile):
        """get_full_text()应包含graphql code block的fence header和内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        assert "```graphql" in full_text, "graphql fence header应出现在full_text中"
        assert "type User {" in full_text, "type User 定义应出现在full_text中"
        assert "type Post {" in full_text, "type Post 定义应出现在full_text中"

    def test_get_full_text_wraps_code_blocks_with_fences(self, parser, graphql_profile):
        """get_full_text()应用```包裹code block内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        fence_count = full_text.count("```")
        assert fence_count >= 6, f"至少应有6个```标记，实际{fence_count}个"

    def test_get_section_content_includes_fences(self, parser, graphql_profile):
        """get_section_content()应包含fence header和内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        schema_content = graphql_profile.get_section_content(doc, "schema")

        assert "```graphql" in schema_content, "Schema章节内容应包含graphql fence header"
        assert "type User {" in schema_content, "Schema章节应包含type User定义"

    def test_iter_code_blocks_yields_all_blocks(self, parser, graphql_profile):
        """iter_code_blocks()应遍历所有章节的code blocks（包括子章节中的）。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)

        blocks = list(graphql_profile.iter_code_blocks(doc))
        languages = [cb.language for _, cb in blocks]

        assert len(blocks) >= 5, f"至少应有5个code blocks，实际{len(blocks)}个"
        assert "directive:query" in languages, "应包含directive:query code blocks"
        assert "directive:mutation" in languages, "应包含directive:mutation code blocks"
        assert "directive:subscription" in languages, "应包含directive:subscription code blocks"
        assert "graphql" in languages, "应包含graphql code blocks"

    def test_iter_code_blocks_in_subsections(self, parser, graphql_profile):
        """iter_code_blocks()应递归遍历子章节中的code blocks。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)

        blocks = list(graphql_profile.iter_code_blocks(doc))
        directive_blocks = [(s.title, cb) for s, cb in blocks if cb.language and cb.language.startswith("directive:")]

        query_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:query"]
        assert len(query_blocks) == 2, f"应找到2个query directive（getUser, listPosts），实际{len(query_blocks)}个"

        mutation_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:mutation"]
        assert len(mutation_blocks) == 1, f"应找到1个mutation directive（createPost），实际{len(mutation_blocks)}个"

        subscription_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:subscription"]
        assert len(subscription_blocks) == 1, f"应找到1个subscription directive（onNewPost），实际{len(subscription_blocks)}个"

    def test_format_fence_header_directive(self, graphql_profile):
        """_format_fence_header()应正确格式化directive fence header。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="directive:query",
            meta="getUser id: ID!",
            content=":arg id: ID!\n:returns User",
            purpose="directive",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == "{query} getUser id: ID!", f"directive header应为{{query}} getUser id: ID!，实际{header}"

    def test_format_fence_header_plain_code(self, graphql_profile):
        """_format_fence_header()应正确格式化普通code block fence header。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="graphql",
            meta="",
            content="type User { id: ID! }",
            purpose="example",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == "graphql", f"plain code header应为'graphql'，实际'{header}'"

    def test_format_fence_header_with_meta(self, graphql_profile):
        """_format_fence_header()应正确格式化带meta的code block。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="python",
            meta='linenums="true"',
            content="print('hello')",
            purpose="example",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == 'python linenums="true"', f"带meta的header应为'python linenums=\"true\"'，实际'{header}'"
