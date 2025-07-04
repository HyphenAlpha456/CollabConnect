from flask import Flask, render_template, request, redirect, url_for
import json
import os
from uuid import uuid4

app = Flask(__name__)


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit-idea', methods=['GET', 'POST'])
def submit_idea():
    if request.method == 'POST':
        idea = {
            "title": request.form['title'],
            "description": request.form['description'],
            "tech": request.form['tech'],
            "email": request.form['email']
        }
        ideas = load_json('data/ideas.json')
        ideas.append(idea)
        save_json(ideas, 'data/ideas.json')
        return redirect(url_for('projects')) #
    return render_template('submit_idea.html')

@app.route('/projects')
def view_projects():
    ideas = load_json('data/ideas.json')
    return render_template('projects.html', ideas=ideas)#


@app.route('/forum')
def forum():
    questions = load_json('data/forum.json')
    return render_template('forum.html', questions=questions)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        question = {
            "id": str(uuid4()),
            "title": request.form['title'],
            "description": request.form['description'],
            "replies": []
        }
        questions = load_json('data/forum.json')
        questions.append(question)
        save_json(questions, 'data/forum.json')
        return redirect(url_for('forum'))
    return render_template('ask.html')

@app.route('/question/<id>', methods=['GET', 'POST'])
def question(id):
    questions = load_json('data/forum.json')
    question = next((q for q in questions if q['id'] == id), None)

    if not question:
        return "Question not found", 404

    if request.method == 'POST':
        reply = request.form['reply']
        question['replies'].append(reply)
        save_json(questions, 'data/forum.json')
        return redirect(url_for('question', id=id))

    return render_template('question.html', question=question)


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  

    os.makedirs('data', exist_ok=True)
    if not os.path.exists('data/ideas.json'):
        save_json([], 'data/ideas.json')
    if not os.path.exists('data/forum.json'):
        save_json([], 'data/forum.json')

    app.run(debug=True, host="0.0.0.0", port=port)

