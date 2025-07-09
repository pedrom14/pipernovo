import os
import subprocess
import uuid
import re
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import html

app = Flask(__name__)
CORS(app)

def preprocess_text_for_tts(conteudo_html):
    soup = BeautifulSoup(conteudo_html, 'html.parser')

    # Adiciona ponto em títulos
    for header in soup.find_all(['h1', 'h2', 'h3']):
        header.string = f"{header.get_text(strip=True)}."

    # Extrai o texto com \n entre parágrafos
    texto_bruto = soup.get_text(separator='\n')

    linhas = texto_bruto.split('\n')
    linhas_processadas = []

    for linha in linhas:
        texto = linha.strip()
        if not texto:
            continue

        # Se já termina com pontuação, mantém
        if re.search(r'[.!?:…]$', texto):
            linhas_processadas.append(texto)
        # Se termina com vírgula, dois pontos ou hífen, não adiciona ponto
        elif re.search(r'[,:;\-–—]$', texto):
            linhas_processadas.append(texto)
        else:
            # Adiciona ponto final para simular pausa
            linhas_processadas.append(texto + '.')

    # Junta com quebras duplas para simular parágrafos
    texto_final = '\n\n'.join(linhas_processadas)
    texto_sem_entidades = html.unescape(texto_final)
    return texto_sem_entidades

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    html_input = data.get("text", "")

    if not html_input:
        return jsonify({"error": "Campo 'text' é obrigatório."}), 400

    text = preprocess_text_for_tts(html_input)

    wav_filename = f"{uuid.uuid4()}.wav"
    mp3_filename = wav_filename.replace(".wav", ".mp3")

    wav_path = os.path.join("/tmp", wav_filename)
    mp3_path = os.path.join("/tmp", mp3_filename)

    voice = data.get("voice", "pt_BR-faber-medium")
    model_path = f"models/ptBR/{voice}.onnx"
    config_path = f"models/ptBR/{voice}.onnx.json"
    piper_bin = "./piper"

    length_scale = "1.35"
    noise_scale = "0.3"
    noise_w = "0.6"

    command = [
        piper_bin,
        "--model", model_path,
        "--config", config_path,
        "--output_file", wav_path,
        "--length_scale", length_scale,
        "--noise_scale", noise_scale,
        "--noise_w", noise_w
    ]

    try:
        subprocess.run(command, input=text.encode("utf-8"), check=True)

        subprocess.run([
            "ffmpeg", "-y",
            "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", "96k",
            mp3_path
        ], check=True)

        return send_file(mp3_path, mimetype="audio/mpeg")

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Erro ao executar o Piper ou ffmpeg: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)








