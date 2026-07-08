---
id: "atomgit-ai-best-practices"
title: "AtomGit AI 平台最佳实践"
source: "https://ai.gitcode.com/docs/faq/best-practices"
x-toml-ref: "../../../.meta/toml/docs/knowledge/learning/atomgit-ai-best-practices.toml"
extracted: "2026-07-07"
tags: ["AtomGit", "AI开发平台", "MLOps", "模型管理", "数据集管理", "Space应用", "Notebook开发", "协作开发", "安全最佳实践", "性能监控"]
---
# AtomGit AI 平台最佳实践

> **来源**: https://ai.gitcode.com/docs/faq/best-practices
> **提取日期**: 2026-07-07
> **内容简介**: 本文档整理了AtomGit AI平台在模型管理、数据集管理、Space应用、Notebook开发、协作开发、安全、性能监控等8大领域的最佳实践，包含详细的操作指南和代码示例。

---

## 执行摘要

本文档系统梳理了AtomGit AI平台在模型管理、数据集管理、Space应用、Notebook开发、协作开发、安全实践、性能监控与实验管理八大核心领域的最佳实践指南。通过遵循规范的命名约定、语义化版本管理、标准化配置文件、模块化架构设计、代码质量控制、多层级安全防护和全链路性能监控等实践，团队能够显著提升AI开发效率30%以上，降低模型部署故障率50%，确保代码质量与系统稳定性，实现安全合规的AI应用交付，同时促进团队高效协作与知识沉淀。

---

## 一、模型管理最佳实践

### 1.1 模型创建与发布

模型创建与发布是MLOps流程的起点，规范的命名、完整的文档和标准化的配置文件能够大幅提升模型的可复用性和团队协作效率。

#### 1.1.1 模型命名规范

**适用场景**：所有新模型创建、模型重命名、衍生模型命名

模型名称应遵循"见名知意"原则，使用清晰的描述性名称，建议采用以下结构：
`[模型架构]-[语言/领域]-[任务类型]`

**命名规则**：
- 使用小写英文字母、数字和连字符（`-`）
- 避免特殊字符、空格和下划线
- 包含模型类型和主要功能信息
- 保持名称简洁但具有辨识度

**命名示例**：
```
bert-chinese-sentiment-analysis    # BERT中文情感分析模型
resnet50-image-classification       # ResNet50图像分类模型
gpt2-chinese-text-generation        # GPT2中文文本生成模型
yolov8-object-detection             # YOLOv8目标检测模型
```

> **注意**：避免使用过于模糊的名称如 `my-model`、`test-model` 或包含版本号的名称如 `bert-v2`，版本号应通过版本管理系统单独维护。

#### 1.1.2 模型描述编写

**适用场景**：模型首次发布、模型重大更新、模型文档完善

完整的模型描述是用户理解和使用模型的关键，建议包含以下五个核心部分：

1. **基本信息**：模型名称、一句话功能概述
2. **功能描述**：主要用途、支持语言/领域、输入输出格式说明
3. **技术细节**：使用的深度学习框架、基于的预训练模型、模型大小、推理速度、训练数据简介
4. **使用示例**：可直接运行的代码示例，包含加载模型和推理调用
5. **注意事项**：使用限制、适用范围、已知问题、引用要求

**Python 使用示例代码**：
```python
from transformers import pipeline

# 加载中文情感分析模型
classifier = pipeline(
    "sentiment-analysis",
    model="bert-chinese-sentiment-analysis",
    tokenizer="bert-base-chinese"
)

# 推理示例
result = classifier("这个产品非常好用，我很满意！")
print(result)  # [{'label': 'positive', 'score': 0.998}]
```

#### 1.1.3 模型配置文件优化

**适用场景**：模型发布、模型版本更新、自动化部署流程

**model-config.yaml**（模型配置文件）是模型的元数据描述文件，用于平台识别模型信息、自动化部署和依赖管理。配置文件应包含以下核心字段：

**model-config.yaml 完整配置示例**：
```yaml
model-name: bert-chinese-sentiment-analysis
version: 1.0.0
framework: pytorch
task: text-classification
tags:
  - nlp
  - sentiment-analysis
  - chinese
  - bert
dependencies:
  - transformers>=4.30.0
  - torch>=2.0.0
  - numpy>=1.24.0
model-info:
  description: "基于BERT的中文情感分析模型，支持正/负/中性三分类"
  author: "AI Team"
  license: "Apache-2.0"
  language: "zh"
  model-size: "412MB"
performance:
  accuracy: 0.945
  f1-score: 0.938
  inference-speed: "50ms/sample (CPU)"
usage-examples:
  - title: "Python推理示例"
    code-path: "examples/inference.py"
```

⚠️ **重要提示**：
- `version` 字段必须遵循语义化版本号规范（详见1.2节）
- `dependencies` 中应明确指定版本范围，避免因依赖升级导致模型不可用
- `tags` 字段用于平台搜索和分类，建议至少包含任务类型和领域标签

> 💡 **交叉参考**：模型管理的配置文件设计思路同样适用于Space应用的配置管理，关于应用配置文件的详细规范可参考「3.1.2 配置文件管理」章节。

---

### 1.2 模型版本管理

规范的版本管理能够确保模型迭代的可追溯性，便于问题回滚和团队协作。AtomGit AI平台推荐结合语义化版本号与Git标签进行版本管理。

#### 1.2.1 版本号规范

**适用场景**：所有模型版本发布、模型迭代更新

**语义化版本号（Semantic Versioning）** 是一种采用"主版本.次版本.修订版本"三段式结构的版本规范，格式为 `MAJOR.MINOR.PATCH`，各段含义如下：

| 版本段 | 说明 | 递增时机 | 示例 |
|--------|------|----------|------|
| 主版本（MAJOR） | 不兼容的API修改 | 模型架构重大变更、输入输出格式改变、无法向后兼容时 | v1.0.0 → v2.0.0 |
| 次版本（MINOR） | 向下兼容的功能新增 | 添加新功能、模型微调提升效果、新增支持语言/领域时 | v1.0.0 → v1.1.0 |
| 修订版本（PATCH） | 向下兼容的问题修正 | 修复Bug、优化推理速度、更新文档、小范围权重调整时 | v1.0.0 → v1.0.1 |

**版本号示例**：
```
v1.0.0    # 初始正式发布版本
v1.0.1    # 修复了长文本推理时的内存泄漏问题
v1.1.0    # 新增中性情感分类支持
v2.0.0    # 重构模型架构，输入格式从文本改为JSON
```

> **注意**：首个正式版本建议从 `v1.0.0` 开始，开发阶段可以使用 `0.x.x` 版本号（如 `v0.1.0` 表示首个开发预览版）。

#### 1.2.2 版本更新策略

**适用场景**：模型版本发布、CI/CD自动化发布流程

使用 Git 标签（tag）标记模型版本是最佳实践，标签名与版本号保持一致（带 `v` 前缀）。

**创建和推送 Git 标签命令**：
```bash
# 创建轻量标签
git tag v1.0.0

# 创建带附注的标签（推荐，包含发布信息）
git tag -a v1.0.0 -m "Release v1.0.0: 初始正式版本，支持中文情感二分类"

# 推送标签到远程仓库
git push origin v1.0.0

# 查看所有标签
git tag -l

# 查看特定版本详情
git show v1.0.0
```

**版本发布规则**：
- 小版本修复（PATCH）：直接在主分支修复后打标签发布，如 `v1.0.1`
- 功能更新（MINOR）：从主分支创建特性分支开发，完成后合并回主分支并打标签，如 `v1.1.0`
- 重大更新（MAJOR）：建议在独立的开发分支长期迭代，充分测试后合并主分支，打标签如 `v2.0.0`，并保留 `v1.x` 分支维护旧版本

⚠️ **重要提示**：一旦版本标签推送到远程仓库，**禁止修改或删除**。如需修复问题，应发布新的修订版本，而非覆盖已有标签。

#### 1.2.3 变更日志维护

**适用场景**：所有版本发布、团队协作开发、用户告知更新内容

维护 CHANGELOG（变更日志）能够让用户清晰了解每个版本的变化，建议在模型仓库根目录创建 `CHANGELOG.md` 文件。

**CHANGELOG 格式示例**：
```markdown
# Changelog

本文件记录模型的所有重要版本变更，格式遵循 [Keep a Changelog](https://keepachangelog.com/) 规范。

## [1.1.0] - 2026-07-01

### 新增
- 新增中性情感分类支持，从二分类升级为三分类
- 添加批量推理接口示例代码
- 支持ONNX格式导出

### 修复
- 修复特殊字符导致tokenization失败的问题
- 优化CPU推理速度，提升30%

### 变更
- 更新依赖库版本：transformers 升级到 4.30.0
- 模型描述文档补充注意事项

## [1.0.1] - 2026-06-15

### 修复
- 修复长文本（>512字符）推理时的截断问题
- 修正示例代码中的参数错误

## [1.0.0] - 2026-06-01

### 新增
- 初始正式版本发布
- 支持中文情感正/负二分类
- 提供Python推理示例代码
```

**变更日志编写原则**：
- 按版本号倒序排列，最新版本在最上方
- 每个版本包含版本号和发布日期
- 统一使用"新增"、"修复"、"变更"三个小节分类
- 描述应清晰具体，避免"优化了性能"这类模糊表述
- 重大变更应标注迁移指南，告知用户如何适配新版本

> **注意**：变更日志应随代码一起提交，每次版本发布前更新，不要积累到多个版本后一起补写。

---

## 二、数据集管理最佳实践

### 2.1 数据集组织

规范的数据集组织是数据复用、团队协作和模型训练可复现性的基础。统一的目录结构、完整的元数据和自动化质量检查能够大幅降低数据管理成本。

#### 2.1.1 目录结构规范

**适用场景**：所有新数据集创建、数据集重构、团队协作数据集共享

标准化的目录结构能够让使用者快速理解数据集组成，便于自动化工具读取和处理。建议采用以下分层目录结构：

**标准数据集目录结构示例**：
```
dataset-name/
├── README.md
├── data/
│   ├── train/
│   ├── validation/
│   └── test/
├── metadata.json
├── schema.json
└── examples/
    ├── sample1.jpg
    ├── sample2.jpg
    └── sample3.jpg
```

**各目录/文件说明**：
- `README.md`：数据集说明文档，包含数据来源、使用方法、许可证等信息
- `data/`：数据文件主目录，按训练/验证/测试集划分
  - `train/`：训练集数据，用于模型训练
  - `validation/`：验证集数据，用于训练过程中的模型调优和超参数选择
  - `test/`：测试集数据，仅用于最终模型评估，禁止在训练过程中使用
- **metadata.json**：数据集元数据文件，描述数据集的基本信息和统计数据
- **schema.json**：数据集模式定义文件，描述数据结构和字段类型
- `examples/`：示例数据目录，存放少量具有代表性的样本，便于快速了解数据内容

> **注意**：对于超大规模数据集（TB级别），可以将 `data/` 目录替换为数据下载脚本或数据清单文件（如 `train.csv` 包含文件路径和标签），避免直接存储大量数据文件在Git仓库中。

#### 2.1.2 元数据文件规范

**适用场景**：数据集首次发布、数据集版本更新、自动化训练流水线

元数据是数据集的"身份证"，完整的元信息有助于平台索引、自动化加载和数据集发现。**metadata.json**（数据集元数据文件，描述数据集的基本信息和统计数据）应包含以下核心字段：

**metadata.json 完整配置示例**：
```json
{
  "name": "chinese-sentiment-corpus",
  "version": "1.0.0",
  "description": "中文电商评论情感分析数据集，包含正向、负向、中性三类标注",
  "license": "CC-BY-4.0",
  "creator": "NLP Data Team",
  "created_date": "2026-06-01",
  "last_updated": "2026-07-01",
  "statistics": {
    "total_samples": 100000,
    "train_samples": 80000,
    "validation_samples": 10000,
    "test_samples": 10000,
    "classes": ["positive", "negative", "neutral"],
    "class_distribution": {
      "positive": 40000,
      "negative": 35000,
      "neutral": 25000
    },
    "avg_text_length": 128,
    "language": "zh-CN"
  },
  "format": {
    "input_type": "text",
    "output_type": "classification",
    "encoding": "UTF-8",
    "file_format": "jsonl"
  },
  "quality_metrics": {
    "completeness": 0.998,
    "consistency": 0.985,
    "accuracy": 0.972
  },
  "tags": ["nlp", "sentiment-analysis", "chinese", "e-commerce", "text-classification"],
  "citation": "请引用本数据集时使用XXX论文引用格式"
}
```

**字段说明**：
- 基础信息：`name`（数据集名称）、`version`（版本号）、`description`（描述）、`license`（许可证）、`creator`（创建者）、日期字段
- statistics：数据统计信息，包含样本数量、类别分布、语言等
- format：数据格式说明，定义输入输出类型和编码
- quality_metrics：**数据质量三指标**，包括：
  - **完整性（completeness）**：数据字段无缺失的比例
  - **一致性（consistency）**：数据格式、标注口径统一的比例
  - **准确性（accuracy）**：标注正确的样本比例
- tags：标签，用于数据集搜索和分类

**schema.json**（数据集模式定义文件，描述数据结构和字段类型）用于定义数据字段的名称、类型和约束：

**schema.json 示例**：
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "样本唯一标识符"
    },
    "text": {
      "type": "string",
      "description": "评论文本内容",
      "minLength": 1
    },
    "label": {
      "type": "string",
      "enum": ["positive", "negative", "neutral"],
      "description": "情感标签"
    },
    "source": {
      "type": "string",
      "description": "数据来源平台"
    }
  },
  "required": ["id", "text", "label"]
}
```

⚠️ **重要提示**：
- `version` 字段建议遵循语义化版本号规范（与模型版本管理一致）
- quality_metrics 中的指标应通过自动化脚本实际计算得出，不应主观填写
- 数据集标签应准确反映数据领域、任务类型和语言，便于平台检索

#### 2.1.3 数据质量保证

**适用场景**：数据集发布前检查、训练流水线数据校验、定期数据审计

数据质量直接决定模型效果，在发布数据集或启动训练前，应使用自动化脚本检查数据质量。**数据质量三指标**——完整性（completeness）、一致性（consistency）、准确性（accuracy）——是衡量数据集质量的核心标准。

**Python 数据质量检查脚本框架**：
```python
import json
import os
from typing import Dict, List, Tuple, Any
from collections import Counter


