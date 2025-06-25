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

    wav_filename = f"{uuid.uuid4()}.wav"
    mp3_filename = wav_filename.replace(".wav", ".mp3")

    wav_path = os.path.join("/tmp", wav_filename)
    mp3_path = os.path.join("/tmp", mp3_filename)

    # Voz selecionada (padrão = faber)
    voice = data.get("voice", "pt_BR-faber-medium")
    model_path = f"models/ptBR/{voice}.onnx"
    config_path = f"models/ptBR/{voice}.onnx.json"
    piper_bin = "./piper"

    # Parâmetros de qualidade ajustados
    length_scale = "1.45"     # Lento, mas ainda fluido
    noise_scale = "0.35"      # Suave, com variação suficiente
    noise_w = "0.65"          # Timbre equilibrado, nem metálico nem abafado


    
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
        # Gera o WAV com o Piper
        subprocess.run(command, input=text.encode("utf-8"), check=True)

        # Converte WAV para MP3 usando ffmpeg
        subprocess.run([
            "ffmpeg", "-y",  # sobrescreve se existir
            "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-b:a", "96k",  # taxa de bits: bom equilíbrio qualidade/tamanho
            mp3_path
        ], check=True)

        return send_file(mp3_path, mimetype="audio/mpeg")

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Erro ao executar o Piper ou ffmpeg: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)





