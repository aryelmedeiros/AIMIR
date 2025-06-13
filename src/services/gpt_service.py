from openai import OpenAI
from services.transcricao_service import openai_client
import hashlib
from src.database.operations import consultaDB, updateDB


def requestGPT(query:str, context):
    response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você deve responder as questões baseado nas trascrições de audio armazenadas do usuario."},
                {"role": "user", "content": f"Question: {query}\nContext: {context}"}
            ]
        )
    return response

def get_cached_response(query:str, image_id, collection):

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
