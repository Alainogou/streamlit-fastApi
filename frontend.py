import streamlit as st
import requests


def get_entity_color(entity):
    # Vous pouvez mapper les entités à des couleurs spécifiques ici
    color_mapping = {
        "PER": "blue",
        "LOC": "green",
        "ORG": "red",
        "O": "black"  # Couleur par défaut pour O
    }
    return color_mapping.get(entity, "black")  # Couleur par défaut


with st.sidebar:
    st.write('BylyAI Chat, une innovation résultant du PAS Challenge. BylyAI Chat est bien plus qu\'un simple chatbot ; il s\'agit d\'un système de reconnaissance d\'entités nommées (NER) intelligent. Lorsque vous saisissez du texte, BylyAI Chat utilise des techniques avancées de NER pour analyser et extraire des informations cruciales. Chaque entité est mise en évidence par une couleur distincte, facilitant ainsi la visualisation et la compréhension.')


st.title("💬 Chatbot BYLYAI")
st.caption("🚀 A chatbot ")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    data = {"text": prompt}
    req = requests.post("http://127.0.0.1:8000/ner", json=data)

    if req.status_code == 200:
        resultat = req.json()
        msg = resultat["entities"]

        st.markdown('<div class="msg-text">', unsafe_allow_html=True)

        text_to_display = []  # Liste pour stocker le texte

        for result in msg:
            text = result["text"]
            entity = result["entity"]
            if entity != "O":
                color = get_entity_color(entity)
                text_to_display.append(f'<span style="background: {color};">{text} ({entity})</span>')
            else:
                text_to_display.append(text)

        # Afficher le texte complet comme un seul paragraphe

        st.chat_message("assistant").write(' '.join(text_to_display), unsafe_allow_html=True)
        res = {"role": "assistant", "content": ' '.join(text_to_display)}
        st.session_state.messages.append(res)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.write("Une erreur s'est produite lors de la demande à l'API.")



