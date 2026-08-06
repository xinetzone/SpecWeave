---
id: 02-agent-class-signatures
title: Agent 类公开方法和属性签名提取
source: veadk-python codebase analysis
---

## 文件位置
veadk/agent.py，类 `Agent(LlmAgent)`。

## 公开属性

| 属性名 | 类型注解 | 默认值 |
|--------|----------|--------|
| id | str | `Field(default_factory=lambda: str(uuid.uuid4()).split("-")[0])` |
| name | str | `DEFAULT_AGENT_NAME` |
| description | str | `DEFAULT_DESCRIPTION` |
| instruction | Union[str, InstructionProvider] | `DEFAULT_INSTRUCTION` |
| model_name | Union[str, list[str]] | `Field(default_factory=lambda: settings.model.name)` |
| model_provider | str | `Field(default_factory=lambda: settings.model.provider)` |
| model_api_base | str | `Field(default_factory=lambda: settings.model.api_base)` |
| model_api_key | str | `""` |
| model_api_key_name | str | `Field(default_factory=lambda: settings.model.api_key_name)` |
| model_extra_config | dict | `Field(default_factory=dict)` |
| tools | list[ToolUnion] | `[]` |
| sub_agents | list[BaseAgent] | `Field(default_factory=list, exclude=True)` |
| prompt_manager | Optional[BasePromptManager] | `None` |
| knowledgebase | Optional[KnowledgeBase] | `None` |
| short_term_memory | Optional[ShortTermMemory] | `None` |
| long_term_memory | Optional[LongTermMemory] | `None` |
| tracers | list[BaseTracer] | `[]` |
| enable_responses | bool | `False` |
| enable_responses_cache | bool | `True` |
| context_cache_config | Optional[ContextCacheConfig] | `None` |
| run_processor | Optional[BaseRunProcessor] | `None` |
| enable_authz | bool | `False` |
| auto_save_session | bool | `False` |
| skills | list[str] | `Field(default_factory=list)` |
| skills_mode | Optional[Literal["skills_sandbox", "aio_sandbox", "local"]] | `None` |
| example_store | Optional[BaseExampleProvider] | `None` |
| enable_supervisor | bool | `False` |
| enable_ghostchar | bool | `False` |
| enable_dataset_gen | bool | `False` |
| enable_dynamic_load_skills | bool | `False` |
| enable_skills_checklist | bool | `False` |
| runtime | Literal["adk", "codex", "piagent"] | `"adk"` |
| codex_runtime_config | Optional[Any] | `None` |
| enable_a2ui | bool | `False` |
| a2ui_catalog | Optional[Any] | `None` |
| enable_tunnel | bool | `False` |

## 公开方法

### model_post_init
```python
def model_post_init(self, __context: Any) -> None
```

### update_model
```python
def update_model(self, model_name: str) -> None
```

### load_skills
```python
def load_skills(self) -> None
```

### run（仅在 google-adk <2.0.0 时存在）
```python
async def run(self, **kwargs)
```

---

本文件提取了 veadk/agent.py 中 Agent 类的所有公开属性和方法签名。属性部分包含35个公开字段的类型注解与默认值信息。方法部分包含4个公开方法的完整签名。所有签名均直接从源代码中提取，未进行主观推断或修改。该文件为理解 Agent 类的公开接口提供直接参考。
