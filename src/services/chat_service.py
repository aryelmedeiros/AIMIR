import streamlit as st
from datetime import datetime
from ..services.gpt_service import classificar_query
from ..utils.imagem import extrair_imageid
from ..database.operations import consultaDB, analizarDB
from ..services.gpt_service import requestGPT
from ..utils.imagem import get_imagem

class ChatSessao():

    def __init__(self):
        self.current_image_id = None  
        self.current_description = None  #description/transcription
        self._history = []  # Historico de conversas

    def add_message(self, role: str, content: str):
        
        self._history.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })

    def display_chat(self):
        
        for msg in self._history:
            #print("Carregou")
            if isinstance(msg, dict) and "role" in msg:
                with st.chat_message(msg["role"]):
                    if "image" in msg and msg["image"] is not None:
                        get_imagem(msg["image"])
                    st.markdown(msg.get("content", ""))
                    if "time" in msg:
                        st.caption(msg["time"][11:19])  # Show HH:MM:SS
            else:
                st.warning(f"Invalid message format: {msg}")

    def update_context(self, image_id: str, description: str):
        
        self.current_image_id = image_id
        self.current_description = description
        st.success(f"Contexto atual: {image_id} - {description[:50]}...")
        self._history.append({
            "role": "system", 
            "content": f"Contexto atual: {image_id} \n {description}",
            "time": datetime.now().isoformat(),
            "image": image_id
        })


    def clear_image_context(self):
        self.current_image_id = None
        self.current_description = None

    @property
    def context_active(self) -> bool:
        return self.current_image_id is not None

def rota_query(user_input, sessao:ChatSessao):
    query_type = classificar_query(user_input)

    if query_type == "EXACT_IMAGE":
        # Regex
        image_id = extrair_imageid(user_input)

        st.success("Requisição por imagem")

        resultado = consultaDB(image_id)
        #print(resultado)
        #print(f"ID Da imagem: {resultado['image_name']}")
        sessao.update_context(resultado['image_name'],resultado['description'])

        get_imagem(resultado['image_name'])
        st.write(f"**Descrição: ** {resultado['description']}")

        return None

    elif query_type == "SEARCH_IMAGE":

        resultado = consultaDB(user_input)
        print(resultado)

        sessao.update_context(resultado['image_name'],resultado['description'])
        get_imagem(resultado['image_name'])
        st.write(f"**Descrição: ** {resultado['description']}")

        return None 

    elif query_type == "DB_QUERY":
        #return analizarDB(user_input)  
        return "  "
    else: #OUTROS 
        #requestGPT(user_input)
        return requestGPT(user_input,sessao.current_description,tokens_max=60)
        #sessao.add_message(role="assistant", content= requestGPT(user_input,sessao.current_description,tokens_max=20))


'''

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Prompt do usuario
if prompt := st.chat_input("Faça uma consulta..."):
    # Add prompt ao historico
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Apresentar mensagem do usuarip
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

O chat deverá ter uma classe Sessão, com um objeto que represente o item da coleção tratado nos prompts.
Caso seja feita uma consulta EXACT_IMAGE ou SEMATIC o item deve ser atribuido e deve permancer até que una dessas novas consultas sejam feitas

'''