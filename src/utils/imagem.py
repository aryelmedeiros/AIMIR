from PIL import Image
import re

def salvar_imagem(imagem):
    image_path = f"data/imagens/{imagem.name}"
    Image.open(imagem).save(image_path)
    return image_path

def extrair_imageid(user_input:str)->str:
    re.search(r"(image_?|img_?)?(\d+)", user_input, re.I).group() 