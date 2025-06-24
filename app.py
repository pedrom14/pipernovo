@app.route('/tts', methods=['POST'])
def tts():
    try:
        data = request.json
        text = data.get('text')
        voice = data.get('voice', 'pt_BR-edresson-low')

        model_path = f"models/ptBR/{voice}.onnx"
        config_path = f"models/ptBR/{voice}.onnx.json"
        output_path = f"/tmp/{uuid.uuid4()}.wav"

        download_if_needed(model_path, config_path)

        result = subprocess.run([
            "./piper",
            "--model", model_path,
            "--config", config_path,
            "--output_file", output_path,
            "--text", text
        ], capture_output=True, text=True)

        # NOVO: mostrar o erro diretamente se houver falha
        if result.returncode != 0:
            return {
                "error": "Erro na execução do Piper",
                "stdout": result.stdout,
                "stderr": result.stderr
            }, 500

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            return {
                "error": "Arquivo de áudio não foi gerado.",
                "output_path": output_path
            }, 500

        return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        # NOVO: capturar qualquer exceção de Python (requests, etc.)
        return {"error": str(e)}, 500

    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

