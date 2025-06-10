import re
import pandas as pd
import requests

def padronizar_nome(nome_original, shop_df, autoral_df):
    nome_base = nome_original.lower()
    nome_base = re.sub(r"[^a-z0-9\-_]", "-", nome_base)
    nome_base = nome_base.replace("_", "-")

    sku_udc = re.findall(r"\d{4}-\d{2}", nome_base)
    sku_udc = sku_udc[0] if sku_udc else "xxxxx"

    linha = shop_df[shop_df['sku'] == sku_udc]
    if linha.empty:
        linha = autoral_df[autoral_df['sku'] == sku_udc]

    sku_forn = linha['cod_fabricante'].values[0] if not linha.empty and 'cod_fabricante' in linha else 'xxxxx'
    gtin = linha['gtin'].values[0] if not linha.empty and 'gtin' in linha else 'xxxxx'
    desc_a = linha['descricao_a'].values[0] if not linha.empty and 'descricao_a' in linha else 'xxxxx'
    modelo = linha['modelo'].values[0] if not linha.empty and 'modelo' in linha else 'xxxxx'
    desc_b = linha['descricao_b'].values[0] if not linha.empty and 'descricao_b' in linha else 'xxxxx'
    desc_c = linha['descricao_c'].values[0] if not linha.empty and 'descricao_c' in linha else 'xxxxx'
    funcao = linha['funcao'].values[0] if not linha.empty and 'funcao' in linha else 'xxxxx'

    def formatar(txt):
        return re.sub(r"[^a-z0-9]+", "-", str(txt).lower()).strip("-")

    nome_final = f"{sku_udc}-{formatar(sku_forn)}-{formatar(gtin)}-copia-proibida-{formatar(desc_a)}-{formatar(modelo)}-{formatar(desc_b)}-{formatar(desc_c)}-{formatar(funcao)}-universo-da-chama-calipe.png"
    return nome_final

def enviar_telegram(caminho_arquivo, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(caminho_arquivo, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id}
        try:
            requests.post(url, data=data, files=files)
        except Exception as e:
            print("Erro ao enviar Telegram:", str(e))