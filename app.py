from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

# ─── data ────────────────────────────────────────────────────────────
from data.exercises import exercises          # exercise list (thumb, name, …)

app = Flask(__name__)
app.secret_key = "dev_key"

with open("data/lessons.json") as f:
    lessons = json.load(f)

with open("data/quiz.json") as f:
    quiz = json.load(f)

# ─── routes ──────────────────────────────────────────────────────────

@app.route("/")
def home():                    # fresh session each visit
    return render_template("index.html")

@app.route("/progress")
def progress():
    completed = session.get("completed", [])   # list of lesson IDs (1-based)
    return render_template(
        "progress.html",
        exercises=exercises,
        completed=completed
    )

@app.route("/learn/<int:lesson_id>")
def learn(lesson_id):
    """
    • Displays the requested lesson.
    • Marks the PREVIOUS lesson as completed (user just hit “Next Lesson”).
    """
    # ── mark previous lesson complete ───────────────────────────────
    if lesson_id > 1:
        comp = session.setdefault("completed", [])
        prev_id = lesson_id - 1
        if prev_id not in comp:
            comp.append(prev_id)
            session.modified = True

    # ── if past last lesson, jump to quiz ───────────────────────────
    if lesson_id > len(lessons):
        return redirect("/quiz/1")

    # ── normal lesson render ────────────────────────────────────────
    return render_template(
        "learn.html",
        lesson=lessons[lesson_id - 1],
        next_id=lesson_id + 1,
        lesson_id=lesson_id,
    )

@app.route("/quiz/<int:question_id>", methods=["GET", "POST"])
def quiz_page(question_id):
    if "quiz_answers" not in session:
        session["quiz_answers"] = {}

    if request.method == "POST":
        session["quiz_answers"][str(question_id - 1)] = request.form.get("answer")
        session.modified = True
        return redirect(url_for("quiz_page", question_id=question_id + 1))

    if question_id > len(quiz):
        return redirect("/result")

    return render_template(
        "quiz.html", question=quiz[question_id - 1], question_id=question_id
    )

@app.route("/result")
def result():
    score = sum(
        1
        for i, q in enumerate(quiz)
        if session["quiz_answers"].get(str(i)) == q["answer"]
    )
    return render_template("result.html", score=score, total=len(quiz))

if __name__ == "__main__":
    app.run(debug=True)
