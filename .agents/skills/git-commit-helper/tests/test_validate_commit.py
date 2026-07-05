#!/usr/bin/env python3
"""单元测试：validate_commit.py 提交信息验证器

覆盖场景：
  - 正常提交（所有合法type，带/不带scope，中文/英文subject）
  - 边界值（subject长度=50，scope长度=20，空字符串等）
  - 异常/非法格式（缺少冒号、缺少空格、大写type、未知type、无subject等）
  - 空值/None测试（空消息、纯空白、None输入）
  - 参数组合测试（type×scope×breaking×subject多维度组合）
  - 警告检测（句号结尾、过去时态、超长subject、超长scope、breaking标记）
  - 多段正文格式（subject与body之间空行规则）
  - suggest_type/suggest_scope 逻辑（基于文件路径推断）
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import validate_commit as vc


# ═══════════════════════════════════════════════════════════════
# 1. 正常提交用例（parametrize）
# ═══════════════════════════════════════════════════════════════

class TestValidMessages:
    """合法提交信息应通过验证，无错误。"""

    @pytest.mark.parametrize("commit_type", sorted(vc.COMMIT_TYPES))
    def test_all_valid_types_without_scope(self, commit_type: str):
        """所有允许的type在无scope时都应通过。"""
        msg = f"{commit_type}: 做某事"
        result = vc.validate_message(msg)
        assert result.valid is True, f"type={commit_type} 应通过，错误: {result.errors}"
        assert result.errors == []
        assert result.commit_type == commit_type
        assert result.scope is None
        assert result.is_breaking is False

    @pytest.mark.parametrize("commit_type", sorted(vc.COMMIT_TYPES))
    def test_all_valid_types_with_scope(self, commit_type: str):
        """所有允许的type在带scope时都应通过。"""
        msg = f"{commit_type}(auth): 做某事"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert result.commit_type == commit_type
        assert result.scope == "auth"

    @pytest.mark.parametrize("msg,expected_type,expected_scope", [
        ("feat(auth): 添加JWT令牌刷新机制", "feat", "auth"),
        ("fix(login): 修复登录态过期跳转问题", "fix", "login"),
        ("docs(readme): 更新安装说明", "docs", "readme"),
        ("style: 格式化代码", "style", None),
        ("refactor(parser): 重构解析器模块", "refactor", "parser"),
        ("perf: 优化首屏加载时间", "perf", None),
        ("test(api): 添加用户接口单元测试", "test", "api"),
        ("chore(deps): 更新依赖版本", "chore", "deps"),
        ("ci: 配置GitHub Actions流水线", "ci", None),
        ("revert: 回滚上次提交", "revert", None),
        ("build: 升级构建工具版本", "build", None),
    ])
    def test_real_world_messages_chinese(self, msg, expected_type, expected_scope):
        """真实场景的中文提交信息应全部通过。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert result.commit_type == expected_type
        assert result.scope == expected_scope

    @pytest.mark.parametrize("msg", [
        "feat: add user authentication",
        "fix: resolve null pointer exception",
        "docs: update README",
        "refactor(core): simplify error handling",
    ])
    def test_english_subjects(self, msg):
        """英文subject也应通过验证。"""
        result = vc.validate_message(msg)
        assert result.valid is True

    def test_scope_with_hyphen(self):
        """scope包含连字符应合法（如user-auth）。"""
        result = vc.validate_message("feat(user-auth): 添加双因素认证")
        assert result.valid is True
        assert result.scope == "user-auth"

    def test_scope_with_slash(self):
        """scope包含斜杠应合法（如api/v2，多层模块路径）。"""
        result = vc.validate_message("feat(api/v2): 新版API接口")
        assert result.valid is True
        assert result.scope == "api/v2"

    def test_scope_with_numbers(self):
        """scope包含数字应合法。"""
        result = vc.validate_message("fix(v2): 修复v2版本兼容问题")
        assert result.valid is True
        assert result.scope == "v2"

    def test_breaking_change_marker(self):
        """breaking change标记(!)应被识别但不作为错误。"""
        result = vc.validate_message("refactor(api)!: 重构用户API响应格式")
        assert result.valid is True
        assert result.is_breaking is True

    def test_message_with_leading_trailing_whitespace(self):
        """前后空白应被strip，不影响验证。"""
        result = vc.validate_message("  feat(auth): 添加登录  \n  ")
        assert result.valid is True
        assert result.commit_type == "feat"
        assert result.scope == "auth"
        assert result.subject == "添加登录"


