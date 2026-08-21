---
id: 10-tools-registry-facts
title: Tools 注册表事实记录
source: veadk-python codebase analysis
---

# Tools 注册表事实记录

## tools/ 目录结构和内置工具文件列表

根目录：veadk/tools/

### 根目录文件
| 文件名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/__init__.py |
| demo_tools.py | veadk/tools/demo_tools.py |
| ghost_char.py | veadk/tools/ghost_char.py |
| load_history_events.py | veadk/tools/load_history_events.py |
| load_knowledgebase_tool.py | veadk/tools/load_knowledgebase_tool.py |

### builtin_tools/ 子目录（veadk/tools/builtin_tools/）
| 文件名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/builtin_tools/__init__.py |
| _agentkit.py | veadk/tools/builtin_tools/_agentkit.py |
| a2a_registry.py | veadk/tools/builtin_tools/a2a_registry.py |
| agent_authorization.py | veadk/tools/builtin_tools/agent_authorization.py |
| coding.py | veadk/tools/builtin_tools/coding.py |
| execute_skills.py | veadk/tools/builtin_tools/execute_skills.py |
| generate_image.py | veadk/tools/builtin_tools/generate_image.py |
| image_edit.py | veadk/tools/builtin_tools/image_edit.py |
| image_generate.py | veadk/tools/builtin_tools/image_generate.py |
| lark.py | veadk/tools/builtin_tools/lark.py |
| las.py | veadk/tools/builtin_tools/las.py |
| link_reader.py | veadk/tools/builtin_tools/link_reader.py |
| llm_shield.py | veadk/tools/builtin_tools/llm_shield.py |
| load_kb_queries.py | veadk/tools/builtin_tools/load_kb_queries.py |
| load_knowledgebase.py | veadk/tools/builtin_tools/load_knowledgebase.py |
| mcp_router.py | veadk/tools/builtin_tools/mcp_router.py |
| mobile_run.py | veadk/tools/builtin_tools/mobile_run.py |
| parallel_web_search.py | veadk/tools/builtin_tools/parallel_web_search.py |
| playwright.py | veadk/tools/builtin_tools/playwright.py |
| ppt_generate.mjs | veadk/tools/builtin_tools/ppt_generate.mjs |
| ppt_generate.py | veadk/tools/builtin_tools/ppt_generate.py |
| run_code.py | veadk/tools/builtin_tools/run_code.py |
| run_sandbox_agent.py | veadk/tools/builtin_tools/run_sandbox_agent.py |
| supabase_toolset.py | veadk/tools/builtin_tools/supabase_toolset.py |
| tts.py | veadk/tools/builtin_tools/tts.py |
| vesearch.py | veadk/tools/builtin_tools/vesearch.py |
| video_generate.py | veadk/tools/builtin_tools/video_generate.py |
| vod.py | veadk/tools/builtin_tools/vod.py |
| web_fetch.py | veadk/tools/builtin_tools/web_fetch.py |
| web_scraper.py | veadk/tools/builtin_tools/web_scraper.py |
| web_search.py | veadk/tools/builtin_tools/web_search.py |

### mcp_tool/ 子目录（veadk/tools/mcp_tool/）
| 文件名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/mcp_tool/__init__.py |
| trusted_mcp_session_manager.py | veadk/tools/mcp_tool/trusted_mcp_session_manager.py |
| trusted_mcp_toolset.py | veadk/tools/mcp_tool/trusted_mcp_toolset.py |

### sandbox/ 子目录（veadk/tools/sandbox/）
| 文件名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/sandbox/__init__.py |
| browser_sandbox.py | veadk/tools/sandbox/browser_sandbox.py |
| code_sandbox.py | veadk/tools/sandbox/code_sandbox.py |
| computer_sandbox.py | veadk/tools/sandbox/computer_sandbox.py |

