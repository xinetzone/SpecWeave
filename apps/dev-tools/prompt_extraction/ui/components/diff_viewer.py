"""优化对比组件：展示优化前后的提示词对比"""

import streamlit as st

from prompt_extraction.messages import (
    DIFF_OPTIMIZED,
    DIFF_ORIGINAL,
    IMPROVEMENTS_LABEL,
    MSG_NO_OPTIMIZE,
)


def render_diff_viewer(original: str, optimized: str, improvements: list[str]) -> None:
    """展示优化前后对比。

    左侧显示原始文本，右侧显示优化后文本。
    如果 optimized 为空，显示"无需优化"。

    Args:
        original: 原始提示词文本。
        optimized: 优化后的提示词文本。
        improvements: 优化改进点列表。
    """
    if not optimized:
        st.info(MSG_NO_OPTIMIZE)
        return

    # 改进点列表
    if improvements:
        st.markdown(IMPROVEMENTS_LABEL)
        for item in improvements:
            st.markdown(f"- {item}")

    # 左右对比展示（使用 markdown 代码块避免 key 冲突）
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(DIFF_ORIGINAL)
        st.markdown(f"```text\n{original}\n```")

    with col_right:
        st.markdown(DIFF_OPTIMIZED)
        st.markdown(f"```text\n{optimized}\n```")