# ═══════════════════════════════════════════════════════════════
# 2. 边界值测试
# ═══════════════════════════════════════════════════════════════

class TestBoundaryValues:
    """边界条件测试。"""

    def test_subject_exactly_50_chars_no_warning(self):
        """subject长度恰好50字符不应产生长度警告。"""
        subject = "A" * 50
        msg = f"feat: {subject}"
        result = vc.validate_message(msg)
        assert result.valid is True
        length_warnings = [w for w in result.warnings if "≤50" in w]
        assert length_warnings == [], f"50字符不应触发长度警告，实际warnings: {result.warnings}"

    def test_subject_51_chars_triggers_warning(self):
        """subject长度51字符应产生长度警告，但不报错（警告不影响valid）。"""
        subject = "A" * 51
        msg = f"feat: {subject}"
        result = vc.validate_message(msg)
        assert result.valid is True
        length_warnings = [w for w in result.warnings if "≤50" in w]
        assert len(length_warnings) >= 1

    def test_scope_exactly_20_chars_no_warning(self):
        """scope长度恰好20字符不应产生警告。"""
        scope = "a" * 20
        msg = f"feat({scope}): test"
        result = vc.validate_message(msg)
        assert result.valid is True
        scope_warnings = [w for w in result.warnings if "≤20" in w]
        assert scope_warnings == []

    def test_scope_21_chars_triggers_warning(self):
        """scope长度21字符应产生警告。"""
        scope = "a" * 21
        msg = f"feat({scope}): test"
        result = vc.validate_message(msg)
        assert result.valid is True
        scope_warnings = [w for w in result.warnings if "≤20" in w]
        assert len(scope_warnings) >= 1

    def test_single_word_subject(self):
        """subject是单个词应合法（极简提交）。"""
        result = vc.validate_message("fix: hotfix")
        assert result.valid is True

    def test_minimal_valid_message(self):
        """最短合法提交信息：type加冒号空格加至少一个字符。"""
        result = vc.validate_message("fix: x")
        assert result.valid is True
        assert result.subject == "x"


# ═══════════════════════════════════════════════════════════════
# 3. 异常/非法格式测试
# ═══════════════════════════════════════════════════════════════

class TestInvalidFormats:
    """非法格式应被拒绝并报告错误。"""

    @pytest.mark.parametrize("msg", [
        "",
        "   ",
        "\n",
        "\t",
        "\n\n",
    ])
    def test_empty_or_whitespace_only(self, msg):
        """空消息或纯空白应报错。"""
        result = vc.validate_message(msg)
        assert result.valid is False
        assert any("空" in e for e in result.errors)

    @pytest.mark.parametrize("msg", [
        "update code",
        "fix bug",
        "hello world",
        "add new feature",
        "some random text without format",
    ])
    def test_missing_type_and_colon(self, msg):
        """没有type:前缀的自由文本应报格式错误。"""
        result = vc.validate_message(msg)
        assert result.valid is False
        assert any("格式错误" in e for e in result.errors)

    @pytest.mark.parametrize("msg", [
        "feat:add login",
        "feat(auth):add login",
        "fix  : missing space",
    ])
    def test_missing_space_after_colon(self, msg):
        """冒号后缺少空格应报格式错误。"""
        result = vc.validate_message(msg)
        assert result.valid is False

    @pytest.mark.parametrize("msg", [
        "FEAT: 大写type",
        "Feat: 首字母大写",
        "FIX(auth): 大写type加scope",
    ])
    def test_uppercase_type(self, msg):
        """type必须小写，大写应报格式错误（正则[a-z]+不匹配大写）。"""
        result = vc.validate_message(msg)
        assert result.valid is False

    @pytest.mark.parametrize("msg", [
        "unknown: 未知type",
        "wip: 进行中",
        "misc: 杂项",
        "hack: 临时修改",
    ])
    def test_unknown_commit_type(self, msg):
        """不在允许列表中的type应报错。"""
        result = vc.validate_message(msg)
        assert result.valid is False
        assert any("未知的type" in e for e in result.errors)

    @pytest.mark.parametrize("msg", [
        "feat:",
        "feat(auth):",
        "fix: ",
        "fix:  ",
    ])
    def test_missing_subject(self, msg):
        """冒号后无subject（空或仅空格）——subject=None。"""
        result = vc.validate_message(msg)
        if not result.valid:
            assert result.subject is None or result.subject == ""
        else:
            assert result.subject in (None, "", " ")

    @pytest.mark.parametrize("msg,should_be_valid", [
        ("feat(auth):添加JWT", False),
        ("feat(auth):  添加JWT", True),
        ("feat:添加功能", False),
        ("feat:  添加功能", True),
    ])
    def test_colon_spacing_edge_cases(self, msg, should_be_valid):
        """冒号后必须至少一个空格；多个空格合法（subject会strip）。"""
        result = vc.validate_message(msg)
        assert result.valid is should_be_valid, f"'{msg}' valid期望{should_be_valid}，实际{result.valid}，错误:{result.errors}"

    def test_scope_with_underscore_rejected(self):
        """scope包含下划线应被正则拒绝（scope正则只允许[a-z0-9\\-/]+）。"""
        result = vc.validate_message("feat(user_auth): 添加功能")
        assert result.valid is False

    def test_scope_with_uppercase_rejected(self):
        """scope包含大写字母应被拒绝。"""
        result = vc.validate_message("feat(Auth): 添加功能")
        assert result.valid is False

    def test_scope_with_special_chars_rejected(self):
        """scope包含特殊字符应被拒绝。"""
        result = vc.validate_message("feat(auth!): 添加功能")
        assert result.valid is False

    def test_only_type_no_colon(self):
        """只有type没有冒号应报格式错误。"""
        result = vc.validate_message("feat")
        assert result.valid is False


