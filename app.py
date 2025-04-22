from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

with open("data/lessons.json") as f:
    lessons = json.load(f)

with open("data/quiz.json") as f:
    quiz = json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/learn")
def learn():
    return render_template("learn.html", lessons=lessons)

@app.route("/quiz", methods=["GET", "POST"])
def quiz_view():
    if request.method == "POST":
        score = 0
        for idx, q in enumerate(quiz):
            if request.form.get(f"q{idx}") == q["answer"]:
                score += 1
        return redirect(url_for("result", score=score, total=len(quiz)))
    return render_template("quiz.html", quiz=quiz)

@app.route("/result")
def result():
    score = int(request.args.get("score", 0))
    total = int(request.args.get("total", 1))
    return render_template("result.html", score=score, total=total)

if __name__ == "__main__":
    app.run(debug=True)