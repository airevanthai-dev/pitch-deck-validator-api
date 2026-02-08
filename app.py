from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

code_text = """
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

@app.route("/")
def health():
    return {"status": "ok"}

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise Exception("Missing ANTHROPIC_API_KEY in Railway Variables")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

EVALUATION_PROMPT = \"\"\"
You are an expert startup pitch deck evaluator.

Evaluate this pitch deck across 5 dimensions (0–20 points each):

1. Problem & Insights Clarity
2. Solution & Value Proposition
3. Go-to-Market & Traction
4. Business Model & Economics
5. Investor Readiness
\"\"\"

@app.route("/evaluate", methods=["POST"])
def evaluate_pitch_deck():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    content = file.read()

    if not content:
        return jsonify({"error": "Empty file"}), 400

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": EVALUATION_PROMPT + "\\n\\nPitch deck text:\\n" + content.decode("utf-8", errors="ignore")
            }
        ],
    )

    return jsonify({"result": response.content[0].text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
"""

styles = getSampleStyleSheet()
doc = SimpleDocTemplate("/mnt/data/api_app.pdf", pagesize=A4)
story = []

for line in code_text.split("\n"):
    story.append(Paragraph(line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"), styles["Code"]))

doc.build(story)

"/mnt/data/api_app.pdf"
