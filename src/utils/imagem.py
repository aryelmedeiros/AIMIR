from PIL import Image

def salvar_imagem(imagem):
    image_path = f"data/imagens/{imagem.name}"
    Image.open(imagem).save(image_path)
    return image_path