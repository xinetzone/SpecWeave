"""确定性工具：供 LangGraph ToolNode 注册。

安全红线：所有工具必须可被 LLM 安全调用，不得暴露任意代码执行或外部副作用。
"""

import ast
import operator
from datetime import datetime


def get_current_time() -> str:
    """返回当前本地日期时间（演示/真实场景均适用的确定性工具）。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_ALLOWED_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_POW_EXPONENT = 1000


def _eval_ast(node: ast.AST):
    """AST 白名单求值：仅允许数字常量、四则运算、取模、一元正负与受限幂运算。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval_ast(node.left), _eval_ast(node.right))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        exponent = _eval_ast(node.right)
        if not isinstance(exponent, (int, float)) or exponent > _MAX_POW_EXPONENT:
            raise ValueError("幂指数超出安全上限")
        return operator.pow(_eval_ast(node.left), exponent)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_ast(node.operand))
    raise ValueError(f"不支持的表达式节点: {type(node).__name__}")


def safe_calculator(expression: str) -> str:
    """安全计算数学表达式（AST 白名单，拒绝任意代码执行）。

    支持：数字、+ - * / // % **（幂指数上限 1000）、一元正负、括号。
    示例："2 * (3 + 4)" -> "14"。不安全表达式返回错误说明，不抛异常。
    """
    expression = expression.strip()
    if not expression:
        return "计算失败: 表达式为空"
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_ast(tree.body)
    except (ValueError, ZeroDivisionError, OverflowError, SyntaxError) as exc:
        return f"计算失败: {exc}"
    if isinstance(result, float) and result.is_integer():
        return str(int(result))
    return str(result)
