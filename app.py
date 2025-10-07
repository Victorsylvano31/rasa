import streamlit as st
import requests
import os

# -------------------------------
# CONFIGURATION DE LA PAGE
# -------------------------------
st.set_page_config(page_title="ChatBot RASA", page_icon="🤖", layout="centered")

# -------------------------------
# STYLES CSS 
# -------------------------------
st.markdown("""
<style>
/* Fond de la page */
body, [data-testid="stAppViewContainer"] {
    background-color: #0a2540 !important;
}

/* Conteneur principal du chat */
.chat-container {
    max-width: 600px;
    margin: 20px auto;
    background: #1c1e21;
    border-radius: 15px;
    padding: 20px;
    height: 60vh;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    display: flex;
    flex-direction: column;
    gap: 10px;
}

/* Messages */
.user-msg, .bot-msg {
    padding: 12px 18px;
    border-radius: 20px;
    max-width: 80%;
    word-wrap: break-word;
    font-size: 14px;
    line-height: 1.4;
    color: #ffffff;
    animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.user-msg {
    background-color: #1877f2;
    align-self: flex-end;
    text-align: left;
    border-bottom-right-radius: 4px;
}

.bot-msg {
    background-color: #2c3e50;
    align-self: flex-start;
    text-align: left;
    border-bottom-left-radius: 4px;
}

/* Barre d'entrée */
.stTextInput > div > div > input {
    border-radius: 25px;
    padding: 12px 20px;
    border: 1px solid #444;
    background-color: #1c1e21;
    color: #ffffff;
}

/* Scrollbar personnalisée */
.chat-container::-webkit-scrollbar {
    width: 6px;
}
.chat-container::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 10px;
}

/* Cacher le label de l'input */
.stTextInput > label {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# INITIALISATION DE L'ÉTAT
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# FONCTION D’APPEL AU SERVEUR RASA
# -------------------------------
def query_rasa(message):
    rasa_url = os.getenv("RASA_WEBHOOK_URL", "http://localhost:5005/webhooks/rest/webhook")
    payload = {"sender": "user", "message": message}
    try:
        response = requests.post(rasa_url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        texts = [item.get("text", "🤖 (Pas de texte dans la réponse)") for item in data if "text" in item]
        return texts if texts else ["🤖 (Pas de réponse valide du bot)"]
    except requests.exceptions.RequestException as e:
        return [f"⚠️ Erreur de connexion à RASA : {str(e)}"]

# -------------------------------
# TITRE
# -------------------------------
st.markdown('<div style="text-align: center; color: white; margin-bottom: 20px;"><h2>💬 ChatBot RASA </h2></div>', unsafe_allow_html=True)

# -------------------------------
# AFFICHAGE DES MESSAGES DANS UN SEUL CONTENEUR
# -------------------------------
chat_html = '<div class="chat-container" id="chat-box">'

for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f'<div class="user-msg">{msg["content"]}</div>'
    else:
        chat_html += f'<div class="bot-msg">{msg["content"]}</div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# -------------------------------
# AUTO-SCROLL VIA JAVASCRIPT
# -------------------------------
st.components.v1.html("""
<script>
function scrollToBottom() {
    const chatBox = parent.document.getElementById('chat-box');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}
// Attendre que le DOM soit prêt
setTimeout(scrollToBottom, 100);
</script>
""", height=0)

# -------------------------------
# ENTRÉE UTILISATEUR
# -------------------------------
user_input = st.chat_input("Écris ton message ici...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_responses = query_rasa(user_input)
    for resp in bot_responses:
        st.session_state.messages.append({"role": "bot", "content": resp})
    st.rerun()