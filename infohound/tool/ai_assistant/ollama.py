from langchain_community.llms import Ollama
from infohound_project.settings import OLLAMA_URL, OLLAMA_MODEL

def ollama_flexible_prompt(in_prompt):
    ollama = Ollama(base_url=OLLAMA_URL, model=OLLAMA_MODEL)

    try:
        res = ollama(in_prompt)
        return res
    except Exception as e:
        print(f"Error en la llamada a Ollama: {e}")
        return None
