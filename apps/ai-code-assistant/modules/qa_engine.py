import os
from openai import OpenAI

class QAEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def ask(self, question, context=''):
        system_prompt = """你是一位耐心、专业的编程导师。请回答用户关于编程的问题。

回答要求：
1. 使用中文，语言清晰易懂
2. 提供代码示例帮助理解
3. 如果涉及概念，给出简明定义
4. 保持回答简洁但完整

如果你不确定答案，请诚实说明。"""

        user_prompt = f"问题：{question}"
        if context:
            user_prompt += f"\n\n上下文：\n{context}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        return response.choices[0].message.content