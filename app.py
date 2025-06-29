from flask import Flask, render_template, request, jsonify
from src.calendar_agent.agent import CalendarAgent
import json

app = Flask(__name__)
agent = CalendarAgent()

@app.route("/")
def index():
    start_message = agent.start_message()
    return render_template("index.html", start_message=start_message)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "メッセージがありません"}), 400
    response_data = agent.send_message_for_ui(user_input)
    return jsonify(response_data)

@app.route("/delete_event", methods=["POST"])
def delete_event():
    event_id = request.json.get("event_id")
    if not event_id:
        return jsonify({"error": "イベントIDがありません"}), 400
    from src.calendar_agent import tools
    response_json = tools.delete_calendar_event(event_id)
    response = json.loads(response_json)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
