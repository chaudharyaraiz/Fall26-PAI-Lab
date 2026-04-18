from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simple chatbot responses
def get_response(user_input):
    user_input = user_input.lower()

    if "admission" in user_input:
        return "Admissions are open from June to August every year."
    elif "programs" in user_input:
        return "We offer BSCS, BBA, BSE, and BS Physics programs."
    elif "fee" in user_input:
        return "Fee structure depends on the program. Approx 50,000 - 120,000 per semester."
    elif "deadline" in user_input:
        return "Last date to apply is 31st August."
    elif "requirements" in user_input:
        return "You need your CNIC/B-Form, Matric, and Intermediate certificates."
    elif "hello" in user_input or "hi" in user_input:
        return "Hello! How can I help you with admissions?"
    else:
        return "Sorry, I can only answer admission-related questions."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_message = request.form["msg"]
    response = get_response(user_message)
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)