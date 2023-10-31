from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline
from fastapi.middleware.cors import CORSMiddleware
import re



app = FastAPI()

# Liste des origines autorisées (ajoutez l'URL de votre interface utilisateur)
origins = ["http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],  # Vous pouvez spécifier d'autres méthodes HTTP si nécessaire
    allow_headers=["*"],  # Vous pouvez spécifier des en-têtes spécifiques si nécessaire
)


# Charger le modèle pré-entraîné et le pipeline NER
tokenizer = AutoTokenizer.from_pretrained("masakhane/afroxlmr-large-ner-masakhaner-1.0_2.0")
model = TFAutoModelForTokenClassification.from_pretrained("masakhane/afroxlmr-large-ner-masakhaner-1.0_2.0")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)


class TextRequest(BaseModel):
    text: str

@app.post("/ner")
async def get_ner_entities(request: TextRequest):
    # Obtenez les entités nommées pour le texte d'entrée
    text = request.text
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

    return {"entities": prediction_text}

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