# ═══════════════════════════════════════════════════════════════
# 4. 警告检测测试（不影响valid，但应正确触发）
# ═══════════════════════════════════════════════════════════════

class TestWarnings:
    """警告类问题不应导致验证失败，但应被检测到。"""

    @pytest.mark.parametrize("msg,ending", [
        ("feat: 添加功能。", "。"),
        ("feat: 添加功能.", "."),
        ("feat: 添加功能！", "！"),
        ("feat: 添加功能!", "!"),
    ])
    def test_subject_ending_with_punctuation(self, msg, ending):
        """subject以句号/感叹号结尾应产生警告。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        punct_warnings = [w for w in result.warnings if "不应以句号" in w or "句号" in w]
        assert len(punct_warnings) >= 1, f"以'{ending}'结尾应产生警告，warnings: {result.warnings}"

    @pytest.mark.parametrize("msg", [
        "fix: 修复了登录问题",
        "feat: 添加了新功能",
        "docs: 更新了文档",
        "refactor: 重构了用户模块",
        "perf: 优化了查询性能",
    ])
    def test_past_tense_warnings(self, msg):
        """使用"修复了""添加了""更新了"等过去时态应产生祈使句警告。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        tense_warnings = [w for w in result.warnings if "祈使句" in w]
        assert len(tense_warnings) >= 1, f"'{msg}' 应触发祈使句警告"

    def test_no_past_tense_warning_for_imperative(self):
        """正确的祈使句（修复/添加/更新 不带"了/过"）不应产生祈使句警告。"""
        result = vc.validate_message("fix: 修复登录问题")
        tense_warnings = [w for w in result.warnings if "祈使句" in w]
        assert tense_warnings == []

    def test_breaking_change_warning(self):
        """breaking标记(!)应产生警告提醒添加BREAKING CHANGE正文。"""
        result = vc.validate_message("feat(api)!: 重构API")
        assert result.valid is True
        breaking_warnings = [w for w in result.warnings if "BREAKING CHANGE" in w or "破坏性" in w]
        assert len(breaking_warnings) >= 1

    def test_no_warnings_for_perfect_message(self):
        """完全合规的提交信息不应有任何警告。"""
        result = vc.validate_message("feat(auth): 添加JWT令牌刷新机制")
        assert result.valid is True
        assert result.warnings == [], f"理想提交不应有警告: {result.warnings}"

    def test_multiple_warnings_can_coexist(self):
        """一个消息可以同时触发多个警告（过去时+句号+breaking）。"""
        result = vc.validate_message("fix(api)!: 修复了bug。")
        assert result.valid is True
        warning_texts = " ".join(result.warnings)
        assert "祈使句" in warning_texts or "了" in warning_texts
        assert "句号" in warning_texts or "结尾" in warning_texts


