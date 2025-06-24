import os
import subprocess
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Campo 'text' é obrigatório."}), 400

    output_filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join("/tmp", output_filename)

    # Caminhos e parâmetros
    model_path =  "models/ptBR/pt_BR-jeff-medium.onnx"
    config_path = "models/ptBR/pt_BR-jeff-medium.onnx.json"
    piper_bin = "./piper"

    command = [
        piper_bin,
        "--model", model_path,
        "--config", config_path,
        "--output_file", output_path
    ]

    # Chamada do Piper com entrada via stdin
    try:
        subprocess.run(command, input=text.encode("utf-8"), check=True)
        return send_file(output_path, mimetype="audio/wav")
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Erro ao executar o Piper: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

