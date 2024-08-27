import google.generativeai as genai
from flask import Flask, jsonify, make_response, request
import pandas as pd
from flask_cors import CORS
import json
# Configura la clave de API de Gemini
def autocompletado(texto):
    GOOGLE_API_KEY = 'AIzaSyAI6SmUQbQ9wJohy53_kssfZuzoLG5FRes'
    genai.configure(api_key=GOOGLE_API_KEY)

    # Configura el modelo de generación de texto
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="Tienes que completar las oraciones que pasa el usuario de una forma que tenga sentido y sea concisa, incluyendo el texto que ingresa el usuario como el principio de la oración completa. Es importante que la respuesta sea únicamente la oración completa, sin agregar información adicional. No usar exactamente el texto que esta en el csv"
    )

    # Lee el archivo CSV y extrae el contenido de interés
    csv_file = 'mati.csv'
    df = pd.read_csv(csv_file, delimiter="|")

    # Supongamos que la columna 'text' contiene los textos de interés
    texts = df['text'].tolist()

    # Función para buscar ejemplos relevantes basados en palabras clave
    def buscar_ejemplos(palabras_clave, textos):
        ejemplos_relevantes = []
        for texto in textos:
            if any(palabra in texto for palabra in palabras_clave):
                ejemplos_relevantes.append(texto)
        return ejemplos_relevantes

    # Función para ajustar la entrada al modelo basado en los ejemplos encontrados
    def generate_prompt(user_input, examples):
        prompt = f"Ingresa el texto: {user_input}\n\n"
        prompt += "Basado en los siguientes ejemplos, completa la oración de manera similar:\n\n"
        for example in examples:
            prompt += f"- {example}\n"
        return prompt

    # Función para completar el texto usando Gemini
    def completar_texto(texto_usuario):
        palabras_clave = texto_usuario.split()
        ejemplos = buscar_ejemplos(palabras_clave, texts)
        if not ejemplos:
            ejemplos = texts[-5:]
        prompt = generate_prompt(texto_usuario, ejemplos)
        response = model.generate_content([prompt])
        return response.text.strip()

    # Generar tres respuestas
    respuestas = [completar_texto(texto) for _ in range(3)]
    return respuestas

# autocompletado(input("Escribe algo: "))
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "I am alive!"

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    texto = json.loads(request.get_data().decode("utf-8"))["texto"]
    respuestas = autocompletado(texto)
    print(respuestas)
    return {"text":respuestas}

if __name__ == "__main__":
    app.run(host="0.0.0.0")