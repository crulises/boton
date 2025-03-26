import os
from boton.review.azure_openai_reviewer import AzureOpenAIReviewer

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT")
LLM_API_KEY = os.getenv("LLM_API_KEY")
PROMPT_FILE = os.getenv("PROMPT_FILE")
REVIEWERS_DISPONIBLES = {
    # "deepseek": DeepSeekReviewer, # Ejemplo 
    "azure_openai": AzureOpenAIReviewer
    }