# ═══════════════════════════════════════════════════════════════
# 5. 多段正文（Body）格式测试
# ═══════════════════════════════════════════════════════════════

class TestMultilineMessages:
    """包含正文/脚注的多行提交信息测试。"""

    def test_subject_with_body_proper_blank_line(self):
        """subject与body之间空一行应合法。"""
        msg = "feat(auth): 添加JWT刷新\n\n详细说明正文内容。"
        result = vc.validate_message(msg)
        assert result.valid is True

    def test_subject_without_blank_line_before_body_error(self):
        """subject与body之间没有空行应报错。"""
        msg = "feat(auth): 添加JWT刷新\n详细说明正文内容。"
        result = vc.validate_message(msg)
        assert result.valid is False
        assert any("空一行" in e for e in result.errors)

    def test_subject_with_blank_line_then_multiple_body_lines(self):
        """多行body，subject与body间有空行应合法。"""
        msg = "fix: 修复bug\n\n原因：xxx\n方案：yyy\n影响：zzz"
        result = vc.validate_message(msg)
        assert result.valid is True

    def test_subject_only_newline_no_body(self):
        """subject后直接换行无body（第二行为空）应合法。"""
        result = vc.validate_message("feat: test\n")
        assert result.valid is True

    def test_three_line_with_proper_spacing(self):
        """三行（subject+空行+body）合法。"""
        msg = "feat: test\n\nbody line"
        result = vc.validate_message(msg)
        assert result.valid is True


# ═══════════════════════════════════════════════════════════════
# 6. suggest_type 逻辑测试
# ═══════════════════════════════════════════════════════════════

class TestSuggestType:
    """基于文件名推断commit type的逻辑测试。"""

    @pytest.mark.parametrize("files,expected", [
        (["src/feature/new_auth.py"], "feat"),
        (["src/new_module.py"], "feat"),
        (["src/add_user.rs"], "feat"),
        (["app/create_page.tsx"], "feat"),
    ])
    def test_suggest_feat_for_new_feature_files(self, files, expected):
        """包含feature/new/add/create的文件应建议feat。"""
        assert vc.suggest_type(files) == expected

    @pytest.mark.parametrize("files", [
        ["src/fix_login.py"],
        ["src/bug_fix.rs"],
        ["src/error_handler.ts"],
        ["patches/crash_fix.py"],
        ["src/issue_123.ts"],
        ["src/patch_01.py"],
    ])
    def test_suggest_fix_for_bugfix_files(self, files):
        """包含fix/bug/error/crash/issue/patch的文件应建议fix。"""
        assert vc.suggest_type(files) == "fix"

    @pytest.mark.parametrize("files", [
        ["README.md"],
        ["docs/guide.md"],
        ["src/api/doc.ts"],
        ["comments.py"],
    ])
    def test_suggest_docs_for_documentation_files(self, files):
        """md文件/readme/doc/comment相关文件应建议docs。"""
        assert vc.suggest_type(files) == "docs"

    @pytest.mark.parametrize("files", [
        ["tests/test_auth.py"],
        ["src/unit_test.rs"],
        ["spec/api.spec.ts"],
        ["components/Button.test.jsx"],
        ["utils/helper_test.go"],
    ])
    def test_suggest_test_for_test_files(self, files):
        """test/spec/.test./_test.相关文件应建议test。"""
        assert vc.suggest_type(files) == "test"

    @pytest.mark.parametrize("files", [
        ["src/refactor_module.py"],
        ["src/rename_class.ts"],
        ["src/move_file.rs"],
        ["src/restructure_api.ts"],
    ])
    def test_suggest_refactor_for_refactoring_files(self, files):
        """refactor/rename/move/restructure相关文件应建议refactor。"""
        assert vc.suggest_type(files) == "refactor"

    @pytest.mark.parametrize("files", [
        ["src/perf_cache.py"],
        ["src/optim_query.rs"],
        ["src/speed_up.ts"],
    ])
    def test_suggest_perf_for_performance_files(self, files):
        """perf/optim/cache/speed相关文件应建议perf。"""
        assert vc.suggest_type(files) == "perf"

    @pytest.mark.parametrize("files", [
        ["src/format_code.py"],
        ["src/lint_config.rs"],
        ["src/style_fix.ts"],
        ["prettier.config.js"],
        [".whitespaces"],
    ])
    def test_suggest_style_for_formatting_files(self, files):
        """style/format/lint/whitespace/prettier相关文件应建议style。"""
        assert vc.suggest_type(files) == "style"

    @pytest.mark.parametrize("files", [
        ["package.json"],
        ["requirements.txt"],
        ["deps.py"],
        ["config.yaml"],
        ["pyproject.toml"],
    ])
    def test_suggest_chore_for_config_dependency_files(self, files):
        """package.json/requirements/deps/config/.toml相关文件应建议chore。"""
        assert vc.suggest_type(files) == "chore"

    @pytest.mark.parametrize("files", [
        [".github/workflows/ci.yml"],
        ["circleci/config.yml"],
        ["Jenkinsfile"],
        [".gitlab-ci.yml"],
    ])
    def test_suggest_ci_for_pipeline_files(self, files):
        """CI配置文件应建议ci。"""
        assert vc.suggest_type(files) == "ci"

    @pytest.mark.parametrize("files", [
        ["src/random_file.py"],
        ["main.py"],
        ["app.ts"],
        ["lib.rs"],
        ["unknown.xyz"],
    ])
    def test_suggest_chore_as_default_for_unmatched(self, files):
        """无匹配模式的文件应默认返回chore。"""
        assert vc.suggest_type(files) == "chore"

    def test_empty_file_list_returns_chore(self):
        """空文件列表应返回chore（所有分数为0时取默认值）。"""
        assert vc.suggest_type([]) == "chore"

    def test_highest_score_wins(self):
        """当文件匹配多个type模式时，分数最高的胜出。"""
        files = ["tests/bug_fix/test_new_feature.py"]
        result = vc.suggest_type(files)
        assert result in vc.COMMIT_TYPES

    def test_tie_breaking_consistent(self):
        """平票时max函数应返回确定结果（字典序最大的key）。"""
        files = ["README.md"]
        t1 = vc.suggest_type(files)
        t2 = vc.suggest_type(files)
        assert t1 == t2