def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """加载JSONL格式数据文件"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"警告: {file_path} 第{line_num}行JSON解析错误: {e}")
    return data


def check_completeness(data: List[Dict[str, Any]], required_fields: List[str]) -> Tuple[float, List[int]]:
    """
    检查数据完整性
    
    完整性（completeness）：必填字段无缺失的样本比例
    返回: (完整率, 有缺失字段的样本索引列表)
    """
    total = len(data)
    incomplete_indices = []
    
    for idx, sample in enumerate(data):
        for field in required_fields:
            if field not in sample or sample[field] is None or (isinstance(sample[field], str) and not sample[field].strip()):
                incomplete_indices.append(idx)
                break
    
    completeness = (total - len(incomplete_indices)) / total if total > 0 else 0.0
    return completeness, incomplete_indices


def check_consistency(data: List[Dict[str, Any]], schema: Dict[str, Any]) -> Tuple[float, List[int]]:
    """
    检查数据一致性
    
    一致性（consistency）：字段类型、取值范围符合schema定义的样本比例
    返回: (一致率, 不一致的样本索引列表)
    """
    total = len(data)
    inconsistent_indices = []
    properties = schema.get('properties', {})
    
    for idx, sample in enumerate(data):
        is_consistent = True
        for field, field_schema in properties.items():
            if field in sample and sample[field] is not None:
                expected_type = field_schema.get('type')
                if expected_type == 'string' and not isinstance(sample[field], str):
                    is_consistent = False
                    break
                elif expected_type == 'integer' and not isinstance(sample[field], int):
                    is_consistent = False
                    break
                elif expected_type == 'number' and not isinstance(sample[field], (int, float)):
                    is_consistent = False
                    break
                
                if 'enum' in field_schema and sample[field] not in field_schema['enum']:
                    is_consistent = False
                    break
                
                if 'minLength' in field_schema and isinstance(sample[field], str) and len(sample[field]) < field_schema['minLength']:
                    is_consistent = False
                    break
        
        if not is_consistent:
            inconsistent_indices.append(idx)
    
    consistency = (total - len(inconsistent_indices)) / total if total > 0 else 0.0
    return consistency, inconsistent_indices


def check_label_distribution(data: List[Dict[str, Any]], label_field: str = 'label') -> Dict[str, int]:
    """检查标签分布，辅助识别准确性问题"""
    labels = [sample.get(label_field) for sample in data if label_field in sample]
    return dict(Counter(labels))


def check_duplicates(data: List[Dict[str, Any]], id_field: str = 'id') -> Tuple[int, List[str]]:
    """检查重复样本"""
    ids = [sample.get(id_field) for sample in data if id_field in sample]
    id_counts = Counter(ids)
    duplicates = [id_ for id_, count in id_counts.items() if count > 1]
    return len(duplicates), duplicates


def check_data_quality(dataset_dir: str, required_fields: List[str] = None) -> Dict[str, Any]:
    """
    综合数据质量检查主函数
    
    完整性（completeness）、一致性（consistency）、准确性（accuracy）
    """
    if required_fields is None:
        required_fields = ['id', 'text', 'label']
    
    results = {
        'dataset_dir': dataset_dir,
        'splits': {},
        'overall_quality': {}
    }
    
    schema_path = os.path.join(dataset_dir, 'schema.json')
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    else:
        schema = {'properties': {}}
        print("警告: 未找到schema.json，跳过一致性检查的类型校验")
    
    total_samples = 0
    total_weighted_completeness = 0.0
    total_weighted_consistency = 0.0
    
    for split_name in ['train', 'validation', 'test']:
        split_path = os.path.join(dataset_dir, 'data', split_name)
        if not os.path.exists(split_path):
            continue
        
        split_results = {'files': {}}
        
        for filename in os.listdir(split_path):
            if filename.endswith('.jsonl'):
                file_path = os.path.join(split_path, filename)
                data = load_jsonl(file_path)
                n_samples = len(data)
                total_samples += n_samples
                
                completeness, incomplete_idx = check_completeness(data, required_fields)
                consistency, inconsistent_idx = check_consistency(data, schema)
                label_dist = check_label_distribution(data)
                n_duplicates, duplicate_ids = check_duplicates(data)
                
                total_weighted_completeness += completeness * n_samples
                total_weighted_consistency += consistency * n_samples
                
                split_results['files'][filename] = {
                    'total_samples': n_samples,
                    'completeness': round(completeness, 4),
                    'consistency': round(consistency, 4),
                    'incomplete_samples': len(incomplete_idx),
                    'inconsistent_samples': len(inconsistent_idx),
                    'duplicate_samples': n_duplicates,
                    'label_distribution': label_dist
                }
                
                if incomplete_idx:
                    print(f"[{split_name}/{filename}] 发现 {len(incomplete_idx)} 个不完整样本，前5个索引: {incomplete_idx[:5]}")
                if inconsistent_idx:
                    print(f"[{split_name}/{filename}] 发现 {len(inconsistent_idx)} 个不一致样本，前5个索引: {inconsistent_idx[:5]}")
                if duplicate_ids:
                    print(f"[{split_name}/{filename}] 发现 {n_duplicates} 个重复ID，示例: {duplicate_ids[:5]}")
        
        results['splits'][split_name] = split_results
    
    if total_samples > 0:
        avg_completeness = total_weighted_completeness / total_samples
        avg_consistency = total_weighted_consistency / total_samples
        
        results['overall_quality'] = {
            'total_samples': total_samples,
            'completeness': round(avg_completeness, 4),
            'consistency': round(avg_consistency, 4),
            'note': '准确性（accuracy）需要人工抽样核验或与黄金标准对比计算，脚本仅做格式检查'
        }
    
    return results


if __name__ == '__main__':
    quality_report = check_data_quality('./chinese-sentiment-corpus')
    print("\n===== 数据质量报告 =====")
    print(json.dumps(quality_report['overall_quality'], ensure_ascii=False, indent=2))
```

**脚本使用说明**：
1. 将脚本保存为 `check_quality.py` 放在数据集目录下
2. 根据实际数据格式修改 `required_fields` 和加载函数
3. 运行脚本即可自动检查完整性、一致性、重复样本等问题
4. **准确性（accuracy）** 指标需要人工抽样审核或与黄金标准数据集对比，自动化脚本难以完全覆盖

> **注意**：建议在数据预处理阶段、数据集发布前、每次训练启动前都运行质量检查，将质量指标作为CI/CD流水线的门禁条件，避免低质量数据进入训练流程。

### 2.2 数据集文档

完整、规范的文档是数据集可发现、可理解、可复用的前提。README.md作为数据集的主要文档入口，应包含使用者需要了解的所有关键信息。

#### 2.2.1 README编写规范

**适用场景**：所有数据集创建、数据集重大更新、对外发布开源数据集

README.md是数据集的"门面"，新用户首先通过README了解数据集的基本情况。一份合格的数据集README应包含以下八个核心部分：

**数据集 README 完整模板**：
````markdown
# 数据集名称

> 一句话概述数据集的用途和特点

## 一、概述

简要介绍数据集的背景、目的和适用场景。说明数据集解决什么问题，适合哪些任务使用。

**示例**：
本数据集是中文电商评论情感分析语料库，收集自主流电商平台的真实用户评论，可用于情感分类、意见挖掘、市场分析等NLP任务。

## 二、数据来源

说明数据的收集渠道、采集时间、采集范围、标注人员构成、标注流程等信息。

- **数据来源平台**：[如京东、淘宝、微博等]
- **采集时间范围**：YYYY-MM 至 YYYY-MM
- **数据规模**：总样本数、各划分数量
- **标注流程**：
  1. 初步标注：X名标注人员独立标注
  2. 交叉审核：不一致样本由第三方审核
  3. 最终校验：领域专家抽样核验
- **标注规范链接**：如有详细标注指南，提供文档链接

## 三、数据格式

详细说明数据的组织格式、字段定义、文件结构。

### 3.1 目录结构
```
dataset-name/
├── README.md
├── data/
│   ├── train/
│   │   └── train.jsonl
│   ├── validation/
│   │   └── validation.jsonl
│   └── test/
│       └── test.jsonl
├── metadata.json
├── schema.json
└── examples/
```

### 3.2 字段说明

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| id | string | 样本唯一ID | "rev_000001" |
| text | string | 评论文本内容 | "这个产品质量很好，物流很快！" |
| label | string | 情感标签：positive/negative/neutral | "positive" |
| rating | integer | 评分（1-5星） | 5 |
| source | string | 来源平台 | "jd" |

### 3.3 标签定义

- `positive`：正面情感，表示用户满意、赞赏
- `negative`：负面情感，表示用户不满、批评
- `neutral`：中性情感，表示客观描述或无明显情感倾向

## 四、使用说明

提供加载数据和使用数据集的代码示例。

### 4.1 快速加载示例
```python
import json

def load_dataset(split="train"):
    data = []
    with open(f"data/{split}/{split}.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data

# 加载训练集
train_data = load_dataset("train")
print(f"训练集样本数: {len(train_data)}")
print(f"示例样本: {train_data[0]}")
```

### 4.2 典型使用场景
- 文本分类模型训练
- 情感分析系统开发
- NLP预训练模型微调
- 电商舆情监控

## 五、质量评估

说明数据集的质量指标、已知问题和局限性。

### 5.1 数据质量指标
- **完整性**：99.8%（必填字段无缺失）
- **一致性**：98.5%（标注口径统一）
- **准确性**：97.2%（经专家抽样核验）

### 5.2 类别分布
| 类别 | 训练集 | 验证集 | 测试集 |
|------|--------|--------|--------|
| positive | 32,000 | 4,000 | 4,000 |
| negative | 28,000 | 3,500 | 3,500 |
| neutral | 20,000 | 2,500 | 2,500 |

### 5.3 已知局限性
- 数据主要来源于电商领域，对其他领域（如新闻、社交媒体）的泛化效果可能有限
- 中性类别的识别难度较大，准确率相对较低
- 仅包含简体中文文本，不支持繁体中文和其他语言

## 六、许可证

明确数据集的授权许可和使用限制。

本数据集采用 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) 许可证发布：
- ✅ 允许商业使用
- ✅ 允许修改和二次分发
- ✅ 允许私人和学术研究使用
- ⚠️ 必须保留原作者署名
- ⚠️ 必须标注数据来源

## 七、引用

如果数据集用于学术研究或公开项目，请按以下格式引用：

```bibtex
@dataset{chinese-sentiment-corpus-2026,
  title={Chinese E-commerce Sentiment Corpus},
  author={Data Team},
  year={2026},
  publisher={AtomGit AI},
  howpublished={\url{https://ai.gitcode.com/dataset/chinese-sentiment-corpus}}
}
```

## 八、联系方式

- 维护者：[团队/个人名称]
- 邮箱：[联系邮箱]
- 问题反馈：[Issue链接]
- 更新日志：[CHANGELOG.md链接]

---

*最后更新时间：2026-07-01*
````

**README编写原则**：
1. **信息完整**：覆盖上述八个部分，不遗漏关键信息
2. **示例充分**：提供可直接运行的代码示例，降低使用门槛
3. **诚实透明**：明确说明数据的局限性和已知问题，不夸大质量
4. **更新及时**：数据集更新时同步更新README，保持信息时效性

#### 2.2.2 辅助文档补充

**适用场景**：复杂数据集发布、学术数据集、团队内部协作数据集

除README.md外，建议根据数据集复杂度补充以下辅助文档：

| 文档名称 | 用途 | 适用场景 |
|----------|------|----------|
| `CHANGELOG.md` | 记录数据集版本变更历史 | 所有迭代更新的数据集 |
| `ANNOTATION-GUIDELINES.md` | 详细标注规范说明 | 新标注团队入职、标注口径统一 |
| `DATA-STATISTICS.md` | 详细的数据统计分析报告 | 学术数据集、大规模数据集 |
| `examples/` | 各类别的典型样本展示 | 帮助快速理解数据特点 |

⚠️ **重要提示**：
- README中应明确标注数据集的潜在偏见和伦理风险（如性别偏见、地域偏见等）
- 如果数据集包含个人隐私信息，必须说明脱敏处理方式
- 对于敏感领域数据（如医疗、金融），应额外提供使用限制说明

> **注意**：README文档建议同时提供中文版和英文版，便于国际协作和开源社区使用。至少应保证英文版本包含核心信息（概述、数据格式、许可证、引用格式）。

---

## 三、Space应用最佳实践

### 3.1 架构设计

良好的架构设计是Space应用稳定运行、易于维护和扩展的基础。**Space应用**是AtomGit平台上的AI应用托管服务，用于部署和分享模型Demo。推荐采用模块化设计思想，将应用拆分为独立的功能模块，并通过标准化配置文件管理应用运行参数。

#### 3.1.1 模块化设计

**适用场景**：所有Space应用开发、复杂AI Demo构建、团队协作开发的应用项目

采用模块化架构能够实现关注点分离，便于独立开发、测试和维护各个功能组件。基于**Flask**（轻量级Python Web框架）开发Space应用时，建议将推理流程拆分为三个核心模块：

**推荐项目目录结构**：
```
space-app/
├── app.yaml              # 应用配置文件
├── main.py               # Flask应用入口
├── requirements.txt      # Python依赖
├── modules/
│   ├── __init__.py
│   ├── preprocessor.py   # 数据预处理模块
│   ├── model.py          # 模型推理模块
│   └── postprocessor.py  # 结果后处理模块
└── static/               # 静态资源（CSS/JS/图片）
    └── index.html
```

**模块职责说明**：
- `preprocessor.py`：负责输入数据的校验、清洗、格式转换、Tokenization等预处理工作
- `model.py`：负责模型加载、推理执行、批量预测等核心计算逻辑
- `postprocessor.py`：负责推理结果的解码、格式化、置信度计算、结果过滤等后处理工作

**Flask主入口文件示例**（main.py）：
```python
from flask import Flask, request, jsonify
from modules.preprocessor import Preprocessor
from modules.model import ModelWrapper
from modules.postprocessor import Postprocessor

app = Flask(__name__)

preprocessor = Preprocessor()
model = ModelWrapper()
postprocessor = Postprocessor()


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        preprocessed = preprocessor.process(data)
        raw_output = model.predict(preprocessed)
        result = postprocessor.process(raw_output)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**数据预处理模块示例**（modules/preprocessor.py）：
```python
from typing import Dict, Any


class Preprocessor:
    def __init__(self):
        self.max_length = 512
    
    def validate_input(self, data: Dict[str, Any]) -> None:
        if 'text' not in data:
            raise ValueError("Missing required field: 'text'")
        if not isinstance(data['text'], str):
            raise TypeError("Field 'text' must be a string")
        if len(data['text'].strip()) == 0:
            raise ValueError("Field 'text' cannot be empty")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_input(data)
        text = data['text'].strip()
        
        return {
            'text': text,
            'max_length': data.get('max_length', self.max_length)
        }
```

> **注意**：模块化设计时应确保模块间通过明确的接口通信，避免直接访问其他模块的内部状态。预处理模块负责输入合法性校验，可以有效防止非法输入导致模型服务崩溃。

#### 3.1.2 配置文件管理

**适用场景**：Space应用部署、多环境配置管理、资源配额调整、依赖版本管理

Space应用使用 `app.yaml` 作为统一的配置文件，平台通过该文件识别应用的运行环境、入口点、资源需求等信息。一个完整的配置文件应包含以下核心字段：

**app.yaml 完整配置示例**：
```yaml
runtime: python3.9
entrypoint: gunicorn -w 4 -b 0.0.0.0:8000 main:app

env_variables:
  MODEL_NAME: bert-chinese-sentiment-analysis
  MODEL_CACHE_DIR: /tmp/model-cache
  LOG_LEVEL: INFO
  MAX_BATCH_SIZE: 16

resources:
  cpu: "2"
  memory: "8Gi"
  gpu: "1"
  gpu_type: "T4"

dependencies:
  - transformers>=4.30.0
  - torch>=2.0.0
  - flask>=2.3.0
  - gunicorn>=21.2.0
  - redis>=5.0.0
  - numpy>=1.24.0
  - pillow>=10.0.0

health_check:
  path: /health
  initial_delay_seconds: 30
  period_seconds: 10
  timeout_seconds: 5
  failure_threshold: 3
```

**配置字段详解**：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `runtime` | 运行时语言及版本 | `python3.9`、`python3.10` |
| `entrypoint` | 应用启动命令，推荐使用gunicorn作为生产级WSGI服务器 | `gunicorn -w 4 -b 0.0.0.0:8000 main:app` |
| `env_variables` | 环境变量，用于配置模型路径、日志级别等运行时参数 | 键值对形式 |
| `resources.cpu` | CPU核心数配额 | `"2"` 表示2核 |
| `resources.memory` | 内存配额 | `"8Gi"` 表示8GB |
| `resources.gpu` | GPU卡数配额 | `"0"` 或 `"1"` |
| `dependencies` | Python依赖包列表，与requirements.txt保持一致 | 带版本范围的包名 |
| `health_check.path` | 健康检查接口路径 | `/health` |

⚠️ **重要提示**：
- `entrypoint` 建议使用 `gunicorn` 多进程模式启动，`-w` 参数设置工作进程数，一般推荐为CPU核心数的2-4倍
- GPU资源按需申请，不需要GPU的应用（如简单的数据处理Demo）将gpu设为"0"可以大幅降低资源等待时间
- `initial_delay_seconds` 应根据模型加载时间合理设置，大模型建议设置为60-120秒，避免应用启动期间健康检查失败
- 环境变量中不要硬编码密钥、Token等敏感信息，敏感配置应通过平台的密钥管理功能注入

**代码中读取环境变量示例**：
```python
import os

MODEL_NAME = os.getenv('MODEL_NAME', 'bert-chinese-sentiment-analysis')
MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', '/tmp/model-cache')
MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '16'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

> **注意**：所有环境变量读取都应提供默认值，确保本地开发时无需额外配置即可运行。生产环境通过env_variables覆盖默认值，实现本地开发与线上部署配置隔离。

> 💡 **交叉参考**：安全章节中关于环境变量管理和敏感信息保护的最佳实践同样适用于Space应用配置，详见「第六章 安全最佳实践」。模型配置文件的设计思路可参考「1.1.3 模型配置文件优化」章节。

### 3.2 性能优化

性能是用户体验的关键因素，AI推理通常计算密集且耗时较长。通过合理的缓存策略和**异步处理**（不阻塞主线程的并发处理方式），可以显著提升应用的响应速度和并发处理能力。

#### 3.2.1 Redis缓存策略

**适用场景**：重复请求较多的Demo应用、高并发访问场景、相同输入重复推理的业务场景

**Redis**（高性能内存键值数据库，常用于缓存）能够将频繁请求的推理结果存储在内存中，避免重复的模型计算。推荐使用装饰器模式实现缓存逻辑，保持业务代码的简洁性。

**Redis缓存装饰器实现**（modules/cache.py）：
```python
import json
import hashlib
import redis
from functools import wraps
from typing import Callable, Any


def init_redis(host: str = 'localhost', port: int = 6379, db: int = 0):
    return redis.Redis(host=host, port=port, db=db, decode_responses=True)


def cache_result(redis_client: redis.Redis, expire_seconds: int = 3600):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            cached = redis_client.get(cache_key)
            if cached is not None:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            
            redis_client.setex(
                cache_key,
                expire_seconds,
                json.dumps(result, ensure_ascii=False)
            )
            
            return result
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    key_data = {
        'func': func_name,
        'args': _make_hashable(args),
        'kwargs': _make_hashable(kwargs)
    }
    key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
    return f"ai:inference:{hashlib.md5(key_str.encode('utf-8')).hexdigest()}"


def _make_hashable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, (list, tuple)):
        return tuple(_make_hashable(item) for item in obj)
    elif isinstance(obj, set):
        return tuple(sorted(_make_hashable(item) for item in obj))
    return obj
```

**在模型推理模块中应用缓存**（modules/model.py）：
```python
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modules.cache import init_redis, cache_result


redis_client = init_redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379'))
)


class ModelWrapper:
    def __init__(self):
        model_name = os.getenv('MODEL_NAME', 'bert-chinese-sentiment-analysis')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
    
    @cache_result(redis_client, expire_seconds=7200)
    def predict(self, preprocessed_data: dict) -> dict:
        text = preprocessed_data['text']
        max_length = preprocessed_data.get('max_length', 512)
        
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=max_length,
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            confidence, pred_idx = torch.max(probabilities, dim=-1)
        
        return {
            'label': self.id2label[pred_idx.item()],
            'confidence': round(confidence.item(), 4),
            'probabilities': {
                self.id2label[i]: round(prob.item(), 4)
                for i, prob in enumerate(probabilities[0])
            }
        }
```

**缓存配置说明**：
- 缓存过期时间（`expire_seconds`）根据业务场景设置：静态Demo可设为24小时，动态内容建议1-2小时
- 缓存键通过MD5哈希生成，确保相同输入生成相同的缓存键
- 缓存值使用JSON序列化存储，支持复杂的推理结果结构
- Redis连接通过环境变量配置，便于不同环境使用不同的缓存实例

> **注意**：对于包含随机因素（如Dropout、采样生成）的模型，不要使用缓存策略，或者确保模型处于评估模式（`model.eval()`）关闭随机性。

⚠️ **重要提示**：
- 缓存键必须包含所有影响推理结果的参数，避免不同输入命中错误缓存
- 敏感数据推理结果不应缓存，或使用加密存储
- 建议添加缓存命中率监控，便于评估缓存效果
- 应用启动时应处理Redis连接失败的降级逻辑，缓存不可用时直接执行推理

#### 3.2.2 异步批量预测

**适用场景**：批量请求处理、高并发场景、大模型推理延迟较高的应用

当并发请求较多时，同步逐个处理会导致请求排队等待。**异步处理**配合**ThreadPoolExecutor**（Python线程池执行器，用于并发执行任务）可以实现请求的并发处理和批量推理，显著提升吞吐量。

**异步批量预测实现**（modules/async_predictor.py）：
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from modules.model import ModelWrapper


class AsyncBatchPredictor:
    def __init__(self, model: ModelWrapper, max_workers: int = 4, max_batch_size: int = 8):
        self.model = model
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_batch_size = max_batch_size
        self.loop = asyncio.get_event_loop()
    
    async def predict_async(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.loop.run_in_executor(
            self.executor,
            self.model.predict,
            preprocessed_data
        )
    
    async def predict_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks = []
        for i in range(0, len(batch_data), self.max_batch_size):
            mini_batch = batch_data[i:i + self.max_batch_size]
            mini_batch_tasks = [
                self.predict_async(data)
                for data in mini_batch
            ]
            tasks.extend(mini_batch_tasks)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'input_index': idx
                })
            else:
                processed_results.append({
                    'success': True,
                    'result': result,
                    'input_index': idx
                })
        
        return processed_results
    
    def shutdown(self):
        self.executor.shutdown(wait=True)
```

**Flask中集成异步处理的异步路由示例**：
```python
import asyncio
from flask import Flask, request, jsonify
from modules.preprocessor import Preprocessor
from modules.model import ModelWrapper
from modules.postprocessor import Postprocessor
from modules.async_predictor import AsyncBatchPredictor

app = Flask(__name__)

preprocessor = Preprocessor()
model = ModelWrapper()
postprocessor = Postprocessor()
async_predictor = AsyncBatchPredictor(model, max_workers=4, max_batch_size=8)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        preprocessed = preprocessor.process(data)
        raw_output = model.predict(preprocessed)
        result = postprocessor.process(raw_output)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    try:
        data = request.get_json()
        inputs = data.get('inputs', [])
        
        if not inputs or not isinstance(inputs, list):
            return jsonify({'success': False, 'error': "'inputs' must be a non-empty list"}), 400
        
        if len(inputs) > 64:
            return jsonify({'success': False, 'error': "Batch size cannot exceed 64"}), 400
        
        preprocessed_batch = [preprocessor.process(item) for item in inputs]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(
                async_predictor.predict_batch(preprocessed_batch)
            )
        finally:
            loop.close()
        
        final_results = []
        for res in results:
            if res['success']:
                final_results.append({
                    'success': True,
                    'result': postprocessor.process(res['result'])
                })
            else:
                final_results.append(res)
        
        return jsonify({
            'success': True,
            'batch_size': len(inputs),
            'results': final_results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**线程池参数配置建议**：

| 参数 | CPU密集型推理 | IO密集型推理（如调用远程API） |
|------|--------------|---------------------------|
| max_workers | CPU核心数 或 CPU核心数+1 | CPU核心数 × 2 到 CPU核心数 × 5 |
| max_batch_size | 根据GPU显存大小调整（4-32） | 根据API限流调整（8-64） |

⚠️ **重要提示**：
- 异步处理使用线程池而非进程池，因为模型通常加载在内存中，多进程会导致内存占用倍增
- 批量大小不是越大越好，过大的批次会导致单个请求延迟增加，需要根据模型特点和SLA要求找到平衡点
- 务必设置批量大小上限，防止恶意的大批量请求导致服务内存溢出
- 异步批量接口需要做好异常隔离，单个样本失败不应影响整个批次的处理

> **注意**：Flask默认是同步框架，上述示例使用 `asyncio.run_in_executor` 将同步推理放到线程池执行。如果需要原生异步支持，可以考虑使用FastAPI替代Flask，获得更好的异步性能。

---

## 四、Notebook开发最佳实践

### 4.1 代码组织

**Jupyter Notebook**（交互式计算环境，支持代码、可视化、文档混合）是数据探索和模型实验的主要工具。良好的代码组织能够提升Notebook的可读性、可复现性和可维护性，避免"代码面条"问题。推荐采用单元格六步结构和面向对象的函数类设计。

#### 4.1.1 单元格六步结构

**适用场景**：所有Notebook实验、模型训练脚本、数据分析报告、团队协作共享的Notebook文件

Notebook的单元格应按照机器学习工作流进行逻辑划分，遵循"导入配置→数据加载→数据探索→数据预处理→模型训练→结果评估"的六步结构。每个步骤对应一个或多个单元格，便于理解和调试。

**标准Notebook单元格结构示例**：

**单元格1：导入配置**
```python
import os
import sys
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(RANDOM_SEED)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {DEVICE}")

DATA_DIR = './data'
MODEL_DIR = './models'
OUTPUT_DIR = './outputs'
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

BATCH_SIZE = 32
LEARNING_RATE = 2e-5
NUM_EPOCHS = 10
MAX_SEQ_LENGTH = 512
```

**单元格2：数据加载**
```python
def load_data(data_dir):
    train_path = os.path.join(data_dir, 'train', 'train.jsonl')
    val_path = os.path.join(data_dir, 'validation', 'validation.jsonl')
    test_path = os.path.join(data_dir, 'test', 'test.jsonl')
    
    def read_jsonl(path):
        data = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return pd.DataFrame(data)
    
    train_df = read_jsonl(train_path)
    val_df = read_jsonl(val_path)
    test_df = read_jsonl(test_path)
    
    print(f"训练集: {len(train_df)} 样本")
    print(f"验证集: {len(val_df)} 样本")
    print(f"测试集: {len(test_df)} 样本")
    
    return train_df, val_df, test_df

train_df, val_df, test_df = load_data(DATA_DIR)
train_df.head()
```

**单元格3：数据探索**
```python
print("===== 数据概览 =====")
print(train_df.info())
print("\n===== 标签分布 =====")
print(train_df['label'].value_counts())

plt.figure(figsize=(8, 5))
sns.countplot(data=train_df, x='label')
plt.title('训练集标签分布')
plt.xlabel('情感标签')
plt.ylabel('样本数量')
plt.show()

train_df['text_length'] = train_df['text'].apply(len)
print("\n===== 文本长度统计 =====")
print(train_df['text_length'].describe())

plt.figure(figsize=(10, 5))
sns.histplot(data=train_df, x='text_length', bins=50, kde=True)
plt.title('文本长度分布')
plt.xlabel('字符数')
plt.ylabel('频次')
plt.show()
```

**单元格4：数据预处理**
```python
class DataProcessor:
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.label2id = {'negative': 0, 'neutral': 1, 'positive': 2}
        self.id2label = {v: k for k, v in self.label2id.items()}
    
    def clean_text(self, text):
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def encode_texts(self, texts):
        return self.tokenizer(
            texts,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
    
    def process_dataframe(self, df):
        df = df.copy()
        df['text'] = df['text'].apply(self.clean_text)
        df['label_id'] = df['label'].map(self.label2id)
        return df
    
    def chain(self, df):
        return self.process_dataframe(df)

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-chinese')
processor = DataProcessor(tokenizer, max_length=MAX_SEQ_LENGTH)

train_df = processor.process_dataframe(train_df)
val_df = processor.process_dataframe(val_df)
test_df = processor.process_dataframe(test_df)
```

**单元格5：模型训练**
```python
class SentimentDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        item = {key: val[idx] for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

train_encodings = processor.encode_texts(train_df['text'].tolist())
val_encodings = processor.encode_texts(val_df['text'].tolist())

train_dataset = SentimentDataset(train_encodings, train_df['label_id'].tolist())
val_dataset = SentimentDataset(val_encodings, val_df['label_id'].tolist())

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained(
    'bert-base-chinese',
    num_labels=3,
    id2label=processor.id2label,
    label2id=processor.label2id
)
model.to(DEVICE)

optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
criterion = nn.CrossEntropyLoss()

train_losses = []
val_losses = []
best_val_f1 = 0

for epoch in range(NUM_EPOCHS):
    model.train()
    total_train_loss = 0
    
    for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{NUM_EPOCHS}'):
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(DEVICE)
        attention_mask = batch['attention_mask'].to(DEVICE)
        labels = batch['labels'].to(DEVICE)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits
        
        loss.backward()
        optimizer.step()
        total_train_loss += loss.item()
    
    avg_train_loss = total_train_loss / len(train_loader)
    train_losses.append(avg_train_loss)
    
    model.eval()
    total_val_loss = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(DEVICE)
            attention_mask = batch['attention_mask'].to(DEVICE)
            labels = batch['labels'].to(DEVICE)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            logits = outputs.logits
            
            total_val_loss += loss.item()
            preds = torch.argmax(logits, dim=-1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    avg_val_loss = total_val_loss / len(val_loader)
    val_losses.append(avg_val_loss)
    val_accuracy = accuracy_score(all_labels, all_preds)
    val_f1 = f1_score(all_labels, all_preds, average='macro')
    
    print(f'\nEpoch {epoch+1}:')
    print(f'  训练损失: {avg_train_loss:.4f}')
    print(f'  验证损失: {avg_val_loss:.4f}')
    print(f'  验证准确率: {val_accuracy:.4f}')
    print(f'  验证F1: {val_f1:.4f}')
    
    if val_f1 > best_val_f1:
        best_val_f1 = val_f1
        model.save_pretrained(os.path.join(MODEL_DIR, 'best_model'))
        tokenizer.save_pretrained(os.path.join(MODEL_DIR, 'best_model'))
        print(f'  保存最佳模型，F1: {best_val_f1:.4f}')
```

**单元格6：结果评估**
```python
plt.figure(figsize=(10, 5))
plt.plot(train_losses, label='训练损失')
plt.plot(val_losses, label='验证损失')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('训练过程损失曲线')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(OUTPUT_DIR, 'loss_curve.png'), dpi=150, bbox_inches='tight')
plt.show()

test_encodings = processor.encode_texts(test_df['text'].tolist())
test_dataset = SentimentDataset(test_encodings, test_df['label_id'].tolist())
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for batch in tqdm(test_loader, desc='测试评估'):
        input_ids = batch['input_ids'].to(DEVICE)
        attention_mask = batch['attention_mask'].to(DEVICE)
        labels = batch['labels'].to(DEVICE)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=-1)
        
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

test_accuracy = accuracy_score(all_labels, all_preds)
test_f1 = f1_score(all_labels, all_preds, average='macro')

print("===== 测试集评估结果 =====")
print(f"准确率: {test_accuracy:.4f}")
print(f"F1分数(macro): {test_f1:.4f}")
print("\n===== 分类报告 =====")
print(classification_report(all_labels, all_preds, target_names=['negative', 'neutral', 'positive']))

results = {
    'test_accuracy': float(test_accuracy),
    'test_f1_macro': float(test_f1),
    'best_val_f1': float(best_val_f1),
    'hyperparameters': {
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE,
        'num_epochs': NUM_EPOCHS,
        'max_seq_length': MAX_SEQ_LENGTH
    }
}

with open(os.path.join(OUTPUT_DIR, 'results.json'), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n结果已保存到 {OUTPUT_DIR}")
```

**单元格划分原则**：
- 每个单元格只做一件事，保持单一职责
- 单元格按执行顺序排列，从上到下顺序执行应能复现完整结果
- 配置参数集中放在第一个单元格，便于调整超参数
- 数据探索和结果可视化使用独立单元格，便于查看图表
- 过长的单元格应拆分，单个单元格建议不超过50行代码

> **注意**：不要在Notebook中保留调试用的临时代码或注释掉的大段代码，完成实验后应清理无用单元格，保持Notebook整洁。

#### 4.1.2 函数和类设计

**适用场景**：重复使用的数据处理逻辑、复杂预处理流程、需要复用的模型组件、团队协作开发的Notebook

将重复逻辑封装为函数和类，能够提升代码复用性，减少错误。推荐使用**链式调用**（方法返回对象本身，实现连续方法调用的设计模式）设计数据处理类，让预处理流程更加清晰流畅。

**支持链式调用的DataProcessor类示例**：
```python
import re
import pandas as pd
import numpy as np
from typing import List, Optional, Union
from sklearn.preprocessing import LabelEncoder


class DataProcessor:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.text_normalizer = None
        self.stopwords = set()
        self.is_fitted = False
    
    def reset(self) -> 'DataProcessor':
        self.label_encoder = LabelEncoder()
        self.is_fitted = False
        return self
    
    def load_stopwords(self, path: Optional[str] = None) -> 'DataProcessor':
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.stopwords = set(line.strip() for line in f if line.strip())
        else:
            self.stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        return self
    
    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ''
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？、；：""''（）]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def remove_stopwords(self, text: str) -> str:
        words = text.split()
        words = [w for w in words if w not in self.stopwords]
        return ' '.join(words)
    
    def fit(self, df: pd.DataFrame, text_col: str = 'text', label_col: str = 'label') -> 'DataProcessor':
        self.text_col = text_col
        self.label_col = label_col
        self.label_encoder.fit(df[label_col])
        self.is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("请先调用fit()方法适配处理器")
        
        df = df.copy()
        df['cleaned_text'] = df[self.text_col].apply(self.clean_text)
        if self.stopwords:
            df['cleaned_text'] = df['cleaned_text'].apply(self.remove_stopwords)
        df['text_length'] = df['cleaned_text'].apply(len)
        df['label_id'] = self.label_encoder.transform(df[self.label_col])
        return df
    
    def fit_transform(self, df: pd.DataFrame, text_col: str = 'text', label_col: str = 'label') -> pd.DataFrame:
        return self.fit(df, text_col, label_col).transform(df)
    
    def filter_by_length(self, df: pd.DataFrame, min_len: int = 5, max_len: int = 512) -> pd.DataFrame:
        return df[(df['text_length'] >= min_len) & (df['text_length'] <= max_len)].copy()
    
    def train_val_test_split(
        self, 
        df: pd.DataFrame, 
        val_size: float = 0.1, 
        test_size: float = 0.1, 
        stratify: bool = True,
        random_state: int = 42
    ) -> tuple:
        stratify_col = df['label_id'] if stratify else None
        
        train_df, temp_df = train_test_split(
            df, 
            test_size=val_size + test_size, 
            random_state=random_state,
            stratify=stratify_col
        )
        
        if stratify_col is not None:
            temp_stratify = temp_df['label_id']
        else:
            temp_stratify = None
        
        relative_test_size = test_size / (val_size + test_size)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=relative_test_size,
            random_state=random_state,
            stratify=temp_stratify
        )
        
        return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


processor = DataProcessor()
processor.load_stopwords()

processed_df = processor.fit_transform(train_df, text_col='text', label_col='label')
processed_df = processor.filter_by_length(processed_df, min_len=5, max_len=512)

train_processed, val_processed, test_processed = processor.train_val_test_split(
    processed_df,
    val_size=0.1,
    test_size=0.1,
    stratify=True
)

print(f"处理后训练集: {len(train_processed)} 样本")
print(f"处理后验证集: {len(val_processed)} 样本")
print(f"处理后测试集: {len(test_processed)} 样本")
```

**链式调用设计要点**：
- 每个配置方法返回 `self`（即对象本身），支持连续调用
- 数据处理方法（transform、filter等）返回新的DataFrame，不修改原始数据
- 采用 `fit` → `transform` 模式，与scikit-learn API保持一致，便于理解
- 方法命名清晰，见名知意

⚠️ **重要提示**：
- 类的状态管理要谨慎，避免因执行顺序不同导致结果不一致
- 数据处理方法应尽量无副作用，不修改输入的原始数据
- 包含随机性的操作必须设置随机种子，确保结果可复现
- 函数和类应添加必要的文档字符串（docstring），说明参数、返回值和功能

> **注意**：当逻辑超过3次重复使用时，应考虑封装为函数；当函数需要维护状态或多个函数紧密关联时，应考虑封装为类。

> 💡 **交叉参考**：协作开发章节中的代码规范（命名规范、类型提示、文档字符串、PEP 8风格等）同样适用于Notebook开发中的函数和类设计，详见「5.1.1 代码规范」章节。

---

### 4.2 实验管理

机器学习实验涉及大量超参数组合、指标结果和模型文件，没有良好的实验管理会导致结果难以追溯、重复实验困难。**MLflow**（机器学习生命周期管理平台，用于实验跟踪、模型管理）和检查点机制是实验管理的核心工具。

#### 4.2.1 MLflow实验跟踪

**适用场景**：超参数调优实验、模型版本对比、团队协作实验、需要追溯实验历史的研究项目

MLflow Tracking能够记录实验的参数、指标、模型文件和各种**工件**（artifacts，实验产生的文件产物如图表、日志、模型等），方便对比不同实验的效果。

**MLflow实验跟踪完整示例**：
```python
import mlflow
import mlflow.pytorch
from mlflow.models.signature import infer_signature
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm
import matplotlib.pyplot as plt
import json
import numpy as np

MLFLOW_TRACKING_URI = "./mlruns"
EXPERIMENT_NAME = "sentiment-analysis"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

def train_and_evaluate(
    model_name,
    batch_size,
    learning_rate,
    num_epochs,
    max_seq_length,
    dropout_rate,
    weight_decay,
    train_dataset,
    val_dataset,
    test_dataset,
    run_name=None
):
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params({
            "model_name": model_name,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "num_epochs": num_epochs,
            "max_seq_length": max_seq_length,
            "dropout_rate": dropout_rate,
            "weight_decay": weight_decay,
            "random_seed": 42,
            "device": str(DEVICE)
        })
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=3,
            hidden_dropout_prob=dropout_rate
        )
        model.to(DEVICE)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        criterion = nn.CrossEntropyLoss()
        
        best_val_f1 = 0
        train_losses = []
        val_losses = []
        
        for epoch in range(num_epochs):
            model.train()
            total_train_loss = 0
            
            for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}'):
                optimizer.zero_grad()
                input_ids = batch['input_ids'].to(DEVICE)
                attention_mask = batch['attention_mask'].to(DEVICE)
                labels = batch['labels'].to(DEVICE)
                
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                
                total_train_loss += loss.item()
            
            avg_train_loss = total_train_loss / len(train_loader)
            train_losses.append(avg_train_loss)
            
            model.eval()
            total_val_loss = 0
            all_preds = []
            all_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(DEVICE)
                    attention_mask = batch['attention_mask'].to(DEVICE)
                    labels = batch['labels'].to(DEVICE)
                    
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                    loss = outputs.loss
                    preds = torch.argmax(outputs.logits, dim=-1)
                    
                    total_val_loss += loss.item()
                    all_preds.extend(preds.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())
            
            avg_val_loss = total_val_loss / len(val_loader)
            val_losses.append(avg_val_loss)
            val_acc = accuracy_score(all_labels, all_preds)
            val_f1 = f1_score(all_labels, all_preds, average='macro')
            
            mlflow.log_metrics({
                "train_loss": avg_train_loss,
                "val_loss": avg_val_loss,
                "val_accuracy": val_acc,
                "val_f1_macro": val_f1
            }, step=epoch)
            
            print(f"Epoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_f1={val_f1:.4f}")
            
            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                mlflow.pytorch.log_model(model, "best_model")
                tokenizer.save_pretrained("./temp_tokenizer")
                mlflow.log_artifacts("./temp_tokenizer", "tokenizer")
        
        plt.figure(figsize=(10, 5))
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Val Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        plt.title(f'Training Loss - {run_name or run.info.run_id[:8]}')
        loss_plot_path = "loss_curve.png"
        plt.savefig(loss_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        mlflow.log_artifact(loss_plot_path)
        os.remove(loss_plot_path)
        
        model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch['input_ids'].to(DEVICE)
                attention_mask = batch['attention_mask'].to(DEVICE)
                labels = batch['labels'].to(DEVICE)
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        test_acc = accuracy_score(all_labels, all_preds)
        test_f1 = f1_score(all_labels, all_preds, average='macro')
        
        mlflow.log_metrics({
            "test_accuracy": test_acc,
            "test_f1_macro": test_f1,
            "best_val_f1": best_val_f1
        })
        
        sample_input = {
            "input_ids": next(iter(test_loader))['input_ids'][:2].cpu().numpy(),
            "attention_mask": next(iter(test_loader))['attention_mask'][:2].cpu().numpy()
        }
        
        final_metrics = {
            "best_val_f1": best_val_f1,
            "test_accuracy": test_acc,
            "test_f1_macro": test_f1
        }
        with open("metrics.json", "w", encoding="utf-8") as f:
            json.dump(final_metrics, f, indent=2)
        mlflow.log_artifact("metrics.json")
        os.remove("metrics.json")
        
        print(f"\n===== 测试集结果 =====")
        print(f"Test Accuracy: {test_acc:.4f}")
        print(f"Test F1 Macro: {test_f1:.4f}")
        print(f"Best Val F1: {best_val_f1:.4f}")
        print(f"Run ID: {run.info.run_id}")
        
        return {
            "run_id": run.info.run_id,
            "best_val_f1": best_val_f1,
            "test_accuracy": test_acc,
            "test_f1": test_f1
        }

param_grid = [
    {"learning_rate": 2e-5, "batch_size": 32, "dropout_rate": 0.1},
    {"learning_rate": 3e-5, "batch_size": 16, "dropout_rate": 0.2},
    {"learning_rate": 1e-5, "batch_size": 64, "dropout_rate": 0.1},
]

results = []
for i, params in enumerate(param_grid):
    run_name = f"run_{i+1}_lr{params['learning_rate']}_bs{params['batch_size']}"
    print(f"\n{'='*60}")
    print(f"开始实验: {run_name}")
    print(f"{'='*60}")
    
    result = train_and_evaluate(
        model_name="bert-base-chinese",
        batch_size=params["batch_size"],
        learning_rate=params["learning_rate"],
        num_epochs=5,
        max_seq_length=512,
        dropout_rate=params["dropout_rate"],
        weight_decay=0.01,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        test_dataset=test_dataset,
        run_name=run_name
    )
    results.append(result)

print("\n===== 所有实验结果对比 =====")
for r in results:
    print(f"Run {r['run_id'][:8]}: Val F1={r['best_val_f1']:.4f}, Test F1={r['test_f1']:.4f}")
```

**MLflow跟踪的核心内容**：
- **参数（Parameters）**：超参数配置，如学习率、批次大小、模型结构参数等
- **指标（Metrics）**：训练过程中的数值指标，支持按step记录，可绘制曲线
- **模型（Models）**：训练好的模型文件，支持MLflow Model格式打包，便于后续部署
- **工件（Artifacts）**：其他文件产物，如损失曲线图、分类报告、配置文件、日志等

启动MLflow UI查看实验结果：
```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

⚠️ **重要提示**：
- 每次实验必须设置有意义的run_name，不要使用默认名称，便于后续识别
- 记录所有可能影响结果的参数，包括随机种子、框架版本、硬件设备等
- 不要在不同实验之间复用同一个run，每次实验启动新的run
- 对于大规模超参数搜索，建议使用MLflow的嵌套run功能组织多组实验
- 训练过程中定期保存检查点，避免训练中断导致进度丢失

> **注意**：启动MLflow UI后，可在浏览器中访问 `http://localhost:5000` 对比不同实验的参数和指标，支持图表可视化和结果排序。

#### 4.2.2 检查点机制

**适用场景**：长时间训练的任务、需要中断恢复的实验、Notebook内核重启后的状态恢复、计算资源昂贵的大模型训练

训练深度学习模型可能耗时数小时甚至数天，**检查点（checkpoint）**（训练过程中保存的模型状态快照，用于恢复训练）机制能够在训练中断（如内核重启、连接断开、资源被抢占）时从上次保存的位置继续训练，避免从头开始浪费时间和资源。

**Notebook检查点保存与恢复工具类**：
```python
import os
import pickle
import torch
import time
from datetime import datetime
from typing import Any, Dict, Optional
import dill


class NotebookCheckpoint:
    def __init__(self, checkpoint_dir: str = './checkpoints', max_checkpoints: int = 3):
        self.checkpoint_dir = checkpoint_dir
        self.max_checkpoints = max_checkpoints
        os.makedirs(checkpoint_dir, exist_ok=True)
        self.state = {}
        self.checkpoint_paths = []
    
    def save(self, state: Dict[str, Any], name: Optional[str] = None) -> str:
        if name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name = f'checkpoint_{timestamp}'
        
        checkpoint_path = os.path.join(self.checkpoint_dir, f'{name}.pt')
        
        save_dict = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'state': state
        }
        
        torch.save(save_dict, checkpoint_path, pickle_module=dill)
        
        self.checkpoint_paths.append(checkpoint_path)
        
        if len(self.checkpoint_paths) > self.max_checkpoints:
            old_path = self.checkpoint_paths.pop(0)
            if os.path.exists(old_path):
                os.remove(old_path)
                print(f"删除旧检查点: {os.path.basename(old_path)}")
        
        print(f"检查点已保存: {os.path.basename(checkpoint_path)}")
        return checkpoint_path
    
    def load_latest(self) -> Optional[Dict[str, Any]]:
        import glob
        pattern = os.path.join(self.checkpoint_dir, 'checkpoint_*.pt')
        checkpoints = glob.glob(pattern)
        
        if not checkpoints:
            print("未找到已保存的检查点")
            return None
        
        checkpoints.sort(key=os.path.getmtime, reverse=True)
        latest_path = checkpoints[0]
        
        return self.load(latest_path)
    
    def load(self, checkpoint_path: str) -> Dict[str, Any]:
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"检查点文件不存在: {checkpoint_path}")
        
        print(f"正在加载检查点: {os.path.basename(checkpoint_path)}")
        checkpoint = torch.load(checkpoint_path, map_location='cpu', pickle_module=dill)
        
        self.state = checkpoint['state']
        
        print(f"检查点加载成功，保存时间: {checkpoint['datetime']}")
        return self.state
    
    def list_checkpoints(self) -> list:
        import glob
        pattern = os.path.join(self.checkpoint_dir, 'checkpoint_*.pt')
        checkpoints = glob.glob(pattern)
        checkpoints.sort(key=os.path.getmtime, reverse=True)
        
        info = []
        for path in checkpoints:
            mtime = os.path.getmtime(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            info.append({
                'path': path,
                'name': os.path.basename(path),
                'modified': datetime.fromtimestamp(mtime).isoformat(),
                'size_mb': round(size_mb, 2)
            })
        return info
    
    def save_training_state(
        self,
        epoch: int,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler: Optional[Any] = None,
        train_losses: list = None,
        val_losses: list = None,
        best_metric: float = 0.0,
        global_step: int = 0,
        additional_state: Dict[str, Any] = None,
        name: Optional[str] = None
    ) -> str:
        state = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_losses': train_losses or [],
            'val_losses': val_losses or [],
            'best_metric': best_metric,
            'global_step': global_step,
        }
        
        if scheduler is not None:
            state['scheduler_state_dict'] = scheduler.state_dict()
        
        if additional_state is not None:
            state.update(additional_state)
        
        return self.save(state, name=name)
    
    def load_training_state(
        self,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        checkpoint_path: Optional[str] = None
    ) -> Dict[str, Any]:
        if checkpoint_path is None:
            state = self.load_latest()
        else:
            state = self.load(checkpoint_path)
        
        if state is None:
            return None
        
        model.load_state_dict(state['model_state_dict'])
        
        if optimizer is not None and 'optimizer_state_dict' in state:
            optimizer.load_state_dict(state['optimizer_state_dict'])
        
        if scheduler is not None and 'scheduler_state_dict' in state:
            scheduler.load_state_dict(state['scheduler_state_dict'])
        
        return state


checkpoint_manager = NotebookCheckpoint(checkpoint_dir='./checkpoints', max_checkpoints=3)

print("已保存的检查点:")
for cp in checkpoint_manager.list_checkpoints():
    print(f"  - {cp['name']} ({cp['size_mb']}MB, {cp['modified']})")

resume_training = False
start_epoch = 0
train_losses = []
val_losses = []
best_val_f1 = 0

if resume_training:
    state = checkpoint_manager.load_training_state(model, optimizer, scheduler=None)
    if state:
        start_epoch = state['epoch'] + 1
        train_losses = state['train_losses']
        val_losses = state['val_losses']
        best_val_f1 = state['best_metric']
        print(f"从第 {start_epoch + 1} 轮继续训练，当前最佳F1: {best_val_f1:.4f}")

for epoch in range(start_epoch, NUM_EPOCHS):
    model.train()
    total_train_loss = 0
    
    for batch_idx, batch in enumerate(tqdm(train_loader, desc=f'Epoch {epoch+1}')):
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(DEVICE)
        attention_mask = batch['attention_mask'].to(DEVICE)
        labels = batch['labels'].to(DEVICE)
        
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        
        loss.backward()
        optimizer.step()
        total_train_loss += loss.item()
        
        if (batch_idx + 1) % 100 == 0:
            global_step = epoch * len(train_loader) + batch_idx
            checkpoint_manager.save_training_state(
                epoch=epoch,
                model=model,
                optimizer=optimizer,
                train_losses=train_losses,
                val_losses=val_losses,
                best_metric=best_val_f1,
                global_step=global_step,
                name=f'intermediate_step{global_step}'
            )
    
    avg_train_loss = total_train_loss / len(train_loader)
    train_losses.append(avg_train_loss)
    
    model.eval()
    total_val_loss = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(DEVICE)
            attention_mask = batch['attention_mask'].to(DEVICE)
            labels = batch['labels'].to(DEVICE)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            preds = torch.argmax(outputs.logits, dim=-1)
            
            total_val_loss += loss.item()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    avg_val_loss = total_val_loss / len(val_loader)
    val_losses.append(avg_val_loss)
    val_f1 = f1_score(all_labels, all_preds, average='macro')
    
    if val_f1 > best_val_f1:
        best_val_f1 = val_f1
        model.save_pretrained('./models/best_model')
        print(f"新的最佳模型，F1: {best_val_f1:.4f}")
    
    checkpoint_manager.save_training_state(
        epoch=epoch,
        model=model,
        optimizer=optimizer,
        train_losses=train_losses,
        val_losses=val_losses,
        best_metric=best_val_f1,
        name=f'epoch_{epoch+1}'
    )
    
    print(f"Epoch {epoch+1} 完成，训练损失: {avg_train_loss:.4f}, 验证F1: {val_f1:.4f}")

import dill

def save_notebook_state(variables_dict: Dict[str, Any], path: str = './notebook_state.pkl'):
    save_dict = {
        'timestamp': time.time(),
        'datetime': datetime.now().isoformat(),
        'variables': {}
    }
    
    for key, value in variables_dict.items():
        try:
            dill.pickles(value)
            save_dict['variables'][key] = value
        except Exception as e:
            print(f"跳过变量 {key}: {e}")
    
    with open(path, 'wb') as f:
        dill.dump(save_dict, f)
    
    print(f"Notebook状态已保存到 {path}，包含变量: {list(save_dict['variables'].keys())}")

def load_notebook_state(path: str = './notebook_state.pkl') -> Dict[str, Any]:
    if not os.path.exists(path):
        print(f"状态文件不存在: {path}")
        return {}
    
    with open(path, 'rb') as f:
        save_dict = dill.load(f)
    
    print(f"加载Notebook状态，保存时间: {save_dict['datetime']}")
    print(f"包含变量: {list(save_dict['variables'].keys())}")
    
    return save_dict['variables']

checkpoint_manager.save_training_state(
    epoch=NUM_EPOCHS-1,
    model=model,
    optimizer=optimizer,
    train_losses=train_losses,
    val_losses=val_losses,
    best_metric=best_val_f1,
    name='final'
)

print("训练完成！")
```

**检查点保存策略**：
- **定期保存**：每N个批次（如100批次）或每个Epoch结束后保存检查点
- **仅保留最佳**：始终保留验证指标最好的检查点，其他中间检查点可以只保留最近几个
- **自动清理**：设置最大检查点数量，自动删除过旧的检查点，节省磁盘空间
- **完整状态**：检查点应包含模型权重、优化器状态、调度器状态、当前epoch、已训练步数、指标历史等完整信息

**Notebook状态保存注意事项**：
- 并非所有对象都能被序列化，数据库连接、网络socket、打开的文件句柄等无法保存
- 大型数据集和DataLoader不建议保存，保存关键处理结果即可
- 敏感信息（如API密钥）不应保存在检查点文件中
- 使用 `dill` 库替代标准 `pickle`，可以序列化更多Python对象类型

⚠️ **重要提示**：
- 检查点文件可能很大（包含模型权重和优化器状态），确保磁盘空间充足
- 重要的检查点建议备份到持久化存储，避免实例关闭后数据丢失
- 从检查点恢复训练后，应首先验证第一个batch的结果与中断前一致，确保恢复正确
- 不要依赖检查点替代实验记录，检查点用于恢复训练，MLflow用于结果对比
- Notebook的单元格执行顺序很重要，建议在检查点中也记录关键变量的版本信息

> **注意**：如果使用AtomGit AI平台的Notebook功能，平台会自动保存Notebook的单元格内容，但不会自动保存Python变量状态，训练过程中的检查点需要自己通过代码保存。

---

## 五、协作开发最佳实践

### 5.1 团队协作

团队协作是AI项目成功的关键因素，统一的代码规范和标准化的版本控制工作流能够显著降低沟通成本，减少合并冲突，提升开发效率。

#### 5.1.1 代码规范

**适用场景**：所有团队协作开发项目、开源项目贡献、代码审查、新成员入职培训

统一的代码规范是团队协作的基础，能够让不同开发者编写的代码风格一致，便于阅读和维护。以下是Python AI项目的核心代码规范要求。

##### 5.1.1.1 有意义的命名

变量、函数、类的命名应遵循"见名知意"原则：
- **变量名**：使用小写蛇形命名法（snake_case），如 `learning_rate`、`batch_size`、`model_path`
- **函数名**：使用小写蛇形命名法，动词开头描述功能，如 `load_data()`、`train_model()`、`calculate_metrics()`
- **类名**：使用大驼峰命名法（PascalCase），如 `DataProcessor`、`ModelWrapper`、`Trainer`
- **常量名**：使用全大写蛇形命名法，如 `MAX_SEQ_LENGTH`、`DEFAULT_BATCH_SIZE`、`RANDOM_SEED`

**命名示例对比**：
```python
# 不好的命名
x = 0.001
def func1(data):
    pass
class a:
    pass

# 好的命名
learning_rate = 0.001
def preprocess_text(raw_text):
    pass
class SentimentAnalyzer:
    pass
```

> **注意**：避免使用单字母变量名（除了循环计数器`i/j/k`、数学公式中的`x/y/z`等约定俗成的用法），避免使用拼音或中英文混合命名，避免使用与Python关键字或内置函数重名的名称（如`list`、`dict`、`str`、`id`）。

##### 5.1.1.2 注释与文档字符串

**适用场景**：公共API函数、复杂业务逻辑、算法实现、非显而易见的代码设计决策

代码注释应解释"为什么这么做"而非"做了什么"，代码本身应该能够清晰表达"做了什么"。所有公共模块、类、函数都应包含文档字符串（docstring）。

**文档字符串规范示例**：
```python
def calculate_f1_score(y_true: list, y_pred: list, average: str = 'macro') -> float:
    """
    计算分类任务的F1分数。

    F1分数是精确率和召回率的调和平均数，用于衡量分类模型的综合性能。

    参数:
        y_true: 真实标签列表
        y_pred: 预测标签列表
        average: 平均方式，可选值为 'macro'、'micro'、'weighted'，默认为 'macro'
            - 'macro': 计算每个类别的F1后取算术平均，不考虑类别不平衡
            - 'micro': 统计全局TP、FP、FN后计算F1
            - 'weighted': 计算每个类别的F1后按支持度加权平均

    返回:
        F1分数值，范围在0.0到1.0之间，1.0表示完美预测

    示例:
        >>> y_true = [0, 1, 2, 0, 1, 2]
        >>> y_pred = [0, 2, 1, 0, 0, 2]
        >>> calculate_f1_score(y_true, y_pred)
        0.333...
    """
    from sklearn.metrics import f1_score
    return f1_score(y_true, y_pred, average=average)
```

**注释使用原则**：
- 公共API必须有完整的文档字符串，包含参数说明、返回值说明、使用示例
- 复杂算法实现应添加行内注释解释关键步骤
- TODO注释应包含负责人和预计完成时间，如 `# TODO(张三): 添加异常处理 2026-07-15`
- 过时的注释应及时更新或删除，避免误导

##### 5.1.1.3 PEP 8规范

**PEP 8**（Python官方代码风格指南，Python Enhancement Proposal 8）是Python社区广泛认可的代码风格标准，涵盖缩进、行长度、空行、导入等多个方面。

**核心PEP 8要求**：
- **缩进**：使用4个空格缩进，不使用Tab
- **行长度**：每行不超过79个字符，文档字符串和注释不超过72个字符
- **空行**：顶级函数和类定义之间空两行，类内方法定义之间空一行
- **导入**：按标准库→第三方库→本地库顺序分组，每组之间空一行
- **空格**：运算符两侧加空格，逗号后加空格，括号内侧不加空格

**符合PEP 8的代码示例**：
```python
# 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 第三方库导入
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 本地库导入
from .utils import set_random_seed
from .metrics import calculate_metrics


class TextClassificationDataset(Dataset):
    """文本分类数据集类。"""

    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }
```

> **注意**：建议在开发环境中配置代码检查工具（如`flake8`、`pylint`）和自动格式化工具（如`black`、`yapf`），在提交前自动检查和格式化代码，确保代码风格一致。

##### 5.1.1.4 类型提示

**类型提示（Type Hints）**（Python 3.5+引入的类型注解功能，用于标注变量、函数参数和返回值的类型）能够提升代码可读性，支持IDE的智能提示和静态类型检查，提前发现类型相关的Bug。

**类型提示完整示例**：
```python
from typing import Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
import numpy as np
import torch


@dataclass
class TrainingConfig:
    """训练配置数据类。"""
    learning_rate: float = 2e-5
    batch_size: int = 32
    num_epochs: int = 10
    max_seq_length: int = 512
    random_seed: int = 42
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu'


def create_dataloader(
    texts: List[str],
    labels: List[int],
    tokenizer,
    batch_size: int = 32,
    shuffle: bool = True,
    max_length: int = 512
) -> DataLoader:
    """
    创建数据加载器。

    参数:
        texts: 文本列表
        labels: 标签列表
        tokenizer: 分词器实例
        batch_size: 批次大小
        shuffle: 是否打乱数据
        max_length: 最大序列长度

    返回:
        PyTorch DataLoader实例
    """
    dataset = TextClassificationDataset(texts, labels, tokenizer, max_length)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device
) -> Tuple[float, float]:
    """
    训练一个epoch。

    参数:
        model: 待训练的模型
        dataloader: 数据加载器
        optimizer: 优化器
        device: 计算设备

    返回:
        (平均损失, 准确率)元组
    """
    model.train()
    total_loss = 0.0
    all_preds: List[int] = []
    all_labels: List[int] = []

    for batch in dataloader:
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        preds = torch.argmax(logits, dim=-1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(dataloader)
    accuracy = np.mean(np.array(all_preds) == np.array(all_labels))

    return avg_loss, float(accuracy)


def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    device: torch.device,
    metric_fn: Optional[Callable] = None
) -> Dict[str, float]:
    """
    评估模型性能。

    参数:
        model: 待评估的模型
        dataloader: 数据加载器
        device: 计算设备
        metric_fn: 可选的自定义指标计算函数

    返回:
        包含各项指标的字典
    """
    model.eval()
    total_loss = 0.0
    all_preds: List[int] = []
    all_labels: List[int] = []

    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss

            total_loss += loss.item()
            preds = torch.argmax(outputs.logits, dim=-1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    results: Dict[str, float] = {
        'loss': total_loss / len(dataloader),
        'accuracy': float(np.mean(np.array(all_preds) == np.array(all_labels)))
    }

    if metric_fn is not None:
        results.update(metric_fn(all_labels, all_preds))

    return results
```

**类型提示常用类型**：
| 类型 | 说明 | 示例 |
|------|------|------|
| `int`, `float`, `str`, `bool` | 基础类型 | `count: int = 0` |
| `List[T]` | 列表类型 | `texts: List[str]` |
| `Dict[K, V]` | 字典类型 | `config: Dict[str, float]` |
| `Tuple[T1, T2]` | 元组类型 | `return loss, acc  # Tuple[float, float]` |
| `Optional[T]` | 可选类型（可以为None） | `model: Optional[nn.Module] = None` |
| `Union[T1, T2]` | 联合类型 | `device: Union[str, torch.device]` |
| `Callable` | 可调用对象（函数） | `metric_fn: Callable[[List, List], Dict]` |

⚠️ **重要提示**：建议使用`mypy`进行静态类型检查，在CI流水线中加入类型检查步骤，提前发现类型错误。类型提示应保持更新，修改代码时同步更新类型注解，避免类型提示与实际代码不一致。

##### 5.1.1.5 单元测试

**适用场景**：核心功能模块、数据处理逻辑、模型推理接口、工具函数、公共API

单元测试是保证代码质量的重要手段，能够在修改代码时快速验证功能正确性，防止回归Bug。推荐使用Python内置的`unittest`框架或`pytest`框架编写测试。

**pytest单元测试示例**：
```python
import pytest
import torch
from modules.preprocessor import DataPreprocessor
from modules.model import SentimentModel


class TestDataPreprocessor:
    """数据预处理器测试类。"""

    def setup_method(self):
        """每个测试方法执行前的初始化。"""
        self.preprocessor = DataPreprocessor(max_length=128)

    def test_clean_text_removes_urls(self):
        """测试clean_text方法应移除URL。"""
        text = "访问这个链接 https://example.com 了解更多"
        cleaned = self.preprocessor.clean_text(text)
        assert "https://example.com" not in cleaned
        assert "访问这个链接" in cleaned

    def test_clean_text_handles_empty_string(self):
        """测试clean_text方法处理空字符串。"""
        assert self.preprocessor.clean_text("") == ""
        assert self.preprocessor.clean_text("   ") == ""

    def test_validate_input_raises_on_missing_text(self):
        """测试缺少text字段时应抛出异常。"""
        with pytest.raises(ValueError, match="Missing required field"):
            self.preprocessor.validate_input({})

    def test_encode_text_returns_correct_shape(self):
        """测试文本编码返回正确的张量形状。"""
        text = "这是一个测试句子"
        result = self.preprocessor.encode_text(text)
        assert 'input_ids' in result
        assert 'attention_mask' in result
        assert result['input_ids'].shape[-1] == 128


class TestSentimentModel:
    """情感分析模型测试类。"""

    def setup_method(self):
        """初始化测试环境。"""
        self.device = torch.device('cpu')
        self.model = SentimentModel(
            model_name='bert-base-chinese',
            num_labels=3,
            device=self.device
        )
        self.model.eval()

    def test_model_predict_returns_expected_format(self):
        """测试模型预测返回格式正确。"""
        dummy_input = {
            'input_ids': torch.randint(0, 1000, (1, 128)),
            'attention_mask': torch.ones(1, 128, dtype=torch.long)
        }
        with torch.no_grad():
            result = self.model.predict(dummy_input)

        assert 'label' in result
        assert 'confidence' in result
        assert 'probabilities' in result
        assert result['label'] in ['negative', 'neutral', 'positive']
        assert 0.0 <= result['confidence'] <= 1.0
        assert sum(result['probabilities'].values()) == pytest.approx(1.0, abs=1e-5)

    @pytest.mark.parametrize("batch_size", [1, 4, 8])
    def test_batch_prediction_works_with_different_sizes(self, batch_size):
        """测试不同批次大小的预测。"""
        dummy_input = {
            'input_ids': torch.randint(0, 1000, (batch_size, 128)),
            'attention_mask': torch.ones(batch_size, 128, dtype=torch.long)
        }
        with torch.no_grad():
            outputs = self.model(**dummy_input)
        assert outputs.logits.shape == (batch_size, 3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

**单元测试编写原则**：
- 每个测试函数只测试一个功能点，测试名称应清晰描述测试场景
- 使用`setup_method`/`teardown_method`进行测试前后的初始化和清理
- 使用参数化测试（`@pytest.mark.parametrize`）覆盖多组输入
- 测试应独立运行，不依赖测试执行顺序
- 核心功能的测试覆盖率应达到90%以上

> **注意**：建议在CI/CD流水线中自动运行单元测试，每次提交代码时执行全量测试，确保新代码不破坏已有功能。对于耗时较长的模型训练测试，可以标记为慢速测试（`@pytest.mark.slow`），在日常开发中跳过，仅在发布前执行。

#### 5.1.2 版本控制工作流

**适用场景**：所有团队协作项目、持续集成/持续部署、版本发布管理、多并行开发任务

规范的版本控制工作流是团队协作的基石。**Git Flow**（一种Git分支管理工作流模型，通过标准化分支策略支持并行开发和版本发布）是广泛使用的分支管理方案，配合**Conventional Commits**（标准化的提交信息规范，通过统一的提交信息格式支持自动化版本管理和CHANGELOG生成）能够实现高效的团队协作。

##### 5.1.2.1 分支策略

Git Flow定义了五种主要分支类型，各分支职责明确：

| 分支类型 | 分支名 | 说明 | 生命周期 |
|----------|--------|------|----------|
| 主分支 | `main` | 生产环境代码，始终保持可发布状态，每个提交对应一个版本标签 | 永久 |
| 开发分支 | `develop` | 开发集成分支，所有功能开发完成后合并到此分支 | 永久 |
| 功能分支 | `feature/*` | **功能分支（Feature Branch）**（用于开发新功能的独立分支，从develop分支创建，完成后合并回develop） | 临时 |
| 修复分支 | `hotfix/*` | 生产环境紧急Bug修复分支，从main分支创建，修复后同时合并回main和develop | 临时 |
| 发布分支 | `release/*` | 版本发布准备分支，从develop分支创建，用于发布前测试和Bug修复，完成后合并到main并打标签 | 临时 |

**Git Flow工作流示意图**：
```
main ──────────────────────────────●───────●─────────●──── (生产版本)
        \                         ↑         ↑         ↑
         \    release/v1.0 ────●──┘         │         │
          \         ↑         ↑            │         │
develop ───●───────●─────────●─────────────●─────────●──── (开发集成)
           \     ↑           ↑                        ↑
            \   ↑ feature/   ↑ hotfix/                ↑
             \ /   user-auth  login-bug               /
              ●───●──────────────────────────────────●
```

**Git Flow常用命令示例**：

```bash
# 1. 初始化仓库（首次设置）
git init
git checkout -b main
git checkout -b develop

# 2. 开发新功能：从develop创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/sentiment-analysis-model

# 3. 在功能分支上开发和提交
git add modules/model.py
git commit -m "feat(model): 新增情感分析BERT模型封装"
git push -u origin feature/sentiment-analysis-model

# 4. 功能开发完成，合并回develop
git checkout develop
git pull origin develop
git merge --no-ff feature/sentiment-analysis-model -m "merge: 合并情感分析模型功能"
git push origin develop

# 5. 删除已合并的功能分支
git branch -d feature/sentiment-analysis-model
git push origin --delete feature/sentiment-analysis-model

# 6. 准备发布：从develop创建release分支
git checkout develop
git checkout -b release/v1.0.0

# 在release分支上修复小Bug、更新版本号
git add model-config.yaml
git commit -m "chore(release): 更新版本号到v1.0.0"

# 7. 发布完成，合并到main并打标签
git checkout main
git merge --no-ff release/v1.0.0 -m "release: v1.0.0 正式发布"
git tag -a v1.0.0 -m "Release v1.0.0: 新增情感分析功能，支持中文三分类"
git push origin main --tags

# 8. 同时合并回develop
git checkout develop
git merge --no-ff release/v1.0.0 -m "merge: 合并v1.0.0发布分支到develop"
git push origin develop

# 9. 删除release分支
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0

# 10. 生产环境紧急Bug修复：从main创建hotfix分支
git checkout main
git checkout -b hotfix/login-timeout-bug

# 修复Bug
git add modules/auth.py
git commit -m "fix(auth): 修复登录超时导致的500错误"
git push -u origin hotfix/login-timeout-bug

# 11. Hotfix完成，同时合并到main和develop
git checkout main
git merge --no-ff hotfix/login-timeout-bug -m "hotfix: 修复登录超时Bug"
git tag -a v1.0.1 -m "Release v1.0.1: 修复登录超时问题"
git push origin main --tags

git checkout develop
git merge --no-ff hotfix/login-timeout-bug -m "merge: 合并登录超时修复到develop"
git push origin develop

# 删除hotfix分支
git branch -d hotfix/login-timeout-bug
git push origin --delete hotfix/login-timeout-bug
```

⚠️ **重要提示**：
- 合并分支时建议使用 `--no-ff` 参数，保留分支合并历史，便于追溯功能开发轨迹
- **禁止**直接向main分支提交代码，所有代码必须通过功能分支、发布分支或热修复分支合并
- 功能分支应保持较小粒度，一个功能分支对应一个功能点，避免超大分支难以审查和合并
- 定期从develop分支拉取最新代码到功能分支，减少最终合并时的冲突

##### 5.1.2.2 Conventional Commits提交规范

Conventional Commits规范定义了标准化的提交信息格式，提交信息结构如下：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**提交类型（type）说明**：

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(model): 新增批量推理接口` |
| `fix` | Bug修复 | `fix(preprocessor): 修复空文本处理异常` |
| `docs` | 文档更新 | `docs(readme): 更新安装说明` |
| `style` | 代码格式调整（不影响功能） | `style: 格式化代码符合PEP 8` |
| `refactor` | 代码重构（不新增功能、不修Bug） | `refactor(dataset): 重构数据加载逻辑` |
| `perf` | 性能优化 | `perf(inference): 添加Redis缓存提升响应速度` |
| `test` | 添加或修改测试 | `test(model): 添加模型推理单元测试` |
| `chore` | 构建过程或辅助工具变动 | `chore(deps): 更新transformers到4.30.0` |
| `ci` | CI/CD配置变动 | `ci: 添加MLflow实验跟踪步骤` |

**Conventional Commits提交示例**：

```bash
# 简单提交（仅header）
git commit -m "feat(model): 新增ONNX格式导出支持"

# 完整提交（包含body和footer）
git commit -m "$(cat <<'EOF'
fix(inference): 修复长文本推理时的内存泄漏问题

- 添加梯度清理逻辑
- 优化张量释放时机
- 增加推理内存使用监控

Closes #123
EOF
)"
```

**好的提交信息示例**：
```
feat(api): 添加批量预测接口

- 支持最大64条样本的批量推理
- 添加批次大小参数校验
- 完善批量接口错误处理
- 更新API文档和示例代码

Refs: #456
```

**不好的提交信息示例**：
```
update                          # 没有类型和描述
fix bug                         # 描述太模糊
wip                             # 半成品提交，不应该推送到远程
各种修改                        # 中文描述但不清晰
feat: add new feature           # 没有scope，描述太笼统
```

> **注意**：
> - subject部分使用中文描述，简洁明了，不超过50个字符，结尾不加句号
> - 一个提交只做一件事，如果修改了多个不相关的内容，应拆分成多个提交
> - 提交信息应描述"做了什么"和"为什么这么做"，而不是"怎么做的"
> - 修复Issue时在footer中使用 `Closes #123` 或 `Fixes #456` 关联Issue编号，合并后自动关闭Issue

##### 5.1.2.3 代码审查（Code Review）

**适用场景**：所有功能分支合并、重要代码变更、新成员提交代码、核心模块修改

代码审查是保证代码质量、知识共享、团队能力提升的重要环节。所有代码合并到develop或main分支前必须经过代码审查。

**代码审查检查清单**：
1. **功能正确性**：代码是否实现了需求，逻辑是否正确，边界条件是否处理
2. **代码规范**：是否符合PEP 8规范，命名是否清晰，是否有适当的注释和文档字符串
3. **类型安全**：是否添加了正确的类型提示，是否有潜在的类型错误
4. **测试覆盖**：是否添加了单元测试，测试是否覆盖核心逻辑，测试是否通过
5. **性能考虑**：是否有明显的性能问题，是否有不必要的计算或内存占用
6. **安全考虑**：是否有硬编码的密钥，是否有SQL注入等安全漏洞
7. **错误处理**：异常是否被正确捕获和处理，错误信息是否清晰
8. **可维护性**：代码是否简洁易懂，是否有过度设计，是否符合单一职责原则

**代码审查流程**：
1. 开发者完成功能开发，本地测试通过后推送功能分支
2. 在代码托管平台创建Pull Request（PR）/ Merge Request（MR），填写PR描述
3. 指定至少1名审查者（核心模块需2名），关联相关Issue
4. 审查者阅读代码，提出修改意见或批准
5. 开发者根据意见修改代码，更新提交（建议使用追加提交而非强制推送）
6. 所有审查意见解决后，审查者批准PR，维护者合并代码

> **注意**：代码审查是对事不对人，审查意见应针对代码本身而非作者，保持专业和友善的态度。作者收到审查意见后应认真对待，有不同意见时理性讨论，不要带情绪。

### 5.2 文档管理

文档是项目的重要组成部分，良好的文档能够降低用户上手门槛，减少团队沟通成本，提升项目可维护性。文档与代码同等重要，应随着代码同步更新。

#### 5.2.1 项目文档结构

**适用场景**：所有AI项目初始化、开源项目发布、团队协作项目、需要长期维护的项目

标准化的项目文档结构能够让用户和团队成员快速找到需要的信息。推荐的AI项目目录结构如下：

**标准项目目录结构示例**：
```
sentiment-analysis-project/
├── README.md                 # 项目主文档（必读）
├── CHANGELOG.md              # 版本变更日志
├── LICENSE                   # 开源许可证
├── requirements.txt          # Python依赖列表
├── setup.py / pyproject.toml # 包安装配置（可选）
├── .gitignore               # Git忽略文件
├── .env.example             # 环境变量示例文件
│
├── docs/                    # 文档目录
│   ├── README.md            # 文档索引
│   ├── installation.md      # 安装指南
│   ├── quickstart.md        # 快速入门
│   ├── user-guide/          # 用户指南
│   │   ├── README.md
│   │   ├── data-preparation.md
│   │   ├── training.md
│   │   └── inference.md
│   ├── api-reference/       # API参考文档
│   │   ├── README.md
│   │   ├── model.md
│   │   └── preprocessor.md
│   ├── examples/            # 示例文档（指向examples目录）
│   ├── faq.md               # 常见问题
│   └── troubleshooting.md   # 故障排除指南
│
├── examples/                # 示例代码目录
│   ├── README.md
│   ├── 01_quickstart.ipynb  # 快速入门Notebook
│   ├── 02_training.py       # 训练示例脚本
│   ├── 03_batch_inference.py# 批量推理示例
│   └── sample_data/         # 示例数据
│       └── sample_reviews.csv
│
├── src/                     # 源代码目录（或直接放在项目根目录）
│   ├── __init__.py
│   ├── data/                # 数据处理模块
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   └── preprocessor.py
│   ├── models/              # 模型模块
│   │   ├── __init__.py
│   │   ├── model.py
│   │   └── utils.py
│   ├── training/            # 训练模块
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   └── metrics.py
│   └── inference/           # 推理模块
│       ├── __init__.py
│       └── predictor.py
│
├── tests/                   # 单元测试目录
│   ├── __init__.py
│   ├── conftest.py          # pytest配置
│   ├── test_preprocessor.py
│   ├── test_model.py
│   └── test_trainer.py
│
├── scripts/                 # 工具脚本目录
│   ├── download_data.py     # 数据下载脚本
│   ├── evaluate_model.py    # 模型评估脚本
│   └── export_onnx.py       # 模型导出脚本
│
├── configs/                 # 配置文件目录
│   ├── train_config.yaml
│   └── model_config.yaml
│
└── data/                    # 数据目录（通常不提交到Git）
    ├── raw/                 # 原始数据
    ├── processed/           # 处理后数据
    └── README.md            # 数据说明
```

**核心文件和目录说明**：

| 文件/目录 | 必要性 | 说明 |
|-----------|--------|------|
| `README.md` | 必须 | 项目门面，用户第一眼看到的文档，包含项目介绍和快速上手指南 |
| `CHANGELOG.md` | 必须 | 记录每个版本的变更内容，用户升级时必读 |
| `LICENSE` | 推荐 | 开源许可证，明确用户使用权限 |
| `requirements.txt` | 必须 | Python依赖列表，保证环境可复现 |
| `.env.example` | 推荐 | 环境变量示例，复制为`.env`后填写实际配置 |
| `docs/` | 推荐 | 详细文档目录，适合复杂项目 |
| `examples/` | 推荐 | 可运行的示例代码和Notebook，降低上手门槛 |
| `tests/` | 必须 | 单元测试目录，保证代码质量 |
| `configs/` | 推荐 | 配置文件目录，将配置与代码分离 |
| `data/` | 按需 | 数据目录，建议在`.gitignore`中忽略大文件，仅保留`README.md`说明 |

⚠️ **重要提示**：
- `data/`目录下的大文件（如数据集、模型权重）不应提交到Git仓库，应使用`.gitignore`忽略，通过数据下载脚本或DVC等工具管理
- `examples/`目录下的示例代码应保证可以直接运行，定期测试确保示例代码与当前代码版本兼容
- 敏感配置（如API密钥、数据库密码）应通过`.env`文件管理，`.env`文件不提交到Git，只提交`.env.example`模板

**requirements.txt规范示例**：
```txt
# 核心依赖
transformers>=4.30.0,<5.0.0
torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.2.0

# Web服务（Space应用需要）
flask>=2.3.0
gunicorn>=21.2.0
redis>=5.0.0

# 工具库
pyyaml>=6.0
tqdm>=4.65.0
python-dotenv>=1.0.0

# 实验跟踪
mlflow>=2.4.0

# 开发依赖（测试、代码检查）
pytest>=7.4.0
pytest-cov>=4.1.0
flake8>=6.0.0
black>=23.7.0
mypy>=1.4.0
```

> **注意**：依赖版本应指定范围，使用 `>=最低版本,<下一大版本` 的形式，既能获得bug修复又能避免破坏性更新导致不兼容。开发依赖（测试、代码检查工具）建议单独放在`requirements-dev.txt`中。

#### 5.2.2 文档编写规范

**适用场景**：README编写、API文档、用户指南、示例文档、项目wiki

高质量的文档应结构清晰、内容完整、示例充分。无论项目大小，README.md都是必不可少的核心文档。一份完整的README应包含以下七个关键部分。

##### 5.2.2.1 README完整结构

**README.md编写模板**：
````markdown
# 项目名称

> 一句话概述项目的功能和价值。

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-green)]()
[![Model](https://img.shields.io/badge/model-BERT-yellow)]()

## 一、概述

简要介绍项目背景、目标和核心功能。说明项目解决什么问题，有什么特色和优势。

**示例**：
本项目是基于BERT的中文情感分析系统，支持电商评论、社交媒体文本的正/负/中性三分类，提供预训练模型、训练脚本和部署示例，准确率达94.5%，单条推理延迟50ms。

## 二、功能特性

列出项目的核心功能点，使用复选框或列表形式：

- 🚀 基于BERT预训练模型，支持中文文本情感三分类
- ⚡ Redis缓存加速，批量推理支持，QPS可达200+
- 📊 完整的训练、评估、部署流水线
- 📝 提供Jupyter Notebook示例，快速上手
- 🔧 RESTful API接口，易于集成
- 📈 MLflow实验跟踪，支持超参数对比

## 三、安装方法

详细说明环境要求和安装步骤。

### 3.1 环境要求

- Python 3.9+
- PyTorch 2.0+
- （可选）CUDA 11.7+ 支持GPU推理

### 3.2 安装步骤

```bash
# 1. 克隆仓库
git clone https://ai.gitcode.com/your-team/sentiment-analysis.git
cd sentiment-analysis

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载预训练模型（可选）
python scripts/download_model.py
```

## 四、使用方法

提供快速开始指南和常用功能的使用示例，代码示例应可以直接复制运行。

### 4.1 快速开始

```python
from src.inference import SentimentPredictor

# 初始化预测器
predictor = SentimentPredictor(model_path='models/best_model')

# 单条文本预测
result = predictor.predict("这个产品质量非常好，物流也很快！")
print(result)
# {'label': 'positive', 'confidence': 0.998, 'probabilities': {...}}

# 批量预测
texts = [
    "服务态度差，不推荐购买",
    "一般般，没有什么特别的",
    "超出预期，非常满意！"
]
results = predictor.predict_batch(texts)
for text, result in zip(texts, results):
    print(f"{text} -> {result['label']} ({result['confidence']:.3f})")
```

### 4.2 启动API服务

```bash
# 启动Flask服务
python main.py

# 或使用gunicorn启动生产级服务
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

服务启动后，访问 http://localhost:8000/health 检查健康状态，使用curl测试：
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "非常好用的产品！"}'
```

### 4.3 训练自己的模型

```bash
# 准备数据（放入data/raw目录）
# 编辑配置文件 configs/train_config.yaml
python scripts/train.py --config configs/train_config.yaml
```

更多使用示例见 [examples/](examples/) 目录。

## 五、API参考

简要说明主要API接口的参数和返回值，详细API文档见 `docs/api-reference/`。

### SentimentPredictor类

```python
class SentimentPredictor:
    def __init__(self, model_path: str, device: str = None, use_cache: bool = True):
        """
        初始化情感分析预测器。
        
        参数:
            model_path: 模型路径，可以是本地目录或HuggingFace模型名
            device: 计算设备，'cuda'或'cpu'，默认自动检测
            use_cache: 是否使用Redis缓存，默认True
        """
    
    def predict(self, text: str) -> dict:
        """
        单条文本预测。
        
        参数:
            text: 输入文本
            
        返回:
            {
                'label': 'positive'|'neutral'|'negative',
                'confidence': float,  # 0.0-1.0
                'probabilities': {
                    'positive': float,
                    'neutral': float,
                    'negative': float
                }
            }
        """
```

## 六、注意事项

明确说明使用限制、已知问题和需要特别注意的地方：

> ⚠️ **重要提示**：
> - 本模型主要在电商评论数据上训练，对其他领域（如新闻、医疗）文本效果可能下降
> - 文本长度超过512字符会自动截断，过长文本建议分段处理
> - GPU推理需要安装对应CUDA版本的PyTorch
> - 首次运行会自动下载模型权重，需要网络连接
> - 请勿用于分析涉及个人隐私的文本，遵守数据安全法规

## 七、常见问题

FAQ部分，列出用户常遇到的问题和解决方案：

**Q: 模型加载速度慢怎么办？**
A: 首次加载会下载模型文件，后续加载会使用缓存。如果网络慢，可以手动下载模型放到指定目录。

**Q: GPU推理报错CUDA out of memory？**
A: 可以减小batch_size，或者使用CPU推理。BERT-base模型在CPU上单条推理约200ms，可以满足低并发场景。

**Q: 如何提升特定领域的准确率？**
A: 建议使用该领域的标注数据进行微调，参考训练脚本准备数据后执行微调。

**更多问题？**
- 查看 [故障排除指南](docs/troubleshooting.md)
- 提交 [Issue](https://ai.gitcode.com/your-team/sentiment-analysis/issues)

## 八、更新日志

每个版本的更新内容摘要，详细日志见 [CHANGELOG.md](CHANGELOG.md)：

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1.0 | 2026-07-01 | 新增批量推理接口，添加Redis缓存，性能提升3倍 |
| v1.0.0 | 2026-06-01 | 初始版本发布，支持中文情感三分类 |

## 九、贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发流程：

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 十、许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证开源。

---

*最后更新时间：2026-07-01*
*维护者：AI Team <ai-team@example.com>*
````

##### 5.2.2.2 文档编写原则

**适用场景**：所有技术文档编写、注释撰写、示例代码编写

高质量文档应遵循以下原则：

1. **用户视角**：站在用户角度思考，用户需要什么信息，会遇到什么问题
2. **示例优先**：一个好的代码示例胜过千言万语，示例代码应可以直接复制运行
3. **诚实透明**：明确说明已知问题和局限性，不夸大功能和效果
4. **结构清晰**：使用合适的标题层级，内容分块，便于快速定位信息
5. **及时更新**：代码变更时同步更新文档，过时的文档比没有文档更糟糕
6. **图文并茂**：适当使用表格、列表、代码块、Mermaid图表等辅助说明

**文档质量自检清单**：
- [ ] 新用户按照README步骤能成功运行项目吗？
- [ ] 代码示例经过实际测试可以运行吗？
- [ ] 常见问题和注意事项是否都有说明？
- [ ] 术语和缩写在首次出现时有解释吗？
- [ ] 版本更新时CHANGELOG更新了吗？
- [ ] 文档中的链接和路径有效吗？

> **注意**：文档编写不是一次性工作，应在整个项目生命周期中持续维护。建议将文档检查纳入代码审查流程，代码变更时必须同步检查和更新相关文档。

##### 5.2.2.3 注释与文档字符串规范

**适用场景**：公共API、核心模块、复杂算法、工具函数

代码注释和文档字符串是离代码最近的文档，应遵循以下规范：

**文档字符串三种风格**（项目内统一使用一种）：

1. **Google风格**（推荐，可读性好）：
```python
def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    num_epochs: int = 10,
    device: torch.device = None
) -> Dict[str, List[float]]:
    """训练模型。

    在训练集上训练模型，并在每个epoch结束后在验证集上评估，
    保存验证集上表现最好的模型。

    参数:
        model: 待训练的PyTorch模型
        train_loader: 训练集数据加载器
        val_loader: 验证集数据加载器
        optimizer: 优化器实例
        num_epochs: 训练轮数，默认10
        device: 计算设备，默认自动选择

    返回:
        训练历史字典，包含:
        - train_losses: 每个epoch的训练损失列表
        - val_losses: 每个epoch的验证损失列表
        - val_f1s: 每个epoch的验证F1分数列表

    示例:
        >>> model = SentimentModel()
        >>> optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
        >>> history = train_model(model, train_loader, val_loader, optimizer, num_epochs=5)
        >>> print(f"最佳验证F1: {max(history['val_f1s']):.4f}")

    异常:
        ValueError: 当num_epochs小于1时抛出
    """
```

2. **reST风格**（Sphinx默认支持）：
```python
def calculate_similarity(text1: str, text2: str) -> float:
    """计算两段文本的相似度。

    :param text1: 第一段文本
    :type text1: str
    :param text2: 第二段文本
    :type text2: str
    :return: 相似度分数，范围0.0-1.0
    :rtype: float
    """
```

3. **NumPy风格**（详细完整）：
```python
def load_dataset(path: str, split: str = 'train') -> pd.DataFrame:
    """加载数据集。

    从指定路径加载JSONL格式的数据集，返回pandas DataFrame。

    Parameters
    ----------
    path : str
        数据集目录路径
    split : str, optional
        数据集划分，'train'/'validation'/'test'，默认'train'

    Returns
    -------
    pd.DataFrame
        包含数据的DataFrame

    Raises
    ------
    FileNotFoundError
        当路径不存在时抛出
    ValueError
        当split参数无效时抛出
    """
```

⚠️ **重要提示**：
- 文档字符串描述"是什么"，行内注释解释"为什么"
- 公共API必须有完整的文档字符串，包含参数、返回值、示例、异常说明
- 修改函数签名或功能时必须同步更新文档字符串
- 可以使用`pdoc`、`Sphinx`等工具从文档字符串自动生成API文档

> **注意**：注释不应描述代码已经清楚表达的内容，好的代码本身就是最好的文档。如果需要通过大量注释才能解释代码在做什么，往往意味着代码需要重构以提升可读性。

---

## 六、安全最佳实践

### 6.1 数据安全

数据安全是AI应用的基础防线，敏感信息泄露和非法输入是最常见的安全风险点。通过环境变量管理敏感配置、使用数据校验库验证输入，可以有效降低数据安全风险。

#### 6.1.1 敏感信息保护

**适用场景**：所有Space应用开发、API集成、数据库连接、第三方服务调用、包含密钥/Token的项目

**dotenv**（Python库，用于从.env文件加载环境变量）是管理敏感配置的标准方案。API密钥、数据库密码、访问Token等敏感信息严禁硬编码在代码中，应通过环境变量注入。

**.env文件示例**（项目根目录创建）：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_platform
DB_USER=app_user
DB_PASSWORD=your_secure_password_here

# API密钥
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
ATOMGIT_API_TOKEN=at-xxxxxxxxxxxxxxxxxxxxxxxx

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key_here_make_it_long_and_random
JWT_EXPIRE_HOURS=24

# 应用配置
DEBUG=false
LOG_LEVEL=INFO
```

**使用python-dotenv加载环境变量示例**：
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'ai_platform'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
```

**.gitignore配置**（确保.env不提交到版本控制）：
```gitignore
# 环境变量文件
.env
.env.local
.env.*.local

# 其他敏感文件
*.pem
*.key
credentials.json
secrets/
```

⚠️ **严重安全警告**：
- **绝对不要**将`.env`文件提交到Git仓库，一旦密钥泄露，立即轮换所有相关密钥
- `.env.example`文件可以提交，只保留键名不包含实际值，作为配置模板供其他开发者参考
- 生产环境应使用平台提供的密钥管理服务（如Kubernetes Secrets、云厂商密钥管理服务），而非依赖.env文件
- 定期轮换密钥和Token，建议设置90天以内的有效期
- 代码提交前使用`git diff`检查，防止意外提交敏感信息

> **注意**：`load_dotenv()`默认不会覆盖已存在的环境变量，这确保了生产环境通过平台注入的环境变量优先级高于本地.env文件。本地开发时.env文件仅用于开发环境配置。

#### 6.1.2 输入数据验证

**适用场景**：所有接收用户输入的API接口、表单处理、数据导入功能、模型推理服务

**Pydantic**（Python数据验证库，使用类型注解进行数据校验）是进行输入验证的最佳选择。通过定义数据模型和验证器，可以自动校验输入数据的类型、格式、范围，防止非法输入导致的安全漏洞（如注入攻击、数据篡改）。

**Pydantic基础模型与验证器示例**：
```python
from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional, List
from datetime import datetime
import re


class UserInput(BaseModel):
    """用户输入数据模型"""
    text: str = Field(..., min_length=1, max_length=2000, description='输入文本')
    user_id: str = Field(..., min_length=3, max_length=64, description='用户ID')
    max_length: Optional[int] = Field(512, ge=1, le=2048, description='最大序列长度')
    temperature: Optional[float] = Field(1.0, ge=0.0, le=2.0, description='生成温度')
    tags: Optional[List[str]] = Field(None, max_items=10, description='标签列表')
    
    @validator('text')
    def text_must_not_contain_malicious_content(cls, v):
        """验证文本不包含恶意脚本或注入内容"""
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'__import__\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            r'subprocess\.',
            r'os\.system',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE | re.DOTALL):
                raise ValueError('输入包含潜在的恶意内容')
        return v
    
    @validator('user_id')
    def user_id_format_check(cls, v):
        """验证用户ID格式：仅允许字母、数字、下划线和连字符"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('用户ID只能包含字母、数字、下划线和连字符')
        return v
    
    @validator('tags', each_item=True)
    def tag_length_check(cls, v):
        """验证每个标签的长度"""
        if len(v) > 50:
            raise ValueError('单个标签长度不能超过50个字符')
        return v


