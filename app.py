import os
import subprocess
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

ONNX_URL = "https://pub-ce3bb4b09b4347da9e4835d744965af1.r2.dev/pt_BR-edresson-low.onnx"
JSON_URL = "https://pub-ce3bb4b09b4347da9e4835d744965af1.r2.dev/pt_BR-edresson-low.onnx.json"

MODEL_DIR = "models/ptBR"
MODEL_PATH = os.path.join(MODEL_DIR, "pt_BR-edresson-low.onnx")
CONFIG_PATH = os.path.join(MODEL_DIR, "pt_BR-edresson-low.onnx.json")


# Faz download dos arquivos se não existirem localmente
def download_models():
    os.makedirs(MODEL_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Baixando modelo ONNX...")
        r = requests.get(ONNX_URL)
        with open(MODEL_PATH, 'wb') as f:
            f.write(r.content)

    if not os.path.exists(CONFIG_PATH):
        print("Baixando config JSON...")
        r = requests.get(JSON_URL)
        with open(CONFIG_PATH, 'wb') as f:
            f.write(r.content)

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Parâmetro "text" obrigatório'}), 400

    text = data['text']

    download_models()

    output_path = 'output.wav'

    command = [
        './piper',
        '--model', MODEL_PATH,
        '--config', CONFIG_PATH,
        '--output_file', output_path,
        '--text', text
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Erro ao gerar áudio', 'details': str(e)}), 500

    return send_file(output_path, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
