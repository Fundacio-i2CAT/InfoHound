from ollama import Client
from infohound_project.settings import OLLAMA_URL,OLLAMA_MODEL

def check_or_pull_model(client):
    models = client.list()
    present = False
    for model in models["models"]:
        if OLLAMA_MODEL == model["name"].split(":")[0]:
            present = True
    if not present:
        client.pull(OLLAMA_MODEL)

def ollama_flexible_prompt(in_prompt):
    client = Client(host=OLLAMA_URL)
    check_or_pull_model(client)
    desc = None
    try:
        res = client.generate(model=OLLAMA_MODEL,prompt=in_prompt)
    except Exception as e:
        print(f"Could not call Ollama instance: {e}")

    if "response" in res:
        desc = res["response"].strip()
    return desc