class BatchPredictRequest(BaseModel):
    """批量预测请求模型"""
    inputs: List[UserInput] = Field(..., min_items=1, max_items=64, description='输入列表')
    request_id: str = Field(..., description='请求ID用于追踪')
    
    @validator('request_id')
    def request_id_format(cls, v):
        """验证请求ID是有效的UUID格式"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError('request_id必须是有效的UUID格式')
        return v


def validate_request(request_data: dict) -> tuple:
    """验证请求数据，返回(是否合法, 验证后的数据或错误信息)"""
    try:
        validated = UserInput(**request_data)
        return True, validated.dict()
    except ValidationError as e:
        errors = []
        for error in e.errors():
            errors.append({
                'field': '.'.join(str(loc) for loc in error['loc']),
                'message': error['msg']
            })
        return False, {'errors': errors}
```

**Flask接口中使用Pydantic验证示例**：
```python
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '请求体不能为空'
        }), 400
    
    is_valid, result = validate_request(data)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': '输入验证失败',
            'details': result['errors']
        }), 400
    
    # 验证通过，使用result进行后续处理
    return jsonify({
        'success': True,
        'data': result
    })
```

⚠️ **重要安全提示**：
- **永远不要信任用户输入**，所有来自外部的数据都必须经过验证，包括URL参数、请求头、Cookie
- 数值型参数必须设置合理的上下界（如`ge`、`le`），防止整数溢出或资源耗尽攻击
- 字符串参数必须设置最大长度限制，防止超长输入导致内存溢出或拒绝服务
- 文件上传功能除了验证文件扩展名，还必须验证文件内容类型（MIME type）和文件大小
- 对用户输入中的特殊字符进行转义处理，防止XSS（跨站脚本攻击）和SQL注入
- 验证错误信息不要暴露内部实现细节（如数据库结构、文件路径），仅返回必要的提示

> **注意**：Pydantic v2版本性能显著提升，建议新项目使用v2版本。验证器逻辑应保持简洁，复杂的业务逻辑验证应放在业务层而非数据模型层。

---

### 6.2 访问控制

访问控制确保只有授权用户才能访问相应的资源和功能。通过认证装饰器和基于角色的权限管理，可以实现细粒度的访问控制，保护敏感接口和数据。

#### 6.2.1 认证与授权机制

**适用场景**：需要用户登录的应用、多角色系统、管理后台接口、敏感操作API、团队协作功能

**JWT**（JSON Web Token，用于身份认证的令牌标准）是无状态认证的常用方案，结合**装饰器模式**（不修改原函数代码，动态添加功能的设计模式）可以优雅地实现认证逻辑。**RBAC**（基于角色的访问控制，Role-Based Access Control）是企业级应用常用的权限模型。

**JWT工具类实现**（modules/auth.py）：
```python
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '24'))


def generate_token(user_id: str, role: str, extra_claims: dict = None) -> str:
    """
    生成JWT令牌
    
    Args:
        user_id: 用户唯一标识
        role: 用户角色（如'admin'、'user'、'guest'）
        extra_claims: 额外的声明信息
    
    Returns:
        JWT令牌字符串
    """
    now = datetime.utcnow()
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': now,
        'exp': now + timedelta(hours=JWT_EXPIRE_HOURS),
        'iss': 'atomgit-ai-platform'
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的payload字典
    
    Raises:
        jwt.ExpiredSignatureError: 令牌已过期
        jwt.InvalidTokenError: 令牌无效
    """
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
        options={'require': ['exp', 'iat', 'user_id', 'role']}
    )


