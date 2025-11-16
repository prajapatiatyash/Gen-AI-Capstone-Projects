import litellm
import os
from dotenv import load_dotenv
load_dotenv()
# Load from environment or config
AZURE_API_KEY = os.getenv("OPENAI_API_KEY")  # your Azure OpenAI key
AZURE_BASE_URL = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")


litellm.api_key = AZURE_API_KEY

def chat(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.4, max_tokens: int = 300):
    print("LLM Config:", AZURE_API_KEY, AZURE_BASE_URL, AZURE_API_VERSION)
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            # Azure-specific params
            base_url=AZURE_BASE_URL,
            api_version=AZURE_API_VERSION
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("LLM Error:", str(e))
        return " Sorry, something went wrong with LLM."

