import google.generativeai as genai
from config import settings

if not settings.gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=settings.gemini_api_key)

model = genai.GenerativeModel(settings.gemini_model)

def ask_chatbot(context, user_question):
    prompt = f"""
{context}

USER QUESTION:
{user_question}

ANSWER:
"""
    response = model.generate_content(prompt)
    return response.text
