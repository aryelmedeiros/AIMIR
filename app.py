import streamlit as st
from loader import generate_answer
from pdf_loader import extract_text_from_pdf
from llm import SimpleRAG

# --- Streamlit UI ---
st.title("🧠📄 Pergunte a seus arquivos PDFs!")

# Upload PDF
uploaded_file = st.file_uploader("Carregar arquivo PDF", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    
    st.success(f"PDF carregado com sucesso! O documento contém {len(text)} caracteres.")
    
    # Question input
    question = st.text_input("Faça uma pergunta sobre o PDF:")
    
    if question:
        # For simplicity, we'll use the whole text as context
        # In a production app, you'd implement chunking and retrieval
        with st.spinner("Gerando resposta..."):
            answer = generate_answer(question, text[:3000])  # Limit context to 3000 chars
        
        st.subheader("Resposta:")
        st.write(answer)

