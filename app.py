from flask import Flask, request, jsonify, render_template, session
from huggingface_hub import InferenceClient
from flask_session import Session

# Fix: Correct the __name__ syntax (using double underscores)
app = Flask(__name__)
app.secret_key = "supersecret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize Hugging Face client
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token="ENTER THE API KEY"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    
    # Fix: Proper indentation for the if block
    if "chat_history" not in session:
        session["chat_history"] = []
    
    history = session["chat_history"]
    history.append({"role": "user", "content": user_input})
    
    try:
        response = client.chat_completion(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {"role": turn["role"], "content": turn["content"]}
                for turn in history
            ],
            max_tokens=200,
            temperature=0.7
        )
        bot_reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        bot_reply = f"Error: {str(e)}"
    
    history.append({"role": "assistant", "content": bot_reply})
    session["chat_history"] = history
    return jsonify({"reply": bot_reply})

# Fix: Correct the __name__ and __main__ syntax
if __name__ == "__main__":
    app.run(debug=True)