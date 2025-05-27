import streamlit as st
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os 
from dotenv import load_dotenv
from PIL import Image
import tempfile

from loader import generate_answer
from pdf_loader import extract_text_from_pdf
from llm import SimpleRAG


load_dotenv()

def trascricao(arquivo_path):
    with open(arquivo_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
    
    return transcription

def salvarDB(imagem, transcricao, collection):
    image_id = imagem.name
    collection.add(
        documents=[transcricao],
        ids=[image_id],
        metadatas=[{"image_name": image_id}]
    )

def RAG(query,collection):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    retrieved_text = results["documents"][0][0]

    return retrieved_text



openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
collection = chroma_client.get_or_create_collection(
    name="image_audio_data",
    embedding_function=openai_ef
)


# --- Streamlit UI ---
st.title("🧠📄 Faça perguntas sobre as imagens com base em audios!")

# Upload PDF
uploaded_image = st.file_uploader("Carregue a imagem", type=["jpg","png","jpeg"])
uplaoded_description = st.file_uploader("Carregue o arquivo de descrição da imagem", type=["txt"])
uploaded_audio = st.file_uploader("Carregue o arquivo de audio", type=["wav","mp3"])


if uploaded_image is not None:

    if uploaded_audio is not None:

        image = Image.open(uploaded_image)
        st.image(image, caption="Imagem Enviada", use_column_width=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(uploaded_audio.read())
            audio_path = tmp_audio.name
        
        audio_transcription = trascricao(audio_path)

        os.unlink(audio_path)  # Delete temp file

        st.write("**Transcrição:**", audio_transcription)

        try:
            salvarDB(uploaded_image,audio_transcription,collection)
            st.success("Transcrição salva com Sucesso")
        except Exception as e:
            st.error("Não foi possivel salvar a transcriação no Banco de Dados")

    elif uplaoded_description is not None:
        descricao = uplaoded_description.read().decode("utf-8")
        st.write("**Descrição inserida: :**", descricao)

        try:
            salvarDB(uploaded_image,descricao,collection)
            st.success("Descrição salva com Sucesso")
        except Exception as e:
            st.error("Não foi possivel salvar a transcriação no Banco de Dados")


    query = st.text_input("Faça uma pergunta sobre os dados armazenados ou passe o nome do arquivo que quira tratar")

    if query:
        resultado = RAG(query,collection)

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você deve responder as questões baseado nas trascrições de audio armazenadas do usuario."},
                {"role": "user", "content": f"Question: {query}\nContext: {resultado}"}
            ]
        )
        st.write("**Resposta:**", response.choices[0].message.content)
