import streamlit as st
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
import os 
from dotenv import load_dotenv
from PIL import Image
import tempfile
import hashlib


load_dotenv()

def trascricao(arquivo_path):
    with open(arquivo_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
    
    return transcription

def salvar_imagem(imagem):
    image_path = f"data/imagens/{imagem.name}"
    Image.open(imagem).save(image_path)
    return image_path

def salvarDB(imagem, transcricao, collection):
    image_path = salvar_imagem(imagem)
    image_id = imagem.name
    st.success(str(image_path))
    collection.add(
        documents=[transcricao],
        ids=[image_id],
        metadatas=[{"image_name": image_id,
                    "image_path": str(image_path),
                    "cahce": ""
        }]
    )

def updateDB(image_id, cache, collection, metadata):
     collection.update(
        ids=[image_id],
        metadatas=[{**metadata, "cache": cache}]
    )

def consultaDB(query, collection,  include_metadata: bool = False, include_documents: bool = True ):

    try:
        result = collection.get(ids=[query], include=["metadatas", "documents"])
        if result["ids"]:  # encontrou
            return {
                "type": "match_id",
                "image_name": result["metadatas"][0]["image_name"],
                "image_path": result["metadatas"][0]["image_path"],
                "description": result["documents"][0]
            }
    except Exception:
        pass 

    results = collection.query(
        query_texts=[query],
        n_results=1,
        include=["metadatas"] if include_metadata else ["documents"]
    )

    if include_metadata:
        return results["metadatas"][0][0]  
    else:
        return results["documents"][0][0] 


def get_transcricao(query,collection):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    retrieved_text = results["documents"][0][0]

    return retrieved_text

def requestGPT(query, context):
    response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você deve responder as questões baseado nas trascrições de audio armazenadas do usuario."},
                {"role": "user", "content": f"Question: {query}\nContext: {context}"}
            ]
        )
    return response

def get_cached_response(query, image_id, collection):

    query_hash = hashlib.md5(query.encode()).hexdigest()
    metadata = consultaDB(query,collection,include_metadata=True)

    #Precisa verificar se o arquivo foi encontrado por ID ou por query, 
    # caso seja por ID da a opção de addicionar uma pergunta sobre os dados
    # caso seja por Query, é verificado se a pergunta está em cache 
    #       caso não esteja em cahce, é requisitada ao GPT
    #       caso esteja, será retornado a resposta associada.
    
    # Verifica o cache
    cache = metadata.get("cache", {})
    if query_hash in cache:
        return cache[query_hash] 

    response = requestGPT(query,metadata)

    # Update cache in ChromaDB
    cache[query_hash] = response.choices[0].message.content
    updateDB(image_id,cache,collection,metadata)
    
    return response



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
with st.sidebar:
    st.title("Adicione Arquivos a Base de Dados 📑")
    st.caption("Adicione uma imagem associada de um arquivo de descrição (Audio ou Texto)")
    uploaded_image = st.file_uploader("Carregue a imagem", type=["jpg","png","jpeg"])
    uplaoded_description = st.file_uploader("Carregue o arquivo de descrição da imagem", type=["txt"])
    uploaded_audio = st.file_uploader("Carregue o arquivo de audio", type=["wav","mp3"])
    botao_enviar = st.button("💾 SALVAR")

st.title("Assistente de Imagens Medicas 🩻")
st.caption("ℹ️ Faça uma pergunta sobre os dados armazenados ou passe o nome do arquivo que quira tratar")

if st.button("⚠️ Delete Entire Collection"):
    try:
        chroma_client.delete_collection("image_audio_data")
        st.success("Collection deleted!") 
        collection = chroma_client.get_or_create_collection(
            name="image_audio_data",
            embedding_function=openai_ef
        )
        st.success("Collection created!")

    except Exception as e:
        st.error(f"Error: {e}")

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

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Imagem Enviada", use_container_width=True)

    if uploaded_audio is not None:

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
            st.error(f"Error: {e}")

    elif uplaoded_description is not None:
        descricao = uplaoded_description.read().decode("utf-8")
        st.write("**Descrição inserida: :**", descricao)

        try:
            salvarDB(uploaded_image,descricao,collection)
            st.success("Descrição salva com Sucesso")
        except Exception as e:
            st.error("Não foi possivel salvar a transcriação no Banco de Dados")
            st.error(f"Error: {e}")


    

    if query:
        resultado = consultaDB(query, collection)

        caminho = resultado.get("image_path", {})
        id = resultado.get("image_name", {})

        img = Image.open(caminho)

        st.image(img, caption=id)

        #response = get_cached_response(query,id,collection)
        response= ""


        #resultado = RAG(query,collection)
       # st.write("**Resposta:**", response.choices[0].message.content)
