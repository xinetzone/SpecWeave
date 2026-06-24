# Agent Global Contract (AGENTS Manifest)

This is the English quick-reference version of the AGENTS Manifest.
For the authoritative full version, see [AGENTS.md](AGENTS.md) (Chinese).

All AI agents in this project MUST read this file first as their highest-priority
entry point. Use the context routing table below to locate the appropriate
`.agents/` specification, then load the corresponding role definition, system
prompt, and collaboration protocol before executing tasks.

## Global Core Rules

- **Communication Language**: All outputs, comments, commit messages, and documentation SHALL be in Chinese. See [AGENTS.md](AGENTS.md) for the authoritative language policy.
- **On-Demand Loading**: Before domain-specific tasks, only read `.agents/` specs directly relevant to the current task.
- **Context Economy**: Search first, read precisely, keep only relevant context.
- **Mermaid First**: Visual logic SHALL use Mermaid. Renderable and versionable.
- **Code Changes**: Convention over configuration. Follow existing code style.
- **No Temporary Dependencies**: Do NOT commit `vendor/`, `.temp/`, `__pycache__/`, `.venv/`, `node_modules/` to Git.
- **Consult Knowledge Base**: Review [docs/knowledge/README.md](docs/knowledge/README.md) and [docs/retrospective/README.md](docs/retrospective/README.md) before starting tasks.

## Role Definition Index

| Role | ID | Responsibility | Entry |
|---|---|---|---|
| Orchestrator | orchestrator | Task decomposition, process coordination, conflict arbitration | .agents/roles/orchestrator.md |
| Architect | architect | Technical architecture design, architecture decisions | .agents/roles/architect.md |
| Developer | developer | Code implementation, refactoring, bug fixing | .agents/roles/developer.md |
| Code Reviewer | reviewer | Code quality review, standards compliance | .agents/roles/reviewer.md |
| Test Engineer | tester | Test case design, execution, coverage | .agents/roles/tester.md |
| Co-Founder | co-founder | Vision establishment, collaboration contract, key decision arbitration | .agents/roles/co-founder.md |
| Team Admin | team-admin | Team management, permission assignment, role auto-creation | .agents/teams/team-admin.md |

## Self-Evolution Module Index

| Module | ID | Layer | Entry |
|---|---|---|---|
| Self-Insight | self-insight | Perception | .agents/modules/self-insight.md |
| Self-Retrospective | self-retrospective | Perception | .agents/modules/self-retrospective.md |
| Self-Extraction | self-extraction | Cognition | .agents/modules/self-extraction.md |
| Self-Evolution | self-evolution | Cognition | .agents/modules/self-evolution.md |
| Self-Iteration | self-iteration | Execution | .agents/modules/self-iteration.md |
| Self-Verification | self-verification | Execution | .agents/modules/self-verification.md |
| Self-Management | self-management | Governance | .agents/modules/self-management.md |
| Self-Development | self-development | Governance | .agents/modules/self-development.md |

## Capability Boundaries

| Role | Non-Goals |
|------|-----------|
| orchestrator | Does NOT write business code; does NOT make architecture decisions |
| architect | Does NOT implement code details; does NOT write test cases |
| developer | Does NOT unilaterally change architecture; does NOT merge without review |
| reviewer | Does NOT modify business code directly; does NOT perform acceptance testing |
| tester | Does NOT handle production deployment; does NOT modify business logic |
| team-admin | Does NOT write business code; does NOT unilaterally change architecture |

## Collaboration Protocol Summary

| Protocol | Purpose | Entry |
|----------|---------|-------|
| Task Handoff | Task transfer between agents | .agents/protocols/handoff.md |
| Messaging | Inter-agent communication | .agents/protocols/messaging.md |
| Conflict Resolution | Dispute arbitration | .agents/protocols/conflict-resolution.md |
| Dependency Management | Temp dependency handling | .agents/protocols/dependency-management.md |

## Standard Workflow Index

| Workflow | Use Case | Participants | Entry |
|----------|----------|-------------|-------|
| Feature Development | New feature from spec to delivery | All roles | .agents/workflows/feature-development.md |
| Code Review | PR quality review | developer, reviewer, orchestrator | .agents/workflows/code-review.md |
| Testing | Test execution & acceptance | tester, developer, reviewer | .agents/workflows/testing.md |

## Tool Specification Index

| Category | Tools Covered | Entry |
|----------|--------------|-------|
| File Operations | read, write, edit, delete, list | .agents/tools/file-operations.md |
| Code Execution | run_command, run_tests, build | .agents/tools/code-execution.md |
| Search | grep_search, glob_find, semantic_search | .agents/tools/search.md |
| Communication | send_message, handoff_task, sync_status | .agents/tools/communication.md |

## Context Routing Table

| Task Type | Required Entry |
|-----------|---------------|
| Role definitions & responsibilities | .agents/roles/ |
| Self-evolution module definitions | .agents/modules/ |
| System prompts & few-shot examples | .agents/prompts/ |
| Tool invocation specifications | .agents/tools/ |
| Collaboration protocols & communication | .agents/protocols/ |
| Standard workflows | .agents/workflows/ |
| Task & handoff templates | .agents/templates/ |
| Team management, permissions, role creation | .agents/teams/ |
| Collaboration execution, environment management | .agents/worlds/ |
| Git ignore rule validation | .agents/scripts/check-gitignore.py |
| Link validity check | .agents/scripts/check-links.py |
| File path migration | .agents/scripts/check-move.py |
| Role permission validation | .agents/scripts/check-role-permissions.py |
| Derived artifact traceability | .agents/scripts/check-source-traceability.py |
| Specification consistency check | .agents/scripts/check-spec-consistency.py |
| Navigation table generation | .agents/scripts/generate-nav.py |
| Test skeleton generation | .agents/scripts/generate-tests.py |
| CI comprehensive check | .agents/scripts/ci-check.ps1 / ci-check.sh |
| Technical knowledge base | docs/knowledge/README.md |
| Retrospective system & reusable patterns | docs/retrospective/README.md |
| Reusable pattern library | docs/retrospective/patterns/ |
| Asset inventory & reuse guide | docs/retrospective/assets/asset-inventory.md |
| Task execution summaries | docs/task-summaries/ |
| Prompt engineering patterns | docs/retrospective/prompt-extraction.md |
| Prompt extraction system | prompt_extraction/ |

## Development Standards (Summary)

- **Code Style**: Follow existing conventions. Naming, indentation, comments, and file organization shall match project standards.
- **Commit Convention**: Follow [Conventional Commits](https://conventionalcommits.org/) — `type(scope): subject`. Body in Chinese.
- **Document Boundaries**: `README.md` is for humans; `.agents/` is for AI agents. Do not mix responsibilities.
- **Derived Artifact Traceability**: Structured artifacts derived from source documents shall carry `source = "<file>#<section>"` in TOML frontmatter.

> **Note**: This English version is a quick-reference index. The full authoritative specification is maintained in [AGENTS.md](AGENTS.md) (Chinese). For detailed role definitions, workflows, and collaboration protocols, please refer to the `.agents/` directory tree.