### skills_tools/ 子目录（veadk/tools/skills_tools/）
| 文件名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/skills_tools/__init__.py |
| bash_tool.py | veadk/tools/skills_tools/bash_tool.py |
| download_skills_tool.py | veadk/tools/skills_tools/download_skills_tool.py |
| file_tool.py | veadk/tools/skills_tools/file_tool.py |
| register_skills_tool.py | veadk/tools/skills_tools/register_skills_tool.py |
| session_path.py | veadk/tools/skills_tools/session_path.py |
| skills_tool.py | veadk/tools/skills_tools/skills_tool.py |
| skills_toolset.py | veadk/tools/skills_tools/skills_toolset.py |

### vanna_tools/ 子目录（veadk/tools/vanna_tools/）
| 文件名/目录名 | 路径 |
|--------|------|
| __init__.py | veadk/tools/vanna_tools/__init__.py |
| clickhouse/ | veadk/tools/vanna_tools/clickhouse/ |
| examples/ | veadk/tools/vanna_tools/examples/ |
| agent_memory.py | veadk/tools/vanna_tools/agent_memory.py |
| file_system.py | veadk/tools/vanna_tools/file_system.py |
| python.py | veadk/tools/vanna_tools/python.py |
| run_sql.py | veadk/tools/vanna_tools/run_sql.py |
| summarize_data.py | veadk/tools/vanna_tools/summarize_data.py |
| vanna_toolset.py | veadk/tools/vanna_tools/vanna_toolset.py |
| vanna_trainer.py | veadk/tools/vanna_tools/vanna_trainer.py |
| vikingdb_agent_memory.py | veadk/tools/vanna_tools/vikingdb_agent_memory.py |
| visualize_data.py | veadk/tools/vanna_tools/visualize_data.py |

vanna_tools/clickhouse/ 子目录文件：
- __init__.py
- sql_runner.py

vanna_tools/examples/ 子目录文件：
- example.py
- example_with_vikingdb_training.py

---

## agent.py 中自动挂载工具的位置和条件

所有自动挂载逻辑位于 veadk/agent.py 的 model_post_init 方法中，按代码执行顺序逐条件记录：

### 条件 1：knowledgebase 挂载
- 代码位置：veadk/agent.py:306-324
- 触发条件：`if self.knowledgebase:`
- 挂载内容：
  1. 导入 LoadKnowledgebaseTool 类
  2. 创建 LoadKnowledgebaseTool(knowledgebase=self.knowledgebase) 实例
  3. append 到 self.tools
  4. 子条件：`if self.knowledgebase.enable_profile:`
     - 导入 load_kb_queries 工具
     - append 到 self.tools

### 条件 2：long_term_memory 挂载
- 代码位置：veadk/agent.py:326-333
- 触发条件：`if self.long_term_memory is not None:`
- 挂载内容：
  1. 从 google.adk.tools 导入 load_memory
  2. 检查 load_memory 是否有 custom_metadata 属性，若有则设置 backend 元数据
  3. append load_memory 到 self.tools

### 条件 3：authz 回调挂载（非直接工具，是 before_agent_callback）
- 代码位置：veadk/agent.py:335-349
- 触发条件：`if self.enable_authz:`
- 挂载内容：导入 check_agent_authorization，添加到 self.before_agent_callback

### 条件 4：auto_save_session 回调挂载（非直接工具，是 after_agent_callback）
- 代码位置：veadk/agent.py:354-375
- 触发条件：`if self.auto_save_session:`
- 挂载内容：导入 save_session_to_long_term_memory，添加到 self.after_agent_callback（要求 long_term_memory 已初始化）

### 条件 5：skills 加载
- 代码位置：veadk/agent.py:377-397
- 触发条件：`if self.skills:`
- 挂载内容：
  1. 调用 self.load_skills() 方法
  2. 子条件：`if self.enable_skills_checklist:`
     - 导入 create_init_skill_check_list_callback
     - 创建 init_callback
     - 添加到 self.before_tool_callback
- load_skills() 方法内部（veadk/agent.py:453-612）：
  - 确定 skills_mode
  - 加载本地目录或云端 skills
  - 修改 self.instruction 添加 skills 描述
  - 第600行：`self.tools.append(SkillsToolset(self.skills_dict, self.skills_mode))`
  - 子条件：`if self.enable_dynamic_load_skills:`（veadk/agent.py:602-612）
     - 导入 check_skills
     - 添加到 self.before_agent_callback