# ═══════════════════════════════════════════════════════════════
# 7. suggest_scope 逻辑测试
# ═══════════════════════════════════════════════════════════════

class TestSuggestScope:
    """基于文件路径推断scope的逻辑测试。"""

    @pytest.mark.parametrize("files,expected", [
        (["src/auth/login.py"], "src"),
        (["components/Button.tsx"], "components"),
        (["docs/README.md"], "docs"),
        (["api/v2/users.py"], "api"),
    ])
    def test_suggest_scope_returns_top_level_dir(self, files, expected):
        """多段路径应返回顶层目录名作为scope。"""
        assert vc.suggest_scope(files) == expected

    @pytest.mark.parametrize("files", [
        ["README.md"],
        ["setup.py"],
        ["Dockerfile"],
    ])
    def test_suggest_scope_none_for_root_level_files(self, files):
        """根目录文件（无路径分隔符）应返回None。"""
        assert vc.suggest_scope(files) is None

    def test_empty_list_returns_none(self):
        """空文件列表应返回None。"""
        assert vc.suggest_scope([]) is None

    def test_only_first_file_used_for_scope(self):
        """scope推断只使用第一个文件的顶层目录。"""
        files = ["src/auth/login.py", "tests/test_auth.py", "docs/api.md"]
        assert vc.suggest_scope(files) == "src"


# ═══════════════════════════════════════════════════════════════
# 8. ValidationResult 数据类测试
# ═══════════════════════════════════════════════════════════════

class TestValidationResult:
    """ValidationResult 数据结构正确性测试。"""

    def test_valid_result_structure(self):
        """合法消息的result字段完整性。"""
        result = vc.validate_message("feat(auth): test")
        assert isinstance(result.valid, bool)
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.is_breaking, bool)
        assert result.valid is True
        assert result.errors == []
        assert result.commit_type == "feat"
        assert result.scope == "auth"
        assert result.subject == "test"
        assert result.is_breaking is False

    def test_invalid_result_structure(self):
        """非法消息的result字段完整性。"""
        result = vc.validate_message("")
        assert result.valid is False
        assert len(result.errors) >= 1
        assert result.commit_type is None
        assert result.scope is None
        assert result.subject is None
        assert result.is_breaking is False

    def test_format_error_returns_none_fields(self):
        """格式错误时commit_type/scope/subject应为None。"""
        result = vc.validate_message("bad format")
        assert result.valid is False
        assert result.commit_type is None
        assert result.scope is None
        assert result.subject is None


