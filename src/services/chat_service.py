import re
from ..services.gpt_service import classificar_query
from ..utils.imagem import extrair_imageid
from ..database.operations import consultaDB, analizarDB
from ..services.gpt_service import requestGPT

def rota_query(user_input):
    query_type = classificar_query(user_input)

    if query_type == "EXACT_IMAGE":
        # Extract filename with regex
        image_id = extrair_imageid(user_input)
        return consultaDB(image_id)

    elif query_type == "SEMANTIC_SEARCH":
        return consultaDB(user_input)  # Your existing semantic search

    elif query_type == "DB_QUERY":
        return analizarDB(user_input)  # New analytics function
    
    else: #OUTROS 
        return requestGPT(user_input)

class Chat():

    def __init__(self) -> None:
        item_sessao = ""

        pass
    
    def set_itemSessao(self, documento):
        
        pass


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