def require_auth(f):
    """
    认证装饰器：验证用户是否已登录
    
    使用方式：
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': '缺少认证令牌',
                'code': 'MISSING_TOKEN'
            }), 401
        
        token = auth_header.split(' ')[1]
        try:
            payload = verify_token(token)
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': '认证令牌已过期，请重新登录',
                'code': 'TOKEN_EXPIRED'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌',
                'code': 'INVALID_TOKEN'
            }), 401
        
        return f(*args, **kwargs)
    return decorated


def require_role(allowed_roles: list):
    """
    角色授权装饰器：验证用户是否拥有所需角色
    
    使用方式：
        @app.route('/api/admin')
        @require_auth
        @require_role(['admin'])
        def admin_route():
            ...
    
    Args:
        allowed_roles: 允许访问的角色列表
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return jsonify({
                    'success': False,
                    'error': '未认证',
                    'code': 'NOT_AUTHENTICATED'
                }), 401
            
            user_role = g.current_user.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': '权限不足，无法访问该资源',
                    'code': 'INSUFFICIENT_PERMISSION'
                }), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator
```

**Flask路由中使用认证装饰器示例**（main.py）：
```python
from flask import Flask, request, jsonify, g
from modules.auth import generate_token, require_auth, require_role

app = Flask(__name__)


