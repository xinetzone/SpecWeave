from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from modules.code_explainer import CodeExplainer
from modules.qa_engine import QAEngine
from modules.learning_path import LearningPathGenerator

load_dotenv()

app = Flask(__name__)

code_explainer = CodeExplainer()
qa_engine = QAEngine()
learning_path_generator = LearningPathGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/explain', methods=['POST'])
def explain_code():
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    result = code_explainer.explain_code(code, language)
    return jsonify({'result': result})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question', '')
    context = data.get('context', '')
    result = qa_engine.ask(question, context)
    return jsonify({'result': result})

@app.route('/api/learning-path', methods=['POST'])
def generate_learning_path():
    data = request.json
    level = data.get('level', 'beginner')
    goals = data.get('goals', [])
    path = learning_path_generator.generate(level, goals)
    return jsonify({'path': path})

if __name__ == '__main__':
    app.run(debug=True)