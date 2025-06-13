import streamlit as st
from ..utils.imagem import salvar_imagem
from ..database.cliente import collection

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

def get_transcricao(query:str):

    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    retrieved_text = results["documents"][0][0]

    return retrieved_text