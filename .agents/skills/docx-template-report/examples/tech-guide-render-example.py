"""tech-guide-template 渲染示例脚本。

演示如何使用 tech-guide-template.docx 模板生成技术文档，
覆盖 2/3/4/5 列全部表格类型。

运行方式：
    py -3.14 examples/tech-guide-render-example.py

输出：
    examples/output/tech-guide-example.docx

依赖：
    pip install docxtpl==0.20.2 python-docx==1.2.0
"""
import os
from docxtpl import DocxTemplate

# 路径：脚本所在目录为 skill 根目录的 examples/
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_DIR, "templates", "tech-guide-template.docx")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT = os.path.join(OUT_DIR, "tech-guide-example.docx")

os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 数据上下文：完整示例，覆盖所有模板结构块
# ============================================================
context = {
    "company": "示例微电子股份有限公司",
    "doc_title": "XMNN SDK 使用指南",
    "doc_meta": "版本 v1.1.0  2025-07-02",

    # ---- 更新记录（5 列表，独立于章节循环） ----
    "revisions": [
        {"version": "1.0.0", "author": "刘新伟", "date": "2025-07-02",
         "desc": "初始版本", "approver": "张振宇"},
        {"version": "1.1.0", "author": "刘新伟", "date": "2025-08-01",
         "desc": "新增量化原理与模型样例", "approver": "张振宇"},
    ],

    # ---- 章节列表 ----
    "chapters": [
        {
            "title": "开发环境准备",
            "intro": [
                "本工具链支持 Conda 与 Docker 两种环境配置方式，请按需选择。",
                "当前版本仅支持 Linux 操作系统环境。",
            ],
            "sections": [
                {
                    "title": "Conda 环境配置",
                    "paragraphs": ["创建并激活 Python 环境："],
                    "code": [
                        "conda env create --file=xmnn.yaml",
                        "conda activate xmenv",
                        "pip install xm_gnpu-1.1.0-py3-none-any.whl",
                    ],
                    # 2 列说明表示例
                    "tables": [
                        {
                            "cols": 2,
                            "headers": ["目录", "说明"],
                            "rows": [
                                ["release/", "工具主程序"],
                                ["npuusertools/", "NPU 用户工具集"],
                                ["models/", "示例模型文件"],
                            ],
                        },
                    ],
                },
                {
                    "title": "Docker 运行参数",
                    "paragraphs": ["使用 docker run 命令启动容器，常用参数如下："],
                    # 2 列参数说明表示例
                    "tables": [
                        {
                            "cols": 2,
                            "headers": ["参数", "说明"],
                            "rows": [
                                ["-it", "交互模式运行，分配伪终端"],
                                ["-d", "后台运行容器，返回容器 ID"],
                                ["--rm", "容器退出后自动删除"],
                                ["-v 本地:容器", "挂载本地目录到容器内"],
                            ],
                        },
                    ],
                },
            ],
        },
        {
            "title": "模型编译",
            "intro": ["编译阶段将前端模型转换为 XMNN 格式，并执行量化优化。"],
            "sections": [
                {
                    "title": "编译参数",
                    "paragraphs": ["编译工具 compile.py 支持以下参数："],
                    "code": [
                        "python3 compile.py -n pytorch.resnet18",
                    ],
                    # 4 列参数表示例（最高频）
                    "tables": [
                        {
                            "cols": 4,
                            "headers": ["参数名", "类型", "可选项", "说明"],
                            "rows": [
                                ["name", "str", "", "模型名称，对应 models/ 下的子目录"],
                                ["target", "str", "vta2.0, sim_vta2.0", "目标硬件平台"],
                                ["quant", "str", "int8, float", "量化方式，默认 int8"],
                            ],
                        },
                    ],
                },
                {
                    "title": "命令行选项",
                    "paragraphs": ["推理工具 inference.py 的完整命令行参数："],
                    # 5 列命令参数表示例
                    "tables": [
                        {
                            "cols": 5,
                            "headers": ["参数名称", "必需/可选", "参数类型", "默认值", "说明"],
                            "rows": [
                                ["-n / --name", "必需", "string", "无", "指定模型名称"],
                                ["-i / --input", "必需", "string", "无", "输入图片路径"],
                                ["-o / --output", "可选", "string", "result.txt", "输出结果文件路径"],
                                ["-d / --device", "可选", "string", "sim", "运行设备：sim / npu"],
                            ],
                        },
                    ],
                },
            ],
        },
        {
            "title": "核心 API 参考",
            "intro": ["XMNN Runtime C/C++ 核心数据结构体说明。"],
            "sections": [
                {
                    "title": "xmnn_tensor_attr 结构体",
                    "paragraphs": ["描述输入输出 tensor 属性的结构体："],
                    "code": [
                        "typedef struct {",
                        "    uint32_t index;",
                        "    char name[64];",
                        "    uint32_t dims[4];",
                        "} xmnn_tensor_attr;",
                    ],
                    # 3 列属性表示例
                    "tables": [
                        {
                            "cols": 3,
                            "headers": ["成员变量", "数据类型", "含义"],
                            "rows": [
                                ["index", "uint32_t", "tensor 的索引位置"],
                                ["name", "char[]", "tensor 名称"],
                                ["dims", "uint32_t[4]", "张量维度（NCHW 格式）"],
                            ],
                        },
                    ],
                },
            ],
        },
    ],
}


def main():
    print("模板路径:", TEMPLATE)
    print("输出路径:", OUTPUT)

    tpl = DocxTemplate(TEMPLATE)
    tpl.render(context)
    tpl.save(OUTPUT)

    # 快速校验
    from docx import Document
    doc = Document(OUTPUT)
    body_text = "\n".join(p.text for p in doc.paragraphs)
    table_text = "\n".join(
        cell.text for tbl in doc.tables for row in tbl.rows for cell in row.cells
    )

    checks = {
        "封面标题": "XMNN SDK 使用指南" in table_text,
        "更新记录 v1.0.0": "1.0.0" in table_text,
        "更新记录 v1.1.0": "1.1.0" in table_text,
        "2列表格_目录说明": "release/" in table_text and "工具主程序" in table_text,
        "3列表格_结构体成员": "index" in table_text and "uint32_t" in table_text and "tensor 的索引位置" in table_text,
        "4列表格_编译参数": "name" in table_text and "模型名称" in table_text,
        "5列表格_命令选项": "-n / --name" in table_text and "指定模型名称" in table_text,
        "代码块_Conda命令": "conda activate xmenv" in body_text,
    }

    print("\n渲染校验：")
    all_pass = True
    for k, v in checks.items():
        status = "PASS" if v else "FAIL"
        if not v:
            all_pass = False
        print(f"  [{status}] {k}")

    print()
    print("全部通过" if all_pass else "存在失败项")
    print("\n产物:", OUTPUT)


if __name__ == "__main__":
    main()