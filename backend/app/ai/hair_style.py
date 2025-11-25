import os
import requests


HF_API_URL = "https://api-inference.huggingface.co/models/<modelo-de-cabelo>"  # exemplo: "dreamlike-art/dreamlike-photoreal-portrait"
HF_TOKEN = "<SEU_HUGGINGFACE_TOKEN>"

def edit_hair_style(file_path: str, style: str) -> bytes:
    """
    Função de teste para simular a IA.
    Apenas retorna os bytes da imagem original sem alterações.
    """
    file_path = file_path.replace("\\", "/")  # garante compatibilidade de caminhos no Windows
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with open(file_path, "rb") as f:
        return f.read()