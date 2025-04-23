from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev_key'

with open("data/lessons.json") as f:
    lessons = json.load(f)

with open("data/quiz.json") as f:
    quiz = json.load(f)

@app.route("/")
def home():
    session.clear() 
    print("SESSION DATA:", dict(session))
    return render_template("index.html")

@app.route("/learn/<int:lesson_id>")
def learn(lesson_id):
    if 'actions' not in session:
        session['actions'] = []
    if lesson_id > len(lessons):
        return redirect("/quiz/1")
    session['actions'].append({
        'lesson': lesson_id,
        'timestamp': datetime.now().isoformat()
        })
    session.modified = True 
    print("SESSION DATA:", dict(session))
    return render_template("learn.html", lesson=lessons[lesson_id - 1], next_id=lesson_id + 1, lesson_id=lesson_id)

@app.route("/quiz/<int:question_id>", methods=["GET", "POST"])
def quiz_page(question_id):
    if 'quiz_answers' not in session:
        session['quiz_answers'] = {}

    if request.method == "POST":
        selected = request.form.get("answer")
        session['quiz_answers'][str(question_id - 1)] = selected
        session.modified = True  # Make sure session updates persist
        return redirect(url_for("quiz_page", question_id=question_id + 1))  # Go to next question

    if question_id > len(quiz):
        return redirect("/result")
    print("SESSION DATA:", dict(session))
    return render_template("quiz.html", question=quiz[question_id - 1], question_id=question_id)

@app.route("/result")
def result():
    print("SESSION DATA:", dict(session))
    score = 0
    for i, q in enumerate(quiz):
        if session['quiz_answers'].get(str(i)) == q['answer']:
            score += 1
    return render_template("result.html", score=score, total=len(quiz))

if __name__ == "__main__":
    app.run(debug=True)