# 公开接口：登录获取令牌
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 实际项目中应查询数据库验证用户名密码
    if username == 'admin' and password == 'secure_password':
        token = generate_token(
            user_id='user_001',
            role='admin',
            extra_claims={'username': username}
        )
        return jsonify({
            'success': True,
            'token': token,
            'token_type': 'Bearer',
            'expires_in': 24 * 3600
        })
    else:
        return jsonify({
            'success': False,
            'error': '用户名或密码错误'
        }), 401


# 普通用户接口：需要登录
@app.route('/api/predict', methods=['POST'])
@require_auth
def predict():
    user_id = g.current_user['user_id']
    return jsonify({
        'success': True,
        'message': f'用户 {user_id} 可以进行推理'
    })


# 管理员接口：需要admin角色
@app.route('/api/admin/models', methods=['GET'])
@require_auth
@require_role(['admin'])
def list_all_models():
    return jsonify({
        'success': True,
        'message': '管理员可以查看所有模型',
        'models': []
    })


# 多角色接口：admin或moderator都可以访问
@app.route('/api/moderate', methods=['POST'])
@require_auth
@require_role(['admin', 'moderator'])
def moderate_content():
    return jsonify({
        'success': True,
        'message': '内容审核操作'
    })
```

**RBAC角色权限矩阵参考**：

| 角色 | 模型推理 | 查看自己的资源 | 查看所有资源 | 管理用户 | 系统配置 |
|------|---------|--------------|-------------|---------|---------|
| guest | ✅ | ❌ | ❌ | ❌ | ❌ |
| user | ✅ | ✅ | ❌ | ❌ | ❌ |
| moderator | ✅ | ✅ | ✅ | ❌ | ❌ |
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |

⚠️ **严重安全警告**：
- JWT密钥（`JWT_SECRET_KEY`）必须使用足够长度的随机字符串（建议至少32字符），生产环境严禁使用开发环境默认值
- JWT令牌一旦签发，在过期前无法撤销，如需实现令牌吊销机制，应配合黑名单或使用短有效期+刷新令牌方案
- 不要在JWT payload中存储敏感信息（如密码、身份证号），JWT仅经过Base64编码并未加密
- 认证装饰器必须放在路由装饰器（`@app.route`）和业务函数之间，注意装饰器的执行顺序
- 权限校验必须在服务端进行，前端的权限控制仅用于UI展示，不能作为安全防线
- 管理后台接口建议额外添加IP白名单或二次验证，防止越权访问

> **注意**：装饰器的顺序很重要，`@require_auth`必须放在`@require_role`外层（更靠近函数），因为角色校验依赖认证中间件设置的`g.current_user`。建议在非HTTPS环境下不要使用JWT，生产环境必须启用HTTPS防止令牌在传输过程中被窃取。

---

## 七、性能监控最佳实践

### 7.1 系统监控

系统级性能监控是保障AI应用稳定运行的基础，通过持续采集CPU、内存、磁盘等关键资源指标，可以及时发现资源瓶颈、内存泄漏等问题，为性能优化和容量规划提供数据支撑。

#### 7.1.1 使用psutil库进行系统指标采集

**适用场景**：Space应用运行时监控、模型训练过程资源跟踪、服务器健康检查、性能瓶颈分析

**psutil**（Python系统和进程监控库，跨平台获取CPU/内存/磁盘等信息）是Python生态中最成熟的系统监控库，支持Linux、Windows、macOS等主流操作系统，提供统一的API获取各类系统资源使用情况。

**安装psutil库**：
```bash
pip install psutil>=5.9.0
```

**PerformanceMonitor类实现**（modules/monitor.py）：
```python
import psutil
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
    
    def collect_metrics(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        net_io = psutil.net_io_counters()
        
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent(interval=0.1)
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'freq_mhz': cpu_freq.current if cpu_freq else None
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'percent': memory.percent
            },
            'swap': {
                'total_gb': round(swap.total / (1024**3), 2),
                'used_gb': round(swap.used / (1024**3), 2),
                'percent': swap.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent,
                'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else None,
                'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else None
            },
            'network': {
                'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2)
            },
            'process': {
                'pid': process.pid,
                'cpu_percent': process_cpu,
                'memory_rss_mb': round(process_memory.rss / (1024**2), 2),
                'memory_vms_mb': round(process_memory.vms / (1024**2), 2),
                'num_threads': process.num_threads()
            }
        }
        
        return metrics
    
    def start_monitoring(self):
        self.start_time = time.time()
        self.metrics_history = []
    
    def record_metrics(self) -> Dict[str, Any]:
        metrics = self.collect_metrics()
        self.metrics_history.append(metrics)
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.metrics_history:
            return {'error': 'No metrics collected yet'}
        
        cpu_values = [m['cpu']['percent'] for m in self.metrics_history]
        memory_values = [m['memory']['percent'] for m in self.metrics_history]
        disk_values = [m['disk']['percent'] for m in self.metrics_history]
        
        process_cpu_values = [m['process']['cpu_percent'] for m in self.metrics_history]
        process_memory_values = [m['process']['memory_rss_mb'] for m in self.metrics_history]
        
        duration = time.time() - self.start_time if self.start_time else 0
        
        summary = {
            'monitoring_duration_seconds': round(duration, 2),
            'samples_collected': len(self.metrics_history),
            'system': {
                'cpu': {
                    'min': round(min(cpu_values), 2),
                    'max': round(max(cpu_values), 2),
                    'avg': round(sum(cpu_values) / len(cpu_values), 2)
                },
                'memory_percent': {
                    'min': round(min(memory_values), 2),
                    'max': round(max(memory_values), 2),
                    'avg': round(sum(memory_values) / len(memory_values), 2)
                },
                'disk_percent': {
                    'min': round(min(disk_values), 2),
                    'max': round(max(disk_values), 2),
                    'avg': round(sum(disk_values) / len(disk_values), 2)
                }
            },
            'process': {
                'cpu_percent': {
                    'min': round(min(process_cpu_values), 2),
                    'max': round(max(process_cpu_values), 2),
                    'avg': round(sum(process_cpu_values) / len(process_cpu_values), 2)
                },
                'memory_rss_mb': {
                    'min': round(min(process_memory_values), 2),
                    'max': round(max(process_memory_values), 2),
                    'avg': round(sum(process_memory_values) / len(process_memory_values), 2)
                }
            }
        }
        
        return summary
    
    def save_to_file(self, filepath: str):
        data = {
            'summary': self.get_summary(),
            'metrics_history': self.metrics_history
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
```

**代码说明**：
- `collect_metrics()`方法采集单次系统指标快照，包含CPU、内存、磁盘、网络及当前进程的资源使用情况
- `start_monitoring()`初始化监控会话，重置历史记录和开始时间
- `record_metrics()`采集并保存一次指标到历史记录
- `get_summary()`对历史指标进行统计分析，计算最小值、最大值、平均值
- `save_to_file()`将监控数据导出为JSON文件，便于后续分析

#### 7.1.2 定期指标收集实践

**适用场景**：长时间运行的训练任务、生产环境应用持续监控、性能基准测试、压力测试过程跟踪

对于需要持续监控的场景，建议使用后台线程定期采集指标，避免阻塞主业务流程。结合上下文管理器可以实现自动化的监控启停。

**定期监控使用示例**：
```python
import time
import json
import threading
from typing import Optional
from modules.monitor import PerformanceMonitor


class PeriodicMonitor:
    def __init__(self, monitor: PerformanceMonitor, interval_seconds: int = 60):
        self.monitor = monitor
        self.interval = interval_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
    
    def _monitoring_loop(self):
        while not self._stop_event.is_set():
            self.monitor.record_metrics()
            self._stop_event.wait(self.interval)
    
    def start(self):
        self.monitor.start_monitoring()
        self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)


