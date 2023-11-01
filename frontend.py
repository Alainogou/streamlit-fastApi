import streamlit as st
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline

import re

# Charger le modèle pré-entraîné et le pipeline NER
tokenizer = AutoTokenizer.from_pretrained("masakhane/afroxlmr-large-ner-masakhaner-1.0_2.0")
model = TFAutoModelForTokenClassification.from_pretrained("masakhane/afroxlmr-large-ner-masakhaner-1.0_2.0")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

def get_entity_color(entity):
    # Vous pouvez mapper les entités à des couleurs spécifiques ici
    color_mapping = {
        "PER": "blue",
        "LOC": "green",
        "ORG": "red",
        "O": "black"  # Couleur par défaut pour O
    }
    return color_mapping.get(entity, "black")  # Couleur par défaut


def get_word_starts(sentence):
    words = re.findall(r'\S+', sentence)
    word_starts = {}
    start = 0

    for word in words:
        word_starts[start] = word
        start += len(word) + 1  # Ajouter 1 pour l'espace

    return word_starts

def assign_entities_to_words(word_dict, entity_list):
    entities = {}

    for word_start, word in word_dict.items():
        entities[word] = "O"  # Par défaut, l'entité est 0

        for entity in entity_list:
            if entity['start'] == word_start:
                entities[word] = entity['entity']
                break

    return entities

def element_existe(element, tableau):
    return element in tableau

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


    text = prompt
    word_starts = get_word_starts(text)
    entities = assign_entities_to_words(word_starts, nlp(text))

    # Formatez la sortie sous forme de liste de dictionnaires
    ner_results = [{"word": word, "entity": entity} for word, entity in entities.items()]
    prediction_text = []  # Pour stocker les entités regroupées
    current_group = {"text": "", "entity": None}  # Pour stocker temporairement les entités en cours de regroupement

    for entity in ner_results:

        if entity['entity']=='O':
            current_group = {"text": entity['word'], "entity":'O'}
        else:
            if entity['entity'].startswith("B-"):
                current_group = {"text": entity['word'], "entity": entity['entity'][2:]}  # Enlever le préfixe "B-"
            elif entity['entity'] == "I-" + current_group['entity']:
                # Ajouter l'entité à la phrase en cours de regroupement
                current_group['text'] += " " + entity['word']

        if not element_existe(current_group, prediction_text):
            prediction_text.append(current_group)


    resultat = {"entities": prediction_text}
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



