"""GraphQL Profile：GraphQL Schema & API规范。
STATUS: EXPERIMENTAL - 实验性特性，API可能变更，未经生产环境验证

定义GraphQL API接口文档的结构要求。
必填Frontmatter: name, description
推荐Frontmatter: version, type, authors, license, endpoint, schemaPath
"""

from dataclasses import dataclass, field
import logging
import re

from .base import BaseProfile, SectionPattern, ProfileValidationResult
from ..models import MDIDocument

logger = logging.getLogger(__name__)


GRAPHQL_SECTION_PATTERNS: tuple[SectionPattern, ...] = (
    SectionPattern(
        key="overview",
        keywords=("概览", "overview", "概述", "简介", "introduction"),
        required=False,
    ),
    SectionPattern(
        key="auth",
        keywords=("认证", "授权", "auth", "authentication", "鉴权", "security"),
        required=False,
    ),
    SectionPattern(
        key="schema",
        keywords=("schema", "类型定义", "type definitions", "类型系统"),
        required=True,
    ),
    SectionPattern(
        key="queries",
        keywords=("查询", "queries", "query", "读取操作"),
        required=False,
    ),
    SectionPattern(
        key="mutations",
        keywords=("变更", "mutations", "mutation", "写入操作"),
        required=False,
    ),
    SectionPattern(
        key="subscriptions",
        keywords=("订阅", "subscriptions", "subscription", "实时"),
        required=False,
    ),
    SectionPattern(
        key="errors",
        keywords=("错误", "errors", "异常", "error handling"),
        required=False,
    ),
)


