import os
from openai import OpenAI

class LearningPathGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def generate(self, level, goals):
        system_prompt = """你是一位专业的编程学习规划师。请根据用户的当前水平和学习目标，制定一份详细的学习路径。

学习路径结构：
1. 评估：分析用户当前水平和目标
2. 阶段规划：分阶段列出学习内容（建议3-4个阶段）
3. 每周任务：每个阶段的具体学习任务
4. 推荐资源：推荐书籍、网站、课程等学习资源
5. 实践项目：建议的实践项目

请使用中文输出，保持结构清晰，内容实用。"""

        goals_str = ', '.join(goals) if goals else '无特定目标'
        user_prompt = f"""用户水平：{level}
用户目标：{goals_str}

请为用户制定一份详细的编程学习路径。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5
        )

        return response.choices[0].message.content