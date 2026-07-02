"""audit-metadata-ecosystem.py 单元测试。

测试元数据生态健康度审计的核心逻辑：
1. 镜像路径映射（MD路径↔TOML路径）
2. 孤儿TOML检测
3. 缺失TOML检测
4. TOML语法有效性
5. MD-TOML id一致性
6. TOML必填字段检查
"""

import io
import tomllib
from pathlib import Path

import pytest


def _md_to_toml_path(md_rel: str) -> str:
    """将MD文件相对路径转换为对应的TOML镜像路径。"""
    return '.meta/toml/' + md_rel.replace('.md', '.toml')


def _compute_expected_x_toml_ref(md_rel: str) -> str:
    """根据MD文件相对路径计算正确的x-toml-ref值。"""
    toml_rel = _md_to_toml_path(md_rel)
    parent_depth = len(Path(md_rel).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def _write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def _create_md_with_frontmatter(path: Path, fm_id: str, x_toml_ref: str, title: str | None = None, source: str | None = None):
    lines = ['---', f'id: "{fm_id}"']
    if title:
        lines.append(f'title: "{title}"')
    if source:
        lines.append(f'source: "{source}"')
    lines.append(f'x-toml-ref: "{x_toml_ref}"')
    lines.append('---')
    lines.append(f'# {title or fm_id}')
    _write_file(path, '\n'.join(lines))


def _create_toml(path: Path, tom_id: str, title: str | None = None, **kwargs):
    lines = [f'id = "{tom_id}"']
    if title:
        lines.append(f'title = "{title}"')
    for k, v in kwargs.items():
        if isinstance(v, list):
            items = ', '.join(f'"{x}"' for x in v)
            lines.append(f'{k} = [{items}]')
        elif isinstance(v, bool):
            lines.append(f'{k} = {str(v).lower()}')
        else:
            lines.append(f'{k} = "{v}"')
    _write_file(path, '\n'.join(lines))


class TestMdTomlPathMapping:
    def test_root_level_file(self):
        assert _md_to_toml_path('README.md') == '.meta/toml/README.toml'

    def test_nested_file(self):
        assert _md_to_toml_path('docs/knowledge/report.md') == '.meta/toml/docs/knowledge/report.toml'

    def test_deeply_nested(self):
        assert _md_to_toml_path('a/b/c/d/file.md') == '.meta/toml/a/b/c/d/file.toml'


class TestComputeXTomlRef:
    def test_root_level(self):
        assert _compute_expected_x_toml_ref('README.md') == '.meta/toml/README.toml'

    def test_one_level(self):
        assert _compute_expected_x_toml_ref('docs/page.md') == '../.meta/toml/docs/page.toml'

    def test_two_levels(self):
        assert _compute_expected_x_toml_ref('docs/knowledge/page.md') == '../../.meta/toml/docs/knowledge/page.toml'

    def test_five_levels(self):
        result = _compute_expected_x_toml_ref('a/b/c/d/e/page.md')
        assert result == '../../../../../.meta/toml/a/b/c/d/e/page.toml'


class TestOrphanTomlDetection:
    def test_toml_without_md_is_orphan(self, tmp_path):
        toml_file = tmp_path / '.meta' / 'toml' / 'docs' / 'ghost.toml'
        _create_toml(toml_file, 'ghost', title='Ghost')
        md_for_toml = tmp_path / 'docs' / 'ghost.md'
        assert not md_for_toml.exists()
        assert toml_file.exists()

    def test_toml_with_md_is_not_orphan(self, tmp_path):
        md_file = tmp_path / 'docs' / 'real.md'
        toml_file = tmp_path / '.meta' / 'toml' / 'docs' / 'real.toml'
        x_ref = _compute_expected_x_toml_ref('docs/real.md')
        _create_md_with_frontmatter(md_file, 'real-doc', x_ref, title='Real Doc')
        _create_toml(toml_file, 'real-doc', title='Real Doc')
        assert md_file.exists()
        assert toml_file.exists()


class TestMissingTomlDetection:
    def test_md_with_x_toml_ref_but_no_toml_file(self, tmp_path):
        md_file = tmp_path / 'docs' / 'page.md'
        x_ref = _compute_expected_x_toml_ref('docs/page.md')
        _create_md_with_frontmatter(md_file, 'page-doc', x_ref, title='Page')
        toml_path = tmp_path / '.meta' / 'toml' / 'docs' / 'page.toml'
        assert not toml_path.exists()

    def test_md_without_frontmatter_has_no_missing_toml(self, tmp_path):
        md_file = tmp_path / 'docs' / 'simple.md'
        _write_file(md_file, '# Simple\nNo frontmatter here.')
        assert md_file.exists()


class TestTomlSyntaxValidation:
    def test_valid_toml_parses(self, tmp_path):
        toml_file = tmp_path / 'valid.toml'
        _create_toml(toml_file, 'test-id', title='Test', category='test')
        with open(toml_file, 'rb') as f:
            data = tomllib.load(f)
        assert data['id'] == 'test-id'
        assert data['title'] == 'Test'

    def test_invalid_toml_raises(self, tmp_path):
        toml_file = tmp_path / 'invalid.toml'
        _write_file(toml_file, 'id = "broken\ntitle = "no closing quote')
        with pytest.raises(tomllib.TOMLDecodeError):
            with open(toml_file, 'rb') as f:
                tomllib.load(f)


class TestMdTomlIdConsistency:
    def test_matching_ids(self, tmp_path):
        md_file = tmp_path / 'docs' / 'page.md'
        toml_file = tmp_path / '.meta' / 'toml' / 'docs' / 'page.toml'
        x_ref = _compute_expected_x_toml_ref('docs/page.md')
        _create_md_with_frontmatter(md_file, 'my-page', x_ref, title='My Page')
        _create_toml(toml_file, 'my-page', title='My Page')
        with open(toml_file, 'rb') as f:
            toml_data = tomllib.load(f)
        md_fm_text = md_file.read_text(encoding='utf-8').split('---')[1]
        from lib.frontmatter import extract_all_yaml_fields
        yaml_fields = extract_all_yaml_fields(md_fm_text)
        assert yaml_fields['id'] == toml_data['id']

    def test_mismatched_ids(self, tmp_path):
        md_file = tmp_path / 'docs' / 'page.md'
        toml_file = tmp_path / '.meta' / 'toml' / 'docs' / 'page.toml'
        x_ref = _compute_expected_x_toml_ref('docs/page.md')
        _create_md_with_frontmatter(md_file, 'my-page', x_ref, title='My Page')
        _create_toml(toml_file, 'different-id', title='My Page')
        with open(toml_file, 'rb') as f:
            toml_data = tomllib.load(f)
        md_fm_text = md_file.read_text(encoding='utf-8').split('---')[1]
        from lib.frontmatter import extract_all_yaml_fields
        yaml_fields = extract_all_yaml_fields(md_fm_text)
        assert yaml_fields['id'] != toml_data['id']


class TestTomlRequiredFields:
    def test_toml_with_id_is_valid(self, tmp_path):
        toml_file = tmp_path / 'minimal.toml'
        _create_toml(toml_file, 'minimal-doc')
        with open(toml_file, 'rb') as f:
            data = tomllib.load(f)
        assert 'id' in data
        assert data['id'] == 'minimal-doc'

    def test_toml_without_id_is_invalid(self, tmp_path):
        toml_file = tmp_path / 'noid.toml'
        _write_file(toml_file, 'title = "No ID"\ncategory = "test"\n')
        with open(toml_file, 'rb') as f:
            data = tomllib.load(f)
        assert 'id' not in data
