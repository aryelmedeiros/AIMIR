import streamlit as st
from ..utils.imagem import salvar_imagem
from ..database.cliente import collection
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
    
   # Get sample metadata to determine available fields
    stats = {
        "total_images": collection.count(),
        "metadata_fields": set(),
        "sample_descriptions": []
    }
    
    # Analyze first 5 items (avoid loading entire collection)
    sample = collection.get(limit=5)
    
    if sample["metadatas"]:
        for meta in sample["metadatas"]:
            stats["metadata_fields"].update(meta.keys())
    
    if sample["documents"]:
        stats["sample_descriptions"] = [
            doc[:100] + "..." for doc in sample["documents"][:3]
        ]

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