_DIRECTIVE_GRAPHQL_RE = re.compile(r"^\{(query|mutation|subscription)\}\s+(\w+)(?:\s+(.*))?$")
_FIELD_DEF_RE = re.compile(r"^\s*(\w+)(\??):\s*(\w+)(?:\s*-\s*(.*))?$")
_OPERATION_NAME_RE = re.compile(r"^\s*(?:query|mutation|subscription)\s+(\w+)")
_TYPE_DEF_RE = re.compile(r"^\s*(type|input|enum|interface|union)\s+([A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)


@dataclass
class GraphQLProfile(BaseProfile):
    """GraphQL API Profile。

    必填Frontmatter: name, description
    推荐Frontmatter: version, type, authors, license, endpoint, schemaPath, tags

    支持的Directive类型: {query}, {mutation}, {subscription}
    """

    profile_type: str = "graphql"

    required_frontmatter: set[str] = field(
        default_factory=lambda: {"name", "description"}
    )
    recommended_frontmatter: set[str] = field(
        default_factory=lambda: {
            "version", "type", "authors", "license",
            "endpoint", "schemaPath", "tags",
        }
    )

    section_patterns: tuple[SectionPattern, ...] = GRAPHQL_SECTION_PATTERNS

    def validate(self, doc: MDIDocument) -> list[ProfileValidationResult]:
        """执行GraphQL Profile特定验证。

        验证项：
        1. 必填frontmatter检查（继承自基类+GraphQL特定）
        2. 推荐frontmatter提示
        3. Schema章节必填检查
        4. 至少有一个Query/Mutation章节警告
        5. {query}/{mutation}/{subscription} directive格式验证
        6. GraphQL类型定义语法检查（基础）
        """
        results: list[ProfileValidationResult] = []
        doc_name = doc.frontmatter.get("name", "<unnamed>")

        logger.info("[GraphQLProfile] 开始验证文档: name=%s, frontmatter_keys=%s",
                     doc_name, list(doc.frontmatter.keys()))

        logger.debug("[GraphQLProfile] Rule1: 必填frontmatter检查 (required_fields=%s)",
                      list(self.required_frontmatter))
        for key in self.required_frontmatter:
            if key not in doc.frontmatter:
                logger.warning("[GraphQLProfile] Rule1[FAIL] 必填字段缺失: key=%s, doc=%s", key, doc_name)
                results.append(ProfileValidationResult(
                    name=f"frontmatter:{key}",
                    passed=False,
                    severity="error",
                    message=f"缺少必填frontmatter字段: {key}",
                ))
            else:
                logger.debug("[GraphQLProfile] Rule1[PASS] 必填字段已设置: key=%s, value=%r", key, doc.frontmatter[key])
                results.append(ProfileValidationResult(
                    name=f"frontmatter:{key}",
                    passed=True,
                    severity="info",
                    message=f"frontmatter字段 {key} 已设置",
                ))

        logger.debug("[GraphQLProfile] Rule2: 推荐frontmatter检查 (recommended_fields=%s)",
                      list(self.recommended_frontmatter))
        for key in self.recommended_frontmatter:
            if key not in doc.frontmatter:
                logger.info("[GraphQLProfile] Rule2[WARN] 推荐字段缺失: key=%s, doc=%s", key, doc_name)
                results.append(ProfileValidationResult(
                    name=f"frontmatter:{key}",
                    passed=False,
                    severity="warning",
                    message=f"建议添加frontmatter字段: {key}",
                ))
            else:
                logger.debug("[GraphQLProfile] Rule2[PASS] 推荐字段已设置: key=%s", key)

        logger.debug("[GraphQLProfile] Rule3: Schema章节检查")
        schema_sections = self.find_sections_by_key(doc, "schema")
        if not schema_sections:
            logger.warning("[GraphQLProfile] Rule3[WARN] Schema章节未找到 (keywords=schema/类型定义/type definitions/类型系统)")
            results.append(ProfileValidationResult(
                name="section:schema",
                passed=False,
                severity="warning",
                message="建议添加Schema/类型定义章节，描述GraphQL类型系统",
            ))
        else:
            schema_titles = [s.title for s in schema_sections]
            logger.info("[GraphQLProfile] Rule3[PASS] Schema章节已找到: count=%d, titles=%s",
                         len(schema_sections), schema_titles)
            results.append(ProfileValidationResult(
                name="section:schema",
                passed=True,
                severity="info",
                message="Schema章节已存在",
            ))

        logger.debug("[GraphQLProfile] Rule4: Query/Mutation章节检查")
        query_sections = self.find_sections_by_key(doc, "queries")
        mutation_sections = self.find_sections_by_key(doc, "mutations")
        subscription_sections = self.find_sections_by_key(doc, "subscriptions")

        logger.debug("[GraphQLProfile] Rule4 章节统计: queries=%d, mutations=%d, subscriptions=%d",
                      len(query_sections), len(mutation_sections), len(subscription_sections))
        if not query_sections and not mutation_sections:
            logger.warning("[GraphQLProfile] Rule4[WARN] 未找到Query/Mutation操作章节")
            results.append(ProfileValidationResult(
                name="section:operations",
                passed=False,
                severity="warning",
                message="建议至少包含Query（查询）或Mutation（变更）章节之一",
            ))
        else:
            logger.info("[GraphQLProfile] Rule4[PASS] 操作章节存在: query_titles=%s, mutation_titles=%s",
                         [s.title for s in query_sections], [s.title for s in mutation_sections])

        full_text = self.get_full_text(doc)
        logger.debug("[GraphQLProfile] Rule5: GraphQL Directive命名规范检查 (directive languages: directive:query/mutation/subscription)")

        directive_count = 0
        directive_errors = 0
        query_count = 0
        mutation_count = 0
        subscription_count = 0

        for section, cb in self.iter_code_blocks(doc):
            if cb.language and cb.language.startswith("directive:"):
                directive_type = cb.language[len("directive:"):]
                if directive_type in ("query", "mutation", "subscription"):
                    directive_count += 1
                    meta_parts = (cb.meta or "").strip().split(None, 1)
                    op_name = meta_parts[0] if meta_parts else ""
                    op_args = meta_parts[1] if len(meta_parts) > 1 else ""
                    logger.debug("[GraphQLProfile] Rule5 发现Directive: section=%s, type=%s, name=%s, args=%r",
                                  section.title, directive_type, op_name, op_args[:80])

                    if directive_type == "query":
                        query_count += 1
                    elif directive_type == "mutation":
                        mutation_count += 1
                    elif directive_type == "subscription":
                        subscription_count += 1

                    if not op_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", op_name):
                        directive_errors += 1
                        logger.error("[GraphQLProfile] Rule5[FAIL] Directive命名不规范: section=%s, type=%s, name=%r",
                                      section.title, directive_type, op_name)
                        results.append(ProfileValidationResult(
                            name=f"directive:{directive_type}:{op_name or '<unnamed>'}",
                            passed=False,
                            severity="error",
                            message=f"{directive_type}名称 '{op_name}' 不符合GraphQL命名规范",
                        ))

        logger.info("[GraphQLProfile] Rule5 Directive扫描完成: total=%d, errors=%d (queries=%d, mutations=%d, subscriptions=%d)",
                     directive_count, directive_errors, query_count, mutation_count, subscription_count)

        logger.debug("[GraphQLProfile] Rule6: endpoint配置检查")
        if "endpoint" not in doc.frontmatter:
            logger.info("[GraphQLProfile] Rule6[INFO] endpoint字段未配置")
            results.append(ProfileValidationResult(
                name="config:endpoint",
                passed=False,
                severity="info",
                message="建议在frontmatter中添加endpoint字段指定GraphQL服务URL",
            ))
        else:
            logger.debug("[GraphQLProfile] Rule6[PASS] endpoint已配置: %s", doc.frontmatter["endpoint"])

        logger.debug("[GraphQLProfile] Rule7: GraphQL type定义检测 (typedef_re=%s)", _TYPE_DEF_RE.pattern)
        type_def_matches: list[tuple[str, str]] = []
        for section, cb in self.iter_code_blocks(doc):
            if cb.language == "graphql" or (cb.language or "").startswith("graphql"):
                block_matches = _TYPE_DEF_RE.findall(cb.content)
                if block_matches:
                    logger.debug("[GraphQLProfile] Rule7 在graphql fence中发现type定义: section=%s, count=%d",
                                  section.title, len(block_matches))
                    type_def_matches.extend(block_matches)
        type_def_count = len(type_def_matches)
        if type_def_count == 0:
            logger.info("[GraphQLProfile] Rule7[INFO] 未检测到GraphQL type定义")
            results.append(ProfileValidationResult(
                name="schema:typedef",
                passed=False,
                severity="info",
                message="文档中未检测到GraphQL type定义（type Xxx { ... }）",
            ))
        else:
            type_def_names = [m[1] for m in type_def_matches]
            logger.info("[GraphQLProfile] Rule7[PASS] 检测到%d个type定义: types=%s",
                         type_def_count, type_def_names)
            results.append(ProfileValidationResult(
                name="schema:typedef",
                passed=True,
                severity="info",
                message=f"检测到 {type_def_count} 个GraphQL类型定义: {', '.join(type_def_names)}",
            ))

        required_root_types: list[str] = []
        operations = doc.frontmatter.get("operations", [])
        for op in operations:
            if op == "query":
                required_root_types.append("Query")
            elif op == "mutation":
                required_root_types.append("Mutation")
            elif op == "subscription":
                required_root_types.append("Subscription")

        if required_root_types:
            defined_type_names = {m[1] for m in type_def_matches}
            missing = [t for t in required_root_types if t not in defined_type_names]
            if missing:
                logger.warning("[GraphQLProfile] Rule7[WARN] 缺失必需的root type: %s", missing)
                results.append(ProfileValidationResult(
                    name="schema:root-types",
                    passed=False,
                    severity="warning",
                    message=f"缺失必需的root类型: {', '.join(missing)}",
                ))
            else:
                logger.debug("[GraphQLProfile] Rule7[PASS] 所有必需root类型已定义: %s", required_root_types)

        pass_count = sum(1 for r in results if r.passed)
        fail_count = len(results) - pass_count
        error_count = sum(1 for r in results if r.severity == "error" and not r.passed)
        warn_count = sum(1 for r in results if r.severity == "warning" and not r.passed)
        logger.info("[GraphQLProfile] 验证完成: doc=%s, total_results=%d, passed=%d, failed=%d (errors=%d, warnings=%d)",
                     doc_name, len(results), pass_count, fail_count, error_count, warn_count)

        return results
