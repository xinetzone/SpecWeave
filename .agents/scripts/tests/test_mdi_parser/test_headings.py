class TestHeadingHierarchy:

    def test_h1_to_h6(self, parser):
        text = "# H1 Title\n\n## H2 Section\n\n### H3 Subsection\n\n#### H4 Deep\n"
        doc = parser.parse_text(text)
        assert doc.title == "H1 Title"
        assert len(doc.sections) == 1
        h1 = doc.sections[0]
        assert h1.level == 1
        assert h1.title == "H1 Title"
        assert len(h1.subsections) == 1
        h2 = h1.subsections[0]
        assert h2.level == 2
        assert h2.title == "H2 Section"
        assert len(h2.subsections) == 1
        h3 = h2.subsections[0]
        assert h3.level == 3
        assert h3.title == "H3 Subsection"

    def test_sibling_h2_sections(self, parser):
        text = "# Doc\n\n## Section A\n\nContent A\n\n## Section B\n\nContent B\n\n## Section C\n\nContent C\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        assert len(h1.subsections) == 3
        titles = [s.title for s in h1.subsections]
        assert "Section A" in titles
        assert "Section B" in titles
        assert "Section C" in titles

    def test_h3_under_correct_h2(self, parser):
        text = "# Doc\n\n## First H2\n\n### H3 under first\n\n## Second H2\n\n### H3 under second\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2s = h1.subsections
        assert len(h2s) == 2
        assert len(h2s[0].subsections) == 1
        assert h2s[0].subsections[0].title == "H3 under first"
        assert len(h2s[1].subsections) == 1
        assert h2s[1].subsections[0].title == "H3 under second"
