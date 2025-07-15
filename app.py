import streamlit as st
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os 
from dotenv import load_dotenv
from PIL import Image
import tempfile
import hashlib
from src.database.operations import consultaDB
from src.database.cliente import ChromaDBClient
from src.services.arquivos_service import salvar_dados
from src.services.chat_service import ChatSessao, rota_query

load_dotenv()

sessao = ChatSessao()
# --- Streamlit UI ---
st.title("Assistente de Imagens Medicas 🩻")
st.caption("ℹ️ Faça uma pergunta sobre os dados armazenados ou passe o nome do arquivo que quira tratar")

with st.sidebar:
    st.title("Adicione Arquivos a Base de Dados 📑")
    st.caption("Adicione uma imagem associada de um arquivo de descrição (Audio ou Texto)")
    uploaded_image = st.file_uploader("Carregue a imagem", type=["jpg","png","jpeg"])
    uplaoded_description = st.file_uploader("Carregue o arquivo de descrição da imagem", type=["txt"])
    uploaded_audio = st.file_uploader("Carregue o arquivo de audio", type=["wav","mp3"])
    botao_enviar = st.button("💾 SALVAR")
    if st.button("⚠️ Apagar Todas Imagens Salvas"):
        if ChromaDBClient.clear_collection():
            st.success("Banco do Imagens Limpo")
        else:
            st.warning("Falha ao Limpar Banco de Imagens")

if botao_enviar:
    salvar_dados(uploaded_image,uploaded_audio,uplaoded_description)

if "session" not in st.session_state:
    st.session_state.session = ChatSessao()  

# Display chat
st.session_state.session.display_chat()

# User input
if prompt := st.chat_input("Faça uma consulta..."):
    
    st.session_state.session.add_message("user", prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Carregando..."):
            # Primeiro agente 
            response = rota_query(prompt, st.session_state.session)

            if response != None:
            
                st.session_state.session.add_message("assistant", response)
                st.markdown(response)

