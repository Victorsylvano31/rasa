from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# URL de l'API Rasa
RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Aucun message reçu."})

    try:
        response = requests.post(RASA_API_URL, json={"sender": "user", "message": user_message})
        if response.status_code == 200:
            messages = [msg.get("text") for msg in response.json() if msg.get("text")]
            if messages:
                return jsonify({"response": " ".join(messages)})
            else:
                return jsonify({"response": "Désolé, je n'ai pas compris."})
        else:
            return jsonify({"response": "Erreur serveur Rasa."})
    except requests.exceptions.RequestException:
        return jsonify({"response": "Impossible de joindre le serveur Rasa."})

if __name__ == "__main__":
    # host="0.0.0.0" pour Codespaces
    app.run(host="0.0.0.0", port=3000, debug=True)
