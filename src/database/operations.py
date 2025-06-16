import streamlit as st
from ..utils.imagem import salvar_imagem
from ..database.cliente import collection
from ..services.gpt_service import requestGPT

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

    try:
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
        n_results=1,
        include=["metadatas"] if include_metadata else ["metadatas","documents"]
    )

    if include_metadata:
        print(results)
        return results["metadatas"][0][0]  
    else:
        st.success("Pesquisa OK")
        print(results)
        return {
            "image_name": results["metadatas"][0][0]["image_name"],
            "image_path": results["metadatas"][0][0]["image_path"],
            "description": results["documents"][0][0]
        }

def analizarDB(query:str, include_metadata: bool = False, include_documents: bool = True):
    
    prompt = f"""Responda baseado nesse database schema:
    - Images: {collection.count()}
    - Metadata fields: {collection.metadata_keys}
    
    Question: {query}
    """
    requestGPT(prompt)

##PRECIOS ATUALIZAR 
    return

def get_transcricao(query:str):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    retrieved_text = results["documents"][0][0]

    return retrieved_text