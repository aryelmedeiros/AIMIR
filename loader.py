import streamlit as st
import requests

API_KEY = "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"

# Configuration
MODEL_NAME = "google/flan-t5-large"  # Can replace with DeepSeek model
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()

def generate_answer(question, context):
    prompt = f"""Use the following context to answer the question. If you don't know the answer, say so.

Context:
{context}

Question: {question}
Answer:"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }
    
    output = query_huggingface(payload)
    
    if "error" in output:
        # Show the detailed error in your Streamlit app
        st.error(f"API Error: {output['error']}")
        st.text(f"Details: {output.get('details', 'No details')}")
        return "Sorry, I couldn't generate an answer due to an API error."
    
    # Handle different response formats from different models
    if isinstance(output, list):
        if len(output) > 0 and 'generated_text' in output[0]:
            full_response = output[0]['generated_text']
            return full_response.split("Answer:")[-1].strip()
    
    return "Sorry, I couldn't generate an answer. (Unexpected response format)"
