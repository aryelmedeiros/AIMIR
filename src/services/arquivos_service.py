import streamlit as st
import tempfile
import os
from PIL import Image

from src.services.transcricao_service import trascricao
from src.database.operations import salvarDB
from src.database.cliente import collection

def salvar_dados(uploaded_image, uploaded_audio, uplaoded_description):
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Imagem Enviada", use_container_width=True)

        if uploaded_audio is not None:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
                tmp_audio.write(uploaded_audio.read())
                audio_path = tmp_audio.name
            
            audio_transcription = trascricao(audio_path)

            os.unlink(audio_path)  # Deletar temp file

            st.write("**Transcrição:**", audio_transcription)

            try:
                salvarDB(uploaded_image,audio_transcription)
                st.success("Transcrição salva com Sucesso")
            except Exception as e:
                st.error("Não foi possivel salvar a transcriação no Banco de Dados")
                st.error(f"Error: {e}")

        elif uplaoded_description is not None:
            descricao = uplaoded_description.read().decode("utf-8")
            st.write("**Descrição inserida: :**", descricao)

            try:
                salvarDB(uploaded_image,descricao)
                st.success("Descrição salva com Sucesso")
            except Exception as e:
                st.error("Não foi possivel salvar a transcriação no Banco de Dados")
                st.error(f"Error: {e}")
        else:
            st.warning("Nenhuma Descrição (Audio ou Texto) Selecionada")
    else:
        st.warning("Nenhuma Imagem Selecionada")