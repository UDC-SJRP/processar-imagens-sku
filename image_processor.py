import os
import io
import re
import pandas as pd
from PIL import Image
from google.cloud import storage
from utils import padronizar_nome, enviar_telegram
from datetime import datetime

BUCKET_ORIGEM = "udc-tubos-conexoes-rio-preto-imagens/para_processar"
BUCKET_DESTINO = "udc-tubos-conexoes-rio-preto-imagens/processados"
CSV_SHOP9 = "produtos-cadastrados-shop9.csv"
CSV_AUTORAL = "arquivo-autoral.csv"
RELATORIO_PROCESSAMENTO = "relatorio-processamento.csv"

client = storage.Client()

TELEGRAM_TOKEN = "<SEU_TOKEN_AQUI>"
TELEGRAM_CHAT_ID = "+5517996299818"

def process_images_from_bucket():
    bucket_name, prefix = BUCKET_ORIGEM.split("/", 1)
    bucket = client.bucket(bucket_name)
    blobs = client.list_blobs(bucket, prefix=prefix)

    resultado = []
    shop_df = pd.read_csv(CSV_SHOP9)
    autoral_df = pd.read_csv(CSV_AUTORAL)

    for blob in blobs:
        if not blob.name.lower().endswith(('.png', '.webp', '.jpg', '.jpeg')):
            continue

        try:
            img_bytes = blob.download_as_bytes()
            imagem = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
            imagem = imagem.resize((800, 800))

            nome_padronizado = padronizar_nome(blob.name, shop_df, autoral_df)
            buffer = io.BytesIO()
            imagem.save(buffer, format="PNG", optimize=True)

            if buffer.getbuffer().nbytes > 300000:
                imagem.save(buffer, format="PNG", optimize=True, quality=80)

            destino_bucket = client.bucket(BUCKET_DESTINO.split("/", 1)[0])
            destino_blob = destino_bucket.blob(BUCKET_DESTINO.split("/", 1)[1] + "/" + nome_padronizado)
            destino_blob.upload_from_string(buffer.getvalue(), content_type="image/png")

            resultado.append({
                "arquivo_original": blob.name,
                "arquivo_final": nome_padronizado,
                "status": "processado"
            })
        except Exception as e:
            resultado.append({
                "arquivo_original": blob.name,
                "arquivo_final": "",
                "status": f"erro: {str(e)}"
            })

    relatorio_nome = gerar_relatorio(resultado)
    salvar_relatorio_no_bucket(relatorio_nome)
    enviar_telegram(relatorio_nome, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    return {"resultado": resultado, "relatorio": relatorio_nome}

def gerar_relatorio(registros):
    df = pd.DataFrame(registros)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    relatorio_nome = f"{RELATORIO_PROCESSAMENTO.replace('.csv', '')}-{timestamp}.csv"
    df.to_csv(relatorio_nome, index=False)
    return relatorio_nome

def salvar_relatorio_no_bucket(relatorio_nome):
    destino_bucket = client.bucket(BUCKET_DESTINO.split("/", 1)[0])
    destino_blob = destino_bucket.blob(BUCKET_DESTINO.split("/", 1)[1] + "/relatorios/" + relatorio_nome)
    with open(relatorio_nome, "rb") as f:
        destino_blob.upload_from_file(f, content_type="text/csv")