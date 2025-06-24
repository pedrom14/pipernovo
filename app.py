from flask import Flask, request, send_file
from flask_cors import CORS
import subprocess
import uuid
import os
import requests

app = Flask(__name__)
CORS(app)

def safe_download(url, path):
    print(f"🔽 Baixando: {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    print(f"✅ Baixado: {path} ({os.path.getsize(path)} bytes)")

def download_if_needed(model_path, config_path):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        safe_download(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR-edresson-low.onnx",
            model_path
        )

    if not os.path.exists(config_path):
        safe_download(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR-edresson-low.onnx.json",
            config_path
        )

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    voice = data.get('voice', 'pt_BR-edresson-low')

    model_path = f"models/ptBR/{voice}.onnx"
    config_path = f"models/ptBR/{voice}.onnx.json"
    output_path = f"/tmp/{uuid.uuid4()}.wav"

    try:
        download_if_needed(model_path, config_path)

        print("🎤 Gerando áudio com Piper...")

        result = subprocess.run([
            "./piper",
            "--model", model_path,
            "--config", config_path,
            "--output_file", output_path,
            "--text", text
        ], capture_output=True, text=True)

        print("📋 STDOUT:", result.stdout)
        print("❗ STDERR:", result.stderr)

        if result.returncode != 0:
            return {"error": result.stderr}, 500

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return {"error": "Arquivo de áudio não gerado ou vazio."}, 500

        return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        return {"error": str(e)}, 500

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

