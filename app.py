import os
import subprocess
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import html

app = Flask(__name__)
CORS(app)

def limpar_html_para_tts(conteudo_html):
    soup = BeautifulSoup(conteudo_html, "html.parser")
    texto_puro = soup.get_text(separator='\n', strip=True)
    texto_sem_entidades = html.unescape(texto_puro)
    return texto_sem_entidades

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    html_input = data.get("text", "")

    if not html_input:
        return jsonify({"error": "Campo 'text' é obrigatório."}), 400

    text = limpar_html_para_tts(html_input)

    wav_filename = f"{uuid.uuid4()}.wav"
    mp3_filename = wav_filename.replace(".wav", ".mp3")

    wav_path = os.path.join("/tmp", wav_filename)
    mp3_path = os.path.join("/tmp", mp3_filename)

    voice = data.get("voice", "pt_BR-faber-medium")
    model_path = f"models/ptBR/{voice}.onnx"
    config_path = f"models/ptBR/{voice}.onnx.json"
    piper_bin = "./piper"

    length_scale = "1.45"
    noise_scale = "0.35"
    noise_w = "0.65"

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