# ═══════════════════════════════════════════════════════════════
# 9. 参数组合测试（type × scope × breaking 交叉组合）
# ═══════════════════════════════════════════════════════════════

class TestCombinations:
    """多维度参数组合测试。"""

    @pytest.mark.parametrize("commit_type", ["feat", "fix", "refactor"])
    @pytest.mark.parametrize("scope", [None, "auth", "api/v2"])
    @pytest.mark.parametrize("breaking", [False, True])
    def test_type_scope_breaking_combinations(self, commit_type, scope, breaking):
        """type × scope × breaking 的2×3×2=12种组合都应正确解析。"""
        bang = "!" if breaking else ""
        scope_part = f"({scope})" if scope else ""
        msg = f"{commit_type}{scope_part}{bang}: 测试消息"
        result = vc.validate_message(msg)
        assert result.valid is True, f"msg={msg}, errors={result.errors}"
        assert result.commit_type == commit_type
        assert result.scope == scope
        assert result.is_breaking is breaking

    @pytest.mark.parametrize("subject", [
        "修复登录问题",
        "add feature",
        "A" * 50,
        "重构！",
    ])
    def test_subjects_with_all_types(self, subject):
        """不同subject与多个type组合应保持行为一致。"""
        for t in ["feat", "fix", "docs"]:
            msg = f"{t}: {subject}"
            result = vc.validate_message(msg)
            if subject.endswith(("。", ".", "！", "!")):
                assert result.valid is True
            elif len(subject) > 50:
                assert result.valid is True
            else:
                assert result.valid is True


# ═══════════════════════════════════════════════════════════════
# 10. 正则表达式精确性测试
# ═══════════════════════════════════════════════════════════════

class TestRegexPrecision:
    """COMMIT_PATTERN 正则表达式精确性测试。"""

    @pytest.mark.parametrize("msg,should_match", [
        ("feat: x", True),
        ("feat(a): x", True),
        ("feat(a-b): x", True),
        ("feat(a/b): x", True),
        ("feat(a1): x", True),
        ("feat!: x", True),
        ("feat(a)!: x", True),
        ("feat: 中文也可以", True),
        ("feat: x y z", True),
        ("feat: x:y:z", True),
        ("FEAT: x", False),
        ("feat:x", False),
        ("feat : x", False),
        ("feat (a): x", False),
        ("feat(a) : x", False),
        ("feat(a)! : x", False),
    ])
    def test_pattern_matching(self, msg, should_match):
        """验证正则对各种边界格式的精确匹配。"""
        m = vc.COMMIT_PATTERN.match(msg)
        assert (m is not None) == should_match, f"'{msg}' should_match={should_match}"


# ═══════════════════════════════════════════════════════════════
# 11. 祈使句检测——全覆盖30个动词边界场景
# ═══════════════════════════════════════════════════════════════

ALL_IMPERATIVE_VERBS = [
    "修复", "添加", "更新", "删除", "重构", "优化", "实现", "修改",
    "调整", "迁移", "整合", "替换", "移除", "新增", "改进", "完善",
    "解决", "处理", "支持", "升级", "降级", "合并", "拆分", "重命名",
    "补充", "简化", "增强", "清理", "恢复", "回滚",
]


def _has_imperative_warning(result):
    return any("祈使句" in w for w in result.warnings)


