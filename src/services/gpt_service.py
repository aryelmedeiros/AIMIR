from openai import OpenAI
from src.services.transcricao_service import openai_client
import hashlib
#from src.database.operations import consultaDB, updateDB

def requestGPT(query:str, context, tokens_max = None):
    if tokens_max == None:
        response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você deve responder as questões baseado nas trascrições de audio armazenadas do usuario."},
                    {"role": "user", "content": f"Question: {query}\nContext: {context}"}
                ]
            )
    else: 
        response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você pode responder as questões baseado na descrição das imagens, quando possivel. Responda de maneira concisa"},
                    {"role": "user", "content": f"Question: {query}\nContext: {context}"}
                ],
                max_tokens= tokens_max
            )

    return response.choices[0].message.content.strip().upper()

def classificar_query(query:str):

    VALID_CATEGORIES = {"EXACT_IMAGE", "SEARCH_IMAGE", "DB_QUERY", "OTHER"}
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classifique a consulta em EXACT_IMAGE, SEARCH_IMAGE, DB_QUERY ou OTHER. "
                        "Responda APENAS com o nome da categoria, sem pontuação ou explicações.\n\n"
                        "EXEMPLOS:\n"
                        "'Mostre IMG_45' → EXACT_IMAGE\n"
                        "'Raio-X com cárie' → SEARCH_IMAGE\n"
                        "'Quantas imagens existem?' → DB_QUERY\n"
                        "'Explique cárie dentária' → OTHER"
                    )
                },
                {"role": "user", "content": query}
            ],
            temperature=0,
            max_tokens=5,
            logprobs=True  # confidence scores
        )
        
        # Validar Resposta
        category = response.choices[0].message.content.strip().upper()
        print(f"Categoria do Prompt: {category}")
        return category if category in VALID_CATEGORIES else "OTHER"
        
    except Exception as e:
        print(f"Classification error: {e}")
        return "OTHER"  
'''
def get_cached_response(query:str, image_id, collection):

    query_hash = hashlib.md5(query.encode()).hexdigest()
    metadata = consultaDB(query,collection,include_metadata=True)
   
        Talvez seja interessante utilizar primeiro o GPT para entender o tipo de requisição feita,
        caso se trate de uma chamada a uma imagem do banco pelo nome (Ex.: Image_00), uma pergunta 
        sobre algum dado do banco (Ex.: Quero uma imagem que apresente uma carie no dente 47) ou uma
        consulta sobre as informações do banco (Ex.: Quantas imgens apresentam carries)


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
'''