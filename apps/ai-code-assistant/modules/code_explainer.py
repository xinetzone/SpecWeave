import os
from openai import OpenAI

class CodeExplainer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def explain_code(self, code, language='python'):
        system_prompt = f"""你是一位资深的{language}编程语言导师。
请用清晰、易懂的语言解释以下代码。

解释结构：
1. 功能概述：这段代码实现了什么功能
2. 核心逻辑：主要的执行流程和关键算法
3. 关键技术点：涉及的重要概念、设计模式或API
4. 代码优化建议：如果有改进空间，请提供具体建议

请使用中文解释，语言要适合编程初学者理解。"""

        user_prompt = f"请解释这段{language}代码：\n\n{code}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content