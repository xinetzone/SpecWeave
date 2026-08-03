"""Zleap-Agent Workspace-first 架构 Python 原型演示入口。

演示"先选工作区、再组装上下文"的完整流程：
1. 创建 Main 调度台工作区 + 多个业务工作区
2. 工具按工作区绑定（不全局暴露）
3. Main 工作区调度到具体业务工作区
4. 按公式装配上下文（Context = System + Workspace + Tools + Memory + History）
5. 记忆三分区 + 经验准入规则
6. 运行轨迹记录（可审计）
7. 四类边界检查
"""

from __future__ import annotations

from workspace import Workspace, WorkspaceRegistry
from tools import ToolRegistry, build_default_registry
from memory import MemoryManager, build_default_memory
from context import ContextAssembler
from runtime import RuntimeRecorder
from boundary import BoundaryChecker, BoundaryViolation


def build_workspaces() -> WorkspaceRegistry:
    """构建 Main 调度台 + 业务工作区。"""
    registry = WorkspaceRegistry()

    # Main 调度台：不承担所有上下文，只负责调度
    main = Workspace(
        workspace_id="main",
        name="Main 调度台",
        workspace_prompt="你是调度台，负责理解用户目标、判断应进入哪个工作区。",
        model="strong-model",
    )
    registry.set_main(main)

    # 业务工作区：文件编辑
    file_ws = Workspace(
        workspace_id="file",
        name="文件编辑工作区",
        workspace_prompt="负责文件读写与编辑。",
        model="cheap-model",
        permission="file",
    )
    registry.register(file_ws)

    # 业务工作区：网页检索
    web_ws = Workspace(
        workspace_id="web",
        name="网页检索工作区",
        workspace_prompt="负责网页搜索与信息检索。",
        model="cheap-model",
        permission="web",
    )
    registry.register(web_ws)

    # 业务工作区：财务报销（敏感，私有）
    finance_ws = Workspace(
        workspace_id="finance",
        name="财务报销工作区",
        workspace_prompt="处理敏感票据，走本地模型，数据不出内网。",
        model="local-model",
        permission="finance",
        private=True,
    )
    registry.register(finance_ws)

    return registry


def bind_tools(registry: WorkspaceRegistry, tool_registry: ToolRegistry) -> None:
    """按工作区绑定工具（工具不全局暴露）。"""
    # 文件工作区：文件读写工具
    tool_registry.bind_many(registry.get("file"), ["read_file", "write_file"])
    # 网页工作区：只暴露搜索工具
    tool_registry.bind_many(registry.get("web"), ["search_web"])
    # 财务工作区：只暴露本地票据处理 + 内网 SQL
    tool_registry.bind_many(registry.get("finance"), ["process_receipt", "run_sql"])
    # Main 工作区：不绑定具体工具（调度台）


def setup_boundaries(checker: BoundaryChecker) -> None:
    """配置四类边界。"""
    # 标记敏感数据
    checker.mark_sensitive("客户财务票据")
    # 模型白名单
    checker.set_allowed_models("finance", ["local-model"])
    checker.set_allowed_models("file", ["cheap-model", "strong-model"])
    checker.set_allowed_models("web", ["cheap-model"])
    # 私有记忆分区
    checker.mark_memory_private("experience")


def main() -> None:
    print("=" * 60)
    print("Zleap-Agent Workspace-first 架构原型演示")
    print("=" * 60)

    # 1. 构建工作区
    registry = build_workspaces()
    tool_registry = build_default_registry()
    bind_tools(registry, tool_registry)

    # 2. 上下文装配器 + 记忆 + 轨迹 + 边界
    assembler = ContextAssembler()
    memory = build_default_memory()
    runtime = RuntimeRecorder()
    checker = BoundaryChecker()
    setup_boundaries(checker)

    print("\n[1] 工作区注册成功：")
    for ws in registry.all():
        print(f"    - {ws}")

    # 3. 演示：Main 调度台调度到财务工作区
    print("\n[2] 用户请求：'处理一张客户报销票据'")
    main_ws = registry.get_main()
    target_ws = registry.get("finance")
    print(f"    Main 调度台调度到 → {target_ws.name}")

    # 4. 边界检查（模型边界 + 数据边界）
    checker.check_all(target_ws)
    print(f"    边界检查通过：模型边界（{target_ws.model}），数据边界（私有）")

    # 5. 装配上下文（prefetch 模式）
    target_ws.memory = memory
    context = assembler.assemble(target_ws, memory=memory, load_mode="prefetch")
    print("\n[3] 装配上下文（prefetch 模式）：")
    print(f"    可见工具：{[t['name'] for t in context['tools']]}")
    print(f"    记忆分区：{list(context['memory'].keys())}")

    # 6. 执行工具调用（工具边界检查）
    print("\n[4] 执行工具调用：")
    visible_tools = target_ws.get_visible_tools()
    # 为每个工具传入对应的参数
    tool_args = {
        "process_receipt": {"image_path": "receipt.jpg"},
        "run_sql": {"sql": "SELECT * FROM invoices WHERE status='pending'"},
    }
    for tool in visible_tools:
        checker.check_tool_boundary(target_ws, tool.name)
        result = tool.execute(**tool_args.get(tool.name, {}))
        print(f"    → {tool.name}: {result}")
        # 记录轨迹
        runtime.record(
            target_ws.workspace_id,
            action=f"调用工具 {tool.name}",
            context_snapshot=context,
            result=result,
        )

    # 7. 演示工具不全局暴露（工具边界检查）
    print("\n[5] 工具边界演示（工具不全局暴露）：")
    try:
        checker.check_tool_boundary(target_ws, "search_web")
        print("    ✗ 错误：应拦截未绑定的工具")
    except BoundaryViolation as e:
        print(f"    ✓ 越权拦截成功：{e}")

    # 8. 演示经验记忆准入规则
    print("\n[6] 经验记忆准入规则：")
    ok = memory.write_experience("可复用流程：先切工作区再组装上下文")
    blocked = memory.write_experience("客户名：某集团公司，财务金额 100 万")
    print(f"    ✓ 允许写入（可复用流程）：{ok}")
    print(f"    ✓ 拦截写入（含客户名/财务事实）：{not blocked}")

    # 9. 轨迹审计
    print("\n[7] 运行轨迹审计：")
    traces = runtime.audit(target_ws.workspace_id)
    for t in traces:
        print(f"    - {t['action']} → {t['result']}")

    # 10. 装配上下文文本输出
    print("\n[8] 完整装配上下文（to_text）：")
    print("-" * 40)
    print(assembler.to_text(context))
    print("-" * 40)

    print("\n✓ 演示完成：Workspace-first 流程覆盖五大模块")


if __name__ == "__main__":
    main()