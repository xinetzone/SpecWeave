import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"


def _make_skill_doc(
    name: str = "test-skill",
    description: str = "当用户提到测试时，必须使用此技能。这是一个测试用的Skill文档，包含足够的描述信息以通过长度检查。",
    version: str = "1.0.0",
    extra_fm: str = "",
    body: str = "",
) -> str:
    fm = f"""---
name: {name}
version: "{version}"
description: "{description}"
argument-hint: "[test]"
user-invocable: true
paths: []
{extra_fm}
---

# {name}

## 1. 功能描述

这是{name}的功能描述章节。

> **为什么需要此功能？** 为了测试验证器的正确性。

## 2. 何时使用

当用户需要测试时使用本技能。

## 3. 核心步骤

1. 步骤一：准备
2. 步骤二：执行
3. 步骤三：**必须**验证结果

> **为什么步骤三必须验证？** 确保操作成功，避免遗漏。
"""
    return fm + body
