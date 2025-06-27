import streamlit as st
from PIL import Image
import re

def salvar_imagem(imagem):
    image_path = f"data/imagens/{imagem.name}"
    print(image_path)
    Image.open(imagem).save(image_path)
    return image_path

def normalize_for_streamlit(image: Image.Image) -> Image.Image:
    if image.mode == "I;16":
        # Convert 16-bit grayscale to 8-bit
        image = image.point(lambda x: x * (255.0 / 65535)).convert("L")
    elif image.mode == "RGBA":
        image = image.convert("RGB")
    elif image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")  # fallback for other modes
    return image

def get_imagem(imagem):
    image_path = f"data/imagens/{imagem}"
    image = Image.open(image_path)
    image = normalize_for_streamlit(image)
    st.image(image, caption="Imagem Recuperada", use_container_width=True)
    return image_path

def extrair_imageid(user_input:str)->str:
    match = re.search(r"(Image_?|img_?)?(\d+)(\.(jpg|jpeg|png|webp))", user_input, re.I)
    
    if match:
        nome = match.group()
        return nome
    else:
        return ""