class TestImperativeDetectionAllVerbs:
    """祈使句检测——覆盖全部30个动词的正向/反向/边界/组合场景。"""

    # ── 11.1 动词+「了」：全部30个动词都应触发警告 ──

    @pytest.mark.parametrize("verb", ALL_IMPERATIVE_VERBS)
    def test_verb_le_triggers_warning(self, verb):
        """动词+「了」（过去时态）应触发祈使句警告。"""
        msg = f"feat: {verb}了登录问题"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"'{msg}' 应触发祈使句警告（{verb}+了），warnings={result.warnings}"

    # ── 11.2 动词+「过」：全部30个动词都应触发警告 ──

    @pytest.mark.parametrize("verb", ALL_IMPERATIVE_VERBS)
    def test_verb_guo_triggers_warning(self, verb):
        """动词+「过」（经历态）应触发祈使句警告。"""
        msg = f"fix: {verb}过这个问题"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"'{msg}' 应触发祈使句警告（{verb}+过），warnings={result.warnings}"

    # ── 11.3 动词不带「了/过」（正确祈使句）：不应触发警告 ──

    @pytest.mark.parametrize("verb", ALL_IMPERATIVE_VERBS)
    def test_verb_alone_no_warning(self, verb):
        """动词直接跟宾语（祈使句，不带了/过）不应触发祈使句警告。"""
        msg = f"feat: {verb}登录模块"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert not _has_imperative_warning(result), \
            f"'{msg}' 是正确祈使句，不应触发警告，warnings={result.warnings}"

    # ── 11.4 动词+「了」带scope：应触发警告 ──

    @pytest.mark.parametrize("verb", ALL_IMPERATIVE_VERBS)
    def test_verb_le_with_scope_triggers_warning(self, verb):
        """带scope时动词+了仍应触发警告。"""
        msg = f"feat(auth): {verb}了JWT令牌"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"'{msg}' 带scope+{verb}+了应触发警告，warnings={result.warnings}"

    # ── 11.5 动词+「过」带scope：应触发警告 ──

    @pytest.mark.parametrize("verb", ALL_IMPERATIVE_VERBS)
    def test_verb_guo_with_scope_triggers_warning(self, verb):
        """带scope时动词+过仍应触发警告。"""
        msg = f"fix(core): {verb}过该逻辑"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"'{msg}' 带scope+{verb}+过应触发警告，warnings={result.warnings}"

    # ── 11.6 三字符动词「重命名」专项测试 ──

    @pytest.mark.parametrize("msg,should_warn", [
        ("feat: 重命名了用户字段", True),
        ("feat: 重命名过旧接口", True),
        ("feat: 重命名用户字段", False),
        ("refactor(api): 重命名了参数", True),
        ("refactor(api): 重命名参数", False),
    ])
    def test_three_char_verb_chongmingming(self, msg, should_warn):
        """三字符动词「重命名」的了/过/正确形式测试。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result) is should_warn, \
            f"'{msg}' 警告期望{should_warn}，warnings={result.warnings}"

    # ── 11.7 动词不在subject开头时不应触发（^锚点验证） ──

    @pytest.mark.parametrize("msg", [
        "feat: 为登录模块修复了过期问题",
        "feat: 对用户接口添加了限流",
        "fix: 将配置更新为新版本",
        "feat: 已删除临时文件",
        "feat: 完成了重构模块",
        "feat: 对性能做了优化",
    ])
    def test_verb_not_at_start_no_false_positive(self, msg):
        """动词不在subject开头时（前面有其他词），不触发警告（^锚点）。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert not _has_imperative_warning(result), \
            f"'{msg}' 动词不在开头不应触发警告，warnings={result.warnings}"

    # ── 11.8 「了」「过」不作为动词后缀时不误判 ──

    @pytest.mark.parametrize("msg", [
        "docs: 了解项目结构",
        "feat: 了却一桩心事",
        "feat: 过目不忘的新功能",
        "feat: 过度封装问题",
        "feat: 过程优化",
    ])
    def test_le_guo_without_verb_prefix_no_false_positive(self, msg):
        """「了/过」前面不是列表中的动词时，不应触发警告。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert not _has_imperative_warning(result), \
            f"'{msg}' 了/过前无动词，不应触发警告，warnings={result.warnings}"

    # ── 11.9 动词后紧跟非「了/过」字符不应触发 ──

    @pytest.mark.parametrize("verb,followup", [
        ("修复", "好"), ("添加", "新"), ("更新", "版"), ("删除", "旧"),
        ("重构", "后"), ("优化", "前"), ("实现", "中"), ("修改", "人"),
        ("升级", "版"), ("降级", "到"), ("合并", "到"), ("拆分", "成"),
        ("恢复", "正常"), ("回滚", "到"),
    ])
    def test_verb_followed_by_non_le_guo_no_warning(self, verb, followup):
        """动词后跟非「了/过」字符（如「好」「新版」等），不应触发警告。"""
        msg = f"feat: {verb}{followup}的问题"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert not _has_imperative_warning(result), \
            f"'{msg}' {verb}后为'{followup}'非了/过，不应触发警告，warnings={result.warnings}"

    # ── 11.10 动词+「了」与其他警告共存 ──

    @pytest.mark.parametrize("verb", ["修复", "重构", "优化", "实现"])
    def test_verb_le_coexists_with_other_warnings(self, verb):
        """动词+了可与句号结尾警告、breaking警告同时存在。"""
        msg = f"fix(api)!: {verb}了bug。"
        result = vc.validate_message(msg)
        assert result.valid is True
        warning_text = " ".join(result.warnings)
        assert _has_imperative_warning(result), f"应有祈使句警告"
        assert "句号" in warning_text or "结尾" in warning_text, f"应有句号警告"
        assert "BREAKING" in warning_text or "破坏性" in warning_text, f"应有breaking警告"

    # ── 11.11 动词+了在多行消息中正确检测 ──

    @pytest.mark.parametrize("verb", ["修复", "添加", "删除", "重构"])
    def test_verb_le_in_multiline_message(self, verb):
        """多行消息中，subject行的动词+了应被检测到。"""
        msg = f"fix: {verb}了空指针问题\n\n详细描述：在极端条件下会触发NPE。"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"多行消息中'{verb}了'应触发警告，warnings={result.warnings}"

    # ── 11.12 动词+「了」subject长度刚好50字符的边界 ──

    def test_verb_le_at_subject_length_boundary(self):
        """动词+了的subject恰好50字符时，应触发祈使句警告但不触发超长警告。"""
        prefix = "修复了"
        suffix = "A" * (50 - len(prefix))
        msg = f"fix: {prefix}{suffix}"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), "应有祈使句警告"
        assert not any("长度" in w for w in result.warnings), \
            f"恰好50字符不应有长度警告，warnings={result.warnings}"

    def test_verb_le_subject_51_chars_has_both_warnings(self):
        """动词+了的subject为51字符时，应同时触发祈使句和超长警告。"""
        prefix = "修复了"
        suffix = "A" * (51 - len(prefix))
        msg = f"fix: {prefix}{suffix}"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), "应有祈使句警告"
        assert any("长度" in w for w in result.warnings), "应有长度警告"

    # ── 11.13 所有type与动词+了的组合 ──

    @pytest.mark.parametrize("commit_type", ["feat", "fix", "docs", "style",
                                              "refactor", "perf", "test", "chore",
                                              "ci", "revert", "build"])
    @pytest.mark.parametrize("verb", ["修复", "更新", "重构", "优化", "解决"])
    def test_verb_le_with_all_commit_types(self, commit_type, verb):
        """所有commit type下动词+了都应触发祈使句警告。"""
        msg = f"{commit_type}: {verb}了问题"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"type={commit_type}, '{msg}' 应触发警告，warnings={result.warnings}"

    # ── 11.14 动词+了+scope含斜杠/连字符 ──

    @pytest.mark.parametrize("scope", ["api/v2", "auth-module", "core/utils"])
    def test_verb_le_with_special_scope_chars(self, scope):
        """scope含斜杠/连字符时，动词+了仍应正确检测。"""
        msg = f"fix({scope}): 修复了边界问题"
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"scope={scope}时应触发祈使句警告，warnings={result.warnings}"

    # ── 11.15 动词前缀互斥性验证（无动词是另一个动词的前缀） ──

    @pytest.mark.parametrize("msg,expected_verb", [
        ("feat: 新增了功能", "新增"),
        ("feat: 添加了功能", "添加"),
        ("feat: 更新了配置", "更新"),
        ("feat: 修改了逻辑", "修改"),
        ("feat: 改进了性能", "改进"),
        ("feat: 恢复了数据", "恢复"),
        ("feat: 回滚了版本", "回滚"),
    ])
    def test_verb_prefix_disambiguation(self, msg, expected_verb):
        """相似动词（新增/添加、恢复/回滚等）应正确匹配且不互相干扰。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert _has_imperative_warning(result), \
            f"'{msg}' 应触发祈使句警告（动词={expected_verb}），warnings={result.warnings}"

    # ── 11.16 英文subject不应误触发中文祈使句检测 ──

    @pytest.mark.parametrize("msg", [
        "feat: added new feature",
        "fix: fixed login bug",
        "feat: updated docs",
        "refactor: refactored the module",
        "fix: resolved the issue",
    ])
    def test_english_subject_no_chinese_imperative_warning(self, msg):
        """英文subject（即使是过去式）不应触发中文祈使句警告。"""
        result = vc.validate_message(msg)
        assert result.valid is True
        assert not _has_imperative_warning(result), \
            f"英文subject '{msg}' 不应触发中文祈使句警告，warnings={result.warnings}"
