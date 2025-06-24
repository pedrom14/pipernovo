from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess
import uuid
import os
import requests

app = Flask(__name__)
CORS(app)

# Função para baixar modelo e config se não existirem
def download_if_needed(model_path, config_path):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        print("📥 Baixando modelo .onnx...")
        model_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR-edresson-low.onnx"
        r = requests.get(model_url)
        with open(model_path, 'wb') as f:
            f.write(r.content)

    if not os.path.exists(config_path):
        print("📥 Baixando config .json...")
        config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR-edresson-low.onnx.json"
        r = requests.get(config_url)
        with open(config_path, 'wb') as f:
            f.write(r.content)

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'pt_BR-edresson-low')

    model_path = f"models/ptBR/{voice}.onnx"
    config_path = f"models/ptBR/{voice}.onnx.json"
    output_path = f"/tmp/{uuid.uuid4()}.wav"

    # Garantir que modelo e config existem
    try:
        download_if_needed(model_path, config_path)
    except Exception as e:
        return {"error": f"Erro ao baixar modelo: {str(e)}"}, 500

    # Executar o Piper
    try:
        result = subprocess.run([
            "./piper",
            "--model", model_path,
            "--config", config_path,
            "--output_file", output_path,
            "--text", text
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("Erro no Piper:", result.stderr)
            return {"error": result.stderr}, 500

        return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