### 条件 6：example_store 挂载
- 代码位置：veadk/agent.py:399-402
- 触发条件：`if self.example_store:`
- 挂载内容：
  1. 从 google.adk.tools.example_tool 导入 ExampleTool
  2. 创建 ExampleTool(examples=self.example_store) 实例
  3. append 到 self.tools

### 条件 7：ghostchar 挂载
- 代码位置：veadk/agent.py:404-410
- 触发条件：`if self.enable_ghostchar:`
- 挂载内容：
  1. 导入 GhostcharTool 类
  2. 创建 GhostcharTool() 实例
  3. append 到 self.tools
  4. 修改 self.instruction 追加提示文本

### 条件 8：a2ui 挂载
- 代码位置：veadk/agent.py:412-416
- 触发条件：`if self.enable_a2ui:`
- 挂载内容：
  1. 从 veadk.a2ui 导入 build_a2ui_toolset 函数
  2. 调用 build_a2ui_toolset(catalog=self.a2ui_catalog)
  3. append 返回结果到 self.tools

### 条件 9：tunnel 挂载
- 代码位置：veadk/agent.py:418-422
- 触发条件：`if self.enable_tunnel:`
- 挂载内容：
  1. 从 veadk.tunnel 导入 TunnelToolset 类
  2. 创建 TunnelToolset(agent_name=self.name) 实例
  3. append 到 self.tools

### 条件 10：dataset_gen 回调挂载（非直接工具，是 after_agent_callback）
- 代码位置：veadk/agent.py:424-438
- 触发条件：`if self.enable_dataset_gen:`
- 挂载内容：导入 dataset_auto_gen_callback，添加到 self.after_agent_callback

---

## _validate_tool_dependencies 方法客观步骤记录

方法位置：veadk/agent.py:614-643

### 执行步骤

1. 代码行号：615
   - 动作：初始化变量 `tool_names = set()`，创建空集合

2. 代码行号：616-620
   - 动作：进入 for 循环遍历 `self.tools`
   - 循环体：
     - 对每个 tool：
       - 若 tool 有 `__name__` 属性：将 `tool.__name__` 添加到 tool_names 集合
       - 若 tool 有 `name` 属性但无 `__name__` 属性：将 `tool.name` 添加到 tool_names 集合

3. 代码行号：622-623
   - 动作：声明两个布尔变量
   - `has_video_generate = "video_generate" in tool_names`
   - `has_video_task_query = "video_task_query" in tool_names`

4. 代码行号：625-635
   - 动作：第一个条件分支
   - 条件：`if has_video_generate and not has_video_task_query:`
   - 条件满足时执行：
     1. 从 veadk.tools.builtin_tools.video_generate 导入 video_task_query
     2. 输出 warning 级别日志，提示 video_generate 已挂载但 video_task_query 未挂载，将自动添加
     3. 执行 `self.tools.append(video_task_query)`

5. 代码行号：636-643
   - 动作：第二个条件分支
   - 条件：`elif has_video_task_query and not has_video_generate:`
   - 条件满足时执行：
     1. 从 veadk.tools.builtin_tools.video_generate 导入 video_generate
     2. 输出 warning 级别日志，提示 video_task_query 已挂载但 video_generate 未挂载，将自动添加
     3. 执行 `self.tools.append(video_generate)`

### 方法边界
- 方法结束位置：veadk/agent.py:643
- 该方法仅处理 video_generate 和 video_task_query 这一对工具的依赖互补，无其他工具依赖检查逻辑

---

本文档记录了 veadk/tools/ 目录下 5 个子目录和根目录的全部内置工具文件清单。本文档按代码执行顺序列出了 model_post_init 方法中 10 个工具/回调自动挂载的触发条件和挂载内容。本文档详细记录了 _validate_tool_dependencies 方法的 5 个执行步骤，该方法仅处理视频生成相关工具的依赖自动补全。
