from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from dotenv import load_dotenv
import os

from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ✅ API key env variable must be GOOGLE_API_KEY
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Missing API Key. Set GOOGLE_API_KEY in .env")

client = genai.Client(api_key=API_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Send a message."})

    if "chat_history" not in session:
        session["chat_history"] = []

    history = session["chat_history"]

    # ✅ convert your session history format to genai contents format
    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": m["content"]}]
        })

    # append new user message
    contents.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        bot_reply = resp.text or "No output."
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    # save history back to session
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": bot_reply})
    session["chat_history"] = history

    return jsonify({"reply": bot_reply, "model_used": "gemini-2.5-flash"})


@app.route("/reset", methods=["POST"])
def reset():
    session.pop("chat_history", None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
