from google.cloud import storage
import io
from PIL import Image
from flask import jsonify

client = storage.Client()
BUCKET_DESTINO = "udc-tubos-conexoes-rio-preto-imagens/processados"

def teste_upload():
    try:
        imagem = Image.new("RGBA", (800, 800), color=(255, 0, 0, 255))
        buffer = io.BytesIO()
        imagem.save(buffer, format="PNG")
        nome_teste = "teste-upload-codigo.png"
        destino_bucket = client.bucket(BUCKET_DESTINO.split("/", 1)[0])
        destino_blob = destino_bucket.blob(BUCKET_DESTINO.split("/", 1)[1] + "/" + nome_teste)
        destino_blob.upload_from_string(buffer.getvalue(), content_type="image/png")
        return jsonify({"status": "ok", "mensagem": "Upload de teste concluído.", "arquivo": nome_teste})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)})