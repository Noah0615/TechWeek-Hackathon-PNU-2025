import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

text_generation_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

for model in text_generation_models:
    print(model.name)