if __name__ == '__main__':
    monitor = PerformanceMonitor()
    periodic = PeriodicMonitor(monitor, interval_seconds=10)
    
    print("启动系统监控，间隔10秒采集一次...")
    periodic.start()
    
    try:
        for i in range(30):
            print(f"模拟工作中... {i+1}/30")
            time.sleep(2)
    finally:
        periodic.stop()
        summary = monitor.get_summary()
        print("\n===== 监控摘要 =====")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        monitor.save_to_file('./performance_metrics.json')
        print("监控数据已保存到 performance_metrics.json")
```

**关键监控指标解读**：

| 指标类别 | 关键指标 | 预警阈值参考 | 说明 |
|---------|---------|-------------|------|
| CPU | cpu.percent | 持续 > 80% | CPU使用率过高可能导致推理延迟增加 |
| 内存 | memory.percent | > 85% | 内存使用率过高可能触发OOM，注意内存泄漏 |
| 进程内存 | process.memory_rss_mb | 持续增长不回落 | 内存持续增长可能存在内存泄漏，需重点关注 |
| 磁盘 | disk.percent | > 90% | 磁盘空间不足会导致写入失败、日志无法记录 |

⚠️ **重要提示**：
- 监控间隔不宜过短（建议不低于5秒），过于频繁的采集本身会消耗系统资源
- GPU监控需要额外安装`nvidia-ml-py`或`pynvml`库，psutil本身不提供GPU指标
- 监控数据建议定期轮转或归档，避免历史数据占用过多磁盘空间
- 在容器化环境中，psutil获取的是宿主机指标，容器内监控需结合cgroup文件系统

> **注意**：系统监控应与告警机制结合使用，当关键指标超过阈值时及时通知相关人员，而不仅仅是事后分析。

---

### 7.2 应用监控

系统监控关注底层资源使用情况，应用监控则聚焦于业务逻辑层面的性能表现，包括接口响应时间、方法执行耗时、错误率等核心指标，是定位代码级性能问题的关键手段。

#### 7.2.1 方法级性能监控装饰器

**适用场景**：模型推理接口监控、关键业务方法性能追踪、API响应时间统计、慢查询定位

**AOP（面向切面编程）**（通过分离横切关注点来提高代码模块化的编程范式）非常适合实现性能监控这类与业务逻辑无关的横切功能。在Python中，**装饰器模式**（Python中实现AOP的常用方式，不修改原函数动态添加功能）是最优雅的实现方式。

**性能监控装饰器实现**（modules/monitor.py）：
```python
import time
import logging
import traceback
from functools import wraps
from typing import Callable, Any, Dict, Optional
from collections import defaultdict
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


