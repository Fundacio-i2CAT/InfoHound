import time
from infohound.models import People
from infohound.tool.ai_assistant import ollama

def summarize_profile(domain_id):
    queryset = People.objects.filter(domain_id=domain_id, ocupation_summary__contains="This profile doesn't have a description yet")

    for entry in queryset.iterator():
        try:
            summarize_prompt = "Summarize the ocupation of the person in just 150 words given the following data: "
            raw_data = entry.raw_metadata
            print ("Executing AI-Powered Profile Analisis of: " + entry.name)
            entry.ocupation_summary = ollama.ollama_flexible_prompt(summarize_prompt + raw_data)
            print ("Summary: " +entry.ocupation_summary)
            entry.save()
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
