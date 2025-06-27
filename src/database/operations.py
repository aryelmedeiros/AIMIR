import streamlit as st
import hashlib
from ..utils.imagem import salvar_imagem
from ..database.cliente import collection, cag
from ..services.gpt_service import requestGPT, requestGPT_DB

def salvarDB(imagem, transcricao):
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

def updateDB(image_id, cache, metadata):
     collection.update(
        ids=[image_id],
        metadatas=[{**metadata, "cache": cache}]
    )

def consultaDB(query:str,  include_metadata: bool = False, include_documents: bool = True ):

    try: #consulta por ID
        result = collection.get(ids=[query], include=["metadatas", "documents"])
        if result["ids"]:  # encontrou
            #st.success("Encontrado")
            return {
                "type": "match_id",
                "image_name": result["metadatas"][0]["image_name"],
                "image_path": result["metadatas"][0]["image_path"],
                "description": result["documents"][0]
            }
    except Exception:
        st.warning(f"Imagem de Id {query} não encontrada")
        pass 
    
    st.success("Consulta Semantica")
    results = collection.query(
        query_texts=[query],
        n_results=10,
        include=["metadatas"] if include_metadata else ["metadatas", "documents", "distances"]
    )

    if include_metadata:
        print(results)
        print("\n")
        return results["metadatas"][0][0]  
    else:
        st.success("Pesquisa OK")

        matches = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            print(f'A distancia é de: {distance}, mas a similaridade é de {1-distance}')
            if distance <= 1.39:  #valor que se distancia
                match = {
                    "image_id": results["ids"][0][i],
                    "image_name": results["metadatas"][0][i]["image_name"],
                    "image_path": results["metadatas"][0][i].get("image_path"),
                    "descricao": results["documents"][0][i], 
                    "distance": distance,
                    "similarity": 1 - distance  # Convert to similarity score (0-1)
                }
                matches.append(match)
        
        return matches

def analizarDB(query:str, include_metadata: bool = False, include_documents: bool = True):
    
   # Amostra dos campos de metadata
    stats = {
        "total_images": collection.count(),
        "metadata_fields": set(),
        "sample_descriptions": []
    }
    
    #
    #sample = collection.get(limit=5)

    todas = collection.get()

    if todas["documents"]:
        stats["sample_descriptions"] = [
            doc[:100] + "..." if len(doc) > 100 else doc
            for doc in todas["documents"]
        ]

    if todas["metadatas"]:
        for meta in todas["metadatas"]:
            if meta:  # Check if metadata is not None
                stats["metadata_fields"].update(meta.keys())
                
    '''
    if sample["metadatas"]:
        for meta in sample["metadatas"]:
            stats["metadata_fields"].update(meta.keys())
    
    if sample["documents"]:
        stats["sample_descriptions"] = [
            doc[:100] + "..." for doc in sample["documents"][:3]
        ]
    '''

    prompt = f"""
    Responda de maneira consisa a pergunta com as infos do DB abaixo, importante mencionar na resposta que é uma estimativa caso a resposta não se trate do 'Total Entries' :
    - Total Entries: {stats['total_images']}
    - Metadata Fields: {', '.join(stats['metadata_fields']) or 'None'}
    - Sample Descriptions: {stats['sample_descriptions']}
    
    User Question: {query}
    """
    #print(prompt)

    resposta = requestGPT_DB(prompt)

    return resposta

def get_transcricao(query:str):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    retrieved_text = results["documents"][0][0]

    return retrieved_text

def _hash_prompt(prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

def get_cashed_response(prompt:str, threshold: float = 0.92, image_name:str = None):

    try: #consulta por ID
        #print(prompt+image_name)
        prompt_id = _hash_prompt(prompt+image_name)
        #print(prompt_id)
        result = cag.get(ids=[prompt_id], include=["metadatas", "documents"])
        #print(f'IDs: {result}')
        if result["ids"]: 
            #print("CAG")
            #print(result["documents"])
            return result["documents"][0] # encontrou

    except Exception as e :
        print(e)
        pass

    result = cag.query(
        query_texts=[prompt],
        n_results=1,
        include=["documents", "metadatas"],
        #where={"image_name": {"$eq": image_name}} if image_name else {}
    )
    #print("Resultado: ")
    #print(result)

    if result["documents"] and result["distances"]:
        if result["documents"] and result["distances"][0][0] < (1 - threshold):
            print("💾 Cache hit")
            return result["documents"][0][0]

    return None

def store_cashed_response(prompt:str, response:str, image_name:str = None):

    #print(prompt)
        
    prompt_id = _hash_prompt(prompt+image_name)
    #print(prompt_id)

    if image_name: #prompt associado a imagem
        cag.add(
            ids=[prompt_id],
            documents=[response],
            metadatas=[{"prompt": prompt}]
        )
        print("Resposta salva")

        #result = cag.get(ids=[prompt_id], include=["documents", "metadatas"])
        #print("✅ Post-add get():", result)
    else: 
        cag.add(
            ids=[prompt_id],
            documents=[response],
            metadatas=[{"prompt": prompt,}]
        )