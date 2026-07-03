class TestLists:

    def test_checkbox_list(self, parser):
        text = "# Doc\n\n## Checklist\n\n- [x] First done\n- [ ] Second pending\n- [ ] Third pending\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        checklists = [l for l in h2.lists if l["type"] == "checklist"]
        assert len(checklists) == 1
        items = checklists[0]["items"]
        assert len(items) == 3
        assert items[0].checked is True
        assert items[0].text == "First done"
        assert items[1].checked is False
        assert items[2].checked is False

    def test_unordered_list(self, parser):
        text = "# Doc\n\n## Items\n\n- Apple\n- Banana\n- Cherry\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        ulists = [l for l in h2.lists if l["type"] == "unordered"]
        assert len(ulists) == 1
        assert len(ulists[0]["items"]) == 3
        assert "Apple" in ulists[0]["items"]

    def test_ordered_list(self, parser):
        text = "# Doc\n\n## Steps\n\n1. First step\n2. Second step\n3. Third step\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        olists = [l for l in h2.lists if l["type"] == "ordered"]
        assert len(olists) == 1
        assert olists[0]["start"] == 1
        assert len(olists[0]["items"]) == 3
        assert "First step" in olists[0]["items"]


class TestMermaidFlowchart:

    def test_basic_flowchart(self, parser):
        text = "# Doc\n\n## Flow\n\n```mermaid\nflowchart TD\n    A[Start] --> B{Is it working?}\n    B -->|Yes| C[Great!]\n    B -->|No| D[Debug]\n    D --> B\n```\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        flowcharts = [l for l in h2.lists if l["type"] == "mermaid_flowchart"]
        assert len(flowcharts) == 1
        nodes = flowcharts[0]["nodes"]
        node_ids = {n.id for n in nodes}
        assert "A" in node_ids
        assert "B" in node_ids
        assert "C" in node_ids
        assert "D" in node_ids
        node_a = [n for n in nodes if n.id == "A"][0]
        assert node_a.label == "Start"
        node_b = [n for n in nodes if n.id == "B"][0]
        assert "Is it working" in node_b.label
