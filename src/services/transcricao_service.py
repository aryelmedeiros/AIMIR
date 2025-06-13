from openai import OpenAI
from config import settings

openai_client = OpenAI(api_key=settings.openai_api_key)

def trascricao(arquivo_path):
    with open(arquivo_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
    
    return transcription