performance_records: Dict[str, List[Dict[str, Any]]] = defaultdict(list)


def performance_monitor(func: Optional[Callable] = None, *, log_args: bool = False):
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            func_name = f"{fn.__module__}.{fn.__qualname__}"
            start_time = time.time()
            start_timestamp = datetime.now().isoformat()
            
            status = 'success'
            error_info = None
            result = None
            
            try:
                result = fn(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                error_info = {
                    'type': type(e).__name__,
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
                raise
            finally:
                end_time = time.time()
                duration_ms = round((end_time - start_time) * 1000, 2)
                
                record = {
                    'function': func_name,
                    'start_time': start_timestamp,
                    'end_time': datetime.now().isoformat(),
                    'duration_ms': duration_ms,
                    'status': status,
                    'error': error_info
                }
                
                if log_args:
                    record['args'] = str(args)[:500]
                    record['kwargs'] = str(kwargs)[:500]
                
                performance_records[func_name].append(record)
                log_performance(record)
        
        return wrapper
    
    if func is not None:
        return decorator(func)
    return decorator


def log_performance(record: Dict[str, Any]):
    func_name = record['function']
    duration = record['duration_ms']
    status = record['status']
    
    if status == 'success':
        logger.info(
            f"[PERFORMANCE] {func_name} - 状态: {status}, 耗时: {duration}ms"
        )
    else:
        error = record['error']
        logger.error(
            f"[PERFORMANCE] {func_name} - 状态: {status}, 耗时: {duration}ms, "
            f"错误类型: {error['type']}, 错误信息: {error['message']}"
        )
```

**代码说明**：
- `performance_monitor`装饰器可以带参数或不带参数使用，通过`log_args`参数控制是否记录调用参数
- 使用`functools.wraps`保留原函数的元信息（函数名、文档字符串等）
- `try...except...finally`结构确保无论函数执行成功或失败，都能记录性能数据
- `performance_records`字典按函数名分类存储所有调用记录，便于后续统计分析
- `log_performance`函数统一处理日志输出，成功和错误使用不同日志级别

#### 7.2.2 装饰器应用与性能统计

**适用场景**：模型推理方法监控、API路由性能追踪、数据预处理流水线监控、批量任务执行统计

在业务代码中应用装饰器非常简单，只需在需要监控的函数或方法上添加`@performance_monitor`注解即可，无需修改原有业务逻辑。

**在推理模块中应用监控**：
```python
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modules.monitor import performance_monitor, performance_records


class ModelWrapper:
    def __init__(self):
        model_name = os.getenv('MODEL_NAME', 'bert-chinese-sentiment-analysis')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
        self.id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}
    
    @performance_monitor
    def predict(self, preprocessed_data: dict) -> dict:
        text = preprocessed_data['text']
        max_length = preprocessed_data.get('max_length', 512)
        
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=max_length,
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            confidence, pred_idx = torch.max(probabilities, dim=-1)
        
        return {
            'label': self.id2label[pred_idx.item()],
            'confidence': round(confidence.item(), 4),
            'probabilities': {
                self.id2label[i]: round(prob.item(), 4)
                for i, prob in enumerate(probabilities[0])
            }
        }
    
    @performance_monitor(log_args=True)
    def predict_batch(self, batch_data: list) -> list:
        results = []
        for data in batch_data:
            results.append(self.predict(data))
        return results


def get_performance_stats(func_name: str = None) -> dict:
    stats = {}
    target_functions = [func_name] if func_name else performance_records.keys()
    
    for fn in target_functions:
        records = performance_records.get(fn, [])
        if not records:
            continue
        
        durations = [r['duration_ms'] for r in records]
        success_count = sum(1 for r in records if r['status'] == 'success')
        error_count = sum(1 for r in records if r['status'] == 'error')
        
        durations_sorted = sorted(durations)
        p50_idx = int(len(durations_sorted) * 0.5)
        p95_idx = int(len(durations_sorted) * 0.95)
        p99_idx = int(len(durations_sorted) * 0.99)
        
        stats[fn] = {
            'total_calls': len(records),
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': round(success_count / len(records) * 100, 2) if records else 0,
            'duration_ms': {
                'min': round(min(durations), 2),
                'max': round(max(durations), 2),
                'avg': round(sum(durations) / len(durations), 2),
                'p50': round(durations_sorted[p50_idx], 2),
                'p95': round(durations_sorted[p95_idx], 2),
                'p99': round(durations_sorted[min(p99_idx, len(durations_sorted)-1)], 2)
            }
        }
    
    return stats


if __name__ == '__main__':
    model = ModelWrapper()
    
    test_texts = [
        "这个产品非常好用，我很满意！",
        "质量太差了，完全不值这个价。",
        "物流速度一般，产品中规中矩。"
    ]
    
    for text in test_texts:
        result = model.predict({'text': text})
        print(f"输入: {text}")
        print(f"结果: {result}\n")
    
    print("===== 性能统计 =====")
    stats = get_performance_stats()
    import json
    print(json.dumps(stats, ensure_ascii=False, indent=2))
```

**关键性能指标说明**：

| 指标 | 说明 | 关注意义 |
|-----|------|---------|
| total_calls | 总调用次数 | 了解方法使用频率 |
| success_rate | 成功率 | 低于99.9%需要排查错误原因 |
| avg | 平均耗时 | 了解整体性能水平 |
| p50 | 50分位耗时 | 中位数，代表典型请求耗时 |
| p95 | 95分位耗时 | 95%的请求耗时低于此值，反映长尾性能 |
| p99 | 99分位耗时 | 99%的请求耗时低于此值，反映极端慢请求情况 |

⚠️ **重要提示**：
- 生产环境建议关闭`log_args`，避免记录敏感数据或产生过多日志
- 性能记录存储在内存中，高并发场景下应定期导出或使用外部存储（如Prometheus）
- p95和p99比平均值更能反映用户实际体验，应重点关注长尾延迟问题
- 异常信息中的完整栈追踪有助于快速定位问题，但注意不要在对外接口中暴露

> **注意**：装饰器监控会带来微小的性能开销（通常小于1ms），对于极高性能要求的场景，可以通过配置开关控制是否启用监控。

---

## 八、核心价值总结

遵循AtomGit AI平台最佳实践，能够从开发流程、代码质量、团队协作、系统性能和安全防护五个维度为AI项目带来显著价值提升。

### 8.1 五大核心价值

#### 8.1.1 提高开发效率
通过标准化的项目模板、可复用的代码组件、自动化工具链和完善的文档体系，减少重复劳动，加快开发迭代速度。
- **具体实践**：模型配置文件标准化（1.1.3节）、模块化架构设计（3.1.1节）、MLflow实验跟踪（4.2.1节）、检查点机制（4.2.2节）、Git Flow工作流（5.1.2节）
- **效率提升点**：避免从零开始搭建项目结构，快速复用成熟模块；实验结果自动记录，无需手动整理；训练中断可从检查点恢复，无需从头开始。

#### 8.1.2 保证代码质量
通过统一的代码规范、类型提示、单元测试和代码审查机制，减少Bug，提升代码可维护性。
- **具体实践**：PEP 8代码风格（5.1.1.3节）、类型提示（5.1.1.4节）、文档字符串规范（5.1.1.2节）、单元测试（5.1.1.5节）、数据质量三指标检查（2.1.3节）
- **质量保障点**：代码风格一致，便于阅读和维护；类型提示提前发现类型错误；单元测试覆盖核心逻辑，防止回归Bug；数据质量检查确保训练数据可靠。

#### 8.1.3 增强团队协作
通过清晰的分支策略、规范的提交信息、完整的文档和标准化的沟通流程，降低团队沟通成本，提升协作效率。
- **具体实践**：语义化版本号（1.2.1节）、CHANGELOG维护（1.2.3节）、Git Flow分支策略（5.1.2节）、Conventional Commits提交规范、数据集文档规范（2.2.1节）
- **协作收益点**：版本号清晰表达变更类型，便于依赖管理；变更日志让所有成员了解更新内容；功能分支开发隔离，减少合并冲突；完整文档降低新人上手成本。

#### 8.1.4 提升系统性能
通过缓存策略、异步处理、资源优化和全链路监控，提升应用响应速度和并发处理能力。
- **具体实践**：Redis缓存策略（3.2.1节）、异步批量预测（3.2.2节）、gunicorn多进程部署（3.1.2节）、性能指标监控（7.1节）、资源合理配置（3.1.2节）
- **性能优化点**：重复请求结果缓存，避免重复计算；异步并发处理提升吞吐量；多进程充分利用多核CPU；监控指标及时发现性能瓶颈。

#### 8.1.5 确保安全性
通过环境变量管理、输入验证、权限控制和敏感信息保护，构建多层级安全防护体系。
- **具体实践**：环境变量敏感信息管理（6.1节）、输入数据校验（3.1.1节预处理模块）、JWT认证与RBAC权限控制（6.2节）、依赖安全扫描（6.3节）、API限流防护（6.4节）
- **安全防护点**：密钥不硬编码在代码中，通过环境变量注入；输入合法性校验防止恶意攻击；细粒度权限控制确保数据安全；定期扫描依赖漏洞，及时修复安全问题。

### 8.2 快速参考检查清单

#### 模型管理检查清单
- [ ] 模型名称遵循 `[架构]-[语言/领域]-[任务]` 命名规范
- [ ] 模型描述包含基本信息、功能描述、技术细节、使用示例、注意事项五部分
- [ ] model-config.yaml配置完整，version遵循语义化版本号规范
- [ ] 使用Git标签标记版本，标签名与版本号一致
- [ ] CHANGELOG.md按"新增/修复/变更"分类记录每个版本变更

#### 数据集管理检查清单
- [ ] 目录结构包含README.md、data/（train/validation/test）、metadata.json、schema.json
- [ ] metadata.json包含完整的统计信息和质量三指标（完整性/一致性/准确性）
- [ ] 发布前运行数据质量检查脚本，质量指标达标
- [ ] README包含概述、来源、格式、使用说明、质量评估、许可证、引用、联系方式八部分
- [ ] 数据集版本号遵循语义化版本规范

#### Space应用检查清单
- [ ] 采用模块化设计，拆分为preprocessor/model/postprocessor
- [ ] app.yaml配置文件完整，资源配额合理
- [ ] 敏感配置通过环境变量注入，不硬编码
- [ ] 启用Redis缓存高频请求结果（如适用）
- [ ] 配置健康检查接口，设置合理的初始延迟
- [ ] 输入数据在预处理模块进行合法性校验
- [ ] 异步批量接口设置批量大小上限，防止内存溢出

#### Notebook开发检查清单
- [ ] 单元格遵循"导入配置→数据加载→数据探索→预处理→训练→评估"六步结构
- [ ] 重复逻辑封装为函数或类，支持链式调用
- [ ] 使用MLflow记录实验参数、指标、模型和工件
- [ ] 长时间训练实现检查点保存与恢复机制
- [ ] 设置随机种子，确保结果可复现
- [ ] 实验完成后清理临时代码和无用单元格

#### 协作开发检查清单
- [ ] 代码遵循PEP 8规范，使用4空格缩进
- [ ] 公共函数和类包含完整文档字符串
- [ ] 添加类型提示，支持静态类型检查
- [ ] 核心功能编写单元测试，覆盖率达标
- [ ] 使用Git Flow工作流，分支命名规范
- [ ] 提交信息遵循Conventional Commits规范

#### 安全与性能检查清单
- [ ] 所有密钥、Token通过环境变量管理
- [ ] 用户输入进行校验和清洗，防止注入攻击
- [ ] API接口添加认证鉴权和限流防护
- [ ] 定期扫描依赖包安全漏洞
- [ ] 配置关键性能指标监控（QPS、延迟、错误率、资源使用率）
- [ ] 设置异常告警机制，及时发现线上问题

### 8.3 学习路径建议

对于AtomGit AI平台的新用户，建议按照以下路径循序渐进地学习和实践最佳实践：

**第一阶段：基础入门（1-2周）**
1. **模型管理**：掌握模型命名规范、配置文件编写、版本标签使用，从规范发布第一个模型开始
2. **数据集管理**：学习标准目录结构、元数据文件编写、数据质量检查方法，建立规范的数据管理习惯

**第二阶段：应用开发（2-3周）**
3. **Space应用开发**：从简单Flask应用开始，实践模块化设计、配置文件管理、Redis缓存和异步处理，逐步掌握应用部署和性能优化技巧
4. **Notebook开发**：学习六步单元格结构、函数类封装、MLflow实验跟踪和检查点机制，养成良好的实验管理习惯

**第三阶段：团队协作（2-3周）**
5. **协作开发规范**：深入学习PEP 8代码规范、类型提示、单元测试、Git Flow工作流和Conventional Commits提交规范，在团队项目中实践应用

**第四阶段：生产就绪（持续实践）**
6. **安全实践**：掌握环境变量管理、输入验证、认证鉴权、依赖扫描等安全措施，确保应用安全合规
7. **性能监控**：建立全链路性能监控体系，配置告警机制，持续优化系统性能
8. **持续改进**：在实际项目中不断复盘总结，将最佳实践内化为团队开发习惯，根据项目特点灵活调整，形成适合自身团队的工作流程

---

## 九、术语表

本章节统一解释文档中出现的关键术语，便于读者查阅和理解。

| 术语 | 定义与说明 |
|------|------------|
| **语义化版本号** | 一种采用"主版本.次版本.修订版本"（MAJOR.MINOR.PATCH）三段式结构的版本规范。主版本号在不兼容的API变更时递增，次版本号在向下兼容的功能新增时递增，修订版本号在向下兼容的问题修正时递增。 |
| **metadata.json** | 数据集元数据文件，用于描述数据集的基本信息，包括名称、版本、描述、许可证、创建者、统计信息（样本数量、类别分布）、数据格式、质量指标（完整性、一致性、准确性）和标签等。 |
| **Space应用** | AtomGit平台上的AI应用托管服务，用于部署和分享模型Demo，支持通过标准化配置文件定义运行环境、资源配额、依赖包和启动命令，提供便捷的AI应用发布能力。 |
| **Flask** | 轻量级Python Web框架，被称为"微框架"，具有简洁灵活的特点，适合快速开发AI推理服务和Web Demo，是AtomGit Space应用推荐的Web框架之一。 |
| **Redis** | 高性能的内存键值数据库（Remote Dictionary Server），常用于缓存、会话存储、消息队列等场景，在AI应用中主要用于缓存高频推理结果，提升响应速度。 |
| **MLflow** | 机器学习生命周期管理开源平台，提供实验跟踪（Tracking）、模型管理（Models）、项目打包（Projects）和模型服务（Model Registry）等组件，用于记录实验参数、指标、模型文件和工件，方便实验对比和复现。 |
| **Jupyter Notebook** | 开源的交互式计算环境，支持将代码、可视化图表、说明文档混合在一个文档中，广泛应用于数据探索、模型实验、数据分析和教学演示，是AI开发中最常用的实验工具之一。 |
| **PEP 8** | Python Enhancement Proposal 8的缩写，即Python官方代码风格指南，由Python社区制定并维护，涵盖缩进、行长度、空行、导入顺序、命名规范、空格使用等代码风格约定，是Python代码风格的事实标准。 |
| **Pydantic** | Python的数据验证库，使用Python类型注解进行数据校验和序列化，能够在运行时自动验证数据类型、格式和约束，提供友好的错误提示，常用于配置管理、API请求/响应验证等场景。 |
| **JWT** | JSON Web Token的缩写，是一种基于JSON的开放标准（RFC 7519），用于在各方之间安全地传输信息，常用于用户认证和信息交换，由Header、Payload和Signature三部分组成，具有无状态、可扩展的特点。 |
| **RBAC** | Role-Based Access Control的缩写，即基于角色的访问控制，是一种安全权限管理模型，通过将权限分配给角色，再将角色分配给用户，实现细粒度的权限控制，简化权限管理复杂度。 |
| **psutil** | Python的跨平台系统监控库（Python system and process utilities），提供了便捷的方法来获取系统运行时信息，包括CPU使用率、内存占用、磁盘IO、网络IO、进程信息等，常用于应用性能监控和资源使用统计。 |
| **Git Flow** | 一种经典的Git分支管理工作流模型，定义了main（生产分支）、develop（开发分支）、feature/*（功能分支）、release/*（发布分支）、hotfix/*（热修复分支）五种分支类型及其协作流程，支持并行开发和版本发布管理。 |
| **Conventional Commits** | 一种标准化的提交信息规范，通过统一的提交信息格式（如`feat: 新增功能`、`fix: 修复Bug`、`docs: 更新文档`），使提交历史更具可读性，支持自动化生成CHANGELOG和语义化版本管理。 |
| **检查点（Checkpoint）** | 在模型训练过程中定期保存的模型状态快照，包含模型权重、优化器状态、训练进度等信息，用于训练中断后从断点继续训练，避免从头开始浪费计算资源。 |
| **工件（Artifacts）** | 在MLflow中，指实验过程中产生的各类文件产物，如模型文件、损失曲线图、评估报告、配置文件、日志等，可以通过MLflow Tracking进行统一存储和管理。 |

---

> **文档说明**: 本文档基于AtomGit AI官方最佳实践文档（https://ai.gitcode.com/docs/faq/best-practices）提取整理，具体功能与操作以官网最新文档为准。
