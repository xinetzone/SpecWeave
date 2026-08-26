# ai-lab-recipes 事实

F-001: 项目包含使用Podman构建和运行容器化AI和LLM应用的配方（recipes），帮助开发者在本地快速原型化AI/LLM应用，无需依赖外部托管服务。
F-002: 配方由至少两个组件组成：模型服务器（model server）和AI应用，模型服务器管理模型，AI应用提供特定任务逻辑。
F-003: 模型服务器是提供机器学习模型（如LLM）服务并通过API暴露功能的程序，默认使用llamacpp_python模型服务器。
F-004: model_servers/目录包含多个模型服务器实现：llamacpp_python、object_detection_python、ollama、whispercpp。
F-005: llamacpp_python模型服务器支持base、cuda、vulkan（amd64/arm64）多种构建变体，包含src/run.sh启动脚本和tests/测试。
F-006: recipes/目录下按类别组织示例应用：audio、computer_vision、multimodal、natural_language_processing。
F-007: audio类别包含audio_to_text（语音转文本，基于whisper）应用。
F-008: computer_vision类别包含object_detection（目标检测）应用。
F-009: multimodal类别包含image_understanding（图像理解）应用。
F-010: natural_language_processing类别包含多个应用：agents（智能体）、chatbot（聊天机器人，含Python/Java Quarkus/Node.js多语言版本、llama-stack、pydantic-ai变体）、codegen（代码生成）、function_calling/function-calling-nodejs（函数调用）、graph-rag、rag（检索增强生成，含Node.js版本rag-nodejs）、summarizer（摘要）。
F-011: data/目录包含三个示例数据文件：fake_meeting.pdf、fake_meeting.txt、jfk.wav（音频文件）。
F-012: 许多应用提供bootc/目录（Bootable Containers支持）、quadlet/目录（Podman Quadlet systemd单元文件）、provision/目录（Ansible playbook配置）。
F-013: convert_models/目录包含模型转换工具，使用HuggingFace下载模型（download_huggingface.py），提供Containerfile和ui.py界面。
F-014: models/目录包含download_hf_models.py脚本用于下载HuggingFace模型，提供Makefile构建。
F-015: 项目提供git hooks（hooks/pre-commit），通过install-hooks.sh安装，确保training/ilab-wrapper/ilab文件复制到对应位置。
F-016: assets/目录包含各应用的截图和logo图片（chatbot_ui.png、codegen_ui.png、object_detection.png、rag_ui.png、summarizer_ui.png、whisper.png等）。
F-017: .github/workflows/目录包含多个CI工作流：chatbot.yaml、codegen.yaml、instructlab.yaml、model_servers.yaml、models.yaml、object_detection.yaml、rag.yaml、summarizer.yaml、training_bootc.yaml等。
F-018: eval/目录包含评估工具：embeddings（自定义评估集）、promptfoo（基于promptfoo的评估框架）。
F-019: training/目录包含用于AI训练的Linux操作系统可启动容器（Bootable containers）相关内容。
F-020: 许多示例应用镜像已构建并发布到quay.io，镜像列表记录在ailab-images.md文件中。
