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

load_dotenv()
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

if botao_enviar:
    salvar_dados(uploaded_image,uploaded_audio,uplaoded_description)

if st.button("⚠️ Apagar Imagens Salvas"):
    if ChromaDBClient.clear_collection():
        st.success("Banco do Imagens Limpo")
    else:
        st.warning("Falha ao Limpar Banco de Imagens")

# Upload PDF

query = st.text_input("Faça uma pergunta sobre os dados armazenados ou passe o nome do arquivo que quira tratar")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display historical messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("Say something..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simulate an AI response (replace with your actual LLM logic)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Your AI model call would go here
            response = f"Echo: {prompt}" # Simple echo for demonstration
            st.markdown(response)
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if query:
    resultado = consultaDB(query)

    caminho = resultado.get("image_path", {})
    id = resultado.get("image_name", {})

    img = Image.open(caminho)

    st.image(img, caption=id)

    #response = get_cached_response(query,id,collection)
    response= ""


    #resultado = RAG(query,collection)
# st.write("**Resposta:**", response.choices[0].message.content)
