from flask import Flask, request, jsonify
from image_processor import process_images_from_bucket
from debug_upload_imagens import teste_upload
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["POST", "GET"])
def handle():
    if request.method == "POST" or request.method == "GET":
        result = process_images_from_bucket()
        return jsonify(result)
    return jsonify({"status": "error", "message": "Método não suportado"}), 405

@app.route("/debug", methods=["GET"])
def debug():
    return teste_upload()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)