from langchain_community.llms import Ollama
from infohound_project import settings

def ollama_flexible_prompt(in_prompt):
    BASE_URL = "http://172.26.0.3:11434"
    MODEL = "llama2"

    ollama = Ollama(base_url=BASE_URL, model=MODEL)

    try:
        res = ollama(in_prompt)
        return res
    except Exception as e:
        print(f"Error en la llamada a Ollama: {e}")
        return None
