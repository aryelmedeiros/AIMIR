import streamlit as st
from PIL import Image
import re

def salvar_imagem(imagem):
    image_path = f"data/imagens/{imagem.name}"
    Image.open(imagem).save(image_path)
    return image_path

def get_imagem(imagem):
    image_path = f"data/imagens/{imagem}"
    image = Image.open(image_path)
    st.image(image, caption="Imagem Recuperada", use_container_width=True)
    return image_path

def extrair_imageid(user_input:str)->str:
    match = re.search(r"(Image_?|img_?)?(\d+)", user_input, re.I)
    
    if match:
        nome = match.group() + str(".jpg")
        return nome
    else:
        return ""